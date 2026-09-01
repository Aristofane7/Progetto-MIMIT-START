"""Product Design workflow state machine. Spec ref: sec. 22 (phases A-F), sec. 22.6
(event log), sec. 22.5 (decision_code enum)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

DESIGN_STAGES = ("A", "B", "C", "D", "E", "F")


class DecisionCode(str, Enum):
    GO = "GO"
    ITERATE = "ITERATE"
    STOP = "STOP"
    HOLD_QUEUE = "HOLD_QUEUE"
    NEXT_CYCLE = "NEXT_CYCLE"


@dataclass(frozen=True)
class DesignEvent:
    design_project_id: str
    stage: str
    event_ts: datetime
    actor: str | None = None
    input_reference: str | None = None
    output_reference: str | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.stage not in DESIGN_STAGES:
            raise ValueError(f"invalid design stage '{self.stage}', expected one of {DESIGN_STAGES}")


def validate_stage_transition(previous_stage: str | None, next_stage: str) -> None:
    """A project must start at stage A (sec. 22.1) and cannot skip a stage forward
    in a single transition. Moving to an earlier stage is allowed (an ITERATE
    decision, sec. 22.5, routes back to D for another prototyping cycle)."""
    if next_stage not in DESIGN_STAGES:
        raise ValueError(f"invalid design stage '{next_stage}', expected one of {DESIGN_STAGES}")

    if previous_stage is None:
        if next_stage != "A":
            raise ValueError("a design project's first recorded event must be stage 'A'")
        return

    prev_idx = DESIGN_STAGES.index(previous_stage)
    next_idx = DESIGN_STAGES.index(next_stage)
    if next_idx > prev_idx + 1:
        raise ValueError(
            f"cannot skip forward from stage '{previous_stage}' directly to '{next_stage}'"
        )
