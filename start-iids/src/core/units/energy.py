"""Canonical energy unit conversions.

Spec ref: `docs/sources/..._Implementation_Spec_v1.0.md` sec. 7.2 (P0 — correzione
tecnica obbligatoria) and sec. 14.3.

The -J manuals (TEI/EFA/EcoFA/SFA) contain an internal inconsistency: several worked
examples label intermediate values as MJ but then convert to GJ by dividing by 1e9
(which is only valid for J -> GJ). This module freezes the corrected, v1-mandatory
convention:

    computational canonical unit: MJ
    reporting unit:                GJ
    gj = mj / 1000.0   (NEVER mj / 1e9)
"""
from __future__ import annotations

MJ_PER_GJ = 1000.0
MJ_PER_KWH = 3.6


def mj_to_gj(value_mj: float) -> float:
    """Convert MJ (internal canonical unit) to GJ (reporting unit).

    Spec ADR-005: `gj = mj / 1000.0`. Using `/ 1e9` here is a P0 defect —
    that divisor only converts J -> GJ, not MJ -> GJ.
    """
    return value_mj / MJ_PER_GJ


def gj_to_mj(value_gj: float) -> float:
    """Inverse of :func:`mj_to_gj`."""
    return value_gj * MJ_PER_GJ


def kwh_to_mj(value_kwh: float) -> float:
    """Electricity exergy conversion, spec sec. 14.3 / 15.2: ``Ex_el[MJ] = kWh * 3.6``."""
    return value_kwh * MJ_PER_KWH


def gas_nm3_to_mj(volume_nm3: float, pci_mj_per_nm3: float, exergy_factor: float) -> float:
    """Gas exergy conversion, spec sec. 14.3: ``Ex_gas[MJ] = Nm3 * PCI * f_ex``.

    ``pci_mj_per_nm3`` and ``exergy_factor`` must come from an APPROVED
    :class:`~src.core.units.coefficients` coefficient set — never hardcoded.
    """
    return volume_nm3 * pci_mj_per_nm3 * exergy_factor


def exergy_from_mass(quantity: float, specific_exergy: float) -> float:
    """Generic mass-based exergy conversion, spec sec. 14.3: ``Ex_x = q_x * b_x``."""
    return quantity * specific_exergy
