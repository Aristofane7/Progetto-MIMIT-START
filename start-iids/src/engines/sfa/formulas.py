"""SFA-J pure formulas (Social Footprint Assessment, Joule-based).

Spec ref: sec. 17 (DOC).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.core.coefficients import CoefficientSet
from src.engines.errors import EngineError, ErrorCategory

_INDIVIDUAL_IDENTIFIER_PATTERN = re.compile(
    r"(^\d{4,}$)|matricola|codice.?fiscale|\bssn\b|nominativ", re.IGNORECASE
)


@dataclass(frozen=True)
class StakeholderValue:
    stakeholder_code: str
    value_eur: float


@dataclass(frozen=True)
class SFAPeriodFlows:
    gamma_eur_coefficient_code: str  # gamma_€
    gamma_co2_mj_coefficient_code: str  # gamma_CO2^MJ
    gamma_co2_daly_coefficient_code: str  # gamma_CO2^DALY — diagnostic only
    rho_train_coefficient_code: str
    b_labor_hour_coefficient_code: str  # b_L,h
    em_co2_kg: float
    hours_lost: float
    hours_training: float
    stakeholder_values: list[StakeholderValue] = field(default_factory=list)


def _require_non_negative(value: float, field_name: str, record_key: str) -> None:
    if value < 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"'{field_name}' must not be negative, got {value}",
            record_key=record_key,
        )


def check_no_individual_identifiers(flows: SFAPeriodFlows, record_key: str) -> None:
    """Sec. 17.8: the social mart must never carry names, employee numbers, or
    individual health data — only plant/line-aggregated stakeholder categories.
    Best-effort static guard on the stakeholder_code label; not a substitute for
    upstream aggregation policy."""
    offending = [
        sv.stakeholder_code
        for sv in flows.stakeholder_values
        if _INDIVIDUAL_IDENTIFIER_PATTERN.search(sv.stakeholder_code)
    ]
    if offending:
        raise EngineError(
            ErrorCategory.VALIDATION_ERROR,
            f"stakeholder_code(s) look like individual identifiers, not aggregates: {offending}",
            record_key=record_key,
        )


def compute_stakeholder_value(flows: SFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 17.2: Ex_SV = sum_stk V_stk * gamma_€."""
    total_value = 0.0
    for sv in flows.stakeholder_values:
        _require_non_negative(sv.value_eur, f"stakeholder[{sv.stakeholder_code}].value_eur", record_key)
        total_value += sv.value_eur
    gamma_eur = coefficients.get(flows.gamma_eur_coefficient_code).value
    return total_value * gamma_eur


def compute_co2_exergy(flows: SFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 17.3: Ex_CO2 = Em_CO2 * gamma_CO2^MJ."""
    _require_non_negative(flows.em_co2_kg, "em_co2_kg", record_key)
    gamma = coefficients.get(flows.gamma_co2_mj_coefficient_code).value
    return flows.em_co2_kg * gamma


def compute_daly_diagnostic(flows: SFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 17.4: DALY = Em_CO2 * gamma_CO2^DALY.

    DIAGNOSTIC ONLY (ADR-010): this value must never be added into f_soc until a
    DALY -> Joule mapping is formally approved (feature flag `daly_to_joule`,
    currently and permanently false for v1 per sec. 17.4 / Appendix F).
    """
    _require_non_negative(flows.em_co2_kg, "em_co2_kg", record_key)
    gamma = coefficients.get(flows.gamma_co2_daly_coefficient_code).value
    return flows.em_co2_kg * gamma


def compute_lost_hours_exergy(flows: SFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 17.5: Ex_lost = H_lost * b_L,h."""
    _require_non_negative(flows.hours_lost, "hours_lost", record_key)
    b_l_h = coefficients.get(flows.b_labor_hour_coefficient_code).value
    return flows.hours_lost * b_l_h


def compute_training_credit_exergy(
    flows: SFAPeriodFlows, coefficients: CoefficientSet, record_key: str
) -> float:
    """Sec. 17.6: Ex_train,cred = rho_train * H_train * b_L,h."""
    _require_non_negative(flows.hours_training, "hours_training", record_key)
    rho_train = coefficients.get(flows.rho_train_coefficient_code).value
    b_l_h = coefficients.get(flows.b_labor_hour_coefficient_code).value
    return rho_train * flows.hours_training * b_l_h


def compute_f_soc(
    ex_sv: float, ex_sv_base: float, ex_train: float, ex_train_base: float,
    ex_lost: float, ex_lost_base: float, ex_co2: float, ex_co2_base: float,
) -> float:
    """Sec. 17.7, verbatim DOC formula. DALY is intentionally absent (sec. 17.4)."""
    return (
        (ex_sv - ex_sv_base)
        + (ex_train - ex_train_base)
        - (ex_lost - ex_lost_base)
        - (ex_co2 - ex_co2_base)
    )
