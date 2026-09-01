from datetime import UTC, datetime

from src.engines.base import CalculationContext
from src.engines.eea.engine import EEAEngine, EEAInputs
from src.engines.eea.formulas import ComparabilityCheck, EEAComponentsMJ, compute_sa_mj, compute_tsi_norm


def _components(**overrides):
    defaults = {"f_env_mj": 1000, "f_econ_mj": 500, "f_soc_mj": 200, "f_tech_mj": 300}
    defaults.update(overrides)
    return EEAComponentsMJ(**defaults)


def _full_comparability(**overrides):
    defaults = {"baseline_available": True, "same_perimeter": True,
                     "same_functional_unit": True, "same_coefficient_set": True}
    defaults.update(overrides)
    return ComparabilityCheck(**defaults)


def _context():
    return CalculationContext(
        period_start=datetime(2026, 1, 1, tzinfo=UTC),
        period_end=datetime(2026, 1, 31, tzinfo=UTC),
        plant_id="D060", baseline_id="BASELINE_2017",
        coefficient_set_id="COEFF_2026_01", scenario="CURRENT", lot_id="LOT-001",
    )


def test_sa_is_sum_of_four_footprints():
    assert compute_sa_mj(_components()) == 2000


def test_nominal_tsi_norm():
    engine = EEAEngine()
    ctx = _context()
    inputs = EEAInputs(components=_components(), sa_historical_mj=2500,
                        comparability=_full_comparability())
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)
    assert result.values["tsi_norm"] == 2000 / 2500
    assert result.quality_flags == []


def test_zero_denominator_sa_historical_zero_yields_null_and_flag():
    tsi, flag = compute_tsi_norm(2000, 0, _full_comparability())
    assert tsi is None
    assert flag == "NON_COMPARABLE"


def test_baseline_unavailable_yields_null_and_flag():
    tsi, flag = compute_tsi_norm(2000, 2500, _full_comparability(baseline_available=False))
    assert tsi is None
    assert flag == "NON_COMPARABLE"


def test_perimeter_mismatch_yields_null_and_flag():
    tsi, flag = compute_tsi_norm(2000, 2500, _full_comparability(same_perimeter=False))
    assert tsi is None
    assert flag == "NON_COMPARABLE"


def test_unit_conversion_gj_matches_sum_of_component_gj():
    engine = EEAEngine()
    ctx = _context()
    inputs = EEAInputs(components=_components(), sa_historical_mj=2500,
                        comparability=_full_comparability())
    result = engine.calculate(ctx, inputs)
    assert result.values["sa_gj"] == (
        result.values["f_env_gj"] + result.values["f_econ_gj"]
        + result.values["f_soc_gj"] + result.values["f_tech_gj"]
    )
    assert result.values["sa_gj"] == result.values["sa_mj"] / 1000.0


def test_non_comparable_engine_output_does_not_raise():
    engine = EEAEngine()
    ctx = _context()
    inputs = EEAInputs(components=_components(), sa_historical_mj=0,
                        comparability=_full_comparability())
    result = engine.calculate(ctx, inputs)
    engine.validate_outputs(result)  # must not raise: NULL tsi_norm is expected here
    assert result.values["tsi_norm"] is None
    assert "NON_COMPARABLE" in result.quality_flags
