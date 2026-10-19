"""Plant/year aggregate EEA+ state (ADR-012).

This is the annual, pre-aggregated computation path validated against the real
`RP7.3_calculation_log.xlsx` (see `tests/regression/test_rp73_calculation_log.py`
and ADR-012). It is distinct from the granular per-lot/per-process
TEI/EFA/EcoFA/SFA engines (sec. 14-18), which remain the path for real-time
E2C/MES-driven calculation — this module instead consumes already-aggregated
annual module terms per plant, matching the report-level granularity documented
in SRC-RP73 ("Digital Grey Shadow").

`coefficient_set` and `weight_set` MUST be APPROVED (sec. 11.3, 24.8) — this
function does not special-case DRAFT sets. `src/run_all.py` handles the
provisional/demo elevation explicitly and locally; this module never does.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.core.weights import WeightSet
from src.engines.ecofa.formulas import compute_f_econ
from src.engines.eea.formulas import (
    EEAComponentsMJ,
    compute_ex_ref_mj,
    compute_phi,
    compute_psi_efficiency,
    compute_sa_mj,
    compute_sa_weighted_mj,
    compute_tsi_abs,
)
from src.engines.efa.formulas import compute_f_env
from src.engines.errors import EngineError, ErrorCategory
from src.engines.sfa.formulas import compute_f_soc
from src.engines.tei.formulas import compute_f_tech
from src.ingestion.rp73_reference_data import BASELINE_YEAR, RP73ReferenceData


def _baseline_terms(reference_data: RP73ReferenceData, plant_id: str, year: int) -> dict[str, float]:
    """Module baseline terms for a plant/year (ADR-012/ADR-025).

    Uses the homologous same-window override (`Riferimento` sheet) when present —
    option A for partial production years such as D020/2025 — otherwise the fixed
    annual `BASELINE_YEAR` (2022) rows. Guards that current and baseline windows
    have the same duration: comparing extensive module terms across windows of
    different length is a ``TEMPORAL_MISMATCH`` blocker (ADR-025), since the
    shorter window would otherwise read as a spurious improvement.
    """
    record_key = f"{plant_id}-{year}"
    cur_months = reference_data.months_active(plant_id, year)
    base_months = reference_data.baseline_months(plant_id, year)
    if cur_months != base_months:
        raise EngineError(
            ErrorCategory.TEMPORAL_MISMATCH,
            f"current window ({cur_months} mo) != baseline window ({base_months} mo); "
            f"an homologous same-window reference is required (ADR-025 option A)",
            record_key=record_key,
        )
    override = reference_data.baseline_override.get((plant_id, year))
    if override is not None:
        return override.terms
    tei_b = reference_data.tei[(plant_id, BASELINE_YEAR)]
    efa_b = reference_data.efa[(plant_id, BASELINE_YEAR)]
    eco_b = reference_data.ecofa[(plant_id, BASELINE_YEAR)]
    sfa_b = reference_data.sfa[(plant_id, BASELINE_YEAR)]
    return {
        "loss_MTS_MJ": tei_b.loss_mts_mj, "loss_MTO_MJ": tei_b.loss_mto_mj, "inv_MJ": tei_b.inv_mj,
        "qual_MTS_MJ": tei_b.qual_mts_mj, "qual_MTO_MJ": tei_b.qual_mto_mj,
        "RI_MJ": efa_b.ri_mj, "IEQ_MJ": efa_b.ieq_mj, "WEX_MJ": efa_b.wex_mj, "CIRC_MJ": efa_b.circ_mj,
        "VA_MJ": eco_b.va_mj, "econ_in_MJ": eco_b.econ_in_mj, "INV_MJ": eco_b.inv_mj,
        "SV_MJ": sfa_b.sv_mj, "train_MJ": sfa_b.train_mj, "lost_MJ": sfa_b.lost_mj, "CO2_MJ": sfa_b.co2_mj,
    }


@dataclass(frozen=True)
class AggregatePlantYearState:
    plant_id: str
    year: int
    f_env_gj: float
    f_econ_gj: float
    f_soc_gj: float
    f_tech_gj: float
    sa_raw_gj: float
    sa_w_gj: float
    ex_ref_gj: float
    phi: float
    psi: float
    tsi_abs: float


def compute_aggregate_state(
    plant_id: str,
    year: int,
    reference_data: RP73ReferenceData,
    coefficient_set: CoefficientSet,
    weight_set: WeightSet,
    psi: float,
    alpha: float = 0.5,
    beta: float = 0.5,
) -> AggregatePlantYearState:
    """Compute one plant/year's full aggregate state vs. the fixed 2022 baseline.

    `psi` must be supplied by the caller (ADR-012 open item: no approved
    `Ex_useful` derivation exists in this corpus yet).
    """
    record_key = f"{plant_id}-{year}"
    base = _baseline_terms(reference_data, plant_id, year)
    tei_cur = reference_data.tei[(plant_id, year)]
    efa_cur = reference_data.efa[(plant_id, year)]
    ecofa_cur = reference_data.ecofa[(plant_id, year)]
    sfa_cur = reference_data.sfa[(plant_id, year)]
    energy = reference_data.energy[(plant_id, year)]

    f_env_mj = compute_f_env(
        efa_cur.ri_mj, base["RI_MJ"], efa_cur.circ_mj, base["CIRC_MJ"],
        efa_cur.ieq_mj, base["IEQ_MJ"], efa_cur.wex_mj, base["WEX_MJ"],
    )
    f_econ_mj = compute_f_econ(
        ecofa_cur.va_mj, base["VA_MJ"], ecofa_cur.econ_in_mj, base["econ_in_MJ"],
        ecofa_cur.inv_mj, base["INV_MJ"],
    )
    f_soc_mj = compute_f_soc(
        sfa_cur.sv_mj, base["SV_MJ"], sfa_cur.train_mj, base["train_MJ"],
        sfa_cur.lost_mj, base["lost_MJ"], sfa_cur.co2_mj, base["CO2_MJ"],
    )
    f_tech_mj = compute_f_tech(
        ex_loss_base_mts_mj=base["loss_MTS_MJ"], ex_loss_base_mto_mj=base["loss_MTO_MJ"],
        ex_loss_mts_mj=tei_cur.loss_mts_mj, ex_loss_mto_mj=tei_cur.loss_mto_mj,
        ex_inv_mj=tei_cur.inv_mj, ex_qual_mts_mj=tei_cur.qual_mts_mj, ex_qual_mto_mj=tei_cur.qual_mto_mj,
    )

    components_gj = EEAComponentsMJ(
        f_env_mj=mj_to_gj(f_env_mj), f_econ_mj=mj_to_gj(f_econ_mj),
        f_soc_mj=mj_to_gj(f_soc_mj), f_tech_mj=mj_to_gj(f_tech_mj),
    )
    sa_raw_gj = compute_sa_mj(components_gj)
    sa_w_gj = compute_sa_weighted_mj(components_gj, weight_set)

    ex_ref_mj = compute_ex_ref_mj(energy.e_el_kwh, energy.v_gas_nm3, coefficient_set, record_key)
    ex_ref_gj = mj_to_gj(ex_ref_mj)

    phi = compute_phi(sa_w_gj, ex_ref_gj, record_key)
    psi_value = compute_psi_efficiency(psi)
    tsi_abs = compute_tsi_abs(phi, psi_value, alpha, beta)

    return AggregatePlantYearState(
        plant_id=plant_id, year=year,
        f_env_gj=components_gj.f_env_mj, f_econ_gj=components_gj.f_econ_mj,
        f_soc_gj=components_gj.f_soc_mj, f_tech_gj=components_gj.f_tech_mj,
        sa_raw_gj=sa_raw_gj, sa_w_gj=sa_w_gj, ex_ref_gj=ex_ref_gj,
        phi=phi, psi=psi_value, tsi_abs=tsi_abs,
    )
