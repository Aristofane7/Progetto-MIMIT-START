from datetime import UTC, datetime

import pytest

from src.engines.base import CalculationContext, make_calc_run_id


def _ctx(**overrides):
    defaults = {
        "period_start": datetime(2026, 1, 1, tzinfo=UTC),
        "period_end": datetime(2026, 1, 31, tzinfo=UTC),
        "plant_id": "D060",
        "baseline_id": "BASELINE_2017",
        "coefficient_set_id": "COEFF_2026_01",
        "scenario": "CURRENT",
    }
    defaults.update(overrides)
    return CalculationContext(**defaults)


def test_context_rejects_invalid_scenario():
    with pytest.raises(ValueError):
        _ctx(scenario="BASELINE")


def test_context_rejects_inverted_period():
    with pytest.raises(ValueError):
        _ctx(
            period_start=datetime(2026, 2, 1, tzinfo=UTC),
            period_end=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_make_calc_run_id_is_deterministic():
    ctx = _ctx()
    run_id_1 = make_calc_run_id("TEI", "1.0.0", ctx, seq="001")
    run_id_2 = make_calc_run_id("TEI", "1.0.0", ctx, seq="001")
    assert run_id_1 == run_id_2
    assert "TEI" in run_id_1 and "D060" in run_id_1


def test_make_calc_run_id_changes_with_seq():
    ctx = _ctx()
    assert make_calc_run_id("TEI", "1.0.0", ctx, "001") != make_calc_run_id("TEI", "1.0.0", ctx, "002")
