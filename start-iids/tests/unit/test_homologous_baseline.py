"""ADR-025 option A: homologous same-window baseline + duration guard."""
import dataclasses
import pathlib

import pytest

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.engines.eea.aggregate import compute_aggregate_state
from src.engines.errors import EngineError, ErrorCategory
from src.ingestion.rp73_reference_data import load_rp73_calculation_log, load_rp73_reference_data

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "reference"
CONFIG = ROOT / "config"

DATASET = load_rp73_reference_data(DATA / "RP7.3_data_collection_20232025.xlsx")
LOG = load_rp73_calculation_log(DATA / "RP7.3_calculation_log.xlsx")
COEFF = load_coefficient_set(CONFIG / "coefficients" / "rp73_provisional_2026.yaml")
WEIGHTS = load_weight_set(CONFIG / "weights" / "eea_ahp_rp73.yaml")


def _state(data, plant, year):
    return compute_aggregate_state(plant, year, data, COEFF, WEIGHTS,
                                   psi=LOG[(plant, year, "Psi")])


def test_d020_2025_uses_homologous_reference_and_stays_comparable():
    """Option A: D020/2025 is computed against the homologous 2022 Jan-July
    baseline and reproduces the golden log. The intensive ratios (Phi, Psi,
    TSI_abs) stay on the comparable 0.1x scale of the full-year plants, while the
    extensive Ex_ref is scaled down to the ~7-month period (not a full year)."""
    state = _state(DATASET, "D020", 2025)
    assert state.tsi_abs == pytest.approx(LOG[("D020", 2025, "TSI_abs")], abs=2e-3)
    assert state.phi == pytest.approx(LOG[("D020", 2025, "Phi")], abs=2e-3)
    assert state.ex_ref_gj == pytest.approx(LOG[("D020", 2025, "Ex_ref")], rel=1e-3)
    assert state.ex_ref_gj < 130_000                          # partial-window, not a full year


def test_duration_mismatch_without_override_is_blocked():
    """A partial window (months_active=7) compared against the full annual 2022
    baseline, with NO homologous override, is a TEMPORAL_MISMATCH blocker."""
    broken = dataclasses.replace(DATASET, baseline_override={})  # drop the D020/2025 override
    with pytest.raises(EngineError) as exc:
        _state(broken, "D020", 2025)
    assert exc.value.category is ErrorCategory.TEMPORAL_MISMATCH


def test_full_year_plants_unaffected():
    """D060/D240 (full 12-month years) keep the annual-2022 baseline and match the log."""
    for plant in ("D060", "D240"):
        state = _state(DATASET, plant, 2025)
        assert state.tsi_abs == pytest.approx(LOG[(plant, 2025, "TSI_abs")], abs=2e-3)
