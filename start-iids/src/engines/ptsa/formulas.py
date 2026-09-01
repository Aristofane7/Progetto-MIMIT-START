"""P-TSA pure formulas (Product Technological Sustainability Assessment).

Spec ref: sec. 24 (DOC). Dimension <-> metric mapping (IOA=SCR*, OP=PsI*,
TQ=OCR*) follows Appendix E and sec. 24.1-24.4 directly.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.weights import WeightSet
from src.engines.errors import EngineError, ErrorCategory

DIM_IOA = "IOA"
DIM_OP = "OP"
DIM_TQ = "TQ"

# Metric codes per Appendix E.
IOA_METRICS = ("SCR_RAW", "SCR_FINISHED", "SCR_GLAZE")
OP_METRICS = ("PSI_ENERGY", "PSI_MATERIAL", "PSI_THROUGHPUT")
TQ_METRICS = ("OCR_FLEXURAL", "OCR_BREAKING", "OCR_SURFACE")


def _require_positive_denominator(value: float, field_name: str, record_key: str) -> None:
    if value == 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            f"'{field_name}' is zero: ratio is undefined",
            record_key=record_key,
        )


def compute_scr(stock: float, daily_consumption: float, record_key: str) -> float:
    """Sec. 24.2: SCR = Stock / DailyConsumption."""
    _require_positive_denominator(daily_consumption, "daily_consumption", record_key)
    return stock / daily_consumption


def compute_psi(real_output: float, real_input: float, record_key: str) -> float:
    """Sec. 24.3: PsI = RealOutput / RealInput."""
    _require_positive_denominator(real_input, "real_input", record_key)
    return real_output / real_input


def compute_ocr(quantity_passed: float, attempted_total: float, record_key: str) -> float:
    """Sec. 24.4: OCR = QP / AT."""
    _require_positive_denominator(attempted_total, "attempted_total", record_key)
    return quantity_passed / attempted_total


@dataclass(frozen=True)
class PopulationStat:
    mean: float
    stdev: float


def compute_zscore(value: float, stat: PopulationStat, metric_code: str, record_key: str) -> float:
    """Sec. 24.5: z_{k,a} = (x_{k,a} - mean_k) / sigma_k."""
    if stat.stdev == 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            f"population stdev for metric '{metric_code}' is zero: z-score is undefined",
            record_key=record_key,
        )
    return (value - stat.mean) / stat.stdev


def compute_subindex(zscores: dict[str, float], weights: dict[str, float]) -> float:
    """Sec. 24.6: IOAI/OPI/TQI = sum_k w_k * z_k. Base case: equal intra-dimension
    weights (1/n_metrics), but weights are always supplied explicitly — never
    assumed silently — so a caller can plug an approved non-uniform weighting."""
    return sum(weights[k] * zscores[k] for k in zscores)


def compute_p_tsi_z(ioai: float, opi: float, tqi: float) -> float:
    """Sec. 24.7: P-TSI_z = (1/3) IOAI + (1/3) OPI + (1/3) TQI."""
    return (ioai / 3.0) + (opi / 3.0) + (tqi / 3.0)


def compute_p_tsi_scoring(
    dimension_scores: dict[str, float], weight_set: WeightSet
) -> float:
    """Sec. 24.8: secondary method — 1-5 scoring per dimension, combined via
    approved AHP weights (never hardcoded; e.g. RP7.4's alpha_IOA/alpha_OP/alpha_TQ
    must come from a versioned, APPROVED `dim_weight_set`)."""
    return sum(
        weight_set.get_dimension_weight(dim) * score
        for dim, score in dimension_scores.items()
    )


def compute_tii(p_tsi_5_current: float, p_tsi_5_previous: float, record_key: str) -> float:
    """Sec. 24.10: TII = (P-TSI_t / P-TSI_{t-1} - 1) * 100.

    Safety rule (ADR-007): TII is defined ONLY on the scoring/AHP variant
    (`P_TSI_5`, positive and ratio-compatible by construction on a 1-5 scale) —
    this module intentionally exposes no z-score TII variant at all.
    """
    if p_tsi_5_previous <= 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            f"P_TSI_5 previous-period value must be positive to compute TII, got {p_tsi_5_previous}",
            record_key=record_key,
        )
    return ((p_tsi_5_current / p_tsi_5_previous) - 1.0) * 100.0
