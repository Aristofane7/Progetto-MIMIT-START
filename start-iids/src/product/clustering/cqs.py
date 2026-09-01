"""Cluster Quality Score. Spec ref: sec. 19.5 (DOC, verbatim weights and reference
result: Balance=0.811, Coherence=0.721, Separation=0.623, BusinessRelevance=1.000
=> CQS=0.780)."""
from __future__ import annotations

from dataclasses import dataclass

BALANCE_WEIGHT = 0.15
COHERENCE_WEIGHT = 0.35
SEPARATION_WEIGHT = 0.25
BUSINESS_RELEVANCE_WEIGHT = 0.25


@dataclass(frozen=True)
class ClusterScoreComponents:
    balance: float
    coherence: float
    separation: float
    business_relevance: float


def compute_cqs(components: ClusterScoreComponents) -> float:
    """Sec. 19.5: CQS = 0.15*Balance + 0.35*Coherence + 0.25*Separation + 0.25*BusinessRelevance."""
    return (
        BALANCE_WEIGHT * components.balance
        + COHERENCE_WEIGHT * components.coherence
        + SEPARATION_WEIGHT * components.separation
        + BUSINESS_RELEVANCE_WEIGHT * components.business_relevance
    )
