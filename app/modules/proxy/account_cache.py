from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import anyio
from sqlalchemy import select

from app.core.balancer import reauth_reason_blocks_routing
from app.core.cache.invalidation import (
    NAMESPACE_ACCOUNT_ROUTING,
    NAMESPACE_ACCOUNT_SELECTION,
    get_cache_invalidation_poller,
)
from app.core.clock import REAL_CLOCK, Clock
from app.core.config.settings import get_settings
from app.core.crypto import TokenEncryptor
from app.core.metrics import prometheus as metrics
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal, close_session
from app.modules.proxy.account_eligibility import (
    ROUTABLE_STATUSES,
    reauth_access_token_is_expired,
    stored_access_token_expires_at,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.modules.proxy.load_balancer import SelectionInputs

_AssignedAccountsKey = tuple[str, ...] | None
_CacheKey = tuple[str | None, str | None, str | None, str, _AssignedAccountsKey]


@dataclass(slots=True)
class _CachedSelectionInputs:
    data: SelectionInputs
    expires_at: float


class AccountSelectionCache:
    def __init__(self, ttl_seconds: int | None = None) -> None:
        if ttl_seconds is None:
            import sys

            ttl_seconds = 0 if "pytest" in sys.modules else 5
        if ttl_seconds < 0:
            raise ValueError("ttl_seconds must be non-negative")
        self._ttl_seconds = ttl_seconds
        self._cache: dict[_CacheKey, _CachedSelectionInputs] = {}
        self._lock = anyio.Lock()
        self._generation: int = 0

    @property
    def generation(self) -> int:
        return self._generation

    async def get(self, key: _CacheKey = (None, None, None, "", None)) -> SelectionInputs | None:
        if self._ttl_seconds == 0:
            return None
        entry = self._cache.get(key)
        if entry is None:
            return None
        if time.monotonic() >= entry.expires_at:
            return None
        return entry.data

    async def set(
        self,
        data: SelectionInputs,
        key: _CacheKey = (None, None, None, "", None),
        *,
        generation: int | None = None,
    ) -> None:
        async with self._lock:
            if generation is not None and generation != self._generation:
                return
            self._cache[key] = _CachedSelectionInputs(
                data=data,
                expires_at=time.monotonic() + self._ttl_seconds,
            )

    def invalidate(self, *, propagate: bool = True) -> None:
        """Invalidate the local cache and, unless ``propagate`` is False, enqueue a
        coalesced cross-replica ``account_selection`` bump.

        The cache-invalidation poller callback registers ``propagate=False`` so a
        remote bump never re-bumps (feedback-loop prevention).
        """
        self._generation += 1
        self._cache.clear()
        if propagate:
            poller = get_cache_invalidation_poller()
            if poller is not None:
                poller.request_bump(NAMESPACE_ACCOUNT_SELECTION)


_ROUTING_UNAVAILABLE_STATUSES = frozenset(
    {
        AccountStatus.PAUSED,
        AccountStatus.DEACTIVATED,
    }
)


def _routing_entry_unavailable(entry: tuple[AccountStatus, str | None] | None) -> bool:
    if entry is None:
        return True
    status, reason = entry
    return status in _ROUTING_UNAVAILABLE_STATUSES or reauth_reason_blocks_routing(reason)


class RoutingAvailabilityCache:
    """Cluster-coherent view of which accounts are unavailable for routing.

    The cache keeps committed account statuses and authentication-failure reasons
    seeded at poller start and rebuilt on every ``account_routing`` bump. An account is
    routing-unavailable when paused, deactivated, or proven authentication-invalidated, or the id
    is absent from the snapshot (deleted), or a local mark
    overlay entry exists (covering the same-replica window between a mark and the
    snapshot rebuild). RATE_LIMITED and QUOTA_EXCEEDED deliberately do NOT map to
    unavailable, preserving cooldown-state bridge-session reuse.

    When the snapshot is unseeded (unit tests, poller not running) the cache degrades
    to the historical process-local set semantics.
    """

    def __init__(self, session_factory: Callable[[], AsyncSession] | None = None, *, clock: Clock = REAL_CLOCK) -> None:
        self._session_factory = session_factory
        self._clock = clock
        self._snapshot: dict[str, tuple[AccountStatus, str | None]] | None = None
        self._local_marks: set[str] = set()
        self._pending_persist_marks: set[str] = set()
        self._generation = 0
        self._repair_generations: dict[str, int] = {}
        self._refresh_lock = anyio.Lock()

    def generation_for_account(self, account_id: str) -> int:
        return self._repair_generations.get(account_id, 0)

    @property
    def seeded(self) -> bool:
        return self._snapshot is not None

    def mark_unavailable(self, account_id: str, *, generation: int | None = None) -> None:
        # Only same-account repair supersedes a guarded write's local mark.
        # A snapshot may have read before it committed. Always reconcile afterward.
        if generation is None or generation == self.generation_for_account(account_id):
            self._local_marks.add(account_id)
            self._record_metrics()
        _request_account_routing_bump()

    def mark_unavailable_pending_persist(self, account_id: str) -> None:
        """Keep a local routing block until its durable status is observed."""
        self._local_marks.add(account_id)
        self._pending_persist_marks.add(account_id)
        self._record_metrics()
        _request_account_routing_bump()

    def clear_unavailable(self, account_id: str) -> None:
        self._generation += 1
        self._repair_generations[account_id] = self._generation
        self._local_marks.discard(account_id)
        self._pending_persist_marks.discard(account_id)
        if self._snapshot is not None:
            self._snapshot[account_id] = (AccountStatus.ACTIVE, None)
        self._record_metrics()
        _request_account_routing_bump()

    def is_unavailable(self, account_id: str) -> bool:
        if account_id in self._local_marks:
            return True
        snapshot = self._snapshot
        if snapshot is None:
            return False
        return _routing_entry_unavailable(snapshot.get(account_id))

    def is_locally_unavailable(self, account_id: str) -> bool:
        return account_id in self._local_marks

    async def refresh_from_db(self) -> None:
        """Publish cache and metric observations in database-read order."""
        # Scrapes and invalidations can overlap. Serialize their reads and
        # publication so a slower old read cannot overwrite a newer snapshot.
        async with self._refresh_lock:
            await self._refresh_from_db()

    async def _refresh_from_db(self) -> None:
        """Rebuild the snapshot from committed account statuses.

        Local overlay marks whose committed status became routable again are dropped —
        this is what lets a reactivation or re-authentication served by another replica
        clear this replica's marker without a restart. Only marks that already existed
        when this refresh started are eligible to be dropped: a mark added while the
        SELECT is in flight may not be reflected in the rows it read (the status commit
        can land after the read), so filtering it against that snapshot would silently
        lose the mark. Such marks are preserved and re-evaluated by the next refresh,
        which the mark's own queued ``account_routing`` bump guarantees. Marks created
        while a keyed stream's durable health write is pending remain until a refresh
        observes the committed blocking status.

        Database errors propagate to the caller: when invoked as an
        ``account_routing`` invalidation callback the poller then leaves the
        namespace version unacknowledged and retries on the next poll cycle, so
        a transient failure cannot make a replica permanently miss a pause,
        deletion, or deactivation.
        """
        marks_before_refresh = frozenset(self._local_marks)
        factory = self._session_factory or SessionLocal
        session = factory()
        publish_metrics = metrics.PROMETHEUS_AVAILABLE and get_settings().metrics_enabled
        counts = dict.fromkeys(AccountStatus, 0)
        available = 0
        try:
            if publish_metrics:
                result = await session.execute(
                    select(
                        Account.id,
                        Account.status,
                        Account.deactivation_reason,
                        Account.access_token_encrypted,
                        Account.delete_requested_at,
                    )
                )
                rows = result.all()
                snapshot: dict[str, tuple[AccountStatus, str | None]] = {
                    (row.id if hasattr(row, "id") else row[0]): (
                        (row.status if hasattr(row, "status") else row[1]),
                        (
                            row.deactivation_reason
                            if hasattr(row, "deactivation_reason")
                            else (row[2] if len(row) > 2 else None)
                        ),
                    )
                    for row in rows
                }
                encryptor: TokenEncryptor | None = None
                now = self._clock.time()
                for row in rows:
                    if getattr(row, "delete_requested_at", None) is not None:
                        continue
                    status = row.status if hasattr(row, "status") else row[1]
                    counts[status] += 1
                    if status not in ROUTABLE_STATUSES:
                        continue
                    expires_at = None
                    if status == AccountStatus.REAUTH_REQUIRED:
                        if encryptor is None:
                            encryptor = TokenEncryptor()
                        enc = getattr(row, "access_token_encrypted", None)
                        expires_at = stored_access_token_expires_at(enc, encryptor)
                    account_id = row.id if hasattr(row, "id") else row[0]
                    available += not reauth_access_token_is_expired(
                        status, expires_at, now=now, deactivation_reason=snapshot[account_id][1]
                    )
            else:
                result = await session.execute(select(Account.id, Account.status, Account.deactivation_reason))
                snapshot = {account_id: (status, reason) for account_id, status, reason in result.all()}
        finally:
            await close_session(session)
        self._snapshot = snapshot
        self._pending_persist_marks = {
            account_id
            for account_id in self._pending_persist_marks
            if (entry := snapshot.get(account_id)) is not None and not _routing_entry_unavailable(entry)
        }
        self._local_marks = {
            account_id
            for account_id in self._local_marks
            if account_id in self._pending_persist_marks
            or account_id not in marks_before_refresh
            or _routing_entry_unavailable(snapshot.get(account_id))
        }
        if publish_metrics:
            assert metrics.accounts_total is not None
            assert metrics.accounts_available is not None
            for status, count in counts.items():
                metrics.accounts_total.labels(status=status.value).set(count)
            metrics.accounts_available.set(available)

    def reset(self) -> None:
        """Drop snapshot and marks without forgetting in-flight repair fences."""
        self._snapshot = None
        self._local_marks.clear()
        self._pending_persist_marks.clear()
        if metrics.PROMETHEUS_AVAILABLE and get_settings().metrics_enabled:
            if metrics.accounts_total is not None:
                for status in AccountStatus:
                    metrics.accounts_total.labels(status=status.value).set(0)
            if metrics.accounts_available is not None:
                metrics.accounts_available.set(0)

    def _record_metrics(self) -> None:
        try:
            from app.core.metrics.prometheus import record_account_metrics
        except ImportError:
            return

        if self._snapshot is None:
            record_account_metrics({})
            return

        statuses = {aid: entry[0] for aid, entry in self._snapshot.items()}
        unavailable_ids = {aid for aid in self._snapshot if self.is_unavailable(aid)}
        record_account_metrics(statuses, routing_unavailable_ids=unavailable_ids)


_account_selection_cache = AccountSelectionCache()
_routing_availability_cache = RoutingAvailabilityCache()


def get_account_selection_cache() -> AccountSelectionCache:
    return _account_selection_cache


def get_routing_availability_cache() -> RoutingAvailabilityCache:
    return _routing_availability_cache


def _request_account_routing_bump() -> None:
    poller = get_cache_invalidation_poller()
    if poller is not None:
        poller.request_bump(NAMESPACE_ACCOUNT_ROUTING)


def mark_account_routing_unavailable(account_id: str, *, generation: int | None = None) -> None:
    _routing_availability_cache.mark_unavailable(account_id, generation=generation)


def mark_account_routing_unavailable_pending_persist(account_id: str) -> None:
    _routing_availability_cache.mark_unavailable_pending_persist(account_id)


def clear_account_routing_unavailable(account_id: str) -> None:
    _routing_availability_cache.clear_unavailable(account_id)


def clear_all_account_routing_unavailable() -> None:
    _routing_availability_cache.reset()


def is_account_routing_unavailable(account_id: str) -> bool:
    return _routing_availability_cache.is_unavailable(account_id)


def is_account_locally_routing_unavailable(account_id: str) -> bool:
    return _routing_availability_cache.is_locally_unavailable(account_id)


async def propagate_account_routing_change() -> bool:
    """Durably bump the ``account_routing`` namespace before returning.

    Used by API-endpoint mutation paths (pause/reactivate/delete, OAuth re-auth,
    proxy-binding reactivation) so the cross-replica signal is written before the
    HTTP response returns. Returns False when no poller is wired or the bump failed
    after retries; the coalesced bump enqueued by ``mark_``/``clear_`` remains the
    fallback path.
    """
    poller = get_cache_invalidation_poller()
    if poller is None:
        return False
    return await poller.bump(NAMESPACE_ACCOUNT_ROUTING)
