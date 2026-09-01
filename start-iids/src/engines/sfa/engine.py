"""SFA-J CalculationEngine implementation. Spec ref: sec. 17, 41, 54 (Agent A4.4)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.core.coefficients import CoefficientSet
from src.core.units.energy import mj_to_gj
from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.errors import EngineError, ErrorCategory
from src.engines.sfa.formulas import (
    SFAPeriodFlows,
    check_no_individual_identifiers,
    compute_co2_exergy,
    compute_daly_diagnostic,
    compute_f_soc,
    compute_lost_hours_exergy,
    compute_stakeholder_value,
    compute_training_credit_exergy,
)


@dataclass(frozen=True)
class SFAInputs:
    current: SFAPeriodFlows
    baseline: SFAPeriodFlows
    coefficients: CoefficientSet
    baseline_coefficient_set_id: str


class SFAEngine(CalculationEngine):
    engine_name = "SFA"
    engine_version = "1.0.0"

    def validate_inputs(self, context: CalculationContext, inputs: SFAInputs) -> None:
        record_key = context.lot_id or context.plant_id
        if inputs.baseline_coefficient_set_id != context.coefficient_set_id:
            raise EngineError(
                ErrorCategory.BASELINE_MISMATCH,
                "current and baseline periods use different coefficient_set_id "
                f"({context.coefficient_set_id!r} vs {inputs.baseline_coefficient_set_id!r})",
                record_key=record_key,
            )
        check_no_individual_identifiers(inputs.current, record_key)
        check_no_individual_identifiers(inputs.baseline, record_key)

    def calculate(self, context: CalculationContext, inputs: SFAInputs) -> CalculationResult:
        record_key = context.lot_id or context.plant_id
        coeff = inputs.coefficients

        ex_sv = compute_stakeholder_value(inputs.current, coeff, record_key)
        ex_sv_base = compute_stakeholder_value(inputs.baseline, coeff, record_key)
        ex_co2 = compute_co2_exergy(inputs.current, coeff, record_key)
        ex_co2_base = compute_co2_exergy(inputs.baseline, coeff, record_key)
        ex_lost = compute_lost_hours_exergy(inputs.current, coeff, record_key)
        ex_lost_base = compute_lost_hours_exergy(inputs.baseline, coeff, record_key)
        ex_train = compute_training_credit_exergy(inputs.current, coeff, record_key)
        ex_train_base = compute_training_credit_exergy(inputs.baseline, coeff, record_key)

        # Diagnostic only (ADR-010) — computed for visibility, excluded from f_soc.
        daly_current = compute_daly_diagnostic(inputs.current, coeff, record_key)

        f_soc_mj = compute_f_soc(ex_sv, ex_sv_base, ex_train, ex_train_base,
                                  ex_lost, ex_lost_base, ex_co2, ex_co2_base)

        values: dict[str, Any] = {
            "ex_sv_mj": ex_sv,
            "ex_co2_mj": ex_co2,
            "ex_lost_mj": ex_lost,
            "ex_train_mj": ex_train,
            "daly_diagnostic": daly_current,
            "f_soc_mj": f_soc_mj,
            "f_soc_gj": mj_to_gj(f_soc_mj),
        }
        return CalculationResult(
            engine=self.engine_name, engine_version=self.engine_version,
            calc_run_id="", context=context, values=values,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("f_soc_mj", "f_soc_gj"):
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
                "f_soc_mj": result.values["f_soc_mj"],
                "f_soc_gj": result.values["f_soc_gj"],
            },
            # daly_diagnostic is reported but never persisted into fact_eea_state /
            # f_soc — it belongs to a diagnostic-only view (ADR-010).
        }
