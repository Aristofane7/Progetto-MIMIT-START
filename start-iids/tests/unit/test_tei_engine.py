"""TEI-J engine tests. Spec sec. 42 mandates 6 categories per formula:
nominal, zero denominator, missing coefficient, negative invalid physical value,
unit conversion, baseline mismatch."""
from datetime import UTC, datetime

import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.core.units.energy import kwh_to_mj
from src.engines.base import CalculationContext
from src.engines.errors import EngineError, ErrorCategory
from src.engines.tei.engine import TEIEngine, TEIInputs
from src.engines.tei.formulas import MTOFlow, MTSFlow, compute_backlog, compute_mts_exergy


def _coeff(code, value, domain="TEI", confidence="A"):
    return Coefficient(coefficient_id=code, domain=domain, code=code, value=value,
                        unit="n/a", confidence=confidence)


def _coefficient_set(**overrides):
    values = {
        "B_RM": 1.2, "B_UW": 0.8, "B_SDM": 1.5, "B_TILE": 25.0,
        "PCI_GAS": 35.0, "F_EX_GAS": 1.04,
        "KAPPA_MTS": 0.1, "Q_THR_MTS": 0.95,
        "KAPPA_MTO": 0.1, "Q_THR_MTO": 0.95,
    }
    values.update(overrides)
    return CoefficientSet(
        coefficient_set_id="COEFF_2026_01",
        status="APPROVED",
        coefficients={code: _coeff(code, v) for code, v in values.items()},
    )


def _context(coefficient_set_id="COEFF_2026_01"):
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060",
        baseline_id="BASELINE_2017",
        coefficient_set_id=coefficient_set_id,
        scenario="CURRENT",
        lot_id="LOT-001",
    )


def _nominal_inputs(**overrides):
    defaults = {
        "current_mts": MTSFlow(m_rm_kg=1000, m_uw_kg=50, m_sdm_kg=900, e_sd_kwh=200, t_prod_h=8),
        "current_mto": MTOFlow(m_sdu_kg=900, n_t_man=1000, n_t_sold=900, e_form_kwh=150,
                             e_kiln_nm3=300, t_prod_h=8),
        "baseline_mts": MTSFlow(m_rm_kg=1100, m_uw_kg=80, m_sdm_kg=950, e_sd_kwh=260, t_prod_h=8),
        "baseline_mto": MTOFlow(m_sdu_kg=950, n_t_man=1000, n_t_sold=1000, e_form_kwh=200,
                              e_kiln_nm3=350, t_prod_h=8),
        "coefficients": _coefficient_set(),
        "baseline_coefficient_set_id": "COEFF_2026_01",
    }
    defaults.update(overrides)
    return TEIInputs(**defaults)


def test_nominal_case_produces_finite_f_tech():
    engine = TEIEngine()
    ctx = _context()
    inputs = _nominal_inputs()
    engine.validate_inputs(ctx, inputs)
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert isinstance(result.values["f_tech_mj"], float)
    assert result.values["f_tech_gj"] == result.values["f_tech_mj"] / 1000.0


def test_zero_denominator_n_man_zero_rejects_run():
    mto = MTOFlow(m_sdu_kg=900, n_t_man=0, n_t_sold=0, e_form_kwh=150, e_kiln_nm3=300, t_prod_h=8)
    with pytest.raises(EngineError) as exc:
        compute_backlog(mto, ex_t_mj=0.0, record_key="LOT-001")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_n_sold_greater_than_n_man_flags_temporal_mismatch_without_clamping():
    mto = MTOFlow(m_sdu_kg=900, n_t_man=100, n_t_sold=150, e_form_kwh=150, e_kiln_nm3=300, t_prod_h=8)
    ex_inv, flags = compute_backlog(mto, ex_t_mj=1000.0, record_key="LOT-001")
    assert "TEMPORAL_MISMATCH" in flags
    assert ex_inv < 0  # not clamped to zero


def test_missing_coefficient_raises():
    mts = MTSFlow(m_rm_kg=100, m_uw_kg=10, m_sdm_kg=90, e_sd_kwh=20, t_prod_h=8)
    with pytest.raises(EngineError) as exc:
        compute_mts_exergy(mts, CoefficientSet("EMPTY", "APPROVED", {}), record_key="LOT-001")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_negative_invalid_physical_value_rejected():
    coeff_set = _coefficient_set()
    mts = MTSFlow(m_rm_kg=-5, m_uw_kg=10, m_sdm_kg=90, e_sd_kwh=20, t_prod_h=8)
    with pytest.raises(EngineError) as exc:
        compute_mts_exergy(mts, coeff_set, record_key="LOT-001")
    assert exc.value.category == ErrorCategory.PHYSICAL_RANGE_ERROR


def test_unit_conversion_electricity_matches_reference():
    mts = MTSFlow(m_rm_kg=0, m_uw_kg=0, m_sdm_kg=0, e_sd_kwh=100, t_prod_h=8)
    ex = compute_mts_exergy(mts, _coefficient_set(), record_key="LOT-001")
    assert ex.ex_e_sd_mj == kwh_to_mj(100) == 360.0


def test_baseline_mismatch_rejected_before_calculation():
    engine = TEIEngine()
    ctx = _context(coefficient_set_id="COEFF_2026_01")
    inputs = _nominal_inputs(baseline_coefficient_set_id="COEFF_2025_12")
    with pytest.raises(EngineError) as exc:
        engine.validate_inputs(ctx, inputs)
    assert exc.value.category == ErrorCategory.BASELINE_MISMATCH
