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
from src.engines.sfa.formulas import compute_f_soc
from src.engines.tei.formulas import compute_f_tech
from src.ingestion.rp73_reference_data import BASELINE_YEAR, RP73ReferenceData


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
    tei_base = reference_data.tei[(plant_id, BASELINE_YEAR)]
    tei_cur = reference_data.tei[(plant_id, year)]
    efa_base = reference_data.efa[(plant_id, BASELINE_YEAR)]
    efa_cur = reference_data.efa[(plant_id, year)]
    ecofa_base = reference_data.ecofa[(plant_id, BASELINE_YEAR)]
    ecofa_cur = reference_data.ecofa[(plant_id, year)]
    sfa_base = reference_data.sfa[(plant_id, BASELINE_YEAR)]
    sfa_cur = reference_data.sfa[(plant_id, year)]
    energy = reference_data.energy[(plant_id, year)]

    f_env_mj = compute_f_env(
        efa_cur.ri_mj, efa_base.ri_mj, efa_cur.circ_mj, efa_base.circ_mj,
        efa_cur.ieq_mj, efa_base.ieq_mj, efa_cur.wex_mj, efa_base.wex_mj,
    )
    f_econ_mj = compute_f_econ(
        ecofa_cur.va_mj, ecofa_base.va_mj, ecofa_cur.econ_in_mj, ecofa_base.econ_in_mj,
        ecofa_cur.inv_mj, ecofa_base.inv_mj,
    )
    f_soc_mj = compute_f_soc(
        sfa_cur.sv_mj, sfa_base.sv_mj, sfa_cur.train_mj, sfa_base.train_mj,
        sfa_cur.lost_mj, sfa_base.lost_mj, sfa_cur.co2_mj, sfa_base.co2_mj,
    )
    f_tech_mj = compute_f_tech(
        ex_loss_base_mts_mj=tei_base.loss_mts_mj, ex_loss_base_mto_mj=tei_base.loss_mto_mj,
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
