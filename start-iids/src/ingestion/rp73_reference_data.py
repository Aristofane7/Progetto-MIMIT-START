"""Loader for the RP7.3 reference data workbook.

Spec ref: ADR-012, ADR-015. Reads `data/reference/RP7.3_data_collection_20232025.xlsx`
(`Unita`, `Energia`, `Moduli_TEI/EFA/EcoFA/SFA`, and — since ADR-015 — `Periodo`
and `Riferimento` sheets) into plain, per-plant/year dataclasses. This module does
NOT touch `Coefficienti`/`AHP` (those are transcribed into
`config/coefficients/rp73_provisional_2026.yaml` and `config/weights/eea_ahp_rp73.yaml`).

ADR-015 (D020 partial production year 2025): the `Unita` sheet now carries
production **per year** (not a single value per plant); an optional `Periodo` sheet
records the activity window (`months_active`) per plant/year; an optional
`Riferimento` sheet overrides a plant/year's module baseline with a homologous
same-window reference (option A). Both optional sheets degrade gracefully: absent
sheets => every plant/year is a full 12-month year baselined on the annual
`BASELINE_YEAR` row (the pre-ADR-015 behaviour, preserved for the beta-1.1 fixture).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import openpyxl

BASELINE_YEAR = 2022  # fixed annual reference year (ADR-012), unless overridden per ADR-015
FULL_YEAR_MONTHS = 12

# term -> module, used to interpret the `Riferimento` long-format sheet
TERM_MODULE = {
    "loss_MTS_MJ": "TEI-J", "loss_MTO_MJ": "TEI-J", "inv_MJ": "TEI-J",
    "qual_MTS_MJ": "TEI-J", "qual_MTO_MJ": "TEI-J",
    "RI_MJ": "EFA-J", "IEQ_MJ": "EFA-J", "WEX_MJ": "EFA-J", "CIRC_MJ": "EFA-J",
    "VA_MJ": "EcoFA-J", "econ_in_MJ": "EcoFA-J", "INV_MJ": "EcoFA-J",
    "SV_MJ": "SFA-J", "train_MJ": "SFA-J", "lost_MJ": "SFA-J", "CO2_MJ": "SFA-J",
}


@dataclass(frozen=True)
class PlantMaster:
    plant_id: str
    description: str


@dataclass(frozen=True)
class EnergyRow:
    plant_id: str
    year: int
    v_gas_nm3: float
    e_el_kwh: float


@dataclass(frozen=True)
class TEIModuleRow:
    plant_id: str
    year: int
    loss_mts_mj: float
    loss_mto_mj: float
    inv_mj: float
    qual_mts_mj: float
    qual_mto_mj: float


@dataclass(frozen=True)
class EFAModuleRow:
    plant_id: str
    year: int
    ri_mj: float
    ieq_mj: float
    wex_mj: float
    circ_mj: float


@dataclass(frozen=True)
class EcoFAModuleRow:
    plant_id: str
    year: int
    va_mj: float
    econ_in_mj: float
    inv_mj: float


@dataclass(frozen=True)
class SFAModuleRow:
    plant_id: str
    year: int
    sv_mj: float
    train_mj: float
    lost_mj: float
    co2_mj: float


@dataclass(frozen=True)
class ActivityPeriod:
    """Activity window of a plant/year (ADR-015). `months_active < 12` marks a
    partial production year (e.g. D020 2025, Jan->July cessation)."""
    plant_id: str
    year: int
    period_start: str
    period_end: str
    months_active: int


@dataclass(frozen=True)
class BaselineOverride:
    """Homologous same-window baseline for a plant/year (ADR-015, option A).

    `terms` maps each module term name (e.g. `RI_MJ`, `loss_MTS_MJ`) to its value
    over the reference window (`ref_period_start`..`ref_period_end`), so the
    plant/year is compared against the SAME calendar window of the reference year
    rather than the full annual `BASELINE_YEAR` row — keeping the duration of
    current and baseline equal."""
    plant_id: str
    year: int
    ref_plant: str
    ref_year: int
    ref_period_start: str
    ref_period_end: str
    months_active: int
    terms: dict[str, float]


@dataclass(frozen=True)
class RP73ReferenceData:
    plants: dict[str, PlantMaster]
    energy: dict[tuple[str, int], EnergyRow]
    tei: dict[tuple[str, int], TEIModuleRow]
    efa: dict[tuple[str, int], EFAModuleRow]
    ecofa: dict[tuple[str, int], EcoFAModuleRow]
    sfa: dict[tuple[str, int], SFAModuleRow]
    production: dict[tuple[str, int], float] = field(default_factory=dict)
    activity: dict[tuple[str, int], ActivityPeriod] = field(default_factory=dict)
    baseline_override: dict[tuple[str, int], BaselineOverride] = field(default_factory=dict)
    _default_production: dict[str, float] = field(default_factory=dict)

    def plant_years(self) -> list[tuple[str, int]]:
        """All (plant_id, year) pairs excluding the baseline year itself."""
        return sorted(k for k in self.energy if k[1] != BASELINE_YEAR)

    def production_m2(self, plant_id: str, year: int) -> float | None:
        """Production (m2) for a plant/year — per-year if available (ADR-015),
        else the plant's single declared value (pre-ADR-015 workbooks)."""
        if (plant_id, year) in self.production:
            return self.production[(plant_id, year)]
        return self._default_production.get(plant_id)

    def months_active(self, plant_id: str, year: int) -> int:
        """Months of activity for a plant/year (12 unless a `Periodo` row says otherwise)."""
        ap = self.activity.get((plant_id, year))
        return ap.months_active if ap else FULL_YEAR_MONTHS

    def baseline_months(self, plant_id: str, year: int) -> int:
        """Duration (months) of the baseline this plant/year is compared against:
        the override window if present, else the full annual baseline (12)."""
        ov = self.baseline_override.get((plant_id, year))
        return ov.months_active if ov else FULL_YEAR_MONTHS


