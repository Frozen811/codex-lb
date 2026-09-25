from __future__ import annotations

import pytest

from scripts.reconcile_status_labels import reconcile_labels_on_comment

pytestmark = pytest.mark.unit


def test_reconcile_issue_needs_info_removes_and_adds_triage() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["bug", "needs-info"],
        commenter="reporter1",
        author="reporter1",
        is_bot=False,
        is_pr=False,
    )
    assert to_remove == ["needs-info"]
    assert to_add == ["triage"]


def test_reconcile_issue_needs_info_and_stale() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["bug", "needs-info", "stale"],
        commenter="reporter1",
        author="reporter1",
        is_bot=False,
        is_pr=False,
    )
    assert set(to_remove) == {"needs-info", "stale"}
    assert to_add == ["triage"]


def test_reconcile_pr_needs_info_adds_awaiting_review() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["enhancement", "needs-info", "stale"],
        commenter="contributor",
        author="contributor",
        is_bot=False,
        is_pr=True,
    )
    assert set(to_remove) == {"needs-info", "stale"}
    assert to_add == ["awaiting-review"]


def test_reconcile_bot_comment_does_nothing() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["bug", "needs-info"],
        commenter="github-actions[bot]",
        author="reporter1",
        is_bot=True,
        is_pr=False,
    )
    assert to_add == []
    assert to_remove == []


def test_reconcile_no_needs_info_does_nothing() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["bug", "triage"],
        commenter="reporter1",
        author="reporter1",
        is_bot=False,
        is_pr=False,
    )
    assert to_add == []
    assert to_remove == []


def test_reconcile_in_progress_preserves_in_progress() -> None:
    to_add, to_remove = reconcile_labels_on_comment(
        current_labels=["bug", "needs-info", "in-progress"],
        commenter="reporter1",
        author="reporter1",
        is_bot=False,
        is_pr=False,
    )
    assert to_remove == ["needs-info"]
    # Does not add triage when in-progress is already set
    assert to_add == []
