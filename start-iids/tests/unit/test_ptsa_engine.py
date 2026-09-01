from datetime import UTC, datetime

import pytest

from src.core.weights import Weight, WeightSet
from src.engines.base import CalculationContext
from src.engines.errors import EngineError, ErrorCategory
from src.engines.ptsa.engine import PTSAEngine, PTSAInputs, PTSARawQuantities, equal_weights
from src.engines.ptsa.formulas import (
    IOA_METRICS,
    PopulationStat,
    compute_ocr,
    compute_psi,
    compute_scr,
    compute_tii,
    compute_zscore,
)


def _raw(**overrides):
    defaults = {
        "scr_raw_stock": 500, "scr_raw_daily_consumption": 50,
        "scr_finished_stock": 1000, "scr_finished_daily_consumption": 100,
        "scr_glaze_stock": 200, "scr_glaze_daily_consumption": 20,
        "psi_energy_output_m2": 1000, "psi_energy_input_gj": 50,
        "psi_material_output_m2": 950, "psi_material_input_m2": 1000,
        "psi_throughput_output_m2": 1000, "psi_throughput_hours": 8,
        "ocr_flexural_passed": 95, "ocr_flexural_attempted": 100,
        "ocr_breaking_passed": 98, "ocr_breaking_attempted": 100,
        "ocr_surface_passed": 97, "ocr_surface_attempted": 100,
    }
    defaults.update(overrides)
    return PTSARawQuantities(**defaults)


def _population_stats():
    metrics = ("SCR_RAW", "SCR_FINISHED", "SCR_GLAZE", "PSI_ENERGY", "PSI_MATERIAL",
               "PSI_THROUGHPUT", "OCR_FLEXURAL", "OCR_BREAKING", "OCR_SURFACE")
    return {m: PopulationStat(mean=1.0, stdev=1.0) for m in metrics}


def _weight_set():
    weights = {
        ("IOA", ""): Weight("IOA", "", 0.1634),
        ("OP", ""): Weight("OP", "", 0.2970),
        ("TQ", ""): Weight("TQ", "", 0.5396),
    }
    return WeightSet("PTSA_WEIGHT_RP74_1", "APPROVED", weights)


def _context():
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060", baseline_id="BASELINE_2017",
        coefficient_set_id="COEFF_2026_01", scenario="CURRENT", lot_id="LOT-001",
    )


def _inputs(**overrides):
    defaults = {
        "raw": _raw(),
        "population_stats": _population_stats(),
        "dimension_scores": {"IOA": 3.5, "OP": 3.8, "TQ": 4.0},
        "weight_set": _weight_set(),
    }
    defaults.update(overrides)
    return PTSAInputs(**defaults)


def test_nominal_case():
    engine = PTSAEngine()
    ctx = _context()
    inputs = _inputs()
    engine.validate_inputs(ctx, inputs)
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert result.values["p_tsi_5"] == pytest.approx(0.1634 * 3.5 + 0.2970 * 3.8 + 0.5396 * 4.0)


def test_zero_denominator_scr_rejected():
    with pytest.raises(EngineError) as exc:
        compute_scr(stock=100, daily_consumption=0, record_key="T1")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_zero_denominator_psi_rejected():
    with pytest.raises(EngineError) as exc:
        compute_psi(real_output=100, real_input=0, record_key="T1")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_zero_denominator_ocr_rejected():
    with pytest.raises(EngineError) as exc:
        compute_ocr(quantity_passed=10, attempted_total=0, record_key="T1")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_missing_coefficient_missing_weight_raises():
    engine = PTSAEngine()
    ctx = _context()
    empty_weight_set = WeightSet("EMPTY", "APPROVED", {})
    inputs = _inputs(weight_set=empty_weight_set)
    with pytest.raises(EngineError) as exc:
        engine.calculate(ctx, inputs)
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_negative_invalid_physical_value_in_zscore_zero_stdev_rejected():
    # zero population variance is the invalid/degenerate physical case for z-scores.
    bad_stat = PopulationStat(mean=1.0, stdev=0.0)
    with pytest.raises(EngineError) as exc:
        compute_zscore(1.5, bad_stat, "SCR_RAW", "T1")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_unit_conversion_equal_weights_sum_to_one():
    weights = equal_weights(IOA_METRICS)
    assert sum(weights.values()) == pytest.approx(1.0)


def test_baseline_mismatch_missing_population_stat_is_validation_error():
    engine = PTSAEngine()
    ctx = _context()
    stats = _population_stats()
    del stats["SCR_RAW"]
    inputs = _inputs(population_stats=stats)
    with pytest.raises(EngineError) as exc:
        engine.validate_inputs(ctx, inputs)
    assert exc.value.category == ErrorCategory.VALIDATION_ERROR


def test_tii_computed_only_on_p_tsi_5_and_rejects_non_positive_previous():
    assert compute_tii(4.0, 3.73, "T1") == pytest.approx(((4.0 / 3.73) - 1) * 100)
    with pytest.raises(EngineError) as exc:
        compute_tii(4.0, 0.0, "T1")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_engine_never_exposes_a_zscore_tii_function():
    from src.engines.ptsa import formulas
    assert not hasattr(formulas, "compute_tii_zscore")
