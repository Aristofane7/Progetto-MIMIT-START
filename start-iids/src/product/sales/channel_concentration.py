"""Distribution-channel concentration risk (issue #8 follow-up, ADR-022).

Not in the implementation spec's fixed field list — this is a new monitoring
point requested directly, motivated by the Piano di Sviluppo's own B2C/B2B
split for Gresmalt (OR7.5) and by the same over-dependency risk VOLT tracks
upstream for raw-material suppliers (SPOF/concentration score), applied here
downstream to sales channels.
"""
from __future__ import annotations


def compute_channel_concentration(channel_sales: dict[str, float]) -> float | None:
    """Herfindahl-Hirschman-style concentration index: sum of squared channel
    shares of total sales, in (1/n, 1] for n channels with sales. 1.0 means
    all sales concentrated in a single channel (highest risk); 1/n means an
    even split across all n channels.

    Returns None when there is nothing to concentrate (no channels, or total
    sales <= 0) rather than a misleading 0.0 or a division error.
    """
    total = sum(v for v in channel_sales.values() if v is not None)
    if not channel_sales or total <= 0:
        return None
    return sum((v / total) ** 2 for v in channel_sales.values() if v is not None)
