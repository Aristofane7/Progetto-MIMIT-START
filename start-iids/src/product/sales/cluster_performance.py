"""Cluster performance trend classification.

Spec ref: sec. 20.2 defines the `trend_class` enum (GROWTH/STABLE/DECLINE/UNKNOWN)
but does not specify the numeric growth-rate thresholds that separate them. This
module's default thresholds are ARCH — pending project-owner approval — and are
kept isolated in one place so they can be revised via ADR without touching the
persisted schema or other engines.
"""
from __future__ import annotations

# ARCH default thresholds (pending approval, see docs/decisions/ADR-011...).
GROWTH_THRESHOLD = 0.05
DECLINE_THRESHOLD = -0.05


def classify_trend(
    sales_m2_per_product_current: float | None,
    sales_m2_per_product_previous: float | None,
) -> str:
    """Sec. 20.2. Returns UNKNOWN whenever a comparison is not meaningful (missing
    data or a zero/negative previous-period baseline) rather than guessing."""
    if sales_m2_per_product_current is None or sales_m2_per_product_previous is None:
        return "UNKNOWN"
    if sales_m2_per_product_previous <= 0:
        return "UNKNOWN"

    growth_rate = (sales_m2_per_product_current / sales_m2_per_product_previous) - 1.0
    if growth_rate >= GROWTH_THRESHOLD:
        return "GROWTH"
    if growth_rate <= DECLINE_THRESHOLD:
        return "DECLINE"
    return "STABLE"
