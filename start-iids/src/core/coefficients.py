"""In-memory representation of an APPROVED coefficient set (`dim_coefficient_set` /
`dim_coefficient`, spec sec. 11). Engines depend on this abstraction rather than on
hardcoded numbers so that no formula ever bakes in a manual placeholder value
(spec sec. 0.6, 11.3, Appendix L).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from src.engines.errors import EngineError, ErrorCategory

VALID_DOMAINS = {"EFA", "ECOFA", "SFA", "TEI", "PTSA"}
VALID_CONFIDENCE = {"A", "B", "C"}


@dataclass(frozen=True)
class Coefficient:
    coefficient_id: str
    domain: str
    code: str
    value: float
    unit: str
    confidence: str
    source: str | None = None
    source_year: int | None = None

    def __post_init__(self) -> None:
        if self.domain not in VALID_DOMAINS:
            raise ValueError(f"invalid coefficient domain '{self.domain}'")
        if self.confidence not in VALID_CONFIDENCE:
            raise ValueError(f"invalid coefficient confidence '{self.confidence}', expected A/B/C")


class CoefficientSet:
    """A coefficient set as loaded from `dim_coefficient_set` + `dim_coefficient`.

    Rule (sec. 11.3 / 0.6): a coefficient set with status != 'APPROVED' must never
    feed a production calculation — manual/manual-derived placeholder values are
    loaded as DRAFT and must stay out of the engines until reviewed and approved.
    """

    def __init__(self, coefficient_set_id: str, status: str, coefficients: dict[str, Coefficient]):
        if status not in ("DRAFT", "APPROVED", "RETIRED"):
            raise ValueError(f"invalid coefficient set status '{status}'")
        self.coefficient_set_id = coefficient_set_id
        self.status = status
        self._coefficients = dict(coefficients)

    def get(self, code: str) -> Coefficient:
        if self.status != "APPROVED":
            raise EngineError(
                ErrorCategory.MISSING_COEFFICIENT,
                f"coefficient set '{self.coefficient_set_id}' is not APPROVED "
                f"(status={self.status}); cannot use '{code}' in a production calculation",
                record_key=code,
            )
        coefficient = self._coefficients.get(code)
        if coefficient is None:
            raise EngineError(
                ErrorCategory.MISSING_COEFFICIENT,
                f"coefficient '{code}' not found in set '{self.coefficient_set_id}'",
                record_key=code,
            )
        return coefficient

    def __contains__(self, code: str) -> bool:
        return code in self._coefficients

    def coefficients(self) -> dict[str, Coefficient]:
        """Read-only snapshot of every coefficient in this set, regardless of
        approval status. For export/reporting/re-wrapping — never a substitute
        for :meth:`get` inside an engine."""
        return dict(self._coefficients)

    def raw_value(self, code: str) -> float:
        """Return a coefficient's numeric value WITHOUT the APPROVED-status gate.

        For provisional/demo pipelines only (e.g. `src/run_all.py` regenerating
        the RP7.3 reference log from an explicitly DRAFT set, ADR-012) — never
        call this from a calculation engine. Engines must always go through
        :meth:`get`, which enforces sec. 11.3.
        """
        coefficient = self._coefficients.get(code)
        if coefficient is None:
            raise EngineError(
                ErrorCategory.MISSING_COEFFICIENT,
                f"coefficient '{code}' not found in set '{self.coefficient_set_id}'",
                record_key=code,
            )
        return coefficient.value


def load_coefficient_set(path: str | Path) -> CoefficientSet:
    """Load a `CoefficientSet` from a YAML file shaped like
    `config/coefficients/*.yaml` (a `coefficient_set` block + a `coefficients`
    list). Never hardcode coefficient values in Python — see Appendix L."""
    raw = yaml.safe_load(Path(path).read_text())
    set_meta = raw["coefficient_set"]
    coefficients = {
        c["code"]: Coefficient(
            coefficient_id=c["coefficient_id"],
            domain=c["domain"],
            code=c["code"],
            value=c["value"],
            unit=c["unit"],
            confidence=c["confidence"],
            source=c.get("source"),
            source_year=c.get("source_year"),
        )
        for c in raw["coefficients"]
    }
    return CoefficientSet(
        coefficient_set_id=set_meta["coefficient_set_id"],
        status=set_meta["status"],
        coefficients=coefficients,
    )
