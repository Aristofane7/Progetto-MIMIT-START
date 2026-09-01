"""EEA+ aggregation and TSI. Spec ref: sec. 18 (DOC)."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.units.energy import mj_to_gj


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
