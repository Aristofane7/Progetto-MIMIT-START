"""Error taxonomy shared by all calculation engines.

Spec ref: sec. 49. An error must be persisted (never silently swallowed in
application logs), carry a record key, and a severity. Severity values mirror
`audit_data_quality.severity` (sec. 29.2): INFO, WARNING, ERROR, BLOCKER.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ErrorCategory(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    MISSING_MASTER = "MISSING_MASTER"
    MISSING_COEFFICIENT = "MISSING_COEFFICIENT"
    UNIT_ERROR = "UNIT_ERROR"
    BASELINE_MISMATCH = "BASELINE_MISMATCH"
    TEMPORAL_MISMATCH = "TEMPORAL_MISMATCH"
    REFERENTIAL_ERROR = "REFERENTIAL_ERROR"
    PHYSICAL_RANGE_ERROR = "PHYSICAL_RANGE_ERROR"
    CALCULATION_ERROR = "CALCULATION_ERROR"


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKER = "BLOCKER"


@dataclass(frozen=True)
class DataQualityFinding:
    """Mirrors a row of `audit_data_quality` (sec. 29.2)."""

    dataset_name: str
    record_key: str
    check_code: str
    severity: Severity
    passed: bool
    observed_value: str | None = None
    expected_rule: str | None = None
    calc_run_id: str | None = None


class EngineError(Exception):
    """Raised by an engine when a BLOCKER-severity condition is hit (sec. 29.3).

    A blocked calculation must still produce an ``audit_calc_run`` row with
    ``status='REJECTED'`` and, where meaningful, an ``audit_data_quality`` finding —
    it must never fail silently.
    """

    def __init__(self, category: ErrorCategory, message: str, record_key: str | None = None):
        super().__init__(message)
        self.category = category
        self.message = message
        self.record_key = record_key

    def to_finding(self, dataset_name: str, calc_run_id: str | None = None) -> DataQualityFinding:
        return DataQualityFinding(
            dataset_name=dataset_name,
            record_key=self.record_key or "",
            check_code=self.category.value,
            severity=Severity.BLOCKER,
            passed=False,
            observed_value=None,
            expected_rule=self.message,
            calc_run_id=calc_run_id,
        )
