from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RequestPersistenceActivitySnapshot(BaseModel):
    model_config = ConfigDict(extra="ignore", strict=True)

    request_persistence_pending: int = Field(ge=0)
    request_persistence_active: bool
    api_key_settlements_pending: int = Field(ge=0)
    persistence_drain_active: bool

    @model_validator(mode="after")
    def consistent_ownership(self) -> Self:
        active = self.request_persistence_pending > 0
        if self.request_persistence_active != active or self.persistence_drain_active != active:
            raise ValueError("Persistence activity flags disagree with the owner count")
        if self.api_key_settlements_pending > self.request_persistence_pending:
            raise ValueError("Settlement owners exceed total persistence owners")
        return self

    @property
    def state(self) -> str:
        return "pending" if self.request_persistence_active else "drained"


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str


class BridgeRingInfo(BaseModel):
    model_config = ConfigDict(extra="ignore")

    ring_fingerprint: str | None = None
    ring_size: int = 0
    instance_id: str | None = None
    is_member: bool = False
    error: str | None = None


class HealthCheckResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    status: str
    checks: dict[str, str] | None = None
    bridge_ring: BridgeRingInfo | None = None
