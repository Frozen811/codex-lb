"""Helper to reconcile status labels on issues and PRs upon comment activity."""

from __future__ import annotations

from collections.abc import Sequence


def reconcile_labels_on_comment(
    *,
    current_labels: Sequence[str],
    commenter: str,
    author: str,
    is_bot: bool,
    is_pr: bool = False,
) -> tuple[list[str], list[str]]:
    """Determine which labels to add and which to remove on comment activity.

    Returns:
        (labels_to_add, labels_to_remove)
    """
    if is_bot:
        return [], []

    labels_set = set(current_labels)
    to_remove: list[str] = []
    to_add: list[str] = []

    if "needs-info" in labels_set:
        to_remove.append("needs-info")
        if "stale" in labels_set:
            to_remove.append("stale")

        next_status = "awaiting-review" if is_pr else "triage"
        if next_status not in labels_set and "in-progress" not in labels_set:
            to_add.append(next_status)

    return to_add, to_remove
