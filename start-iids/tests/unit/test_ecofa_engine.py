from datetime import UTC, datetime

import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.engines.base import CalculationContext
from src.engines.ecofa.engine import EcoFAEngine, EcoFAInputs
from src.engines.ecofa.formulas import (
    CostItem,
    EcoFAPeriodFlows,
    check_deflator_version,
    check_physical_driver_priority,
    compute_economic_input,
)
from src.engines.errors import EngineError, ErrorCategory


def _coeff(code, value):
    return Coefficient(coefficient_id=code, domain="ECOFA", code=code, value=value,
                        unit="MJ/EUR", confidence="A")


def _coefficient_set():
    values = {"GAMMA_SERVICES": 0.4, "GAMMA_VA": 0.6, "GAMMA_INV": 0.3}
    return CoefficientSet("COEFF_2026_01", "APPROVED", {k: _coeff(k, v) for k, v in values.items()})


def _flows(**overrides):
    defaults = {
        "deflator_version": "DEFL_2026_BASE2017",
        "value_added_eur": 100000,
        "value_added_coefficient_code": "GAMMA_VA",
        "fixed_assets_eur": 50000,
        "fixed_assets_coefficient_code": "GAMMA_INV",
        "costs": [CostItem("SERVICES", amount_eur=20000, coefficient_code="GAMMA_SERVICES")],
    }
    defaults.update(overrides)
    return EcoFAPeriodFlows(**defaults)


def _context(coefficient_set_id="COEFF_2026_01"):
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060", baseline_id="BASELINE_2017",
        coefficient_set_id=coefficient_set_id, scenario="CURRENT", lot_id="LOT-001",
    )


def test_nominal_case():
    engine = EcoFAEngine()
    ctx = _context()
    inputs = EcoFAInputs(current=_flows(), baseline=_flows(value_added_eur=90000),
                          coefficients=_coefficient_set(), baseline_coefficient_set_id="COEFF_2026_01")
    engine.validate_inputs(ctx, inputs)
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert result.values["f_econ_gj"] == result.values["f_econ_mj"] / 1000.0


def test_zero_costs_boundary_case():
    engine = EcoFAEngine()
    ctx = _context()
    flows = _flows(costs=[])
    inputs = EcoFAInputs(current=flows, baseline=flows, coefficients=_coefficient_set(),
                          baseline_coefficient_set_id="COEFF_2026_01")
    result = engine.calculate(ctx, inputs)
    assert result.values["f_econ_mj"] == 0.0


def test_missing_coefficient_raises():
    with pytest.raises(EngineError) as exc:
        compute_economic_input(_flows(), CoefficientSet("EMPTY", "APPROVED", {}), "LOT-001")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_negative_invalid_value_rejected():
    bad = _flows(costs=[CostItem("SERVICES", amount_eur=-100, coefficient_code="GAMMA_SERVICES")])
    with pytest.raises(EngineError) as exc:
        compute_economic_input(bad, _coefficient_set(), "LOT-001")
    assert exc.value.category == ErrorCategory.PHYSICAL_RANGE_ERROR


def test_missing_deflator_version_rejected():
    flows = _flows(deflator_version="")
    with pytest.raises(EngineError) as exc:
        check_deflator_version(flows, "LOT-001")
    assert exc.value.category == ErrorCategory.VALIDATION_ERROR


def test_baseline_mismatch_rejected():
    engine = EcoFAEngine()
    ctx = _context(coefficient_set_id="COEFF_2026_01")
    inputs = EcoFAInputs(current=_flows(), baseline=_flows(), coefficients=_coefficient_set(),
                          baseline_coefficient_set_id="COEFF_2025_12")
    with pytest.raises(EngineError) as exc:
        engine.validate_inputs(ctx, inputs)
    assert exc.value.category == ErrorCategory.BASELINE_MISMATCH


def test_physical_driver_priority_rejects_eur_to_mj_when_tkm_available():
    flows = _flows(costs=[CostItem("LOGISTICS_EUR", amount_eur=500, coefficient_code="GAMMA_SERVICES",
                                    has_physical_driver=True)])
    with pytest.raises(EngineError) as exc:
        check_physical_driver_priority(flows, "LOT-001")
    assert exc.value.category == ErrorCategory.VALIDATION_ERROR
