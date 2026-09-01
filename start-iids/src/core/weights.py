"""In-memory representation of an APPROVED weight set (`dim_weight_set` /
`dim_weight`, spec sec. 24.9). Mirrors `CoefficientSet` so that AHP weights (e.g.
RP7.4's alpha_IOA=0.1634, alpha_OP=0.2970, alpha_TQ=0.5396) are never hardcoded in
an engine (spec sec. 24.8, Appendix L).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.engines.errors import EngineError, ErrorCategory

DIMENSION_LEVEL = ""  # sentinel metric_code for a whole-dimension AHP weight


@dataclass(frozen=True)
class Weight:
    dimension_code: str
    metric_code: str  # DIMENSION_LEVEL for a dimension-level (AHP) weight
    value: float


class WeightSet:
    """Reuses ErrorCategory.MISSING_COEFFICIENT on lookup failure: spec sec. 49's
    fixed error taxonomy has no dedicated "weight" category, and a weight set is
    architecturally a sibling registry to a coefficient set (both are APPROVED,
    versioned, governed parameter sets — see sec. 11 vs 24.9)."""

    def __init__(self, weight_set_id: str, status: str, weights: dict[tuple[str, str], Weight]):
        if status not in ("DRAFT", "APPROVED", "RETIRED"):
            raise ValueError(f"invalid weight set status '{status}'")
        self.weight_set_id = weight_set_id
        self.status = status
        self._weights = dict(weights)

    def _get(self, dimension_code: str, metric_code: str) -> Weight:
        if self.status != "APPROVED":
            raise EngineError(
                ErrorCategory.MISSING_COEFFICIENT,
                f"weight set '{self.weight_set_id}' is not APPROVED (status={self.status})",
                record_key=f"{dimension_code}/{metric_code}",
            )
        weight = self._weights.get((dimension_code, metric_code))
        if weight is None:
            raise EngineError(
                ErrorCategory.MISSING_COEFFICIENT,
                f"weight for dimension={dimension_code!r} metric={metric_code!r} "
                f"not found in set '{self.weight_set_id}'",
                record_key=f"{dimension_code}/{metric_code}",
            )
        return weight

    def get_metric_weight(self, dimension_code: str, metric_code: str) -> float:
        return self._get(dimension_code, metric_code).value

    def get_dimension_weight(self, dimension_code: str) -> float:
        """The AHP alpha weight for a whole dimension (sec. 24.8)."""
        return self._get(dimension_code, DIMENSION_LEVEL).value
