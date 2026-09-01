"""EFA-J CalculationEngine implementation. Spec ref: sec. 15, 41, 54 (Agent A4.2)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.efa.formulas import (
    EFAPeriodFlows,
    check_no_double_counting,
    compute_circularity_credit,
    compute_f_env,
    compute_impact_equivalent,
    compute_resource_intake,
    compute_waste_exergy,
)
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class EFAInputs:
    current: EFAPeriodFlows
    baseline: EFAPeriodFlows
    coefficients: CoefficientSet
    baseline_coefficient_set_id: str


class EFAEngine(CalculationEngine):
    engine_name = "EFA"
    engine_version = "1.0.0"

    def validate_inputs(self, context: CalculationContext, inputs: EFAInputs) -> None:
        if inputs.baseline_coefficient_set_id != context.coefficient_set_id:
            raise EngineError(
                ErrorCategory.BASELINE_MISMATCH,
                "current and baseline periods use different coefficient_set_id "
                f"({context.coefficient_set_id!r} vs {inputs.baseline_coefficient_set_id!r})",
                record_key=context.lot_id or context.plant_id,
            )
        record_key = context.lot_id or context.plant_id
        check_no_double_counting(inputs.current, record_key)
        check_no_double_counting(inputs.baseline, record_key)

    def calculate(self, context: CalculationContext, inputs: EFAInputs) -> CalculationResult:
        record_key = context.lot_id or context.plant_id
        coeff = inputs.coefficients

        ri = compute_resource_intake(inputs.current, coeff, record_key)
        ri_base = compute_resource_intake(inputs.baseline, coeff, record_key)
        wex = compute_waste_exergy(inputs.current, coeff, record_key)
        wex_base = compute_waste_exergy(inputs.baseline, coeff, record_key)
        ieq = compute_impact_equivalent(inputs.current, coeff, record_key)
        ieq_base = compute_impact_equivalent(inputs.baseline, coeff, record_key)
        circ = compute_circularity_credit(inputs.current)
        circ_base = compute_circularity_credit(inputs.baseline)

        f_env_mj = compute_f_env(ri, ri_base, circ, circ_base, ieq, ieq_base, wex, wex_base)

        values: dict[str, Any] = {
            "resource_intake_mj": ri,
            "waste_exergy_mj": wex,
            "impact_equivalent_mj": ieq,
            "circularity_credit_mj": circ,
            "f_env_mj": f_env_mj,
            "f_env_gj": mj_to_gj(f_env_mj),
        }
        return CalculationResult(
            engine=self.engine_name, engine_version=self.engine_version,
            calc_run_id="", context=context, values=values,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("f_env_mj", "f_env_gj"):
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
                "f_env_mj": result.values["f_env_mj"],
                "f_env_gj": result.values["f_env_gj"],
            },
        }
