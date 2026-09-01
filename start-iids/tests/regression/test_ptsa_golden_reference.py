"""Golden regression against the REAL RP7.4 report (issue #6, ADR-020).

Every raw input here is transcribed verbatim from "RP 7.4 Report di Product
Technological Sustainability Assessment.pdf" (repo root) Tabelle 3-5 (the
SCR/PsI/OCR indicator matrix) and Tabella 7 (the per-dimension 1-5 scores) —
real project data, not fabricated (spec sec. 64: "Non fabbricare input per
far tornare i valori"). Targets are Tabella 6 (z-score P-TSI, sec. 43.2's
published -0.047/-0.115/+0.162) and Tabella 7 (scoring/AHP P-TSI).

See docs/decisions/ADR-020-rp74-report-found.md for how this was found and
why it supersedes ADR-011 item 5.
"""
import csv
import pathlib
import statistics

import pytest

from src.core.weights import Weight, WeightSet
from src.engines.ptsa.formulas import (
    IOA_METRICS,
    OP_METRICS,
    TQ_METRICS,
    PopulationStat,
    compute_p_tsi_scoring,
    compute_p_tsi_z,
    compute_subindex,
    compute_zscore,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "reference"

# Sec. 43.2 — P-TSI z (z-score / equal-weight method), Tabella 6:
PTSI_Z_REFERENCE = {"T1": -0.047, "T2": -0.115, "T3": 0.162}
SUBINDEX_Z_REFERENCE = {
    "T1": {"IOA": -0.920, "OP": 0.970, "TQ": -0.191},
    "T2": {"IOA": -0.466, "OP": 0.403, "TQ": -0.280},
    "T3": {"IOA": 1.385, "OP": -1.372, "TQ": 0.472},
}

# Sec. 43.2 — P-TSI scoring/AHP method, Tabella 7:
PTSI_SCORING_REFERENCE = {"T1": 3.73, "T2": 3.46, "T3": 3.81}

# Sec. 24.8 — RP7.4 AHP weights, Tabella 7 (must be loaded from an APPROVED
# dim_weight_set in production, never hardcoded in an engine; pinned here
# only for the regression check of the aggregation formula itself).
RP74_ALPHA_IOA = 0.1634
RP74_ALPHA_OP = 0.2970
RP74_ALPHA_TQ = 0.5396
RP74_CONSISTENCY_RATIO = 0.0079

DIMENSION_METRICS = {"IOA": IOA_METRICS, "OP": OP_METRICS, "TQ": TQ_METRICS}
PRODUCT_TYPES = ("T1", "T2", "T3")


def _load_indicator_matrix() -> dict[tuple[str, str], float]:
    """(product_type_id, metric_code) -> raw value, from Tabelle 3-5."""
    matrix: dict[tuple[str, str], float] = {}
    with (DATA_DIR / "RP7.4_indicator_matrix.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            matrix[(row["product_type_id"], row["metric_code"])] = float(row["value"])
    return matrix


def _load_dimension_scores() -> dict[str, dict[str, float]]:
    """product_type_id -> {S_IOA, S_OP, S_TQ}, from Tabella 7."""
    scores: dict[str, dict[str, float]] = {}
    with (DATA_DIR / "RP7.4_dimension_scores.csv").open(newline="") as f:
        for row in csv.DictReader(f):
            scores[row["product_type_id"]] = {
                "IOA": float(row["S_IOA"]), "OP": float(row["S_OP"]), "TQ": float(row["S_TQ"]),
            }
    return scores


INDICATOR_MATRIX = _load_indicator_matrix()
DIMENSION_SCORES = _load_dimension_scores()


def _population_stat(metric_code: str) -> PopulationStat:
    """Sec. 24.5 / RP7.4 sec. 2.5: mean and population stdev (N divisor, not
    N-1) of a metric across the three product types."""
    values = [INDICATOR_MATRIX[(t, metric_code)] for t in PRODUCT_TYPES]
    return PopulationStat(mean=statistics.mean(values), stdev=statistics.pstdev(values))


def _rp74_weight_set() -> WeightSet:
    weights = {
        ("IOA", ""): Weight("IOA", "", RP74_ALPHA_IOA),
        ("OP", ""): Weight("OP", "", RP74_ALPHA_OP),
        ("TQ", ""): Weight("TQ", "", RP74_ALPHA_TQ),
    }
    return WeightSet("PTSA_WEIGHT_RP74_1", "APPROVED", weights)


def _subindex_z(product_type_id: str, dimension: str) -> float:
    metrics = DIMENSION_METRICS[dimension]
    zscores = {
        m: compute_zscore(
            INDICATOR_MATRIX[(product_type_id, m)], _population_stat(m), m, product_type_id
        )
        for m in metrics
    }
    equal_weights = {m: 1.0 / len(metrics) for m in metrics}
    return compute_subindex(zscores, equal_weights)


@pytest.mark.parametrize("product_type_id,dimension", [
    (t, d) for t in PRODUCT_TYPES for d in ("IOA", "OP", "TQ")
])
def test_subindex_z_matches_rp74_tabella6(product_type_id, dimension):
    expected = SUBINDEX_Z_REFERENCE[product_type_id][dimension]
    assert _subindex_z(product_type_id, dimension) == pytest.approx(expected, abs=5e-3)


@pytest.mark.parametrize("product_type_id,expected_p_tsi_z", sorted(PTSI_Z_REFERENCE.items()))
def test_zscore_p_tsi_matches_rp74_published_values(product_type_id, expected_p_tsi_z):
    """Un-skipped (issue #6, ADR-020): the raw SCR/PsI/OCR matrix behind these
    published z-score P-TSI values (sec. 43.2) is real data transcribed from
    the RP7.4 report's own Tabelle 3-5, not fabricated."""
    ioai = _subindex_z(product_type_id, "IOA")
    opi = _subindex_z(product_type_id, "OP")
    tqi = _subindex_z(product_type_id, "TQ")
    actual = compute_p_tsi_z(ioai, opi, tqi)
    assert actual == pytest.approx(expected_p_tsi_z, abs=5e-3)


@pytest.mark.parametrize("product_type_id,expected_p_tsi_5", sorted(PTSI_SCORING_REFERENCE.items()))
def test_ahp_weighted_sum_matches_rp74_real_dimension_scores(product_type_id, expected_p_tsi_5):
    """Stronger than the old self-consistency probe below: uses the REAL
    per-type S_IOA/S_OP/S_TQ scores from Tabella 7 (not back-solved), fed
    through RP7.4's own AHP weights."""
    weight_set = _rp74_weight_set()
    # abs=1e-2, not 5e-3: Tabella 7's S_IOA/S_OP/S_TQ are themselves displayed
    # rounded to 2 decimals, so the propagated rounding error is a bit larger
    # than for the raw (also rounded) SCR/PsI/OCR inputs used above.
    assert compute_p_tsi_scoring(DIMENSION_SCORES[product_type_id], weight_set) == pytest.approx(
        expected_p_tsi_5, abs=1e-2
    )


@pytest.mark.parametrize("product_type_id,expected_p_tsi_5", sorted(PTSI_SCORING_REFERENCE.items()))
def test_ahp_weighted_sum_formula_is_consistent_with_rp74_reference(
    product_type_id, expected_p_tsi_5
):
    """Superseded in strength by test_ahp_weighted_sum_matches_rp74_real_dimension_scores
    above (kept per Appendix M as the "old test" of record): proves the
    formula's arithmetic is self-consistent even without real per-dimension
    scores, by scoring every dimension at the published aggregate value.
    """
    weight_set = _rp74_weight_set()
    consistency_check_weights = {
        "IOA": RP74_ALPHA_IOA, "OP": RP74_ALPHA_OP, "TQ": RP74_ALPHA_TQ,
    }
    assert sum(consistency_check_weights.values()) == pytest.approx(1.0)
    uniform_scores = {"IOA": expected_p_tsi_5, "OP": expected_p_tsi_5, "TQ": expected_p_tsi_5}
    assert compute_p_tsi_scoring(uniform_scores, weight_set) == pytest.approx(expected_p_tsi_5)
