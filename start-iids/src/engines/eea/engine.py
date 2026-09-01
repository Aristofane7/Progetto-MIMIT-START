"""EEA+ CalculationEngine implementation. Spec ref: sec. 18, 41, 54 (Agent A4.5).

This engine aggregates the already-computed outputs of TEI/EFA/EcoFA/SFA — it does
not re-derive them, keeping each sub-engine independently testable (sec. 54).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.eea.formulas import ComparabilityCheck, EEAComponentsMJ, build_eea_state
from src.engines.errors import EngineError, ErrorCategory


@dataclass(frozen=True)
class EEAInputs:
    components: EEAComponentsMJ
    sa_historical_mj: float
    comparability: ComparabilityCheck
    data_quality_score: float | None = None


class EEAEngine(CalculationEngine):
    engine_name = "EEA"
    engine_version = "1.0.0"

    def validate_inputs(self, context: CalculationContext, inputs: EEAInputs) -> None:
        return None

    def calculate(self, context: CalculationContext, inputs: EEAInputs) -> CalculationResult:
        state = build_eea_state(inputs.components, inputs.sa_historical_mj, inputs.comparability)
        values: dict[str, Any] = {
            "f_env_mj": state.f_env_mj, "f_econ_mj": state.f_econ_mj,
            "f_soc_mj": state.f_soc_mj, "f_tech_mj": state.f_tech_mj, "sa_mj": state.sa_mj,
            "f_env_gj": state.f_env_gj, "f_econ_gj": state.f_econ_gj,
            "f_soc_gj": state.f_soc_gj, "f_tech_gj": state.f_tech_gj, "sa_gj": state.sa_gj,
            "tsi_norm": state.tsi_norm,
        }
        quality_flags = [state.quality_flag] if state.quality_flag else []
        return CalculationResult(
            engine=self.engine_name, engine_version=self.engine_version,
            calc_run_id="", context=context, values=values,
            data_quality_score=inputs.data_quality_score, quality_flags=quality_flags,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("sa_mj", "sa_gj"):
            if math.isnan(result.values[key]):
                raise EngineError(ErrorCategory.CALCULATION_ERROR, f"'{key}' is NaN")
        tsi = result.values.get("tsi_norm")
        if tsi is None and "NON_COMPARABLE" not in result.quality_flags:
            raise EngineError(
                ErrorCategory.CALCULATION_ERROR,
                "tsi_norm is NULL without a NON_COMPARABLE quality flag",
            )

    def persist(self, result: CalculationResult) -> dict[str, Any]:
        row = {
            "calc_run_id": result.calc_run_id,
            "plant_id": result.context.plant_id,
            "line_id": result.context.line_id,
            "lot_id": result.context.lot_id,
            "period_start": result.context.period_start,
            "period_end": result.context.period_end,
            "scenario": result.context.scenario,
            "data_quality_score": result.data_quality_score,
            **result.values,
        }
        return {"table": "fact_eea_state", "row": row, "quality_flags": result.quality_flags}
