"""EFA-J pure formulas (Environmental Footprint Assessment, Joule-based).

Spec ref: sec. 15 (DOC — direct transcription).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.core.coefficients import CoefficientSet
from src.core.units.energy import exergy_from_mass, kwh_to_mj
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class MaterialFlow:
    accounting_term_id: str
    mass_kg: float
    coefficient_code: str  # b_i


@dataclass(frozen=True)
class FuelFlow:
    accounting_term_id: str
    volume: float
    coefficient_code: str  # b_fuel


@dataclass(frozen=True)
class WaterFlow:
    accounting_term_id: str
    volume_m3: float
    coefficient_code: str  # b_H2O


@dataclass(frozen=True)
class WasteFlow:
    accounting_term_id: str
    quantity_kg: float
    coefficient_code: str  # b_w,k
    is_internal_recycle: bool = False  # sec. 15.3: cut-off, priced at b=0 upstream


@dataclass(frozen=True)
class EmissionFlow:
    accounting_term_id: str
    quantity: float
    coefficient_code: str  # gamma_j


@dataclass(frozen=True)
class RecoveryCredit:
    accounting_term_id: str
    ex_rec_mat_mj: float
    ex_rec_th_mj: float


@dataclass(frozen=True)
class EFAPeriodFlows:
    electricity_kwh: float
    materials: list[MaterialFlow] = field(default_factory=list)
    fuels: list[FuelFlow] = field(default_factory=list)
    water: list[WaterFlow] = field(default_factory=list)
    wastes: list[WasteFlow] = field(default_factory=list)
    emissions: list[EmissionFlow] = field(default_factory=list)
    recoveries: list[RecoveryCredit] = field(default_factory=list)


def _require_non_negative(value: float, field_name: str, record_key: str) -> None:
    if value < 0:
        raise EngineError(
            ErrorCategory.PHYSICAL_RANGE_ERROR,
            f"'{field_name}' must not be negative, got {value}",
            record_key=record_key,
        )


def check_no_double_counting(flows: EFAPeriodFlows, record_key: str) -> None:
    """Sec. 15.7: a recovered stream must not both cut off resource intake (via
    an internal-recycle waste flow) and be counted again as a circularity credit."""
    recycled_terms = {w.accounting_term_id for w in flows.wastes if w.is_internal_recycle}
    recovery_terms = {r.accounting_term_id for r in flows.recoveries}
    overlap = recycled_terms & recovery_terms
    if overlap:
        raise EngineError(
            ErrorCategory.VALIDATION_ERROR,
            f"double counting detected on accounting_term_id(s): {sorted(overlap)}",
            record_key=record_key,
        )


def compute_resource_intake(flows: EFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 15.2: RI = Ex_mat + Ex_el + Ex_fuel + Ex_H2O."""
    ex_mat = 0.0
    for m in flows.materials:
        _require_non_negative(m.mass_kg, f"material[{m.accounting_term_id}].mass_kg", record_key)
        ex_mat += exergy_from_mass(m.mass_kg, coefficients.get(m.coefficient_code).value)

    _require_non_negative(flows.electricity_kwh, "electricity_kwh", record_key)
    ex_el = kwh_to_mj(flows.electricity_kwh)

    ex_fuel = 0.0
    for f in flows.fuels:
        _require_non_negative(f.volume, f"fuel[{f.accounting_term_id}].volume", record_key)
        ex_fuel += exergy_from_mass(f.volume, coefficients.get(f.coefficient_code).value)

    ex_h2o = 0.0
    for w in flows.water:
        _require_non_negative(w.volume_m3, f"water[{w.accounting_term_id}].volume_m3", record_key)
        ex_h2o += exergy_from_mass(w.volume_m3, coefficients.get(w.coefficient_code).value)

    return ex_mat + ex_el + ex_fuel + ex_h2o


def compute_waste_exergy(flows: EFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 15.3: WEX = sum_k R_k * b_w,k. Internal-recycle waste is cut off
    (b=0 upstream) — only non-recycled waste streams are priced."""
    wex = 0.0
    for w in flows.wastes:
        _require_non_negative(w.quantity_kg, f"waste[{w.accounting_term_id}].quantity_kg", record_key)
        if w.is_internal_recycle:
            continue
        wex += exergy_from_mass(w.quantity_kg, coefficients.get(w.coefficient_code).value)
    return wex


def compute_impact_equivalent(flows: EFAPeriodFlows, coefficients: CoefficientSet, record_key: str) -> float:
    """Sec. 15.4: IEQ = sum_j Em_j * gamma_j."""
    ieq = 0.0
    for e in flows.emissions:
        _require_non_negative(e.quantity, f"emission[{e.accounting_term_id}].quantity", record_key)
        ieq += e.quantity * coefficients.get(e.coefficient_code).value
    return ieq


def compute_circularity_credit(flows: EFAPeriodFlows) -> float:
    """Sec. 15.5: CIRC = Ex_rec,mat + Ex_rec,th."""
    return sum(r.ex_rec_mat_mj + r.ex_rec_th_mj for r in flows.recoveries)


def compute_f_env(
    ri: float, ri_base: float, circ: float, circ_base: float, ieq: float, ieq_base: float,
    wex: float, wex_base: float,
) -> float:
    """Sec. 15.6, verbatim DOC formula."""
    return (ri_base - ri) + (circ - circ_base) - (ieq - ieq_base) - (wex - wex_base)
