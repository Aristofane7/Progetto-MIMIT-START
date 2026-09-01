"""EcoFA-J CalculationEngine implementation. Spec ref: sec. 16, 41, 54 (Agent A4.3)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.ecofa.formulas import (
    EcoFAPeriodFlows,
    check_deflator_version,
    check_physical_driver_priority,
    compute_economic_input,
    compute_f_econ,
    compute_fixed_assets,
    compute_value_added,
)
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class EcoFAInputs:
    current: EcoFAPeriodFlows
    baseline: EcoFAPeriodFlows
    coefficients: CoefficientSet
    baseline_coefficient_set_id: str


class EcoFAEngine(CalculationEngine):
    engine_name = "ECOFA"
    engine_version = "1.0.0"

    def validate_inputs(self, context: CalculationContext, inputs: EcoFAInputs) -> None:
        record_key = context.lot_id or context.plant_id
        if inputs.baseline_coefficient_set_id != context.coefficient_set_id:
            raise EngineError(
                ErrorCategory.BASELINE_MISMATCH,
                "current and baseline periods use different coefficient_set_id "
                f"({context.coefficient_set_id!r} vs {inputs.baseline_coefficient_set_id!r})",
                record_key=record_key,
            )
        for flows in (inputs.current, inputs.baseline):
            check_deflator_version(flows, record_key)
            check_physical_driver_priority(flows, record_key)

    def calculate(self, context: CalculationContext, inputs: EcoFAInputs) -> CalculationResult:
        record_key = context.lot_id or context.plant_id
        coeff = inputs.coefficients

        ex_va = compute_value_added(inputs.current, coeff, record_key)
        ex_va_base = compute_value_added(inputs.baseline, coeff, record_key)
        ex_econ_in = compute_economic_input(inputs.current, coeff, record_key)
        ex_econ_in_base = compute_economic_input(inputs.baseline, coeff, record_key)
        ex_inv = compute_fixed_assets(inputs.current, coeff, record_key)
        ex_inv_base = compute_fixed_assets(inputs.baseline, coeff, record_key)

        f_econ_mj = compute_f_econ(ex_va, ex_va_base, ex_econ_in, ex_econ_in_base, ex_inv, ex_inv_base)

        values: dict[str, Any] = {
            "ex_va_mj": ex_va,
            "ex_econ_in_mj": ex_econ_in,
            "ex_inv_mj": ex_inv,
            "f_econ_mj": f_econ_mj,
            "f_econ_gj": mj_to_gj(f_econ_mj),
        }
        return CalculationResult(
            engine=self.engine_name, engine_version=self.engine_version,
            calc_run_id="", context=context, values=values,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("f_econ_mj", "f_econ_gj"):
            if math.isnan(result.values[key]):
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
                "f_econ_mj": result.values["f_econ_mj"],
                "f_econ_gj": result.values["f_econ_gj"],
            },
        }
