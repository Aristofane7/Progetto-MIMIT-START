from datetime import UTC, datetime

import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.engines.base import CalculationContext
from src.engines.efa.engine import EFAEngine, EFAInputs
from src.engines.efa.formulas import (
    EFAPeriodFlows,
    MaterialFlow,
    RecoveryCredit,
    WasteFlow,
    check_no_double_counting,
    compute_resource_intake,
)
from src.engines.errors import EngineError, ErrorCategory


def _coeff(code, value):
    return Coefficient(coefficient_id=code, domain="EFA", code=code, value=value,
                        unit="n/a", confidence="A")


def _coefficient_set(**overrides):
    values = {"B_CLAY": 2.0, "B_WASTE": 0.5, "GAMMA_CO2": 1.5}
    values.update(overrides)
    return CoefficientSet("COEFF_2026_01", "APPROVED", {k: _coeff(k, v) for k, v in values.items()})


def _flows(**overrides):
    defaults = {
        "electricity_kwh": 100,
        "materials": [MaterialFlow("MAT_CLAY", mass_kg=500, coefficient_code="B_CLAY")],
        "wastes": [WasteFlow("WASTE_1", quantity_kg=20, coefficient_code="B_WASTE")],
    }
    defaults.update(overrides)
    return EFAPeriodFlows(**defaults)


def _context(coefficient_set_id="COEFF_2026_01"):
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060", baseline_id="BASELINE_2017",
        coefficient_set_id=coefficient_set_id, scenario="CURRENT", lot_id="LOT-001",
    )


def test_nominal_case():
    engine = EFAEngine()
    ctx = _context()
    inputs = EFAInputs(current=_flows(), baseline=_flows(electricity_kwh=120),
                        coefficients=_coefficient_set(), baseline_coefficient_set_id="COEFF_2026_01")
    engine.validate_inputs(ctx, inputs)
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert result.values["f_env_gj"] == result.values["f_env_mj"] / 1000.0


def test_all_zero_boundary_case():
    # f_env has no denominator; the equivalent boundary case is all-zero flows.
    engine = EFAEngine()
    ctx = _context()
    empty = EFAPeriodFlows(electricity_kwh=0)
    inputs = EFAInputs(current=empty, baseline=empty, coefficients=_coefficient_set(),
                        baseline_coefficient_set_id="COEFF_2026_01")
    result = engine.calculate(ctx, inputs)
    assert result.values["f_env_mj"] == 0.0


def test_missing_coefficient_raises():
    with pytest.raises(EngineError) as exc:
        compute_resource_intake(_flows(), CoefficientSet("EMPTY", "APPROVED", {}), "LOT-001")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_negative_invalid_physical_value_rejected():
    bad = _flows(materials=[MaterialFlow("MAT_CLAY", mass_kg=-10, coefficient_code="B_CLAY")])
    with pytest.raises(EngineError) as exc:
        compute_resource_intake(bad, _coefficient_set(), "LOT-001")
    assert exc.value.category == ErrorCategory.PHYSICAL_RANGE_ERROR


def test_unit_conversion_electricity():
    ri = compute_resource_intake(EFAPeriodFlows(electricity_kwh=10), _coefficient_set(), "LOT-001")
    assert ri == 36.0  # 10 kWh * 3.6 MJ/kWh


def test_baseline_mismatch_rejected():
    engine = EFAEngine()
    ctx = _context(coefficient_set_id="COEFF_2026_01")
    inputs = EFAInputs(current=_flows(), baseline=_flows(), coefficients=_coefficient_set(),
                        baseline_coefficient_set_id="COEFF_2025_12")
    with pytest.raises(EngineError) as exc:
        engine.validate_inputs(ctx, inputs)
    assert exc.value.category == ErrorCategory.BASELINE_MISMATCH


def test_double_counting_rejected():
    flows = EFAPeriodFlows(
        electricity_kwh=0,
        wastes=[WasteFlow("REC_1", quantity_kg=10, coefficient_code="B_WASTE", is_internal_recycle=True)],
        recoveries=[RecoveryCredit("REC_1", ex_rec_mat_mj=5.0, ex_rec_th_mj=0.0)],
    )
    with pytest.raises(EngineError) as exc:
        check_no_double_counting(flows, "LOT-001")
    assert exc.value.category == ErrorCategory.VALIDATION_ERROR
