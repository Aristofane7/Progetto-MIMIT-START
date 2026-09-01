"""Unit tests for the ADR-012 aggregate model (Ex_ref, SA_w, Phi, Psi, TSI_abs,
TSI_rel). Numbers below are the D020/2023 values hand-verified against the real
RP7.3_calculation_log.xlsx (R001-R010) in ADR-012 — not fabricated."""
import pytest

from src.core.coefficients import Coefficient, CoefficientSet
from src.core.weights import Weight, WeightSet
from src.engines.eea.formulas import (
    DIM_ECON,
    DIM_ENV,
    DIM_SOC,
    DIM_TECH,
    EEAComponentsMJ,
    compute_ex_ref_mj,
    compute_phi,
    compute_psi_efficiency,
    compute_sa_weighted_mj,
    compute_tsi_abs,
    compute_tsi_rel,
)
from src.engines.errors import EngineError, ErrorCategory


def _coeff(code, value):
    return Coefficient(coefficient_id=code, domain="TEI", code=code, value=value,
                        unit="n/a", confidence="B")


def _rp73_coefficient_set():
    return CoefficientSet("COEFF_RP73_PROVISIONAL_2026", "APPROVED", {
        "EL_EX": _coeff("EL_EX", 3.6),
        "GAS_EX": _coeff("GAS_EX", 42),
    })


def _rp73_weight_set():
    weights = {
        (DIM_ENV, ""): Weight(DIM_ENV, "", 0.3661),
        (DIM_ECON, ""): Weight(DIM_ECON, "", 0.1451),
        (DIM_SOC, ""): Weight(DIM_SOC, "", 0.0955),
        (DIM_TECH, ""): Weight(DIM_TECH, "", 0.3934),
    }
    return WeightSet("EEA_AHP_RP73_1", "APPROVED", weights)


def test_ex_ref_matches_d020_2023():
    ex_ref_mj = compute_ex_ref_mj(
        e_el_kwh=10872222, v_gas_nm3=3727619, coefficients=_rp73_coefficient_set(), record_key="D020-2023"
    )
    assert ex_ref_mj / 1000.0 == pytest.approx(195700, rel=1e-4)


def test_ex_ref_rejects_negative_input():
    with pytest.raises(EngineError) as exc:
        compute_ex_ref_mj(-1, 100, _rp73_coefficient_set(), "D020-2023")
    assert exc.value.category == ErrorCategory.PHYSICAL_RANGE_ERROR


def test_ex_ref_missing_coefficient_raises():
    with pytest.raises(EngineError) as exc:
        compute_ex_ref_mj(100, 100, CoefficientSet("EMPTY", "APPROVED", {}), "D020-2023")
    assert exc.value.category == ErrorCategory.MISSING_COEFFICIENT


def test_sa_weighted_matches_d020_2023():
    # Sec. ADR-012: components in GJ already (SA_w computed directly on GJ
    # footprints in the real log, so we mirror that here for the reference check).
    components = EEAComponentsMJ(f_env_mj=6283.68, f_econ_mj=7234.288, f_soc_mj=4495.248, f_tech_mj=22.5568)
    sa_w = compute_sa_weighted_mj(components, _rp73_weight_set())
    assert sa_w == pytest.approx(3788.0178, rel=1e-3)


def test_phi_matches_d020_2023():
    phi = compute_phi(sa_w_gj=3788.0178, ex_ref_gj=195700, record_key="D020-2023")
    assert phi == pytest.approx(0.0194, abs=1e-3)


def test_phi_zero_ex_ref_rejected():
    with pytest.raises(EngineError) as exc:
        compute_phi(sa_w_gj=100, ex_ref_gj=0, record_key="D020-2023")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR


def test_psi_is_pass_through():
    assert compute_psi_efficiency(0.154) == 0.154


def test_tsi_abs_matches_d020_2023():
    tsi_abs = compute_tsi_abs(phi=0.0194, psi=0.154)
    assert tsi_abs == pytest.approx(0.0867, abs=1e-4)


def test_tsi_abs_custom_alpha_beta():
    assert compute_tsi_abs(phi=1.0, psi=0.0, alpha=0.2, beta=0.8) == pytest.approx(0.2)


def test_tsi_rel_matches_d020_2025_over_2023():
    tsi_rel = compute_tsi_rel(tsi_abs_current=0.118, tsi_abs_baseline=0.0867, record_key="D020")
    assert tsi_rel == pytest.approx(1.3616, rel=1e-2)


def test_tsi_rel_zero_baseline_rejected():
    with pytest.raises(EngineError) as exc:
        compute_tsi_rel(tsi_abs_current=0.1, tsi_abs_baseline=0.0, record_key="D020")
    assert exc.value.category == ErrorCategory.CALCULATION_ERROR
