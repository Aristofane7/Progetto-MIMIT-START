"""Golden regression against the REAL RP7.3 calculation log (ADR-012).

Every input here comes from `data/reference/RP7.3_data_collection_20232025.xlsx`
and every target from `data/reference/RP7.3_calculation_log.xlsx` — both real
project artifacts, not fabricated (spec sec. 64: "Non fabbricare input per far
tornare i valori"). Baseline year is fixed at 2022 for every plant (ADR-012).

Coefficients/weights come from the DRAFT `COEFF_RP73_PROVISIONAL_2026` /
`EEA_AHP_RP73_1` sets (`config/coefficients/...`, `config/weights/...`); this
test exercises formula correctness against known-good outputs, which is exactly
what DRAFT sets are for (sec. 11.3) — it does not claim production sign-off.
"""
import pathlib

import pytest

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.engines.ecofa.formulas import compute_f_econ
from src.engines.eea.formulas import (
    EEAComponentsMJ,
    compute_phi,
    compute_psi_efficiency,
    compute_sa_mj,
    compute_tsi_abs,
    compute_tsi_rel,
)
from src.engines.efa.formulas import compute_f_env
from src.engines.sfa.formulas import compute_f_soc
from src.engines.tei.formulas import compute_f_tech
from src.ingestion.rp73_reference_data import (
    BASELINE_YEAR,
    load_rp73_calculation_log,
    load_rp73_reference_data,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "reference"
CONFIG_DIR = ROOT / "config"

REFERENCE_DATA = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
CALCULATION_LOG = load_rp73_calculation_log(DATA_DIR / "RP7.3_calculation_log.xlsx")
COEFFICIENT_SET = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
WEIGHT_SET = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")

PLANT_YEARS_2025 = [(p, y) for p, y in REFERENCE_DATA.plant_years() if y == 2025]


def _ex_ref_mj_from_draft_coefficients(e_el_kwh: float, v_gas_nm3: float) -> float:
    """`compute_ex_ref_mj` correctly refuses a DRAFT coefficient set (sec.
    11.3) — that gate is exactly right for production engines. This regression
    test exists precisely to validate the DRAFT set's numbers against known-good
    outputs before it can ever be promoted to APPROVED, so it reads the raw
    values directly (`CoefficientSet.raw_value`, ADR-012) rather than bypassing
    the engine's own safety check."""
    return (
        e_el_kwh * COEFFICIENT_SET.raw_value("EL_EX")
        + v_gas_nm3 * COEFFICIENT_SET.raw_value("GAS_EX")
    )


def _footprints_gj(plant_id: str, year: int) -> EEAComponentsMJ:
    tei_base = REFERENCE_DATA.tei[(plant_id, BASELINE_YEAR)]
    tei_cur = REFERENCE_DATA.tei[(plant_id, year)]
    efa_base = REFERENCE_DATA.efa[(plant_id, BASELINE_YEAR)]
    efa_cur = REFERENCE_DATA.efa[(plant_id, year)]
    ecofa_base = REFERENCE_DATA.ecofa[(plant_id, BASELINE_YEAR)]
    ecofa_cur = REFERENCE_DATA.ecofa[(plant_id, year)]
    sfa_base = REFERENCE_DATA.sfa[(plant_id, BASELINE_YEAR)]
    sfa_cur = REFERENCE_DATA.sfa[(plant_id, year)]

    f_env_mj = compute_f_env(
        efa_cur.ri_mj, efa_base.ri_mj, efa_cur.circ_mj, efa_base.circ_mj,
        efa_cur.ieq_mj, efa_base.ieq_mj, efa_cur.wex_mj, efa_base.wex_mj,
    )
    f_econ_mj = compute_f_econ(
        ecofa_cur.va_mj, ecofa_base.va_mj, ecofa_cur.econ_in_mj, ecofa_base.econ_in_mj,
        ecofa_cur.inv_mj, ecofa_base.inv_mj,
    )
    f_soc_mj = compute_f_soc(
        sfa_cur.sv_mj, sfa_base.sv_mj, sfa_cur.train_mj, sfa_base.train_mj,
        sfa_cur.lost_mj, sfa_base.lost_mj, sfa_cur.co2_mj, sfa_base.co2_mj,
    )
    f_tech_mj = compute_f_tech(
        ex_loss_base_mts_mj=tei_base.loss_mts_mj, ex_loss_base_mto_mj=tei_base.loss_mto_mj,
        ex_loss_mts_mj=tei_cur.loss_mts_mj, ex_loss_mto_mj=tei_cur.loss_mto_mj,
        ex_inv_mj=tei_cur.inv_mj, ex_qual_mts_mj=tei_cur.qual_mts_mj, ex_qual_mto_mj=tei_cur.qual_mto_mj,
    )
    # The log reports these already in GJ; MJ/1000 is exactly our P0 mj_to_gj rule.
    return EEAComponentsMJ(
        f_env_mj=f_env_mj / 1000.0, f_econ_mj=f_econ_mj / 1000.0,
        f_soc_mj=f_soc_mj / 1000.0, f_tech_mj=f_tech_mj / 1000.0,
    )


def _tsi_abs(plant_id: str, year: int) -> float:
    footprints_gj = _footprints_gj(plant_id, year)
    sa_w_gj = (
        WEIGHT_SET.raw_dimension_weight("env") * footprints_gj.f_env_mj
        + WEIGHT_SET.raw_dimension_weight("econ") * footprints_gj.f_econ_mj
        + WEIGHT_SET.raw_dimension_weight("soc") * footprints_gj.f_soc_mj
        + WEIGHT_SET.raw_dimension_weight("tech") * footprints_gj.f_tech_mj
    )
    energy = REFERENCE_DATA.energy[(plant_id, year)]
    ex_ref_mj = _ex_ref_mj_from_draft_coefficients(energy.e_el_kwh, energy.v_gas_nm3)
    ex_ref_gj = ex_ref_mj / 1000.0
    phi = compute_phi(sa_w_gj, ex_ref_gj, record_key=f"{plant_id}-{year}")
    psi = compute_psi_efficiency(CALCULATION_LOG[(plant_id, year, "Psi")])
    return compute_tsi_abs(phi, psi)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_env_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_env")]
    assert _footprints_gj(plant_id, year).f_env_mj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_econ_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_econ")]
    assert _footprints_gj(plant_id, year).f_econ_mj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_soc_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_soc")]
    assert _footprints_gj(plant_id, year).f_soc_mj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_f_tech_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "f_tech")]
    assert _footprints_gj(plant_id, year).f_tech_mj == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_sa_raw_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "SA_raw")]
    assert compute_sa_mj(_footprints_gj(plant_id, year)) == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_ex_ref_matches_log(plant_id, year):
    energy = REFERENCE_DATA.energy[(plant_id, year)]
    ex_ref_mj = _ex_ref_mj_from_draft_coefficients(energy.e_el_kwh, energy.v_gas_nm3)
    expected = CALCULATION_LOG[(plant_id, year, "Ex_ref")]
    assert ex_ref_mj / 1000.0 == pytest.approx(expected, rel=1e-3)


@pytest.mark.parametrize("plant_id,year", REFERENCE_DATA.plant_years())
def test_tsi_abs_matches_log(plant_id, year):
    expected = CALCULATION_LOG[(plant_id, year, "TSI_abs")]
    assert _tsi_abs(plant_id, year) == pytest.approx(expected, abs=2e-3)


@pytest.mark.parametrize("plant_id,year", PLANT_YEARS_2025)
def test_tsi_rel_matches_log(plant_id, year):
    tsi_abs_2025 = _tsi_abs(plant_id, 2025)
    tsi_abs_2023 = _tsi_abs(plant_id, 2023)
    expected = CALCULATION_LOG[(plant_id, year, "TSI_rel")]
    actual = compute_tsi_rel(tsi_abs_2025, tsi_abs_2023, record_key=plant_id)
    assert actual == pytest.approx(expected, rel=2e-2)
