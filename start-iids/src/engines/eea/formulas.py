"""EEA+ aggregation and TSI. Spec ref: sec. 18 (DOC)."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.core.weights import WeightSet
from src.engines.errors import EngineError, ErrorCategory

# Sec. 18.1 dimension codes, as published in ahp_weights.xlsx / RP7.3_calculation_log.xlsx.
DIM_ENV = "env"
DIM_ECON = "econ"
DIM_SOC = "soc"
DIM_TECH = "tech"


@dataclass(frozen=True)
class EEAComponentsMJ:
    f_env_mj: float
    f_econ_mj: float
    f_soc_mj: float
    f_tech_mj: float


@dataclass(frozen=True)
class ComparabilityCheck:
    """Sec. 18.4 preconditions for a valid tsi_norm ratio."""

    baseline_available: bool
    same_perimeter: bool
    same_functional_unit: bool
    same_coefficient_set: bool

    def is_comparable(self) -> bool:
        return (
            self.baseline_available
            and self.same_perimeter
            and self.same_functional_unit
            and self.same_coefficient_set
        )


def compute_sa_mj(components: EEAComponentsMJ) -> float:
    """Sec. 18.1: SA = f_env + f_econ + f_soc + f_tech."""
    return components.f_env_mj + components.f_econ_mj + components.f_soc_mj + components.f_tech_mj


def compute_tsi_norm(
    sa_current_mj: float, sa_historical_mj: float, comparability: ComparabilityCheck
) -> tuple[float | None, str | None]:
    """Sec. 18.2 / 18.4: TSI_norm = SA_current / SA_historical, gated by
    comparability preconditions and a non-zero historical denominator. Returns
    ``(tsi_norm, quality_flag)`` where quality_flag is ``'NON_COMPARABLE'`` when
    tsi_norm must be NULL — never silently coerced to 0 or 1."""
    if not comparability.is_comparable():
        return None, "NON_COMPARABLE"
    if sa_historical_mj == 0:
        return None, "NON_COMPARABLE"
    return sa_current_mj / sa_historical_mj, None


@dataclass(frozen=True)
class EEAState:
    f_env_mj: float
    f_econ_mj: float
    f_soc_mj: float
    f_tech_mj: float
    sa_mj: float
    f_env_gj: float
    f_econ_gj: float
    f_soc_gj: float
    f_tech_gj: float
    sa_gj: float
    tsi_norm: float | None
    quality_flag: str | None


def build_eea_state(
    components: EEAComponentsMJ, sa_historical_mj: float, comparability: ComparabilityCheck
) -> EEAState:
    sa_mj = compute_sa_mj(components)
    tsi_norm, quality_flag = compute_tsi_norm(sa_mj, sa_historical_mj, comparability)
    return EEAState(
        f_env_mj=components.f_env_mj,
        f_econ_mj=components.f_econ_mj,
        f_soc_mj=components.f_soc_mj,
        f_tech_mj=components.f_tech_mj,
        sa_mj=sa_mj,
        f_env_gj=mj_to_gj(components.f_env_mj),
        f_econ_gj=mj_to_gj(components.f_econ_mj),
        f_soc_gj=mj_to_gj(components.f_soc_mj),
        f_tech_gj=mj_to_gj(components.f_tech_mj),
        sa_gj=mj_to_gj(sa_mj),
        tsi_norm=tsi_norm,
        quality_flag=quality_flag,
    )


# --- Real RP7.3 aggregate model (ADR-012): Ex_ref, SA_w, Phi, Psi, TSI_abs, TSI_rel ---
# Verified by hand against RP7.3_calculation_log.xlsx (D020/2023: R001-R010) before
# being implemented — see ADR-012 for the worked-through numbers.


def compute_ex_ref_mj(
    e_el_kwh: float, v_gas_nm3: float, coefficients: CoefficientSet, record_key: str
) -> float:
    """Reference plant exergy input: Ex_ref = Ex_el + Ex_fuel.

    Ex_el = E_el_kWh * EL_EX (EL_EX = 3.6 MJ/kWh, same physical constant as
    `kwh_to_mj` — sourced from the `Coefficienti` sheet as an APPROVABLE
    coefficient rather than hardcoded here). Ex_fuel = V_gas_Nm3 * GAS_EX
    (chemical exergy of natural gas, MJ/Nm3). Confirmed verbatim as Eq. (18) in
    "RP7.3 Report di Assessment termodinamico della fabbrica.pdf" sec. 2.3
    (ADR-019) — fuel conversion efficiency is deliberately kept inside Psi,
    not this denominator ("tenendo l'efficienza di conversione all'interno di
    Ψ e non nel denominatore Ex_ref").
    """
    if e_el_kwh < 0 or v_gas_nm3 < 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"e_el_kwh and v_gas_nm3 must not be negative, got {e_el_kwh!r}, {v_gas_nm3!r}",
            record_key=record_key,
        )
    el_ex = coefficients.get("EL_EX").value
    gas_ex = coefficients.get("GAS_EX").value
    ex_el_mj = e_el_kwh * el_ex
    ex_fuel_mj = v_gas_nm3 * gas_ex
    return ex_el_mj + ex_fuel_mj


def compute_sa_weighted_mj(components: EEAComponentsMJ, weight_set: WeightSet) -> float:
    """SA_w = sum(w_i * f_i) over the four sustainability dimensions, AHP-weighted
    (sec. 24.8-style governance: weights come from an approved/versioned
    `WeightSet`, never hardcoded). Weights are used as published even when they
    do not sum to exactly 1 (rounding in the source AHP sheet) — see ADR-012."""
    return (
        weight_set.get_dimension_weight(DIM_ENV) * components.f_env_mj
        + weight_set.get_dimension_weight(DIM_ECON) * components.f_econ_mj
        + weight_set.get_dimension_weight(DIM_SOC) * components.f_soc_mj
        + weight_set.get_dimension_weight(DIM_TECH) * components.f_tech_mj
    )


def compute_phi(sa_w_gj: float, ex_ref_gj: float, record_key: str) -> float:
    """Phi = SA_w / Ex_ref (both in GJ, dimensionless result)."""
    if ex_ref_gj == 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            "ex_ref_gj is zero: Phi is undefined",
            record_key=record_key,
        )
    return sa_w_gj / ex_ref_gj


def compute_psi_efficiency(psi_reported: float) -> float:
    """Psi = Ex_useful / Ex_ref.

    ADR-012's open item is resolved by ADR-019: "RP7.3 Report di Assessment
    termodinamico della fabbrica.pdf" sec. 2.3 confirms Ex_useful is a
    directly-tracked exergy quantity in the beta methodology, not decomposed
    via a production coefficient — that decomposition is explicit *future*
    work ("consolidamento della libreria dei coefficienti su dati primari ed
    EPD", sec. 4.5), not a gap in this implementation. This function therefore
    stays a documented pass-through of a directly reported Psi value (sourced
    from the real RP7.3 calculation log; cross-checked against the report's
    own Ex_useful column in `tests/regression/test_rp73_calculation_log.py`)
    — it does not, and per the source's own methodology should not, compute
    Psi from an invented coefficient (spec sec. 64 / Appendix L/M).
    """
    return psi_reported


def compute_tsi_abs(phi: float, psi: float, alpha: float = 0.5, beta: float = 0.5) -> float:
    """TSI_abs = alpha*Phi + beta*Psi. RP7.3's logged runs use alpha=beta=0.5;
    both are exposed as parameters (not hardcoded in the caller) so a different,
    approved blend can be supplied without touching this function."""
    return alpha * phi + beta * psi


def compute_tsi_rel(tsi_abs_current: float, tsi_abs_baseline: float, record_key: str) -> float:
    """TSI_rel = TSI_abs(t) / TSI_abs(baseline) — the real RP7.3 ratio underlying
    the spec's simplified `tsi_norm` description (sec. 18.2), see ADR-012."""
    if tsi_abs_baseline == 0:
        raise EngineError(
            ErrorCategory.CALCULATION_ERROR,
            "tsi_abs_baseline is zero: TSI_rel is undefined",
            record_key=record_key,
        )
    return tsi_abs_current / tsi_abs_baseline
