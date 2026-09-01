"""EcoFA-J pure formulas (Economic Footprint Assessment, Joule-based).

Spec ref: sec. 16 (DOC). Scope include/exclude list is sec. 16.1-16.2 and is
enforced upstream by the data contract / accounting_owner tagging (sec. 10.11),
not re-validated numerically here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.core.coefficients import CoefficientSet
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class CostItem:
    accounting_term_id: str
    amount_eur: float  # already deflated to constant base-year prices (sec. 7.3)
    coefficient_code: str  # gamma_c
    has_physical_driver: bool = False  # sec. 16.7/30.3: e.g. LOGISTICS_TKM covered by EFA


@dataclass(frozen=True)
class EcoFAPeriodFlows:
    deflator_version: str
    value_added_eur: float
    value_added_coefficient_code: str  # gamma_VA
    fixed_assets_eur: float
    fixed_assets_coefficient_code: str  # gamma_INV
    costs: list[CostItem] = field(default_factory=list)


def _require_non_negative(value: float, field_name: str, record_key: str) -> None:
    if value < 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"'{field_name}' must not be negative, got {value}",
            record_key=record_key,
        )


def check_deflator_version(flows: EcoFAPeriodFlows, record_key: str) -> None:
    """Sec. 7.3: nominal amounts must never be converted directly to Joule; a
    deflator_version tying the amounts to constant base-year prices is mandatory."""
    if not flows.deflator_version:
        raise EngineError(
            ErrorCategory.VALIDATION_ERROR,
            "missing deflator_version: nominal EUR amounts must not be converted "
            "directly into Joule without a constant-price deflation reference",
            record_key=record_key,
        )


def check_physical_driver_priority(flows: EcoFAPeriodFlows, record_key: str) -> None:
    """Sec. 16.7/30.3: 'physical driver wins' — if a t*km (or other physical)
    driver is available for an activity, EcoFA must not also price it via EUR->MJ."""
    offending = [c.accounting_term_id for c in flows.costs if c.has_physical_driver]
    if offending:
        raise EngineError(
            ErrorCategory.VALIDATION_ERROR,
            f"cost item(s) {offending} have a physical driver available in EFA; "
            "must not be priced via EUR->MJ in EcoFA for the same activity",
            record_key=record_key,
        )


def compute_economic_input(flows: EcoFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 16.3: Ex_econ,in = sum_c C_c * gamma_c."""
    total = 0.0
    for c in flows.costs:
        _require_non_negative(c.amount_eur, f"cost[{c.accounting_term_id}].amount_eur", record_key)
        total += c.amount_eur * coefficients.get(c.coefficient_code).value
    return total


def compute_value_added(flows: EcoFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 16.4: Ex_VA = VA * gamma_VA."""
    _require_non_negative(flows.value_added_eur, "value_added_eur", record_key)
    return flows.value_added_eur * coefficients.get(flows.value_added_coefficient_code).value


def compute_fixed_assets(flows: EcoFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 16.5: Ex_INV = INV * gamma_INV."""
    _require_non_negative(flows.fixed_assets_eur, "fixed_assets_eur", record_key)
    return flows.fixed_assets_eur * coefficients.get(flows.fixed_assets_coefficient_code).value


def compute_f_econ(
    ex_va: float, ex_va_base: float, ex_econ_in: float, ex_econ_in_base: float,
    ex_inv: float, ex_inv_base: float,
) -> float:
    """Sec. 16.6, verbatim DOC formula."""
    return (ex_va - ex_va_base) - (ex_econ_in - ex_econ_in_base) - (ex_inv - ex_inv_base)
