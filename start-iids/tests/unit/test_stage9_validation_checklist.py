"""Structural test for the Stage 9 checklist runner (issue #9, ADR-017) --
does not re-run the real pytest subprocess checks (that's the ~10s job the
script itself does; tests/ already covers every check it wraps individually).
Just proves the checklist stays well-formed: 21 items matching issue #9's
own checklist, valid statuses, gated items actually gate.
"""
from unittest.mock import patch

from scripts.stage9_validation_checklist import ChecklistItem, build_checklist, main

VALID_STATUSES = {"PASS", "PARTIAL", "BLOCKED"}


def test_checklist_has_21_items_matching_issue_9(tmp_path):
    with patch("scripts.stage9_validation_checklist._pytest_passes", return_value=True):
        items = build_checklist()
    assert len(items) == 21
    assert [item.n for item in items] == list(range(1, 22))
    assert all(item.status in VALID_STATUSES for item in items)
    assert all(item.evidence for item in items)


def test_a_failing_gated_check_flips_exit_code():
    with patch("scripts.stage9_validation_checklist._pytest_passes", return_value=True):
        assert main() == 0
    with patch("scripts.stage9_validation_checklist._pytest_passes", return_value=False):
        assert main() == 1


def test_ungated_items_never_fail_the_exit_code_on_their_own():
    # Items 2 (master data), 4 (lot mapping), 5 (E2C), 21 (UAT) are BLOCKED by
    # design (external prerequisites) and must never gate this script's exit
    # code -- only items this repository alone should be able to keep PASSing.
    with patch("scripts.stage9_validation_checklist._pytest_passes", return_value=True):
        items = build_checklist()
    always_blocked = {2, 4, 5, 21}
    for item in items:
        if item.n in always_blocked:
            assert not item.gate, f"item {item.n} is structurally blocked and must not gate"


def test_checklist_item_is_immutable():
    item = ChecklistItem(1, "x", "PASS", "evidence")
    try:
        item.status = "BLOCKED"  # type: ignore[misc]
    except Exception:
        pass
    else:
        raise AssertionError("ChecklistItem should be frozen")
