"""Golden regression against the REAL RP7.3 calculation log (ADR-012, ADR-013).

Every input here comes from `data/reference/RP7.3_data_collection_20232025.xlsx`
and every target from `data/reference/RP7.3_calculation_log.xlsx` — both real
project artifacts, not fabricated (spec sec. 64: "Non fabbricare input per far
tornare i valori"). Baseline year is fixed at 2022 for every plant (ADR-012).

Coefficients/weights come from the APPROVED `COEFF_RP73_PROVISIONAL_2026` /
`EEA_AHP_RP73_1` sets (ADR-013, signed off by the project owner on 2026-09-01)
— this test now exercises the exact same production path
(`src/engines/eea/aggregate.py::compute_aggregate_state`) that `src/run_all.py`
uses, with no DRAFT-only bypass.
"""
import pathlib

import pytest

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.engines.eea.aggregate import compute_aggregate_state
from src.engines.eea.formulas import compute_tsi_rel
from src.ingestion.rp73_reference_data import load_rp73_calculation_log, load_rp73_reference_data

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "reference"
CONFIG_DIR = ROOT / "config"

REFERENCE_DATA = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
CALCULATION_LOG = load_rp73_calculation_log(DATA_DIR / "RP7.3_calculation_log.xlsx")
COEFFICIENT_SET = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
WEIGHT_SET = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")

PLANT_YEARS_2025 = [(p, y) for p, y in REFERENCE_DATA.plant_years() if y == 2025]


def test_coefficient_and_weight_sets_are_approved():
    assert COEFFICIENT_SET.status == "APPROVED"
    assert WEIGHT_SET.status == "APPROVED"


def _state(plant_id: str, year: int):
    psi = CALCULATION_LOG[(plant_id, year, "Psi")]
    return compute_aggregate_state(plant_id, year, REFERENCE_DATA, COEFFICIENT_SET, WEIGHT_SET, psi=psi)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_env_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_env")]
    assert _state(plant_id, year).f_env_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_econ_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_econ")]
    assert _state(plant_id, year).f_econ_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_soc_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_soc")]
    assert _state(plant_id, year).f_soc_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_tech_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_tech")]
    assert _state(plant_id, year).f_tech_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_sa_raw_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "SA_raw")]
    assert _state(plant_id, year).sa_raw_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_ex_ref_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "Ex_ref")]
    assert _state(plant_id, year).ex_ref_gj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_tsi_abs_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "TSI_abs")]
    assert _state(plant_id, year).tsi_abs == pytest.approx(expected, abs=2e-3)


@pytest.mark.parametrize("plant_id,year", PLANT_YEARS_2025)
def test_tsi_rel_matches_log(plant_id, year):
    tsi_abs_2025 = _state(plant_id, 2025).tsi_abs
    tsi_abs_2023 = _state(plant_id, 2023).tsi_abs
    expected = CALCULATION_LOG[(plant_id, year, "TSI_rel")]
    actual = compute_tsi_rel(tsi_abs_2025, tsi_abs_2023, record_key=plant_id)
    assert actual == pytest.approx(expected, rel=2e-2)