def _rows(ws) -> list[tuple]:
    return list(ws.iter_rows(values_only=True))[1:]  # skip header


def _header(ws) -> list:
    return [c for c in next(ws.iter_rows(values_only=True))]


def load_rp73_reference_data(path: str | Path) -> RP73ReferenceData:
    wb = openpyxl.load_workbook(path, data_only=True)

    # --- Unita: per-year (ADR-015) or legacy single-value ---
    plants: dict[str, PlantMaster] = {}
    production: dict[tuple[str, int], float] = {}
    default_production: dict[str, float] = {}
    u_hdr = _header(wb["Unita"])
    if "year" in u_hdr:
        iy = u_hdr.index("year")
        ip = u_hdr.index("produzione_m2")
        idesc = u_hdr.index("descrizione") if "descrizione" in u_hdr else None
        for row in _rows(wb["Unita"]):
            plant = row[0]
            production[(plant, row[iy])] = row[ip]
            if plant not in plants:
                plants[plant] = PlantMaster(plant_id=plant, description=(row[idesc] if idesc is not None else ""))
    else:  # legacy: (plant, descrizione, produzione_m2)
        for row in _rows(wb["Unita"]):
            plants[row[0]] = PlantMaster(plant_id=row[0], description=row[1])
            default_production[row[0]] = row[2]

    energy = {
        (row[0], row[1]): EnergyRow(plant_id=row[0], year=row[1], v_gas_nm3=row[2], e_el_kwh=row[3])
        for row in _rows(wb["Energia"])
    }
    tei = {
        (row[0], row[1]): TEIModuleRow(
            plant_id=row[0], year=row[1], loss_mts_mj=row[2], loss_mto_mj=row[3],
            inv_mj=row[4], qual_mts_mj=row[5], qual_mto_mj=row[6])
        for row in _rows(wb["Moduli_TEI"])
    }
    efa = {
        (row[0], row[1]): EFAModuleRow(
            plant_id=row[0], year=row[1], ri_mj=row[2], ieq_mj=row[3], wex_mj=row[4], circ_mj=row[5])
        for row in _rows(wb["Moduli_EFA"])
    }
    ecofa = {
        (row[0], row[1]): EcoFAModuleRow(
            plant_id=row[0], year=row[1], va_mj=row[2], econ_in_mj=row[3], inv_mj=row[4])
        for row in _rows(wb["Moduli_EcoFA"])
    }
    sfa = {
        (row[0], row[1]): SFAModuleRow(
            plant_id=row[0], year=row[1], sv_mj=row[2], train_mj=row[3], lost_mj=row[4], co2_mj=row[5])
        for row in _rows(wb["Moduli_SFA"])
    }

    # --- optional Periodo sheet (ADR-015) ---
    activity: dict[tuple[str, int], ActivityPeriod] = {}
    if "Periodo" in wb.sheetnames:
        for row in _rows(wb["Periodo"]):
            if row[0] is None:
                continue
            activity[(row[0], row[1])] = ActivityPeriod(
                plant_id=row[0], year=row[1], period_start=str(row[2]),
                period_end=str(row[3]), months_active=int(row[4]))

    # --- optional Riferimento sheet (ADR-015 option A homologous baseline) ---
    baseline_override: dict[tuple[str, int], BaselineOverride] = {}
    if "Riferimento" in wb.sheetnames:
        grouped: dict[tuple[str, int], dict] = {}
        for row in _rows(wb["Riferimento"]):
            if row[0] is None:
                continue
            key = (row[0], row[1])
            meta = grouped.setdefault(key, {
                "ref_plant": row[2], "ref_year": row[3],
                "ref_period_start": str(row[4]), "ref_period_end": str(row[5]), "terms": {}})
            meta["terms"][row[7]] = row[8]  # term -> value_MJ
        for key, meta in grouped.items():
            months = activity[key].months_active if key in activity else FULL_YEAR_MONTHS
            baseline_override[key] = BaselineOverride(
                plant_id=key[0], year=key[1], ref_plant=meta["ref_plant"], ref_year=meta["ref_year"],
                ref_period_start=meta["ref_period_start"], ref_period_end=meta["ref_period_end"],
                months_active=months, terms=meta["terms"])

    return RP73ReferenceData(
        plants=plants, energy=energy, tei=tei, efa=efa, ecofa=ecofa, sfa=sfa,
        production=production, activity=activity, baseline_override=baseline_override,
        _default_production=default_production)


def load_rp73_calculation_log(path: str | Path) -> dict[tuple[str, int, str], float]:
    """Load `RP7.3_calculation_log.xlsx` (`calculation_log` sheet) into
    ``{(plant_id, year, variable): output}`` — the golden regression targets."""
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb["calculation_log"]
    log: dict[tuple[str, int, str], float] = {}
    for row in _rows(ws):
        _result_id, _report_table, plant, year, variable, *_rest, output, _unit, _date, _version = row
        log[(plant, year, variable)] = output
    return log
