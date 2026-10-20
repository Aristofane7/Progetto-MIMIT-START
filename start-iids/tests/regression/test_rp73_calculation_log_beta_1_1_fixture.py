"""Traceability regression against the archived beta-1.1 RP7.3 artifacts (ADR-025, sec. 11.3 point 1).

The live `data/reference/RP7.3_calculation_log.xlsx` was bumped to beta-1.2 when
D020's 2025 partial production year was reconciled (ADR-025). This test pins the
PREVIOUS golden set — `tests/fixtures/rp73/RP7.3_calculation_log_beta-1.1.xlsx`
together with its matching data workbook — so the pre-ADR-025 numbers stay
reproducible by the SAME engine. The beta-1.1 workbook has no `Periodo`/
`Riferimento` sheets, so every plant/year is a full 12-month year baselined on the
annual 2022 row (the engine's default path) — including D020/2025, which in
beta-1.1 was still treated as a full year.
"""
import pathlib

import pytest

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.engines.eea.aggregate import compute_aggregate_state
from src.ingestion.rp73_reference_data import load_rp73_calculation_log, load_rp73_reference_data

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIX = ROOT / "tests" / "fixtures" / "rp73"
CONFIG_DIR = ROOT / "config"

REFERENCE_DATA = load_rp73_reference_data(FIX / "RP7.3_data_collection_beta-1.1.xlsx")
CALCULATION_LOG = load_rp73_calculation_log(FIX / "RP7.3_calculation_log_beta-1.1.xlsx")
COEFFICIENT_SET = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
WEIGHT_SET = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")


def _state(plant_id: str, year: int):
    psi = CALCULATION_LOG[(plant_id, year, "Psi")]
    return compute_aggregate_state(plant_id, year, REFERENCE_DATA, COEFFICIENT_SET, WEIGHT_SET, psi=psi)


@pytest.mark.parametrize("plant_id,year", [("D020", 2025), ("D060", 2024), ("D240", 2023)])
def test_beta_1_1_fixture_still_reproduces(plant_id, year):
    state = _state(plant_id, year)
    assert state.f_env_gj == pytest.approx(CALCULATION_LOG[(plant_id, year, "f_env")], rel=1e-3)
    assert state.sa_raw_gj == pytest.approx(CALCULATION_LOG[(plant_id, year, "SA_raw")], rel=1e-3)
    assert state.tsi_abs == pytest.approx(CALCULATION_LOG[(plant_id, year, "TSI_abs")], abs=2e-3)


def test_beta_1_1_d020_2025_was_full_year():
    # In beta-1.1 D020/2025 was a full 12-month year (no Periodo/Riferimento sheets).
    assert REFERENCE_DATA.months_active("D020", 2025) == 12
    assert ("D020", 2025) not in REFERENCE_DATA.baseline_override
    # its Ex_ref is the full-year value (184,300 GJ), unlike beta-1.2's partial 115,556 GJ
    assert _state("D020", 2025).ex_ref_gj == pytest.approx(184300, rel=1e-3)
