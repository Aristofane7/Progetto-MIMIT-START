import pathlib

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.ingestion.rp73_reference_data import BASELINE_YEAR, load_rp73_reference_data

DATA_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "reference"
CONFIG_DIR = pathlib.Path(__file__).resolve().parents[2] / "config"


def test_load_coefficient_set_from_yaml_is_draft():
    coeff_set = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
    assert coeff_set.coefficient_set_id == "COEFF_RP73_PROVISIONAL_2026"
    assert coeff_set.status == "DRAFT"
    assert coeff_set.raw_value("EL_EX") == 3.6
    assert coeff_set.raw_value("GAS_EX") == 42


def test_load_weight_set_from_yaml_is_draft():
    weight_set = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")
    assert weight_set.weight_set_id == "EEA_AHP_RP73_1"
    assert weight_set.status == "DRAFT"
    assert weight_set.raw_dimension_weight("env") == 0.3661
    assert weight_set.raw_dimension_weight("tech") == 0.3934


def test_load_rp73_reference_data_has_three_plants():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    assert set(data.plants) == {"D020", "D060", "D240"}
    assert data.plants["D060"].production_m2 == 6400000


def test_baseline_year_present_for_every_plant():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    for plant_id in data.plants:
        assert (plant_id, BASELINE_YEAR) in data.energy
        assert (plant_id, BASELINE_YEAR) in data.tei
        assert (plant_id, BASELINE_YEAR) in data.efa
        assert (plant_id, BASELINE_YEAR) in data.ecofa
        assert (plant_id, BASELINE_YEAR) in data.sfa


def test_plant_years_excludes_baseline():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    years = {y for _, y in data.plant_years()}
    assert BASELINE_YEAR not in years
    assert years == {2023, 2024, 2025}


def test_d020_2023_energy_matches_source():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    row = data.energy[("D020", 2023)]
    assert row.v_gas_nm3 == 3727619
    assert row.e_el_kwh == 10872222
