import pytest

from src.product.clustering.cqs import ClusterScoreComponents, compute_cqs

# Golden regression, spec sec. 19.5 — these are the published RP6.8 component
# scores AND the published aggregate result, both quoted verbatim in the
# implementation spec: no fabricated input.
RP68_COMPONENTS = ClusterScoreComponents(
    balance=0.811, coherence=0.721, separation=0.623, business_relevance=1.000,
)
RP68_CQS = 0.780


def test_cqs_matches_rp68_published_reference():
    assert compute_cqs(RP68_COMPONENTS) == pytest.approx(RP68_CQS, abs=1e-3)


def test_cqs_all_zero_boundary():
    assert compute_cqs(ClusterScoreComponents(0, 0, 0, 0)) == 0.0


def test_cqs_all_one_boundary():
    assert compute_cqs(ClusterScoreComponents(1, 1, 1, 1)) == pytest.approx(1.0)
