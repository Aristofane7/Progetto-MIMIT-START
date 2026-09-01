"""Common interface for all calculation engines (TEI, EFA, EcoFA, SFA, EEA, P-TSA).

Spec ref: sec. 41 (Python engine interface), sec. 13 (calc_run auditability),
sec. 54 (rule: "ogni sub-engine deve essere indipendentemente testabile").
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class CalculationContext:
    """Minimum context required to run any engine (spec sec. 41)."""

    period_start: datetime
    period_end: datetime
    plant_id: str
    baseline_id: str
    coefficient_set_id: str
    scenario: str  # 'HISTORICAL' | 'CURRENT' (sec. 47)
    line_id: str | None = None
    lot_id: str | None = None
    weight_set_id: str | None = None

    def __post_init__(self) -> None:
        if self.scenario not in ("HISTORICAL", "CURRENT"):
            raise ValueError(f"invalid scenario '{self.scenario}', expected HISTORICAL or CURRENT")
        if self.period_end < self.period_start:
            raise ValueError("period_end must not precede period_start")


@dataclass
class CalculationResult:
    """Generic engine output envelope, ready for persistence into the matching
    `fact_*_state` table together with its `audit_calc_run` row."""

    engine: str
    engine_version: str
    calc_run_id: str
    context: CalculationContext
    values: dict[str, Any] = field(default_factory=dict)
    data_quality_score: float | None = None
    quality_flags: list[str] = field(default_factory=list)


def make_calc_run_id(engine: str, engine_version: str, context: CalculationContext, seq: str) -> str:
    """Deterministic, human-traceable calc_run_id (sec. 13.2 reproducibility chain).

    Format: ``<ENGINE>_<VERSION>_<PLANT>_<PERIOD_START>_<PERIOD_END>_<SEQ>``.
    ``seq`` must be supplied by the caller (e.g. a monotonically increasing run
    counter or a uuid4) — this module does not silently generate randomness so that
    calc_run_id derivation stays fully auditable and reproducible in tests.
    """
    return (
        f"{engine}_{engine_version}_{context.plant_id}_"
        f"{context.period_start.strftime('%Y%m%dT%H%M%SZ')}_"
        f"{context.period_end.strftime('%Y%m%dT%H%M%SZ')}_{seq}"
    )


class CalculationEngine(ABC):
    """Every engine (TEI/EFA/EcoFA/SFA/EEA/P-TSA) implements this contract."""

    engine_name: str
    engine_version: str

    @abstractmethod
    def validate_inputs(self, context: CalculationContext, inputs: Any) -> None:
        """Raise :class:`~src.engines.errors.EngineError` on any BLOCKER condition
        (sec. 29.3): missing master data, missing APPROVED coefficient, unknown
        unit, baseline mismatch, etc. Must not silently coerce or clamp."""

    @abstractmethod
    def calculate(self, context: CalculationContext, inputs: Any) -> CalculationResult:
        """Pure computation. Must not perform I/O beyond reading already-validated
        `inputs`; all persistence happens in :meth:`persist`."""

    @abstractmethod
    def validate_outputs(self, result: CalculationResult) -> None:
        """Sanity-check the computed result (e.g. reject NaN/inf, dimension checks)
        before it is considered publishable."""

    @abstractmethod
    def persist(self, result: CalculationResult) -> dict[str, Any]:
        """Return the row(s) ready for insertion into the target `fact_*` table
        plus the matching `audit_calc_run` row. Actual DB I/O is the caller's
        responsibility (keeps engines DB-agnostic and unit-testable)."""


def utcnow() -> datetime:
    return datetime.now(UTC)
