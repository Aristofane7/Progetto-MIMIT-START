import pathlib

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.ingestion.rp73_reference_data import BASELINE_YEAR, load_rp73_reference_data

DATA_DIR = pathlib.Path(__file__).resolve().parents[2] / "data" / "reference"
CONFIG_DIR = pathlib.Path(__file__).resolve().parents[2] / "config"


def test_load_coefficient_set_from_yaml_is_approved():
    # ADR-013: promoted from DRAFT to APPROVED on 2026-09-01.
    coeff_set = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
    assert coeff_set.coefficient_set_id == "COEFF_RP73_PROVISIONAL_2026"
    assert coeff_set.status == "APPROVED"
    assert coeff_set.approved_by == "Davide Settembre"
    assert coeff_set.approved_at == "2026-09-01"
    assert coeff_set.get("EL_EX").value == 3.6
    assert coeff_set.get("GAS_EX").value == 42


def test_load_weight_set_from_yaml_is_approved():
    # ADR-013: promoted from DRAFT to APPROVED on 2026-09-01.
    weight_set = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")
    assert weight_set.weight_set_id == "EEA_AHP_RP73_1"
    assert weight_set.status == "APPROVED"
    assert weight_set.approved_by == "Davide Settembre"
    assert weight_set.approved_at == "2026-09-01"
    assert weight_set.get_dimension_weight("env") == 0.3661
    assert weight_set.get_dimension_weight("tech") == 0.3934


def test_load_rp73_reference_data_has_three_plants():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    assert set(data.plants) == {"D020", "D060", "D240"}
    assert data.plants["D060"].description == "Scandiano — ibrido MTS+MTO"
    # ADR-015: production is now per-year
    assert data.production_m2("D060", 2023) == 6400000


def test_production_is_per_year_and_d020_2025_is_partial():
    # ADR-015: D020 ceased in July 2025 -> 2025 production is the partial-period value,
    # earlier years stay at the full annual figure.
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    assert data.production_m2("D020", 2023) == 3800000
    assert data.production_m2("D020", 2025) == 2382600
    assert data.production_m2("D020", 2025) < data.production_m2("D020", 2024)


def test_activity_period_marks_d020_2025_partial():
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    assert data.months_active("D020", 2025) == 7          # Jan -> July cessation
    assert data.months_active("D060", 2025) == 12
    assert data.months_active("D240", 2024) == 12


def test_homologous_baseline_override_for_d020_2025():
    # ADR-015 option A: D020/2025's module baseline is the SAME Jan-July window of 2022.
    data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    assert ("D020", 2025) in data.baseline_override
    ov = data.baseline_override[("D020", 2025)]
    assert ov.ref_year == 2022
    assert ov.months_active == 7
    assert data.baseline_months("D020", 2025) == 7
    assert "RI_MJ" in ov.terms
    # D060/D240 keep the default annual-2022 baseline (no override)
    assert ("D060", 2025) not in data.baseline_override


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
