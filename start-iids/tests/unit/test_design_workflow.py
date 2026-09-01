import pytest

from src.design.workflow import DecisionCode, validate_stage_transition


def test_must_start_at_stage_a():
    with pytest.raises(ValueError):
        validate_stage_transition(previous_stage=None, next_stage="B")
    validate_stage_transition(previous_stage=None, next_stage="A")  # does not raise


def test_forward_single_step_allowed():
    validate_stage_transition(previous_stage="A", next_stage="B")
    validate_stage_transition(previous_stage="D", next_stage="E")


def test_skipping_forward_rejected():
    with pytest.raises(ValueError):
        validate_stage_transition(previous_stage="A", next_stage="D")


def test_iterate_back_to_earlier_stage_allowed():
    # ITERATE decision (sec. 22.5) routes back to D for another prototyping cycle.
    validate_stage_transition(previous_stage="E", next_stage="D")


def test_decision_code_enum_matches_ddl_check_constraint():
    assert {d.value for d in DecisionCode} == {"GO", "ITERATE", "STOP", "HOLD_QUEUE", "NEXT_CYCLE"}
