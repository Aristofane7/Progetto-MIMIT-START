from datetime import UTC, datetime

import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.engines.base import CalculationContext
from src.engines.errors import EngineError, ErrorCategory
from src.engines.sfa.engine import SFAEngine, SFAInputs
from src.engines.sfa.formulas import (
    SFAPeriodFlows,
    StakeholderValue,
    check_no_individual_identifiers,
    compute_stakeholder_value,
)


def _coeff(code, value):
    return Coefficient(coefficient_id=code, domain="SFA", code=code, value=value,
                        unit="n/a", confidence="A")


def _coefficient_set():
    values = {"GAMMA_EUR": 0.5, "GAMMA_CO2_MJ": 2.0, "GAMMA_CO2_DALY": 0.001,
              "RHO_TRAIN": 0.2, "B_LABOR_H": 10.0}
    return CoefficientSet("COEFF_2026_01", "APPROVED", {k: _coeff(k, v) for k, v in values.items()})


def _flows(**overrides):
    defaults = {
        "gamma_eur_coefficient_code": "GAMMA_EUR",
        "gamma_co2_mj_coefficient_code": "GAMMA_CO2_MJ",
        "gamma_co2_daly_coefficient_code": "GAMMA_CO2_DALY",
        "rho_train_coefficient_code": "RHO_TRAIN",
        "b_labor_hour_coefficient_code": "B_LABOR_H",
        "em_co2_kg": 1000,
        "hours_lost": 20,
        "hours_training": 40,
        "stakeholder_values": [StakeholderValue("LINE_D060_OPERATORS", value_eur=5000)],
    }
    defaults.update(overrides)
    return SFAPeriodFlows(**defaults)


def _context(coefficient_set_id="COEFF_2026_01"):
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060", baseline_id="BASELINE_2017",
        coefficient_set_id=coefficient_set_id, scenario="CURRENT", lot_id="LOT-001",
    )


def test_nominal_case():
    engine = SFAEngine()
    ctx = _context()
    inputs = SFAInputs(current=_flows(), baseline=_flows(em_co2_kg=1200),
                        coefficients=_coefficient_set(), baseline_coefficient_set_id="COEFF_2026_01")
    engine.validate_inputs(ctx, inputs)
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert result.values["f_soc_gj"] == result.values["f_soc_mj"] / 1000.0


def test_daly_is_diagnostic_only_and_excluded_from_f_soc():
    engine = SFAEngine()
    ctx = _context()
    inputs = SFAInputs(current=_flows(), baseline=_flows(), coefficients=_coefficient_set(),
                        baseline_coefficient_set_id="COEFF_2026_01")
    result = engine.calculate(ctx, inputs)
    assert "daly_diagnostic" in result.values
    persisted = engine.persist(result)
    assert "daly" not in persisted["row"]


def test_zero_boundary_case():
    engine = SFAEngine()
    ctx = _context()
    empty = _flows(em_co2_kg=0, hours_lost=0, hours_training=0, stakeholder_values=[])
    inputs = SFAInputs(current=empty, baseline=empty, coefficients=_coefficient_set(),
                        baseline_coefficient_set_id="COEFF_2026_01")
    result = engine.calculate(ctx, inputs)
    assert result.values["f_soc_mj"] == 0.0


def test_missing_coefficient_raises():
    with pytest.raises(EngineError) as exc:
        compute_stakeholder_value(_flows(), CoefficientSet("EMPTY", "APPROVED", {}), "LOT-001")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_negative_invalid_value_rejected():
    bad = _flows(stakeholder_values=[StakeholderValue("LINE_D060", value_eur=-1)])
    with pytest.raises(EngineError) as exc:
        compute_stakeholder_value(bad, _coefficient_set(), "LOT-001")
    assert exc.value.category == ErrorCategory.PHYSICAL_RANGE_ERROR


def test_baseline_mismatch_rejected():
    engine = SFAEngine()
    ctx = _context(coefficient_set_id="COEFF_2026_01")
    inputs = SFAInputs(current=_flows(), baseline=_flows(), coefficients=_coefficient_set(),
                        baseline_coefficient_set_id="COEFF_2025_12")
    with pytest.raises(EngineError) as exc:
        engine.validate_inputs(ctx, inputs)
    assert exc.value.category == ErrorCategory.BASELINE_MISMATCH


def test_privacy_guard_rejects_individual_identifiers():
    bad = _flows(stakeholder_values=[StakeholderValue("123456", value_eur=100)])
    with pytest.raises(EngineError) as exc:
        check_no_individual_identifiers(bad, "LOT-001")
    assert exc.value.category == ErrorCategory.VALIDATION_ERROR
