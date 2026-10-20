"""TEI-J CalculationEngine implementation. Spec ref: sec. 14, 41, 54 (Agent A4.1)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.errors import EngineError, ErrorCategory
from src.engines.tei.formulas import (
    MTOFlow,
    MTSFlow,
    compute_backlog,
    compute_f_tech,
    compute_mto_exergy,
    compute_mts_exergy,
    compute_quality_penalty,
)


@dataclass(frozen=True)
class TEIInputs:
    current_mts: MTSFlow
    current_mto: MTOFlow
    baseline_mts: MTSFlow
    baseline_mto: MTOFlow
    coefficients: CoefficientSet
    baseline_coefficient_set_id: str


class TEIEngine(CalculationEngine):
    engine_name = "TEI"
    engine_version = "1.1.0"  # ADR-018: quality-penalty formula corrected against SRC-TEI

    def validate_inputs(self, context: CalculationContext, inputs: TEIInputs) -> None:
        # Baseline rule (spec sec. 12.2): current and baseline runs must share the
        # same coefficient set for the comparison to be valid.
        if inputs.baseline_coefficient_set_id != context.coefficient_set_id:
            raise EngineError(
                ErrorCategory.BASELINE_MISMATCH,
                "current and baseline periods use different coefficient_set_id "
                f"({context.coefficient_set_id!r} vs {inputs.baseline_coefficient_set_id!r})",
                record_key=context.lot_id or context.plant_id,
            )

    def calculate(self, context: CalculationContext, inputs: TEIInputs) -> CalculationResult:
        record_key = context.lot_id or context.plant_id

        current_mts_ex = compute_mts_exergy(inputs.current_mts, inputs.coefficients, record_key)
        current_mto_ex = compute_mto_exergy(inputs.current_mto, inputs.coefficients, record_key)
        baseline_mts_ex = compute_mts_exergy(inputs.baseline_mts, inputs.coefficients, record_key)
        baseline_mto_ex = compute_mto_exergy(inputs.baseline_mto, inputs.coefficients, record_key)

        ex_inv, quality_flags = compute_backlog(inputs.current_mto, current_mto_ex.ex_t_mj, record_key)

        kappa_mts = q_target_mts = None
        if inputs.current_mts.q_mts is not None:
            kappa_mts = inputs.coefficients.get("KAPPA_MTS").value
            q_target_mts = inputs.coefficients.get("Q_THR_MTS").value
        ex_qual_mts = compute_quality_penalty(
            inputs.current_mts.q_mts, q_target_mts, kappa_mts,
            current_mts_ex.ex_rm_mj + current_mts_ex.ex_uw_mj + current_mts_ex.ex_e_sd_mj,
            record_key=record_key,
        )

        kappa_mto = q_target_mto = None
        if inputs.current_mto.q_mto is not None:
            kappa_mto = inputs.coefficients.get("KAPPA_MTO").value
            q_target_mto = inputs.coefficients.get("Q_THR_MTO").value
        ex_qual_mto = compute_quality_penalty(
            inputs.current_mto.q_mto, q_target_mto, kappa_mto, current_mto_ex.ex_t_mj,
            record_key=record_key,
        )

        f_tech_mj = compute_f_tech(
            ex_loss_base_mts_mj=baseline_mts_ex.ex_loss_mts_mj,
            ex_loss_base_mto_mj=baseline_mto_ex.ex_loss_mto_mj,
            ex_loss_mts_mj=current_mts_ex.ex_loss_mts_mj,
            ex_loss_mto_mj=current_mto_ex.ex_loss_mto_mj,
            ex_inv_mj=ex_inv,
            ex_qual_mts_mj=ex_qual_mts,
            ex_qual_mto_mj=ex_qual_mto,
        )

        values: dict[str, Any] = {
            "ex_loss_mts_mj": current_mts_ex.ex_loss_mts_mj,
            "ex_loss_mto_mj": current_mto_ex.ex_loss_mto_mj,
            "ex_inv_mj": ex_inv,
            "ex_qual_mts_mj": ex_qual_mts,
            "ex_qual_mto_mj": ex_qual_mto,
            "f_tech_mj": f_tech_mj,
            "f_tech_gj": mj_to_gj(f_tech_mj),
        }

        return CalculationResult(
            engine=self.engine_name,
            engine_version=self.engine_version,
            calc_run_id="",  # assigned by the orchestrator via make_calc_run_id
            context=context,
            values=values,
            quality_flags=quality_flags,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("f_tech_mj", "f_tech_gj"):
            value = result.values[key]
            if math.isnan(value):
                raise EngineError(ErrorCategory.CALCULATION_ERROR, f"'{key}' is NaN")

    def persist(self, result: CalculationResult) -> dict[str, Any]:
        return {
            "table": "fact_eea_state",
            "row": {
                "calc_run_id": result.calc_run_id,
                "plant_id": result.context.plant_id,
                "line_id": result.context.line_id,
                "lot_id": result.context.lot_id,
                "period_start": result.context.period_start,
                "period_end": result.context.period_end,
                "scenario": result.context.scenario,
                "f_tech_mj": result.values["f_tech_mj"],
                "f_tech_gj": result.values["f_tech_gj"],
            },
            "quality_flags": result.quality_flags,
        }
