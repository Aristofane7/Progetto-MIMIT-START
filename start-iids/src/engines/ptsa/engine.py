"""P-TSA CalculationEngine implementation. Spec ref: sec. 24-25, 41, 54 (Agent A6)."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from src.core.weights import WeightSet
from src.engines.base import CalculationContext, CalculationEngine, CalculationResult
from src.engines.errors import EngineError, ErrorCategory
from src.engines.ptsa.formulas import (
    DIM_IOA,
    DIM_OP,
    DIM_TQ,
    IOA_METRICS,
    OP_METRICS,
    TQ_METRICS,
    PopulationStat,
    compute_ocr,
    compute_p_tsi_scoring,
    compute_p_tsi_z,
    compute_psi,
    compute_scr,
    compute_subindex,
    compute_tii,
    compute_zscore,
)


def equal_weights(metrics: tuple[str, ...]) -> dict[str, float]:
    """Sec. 24.6 base case: equal weights within a dimension."""
    return {m: 1.0 / len(metrics) for m in metrics}


@dataclass(frozen=True)
class PTSARawQuantities:
    scr_raw_stock: float
    scr_raw_daily_consumption: float
    scr_finished_stock: float
    scr_finished_daily_consumption: float
    scr_glaze_stock: float
    scr_glaze_daily_consumption: float
    psi_energy_output_m2: float
    psi_energy_input_gj: float
    psi_material_output_m2: float
    psi_material_input_m2: float
    psi_throughput_output_m2: float
    psi_throughput_hours: float
    ocr_flexural_passed: float
    ocr_flexural_attempted: float
    ocr_breaking_passed: float
    ocr_breaking_attempted: float
    ocr_surface_passed: float
    ocr_surface_attempted: float


@dataclass(frozen=True)
class PTSAInputs:
    raw: PTSARawQuantities
    population_stats: dict[str, PopulationStat]
    dimension_scores: dict[str, float]  # {"IOA": 1-5, "OP": 1-5, "TQ": 1-5}
    weight_set: WeightSet
    zscore_weights: dict[str, dict[str, float]] | None = None  # per-dimension override
    previous_p_tsi_5: float | None = None


class PTSAEngine(CalculationEngine):
    engine_name = "PTSA"
    engine_version = "1.0.0"

    def validate_inputs(self, context: CalculationContext, inputs: PTSAInputs) -> None:
        required_metrics = set(IOA_METRICS) | set(OP_METRICS) | set(TQ_METRICS)
        missing = required_metrics - set(inputs.population_stats)
        if missing:
            raise EngineError(
                ErrorCategory.VALIDATION_ERROR,
                f"missing population statistics for metric(s): {sorted(missing)}",
                record_key=context.lot_id or context.plant_id,
            )
        missing_dims = {DIM_IOA, DIM_OP, DIM_TQ} - set(inputs.dimension_scores)
        if missing_dims:
            raise EngineError(
                ErrorCategory.VALIDATION_ERROR,
                f"missing dimension score(s): {sorted(missing_dims)}",
                record_key=context.lot_id or context.plant_id,
            )

    def calculate(self, context: CalculationContext, inputs: PTSAInputs) -> CalculationResult:
        record_key = context.lot_id or context.plant_id
        raw = inputs.raw

        raw_ratios = {
            "SCR_RAW": compute_scr(raw.scr_raw_stock, raw.scr_raw_daily_consumption, record_key),
            "SCR_FINISHED": compute_scr(raw.scr_finished_stock, raw.scr_finished_daily_consumption, record_key),
            "SCR_GLAZE": compute_scr(raw.scr_glaze_stock, raw.scr_glaze_daily_consumption, record_key),
            "PSI_ENERGY": compute_psi(raw.psi_energy_output_m2, raw.psi_energy_input_gj, record_key),
            "PSI_MATERIAL": compute_psi(raw.psi_material_output_m2, raw.psi_material_input_m2, record_key),
            "PSI_THROUGHPUT": compute_psi(raw.psi_throughput_output_m2, raw.psi_throughput_hours, record_key),
            "OCR_FLEXURAL": compute_ocr(raw.ocr_flexural_passed, raw.ocr_flexural_attempted, record_key),
            "OCR_BREAKING": compute_ocr(raw.ocr_breaking_passed, raw.ocr_breaking_attempted, record_key),
            "OCR_SURFACE": compute_ocr(raw.ocr_surface_passed, raw.ocr_surface_attempted, record_key),
        }

        zscore_weights = inputs.zscore_weights or {
            DIM_IOA: equal_weights(IOA_METRICS),
            DIM_OP: equal_weights(OP_METRICS),
            DIM_TQ: equal_weights(TQ_METRICS),
        }

        def zscores_for(metrics: tuple[str, ...]) -> dict[str, float]:
            return {
                m: compute_zscore(raw_ratios[m], inputs.population_stats[m], m, record_key)
                for m in metrics
            }

        ioa_z = zscores_for(IOA_METRICS)
        op_z = zscores_for(OP_METRICS)
        tq_z = zscores_for(TQ_METRICS)

        ioai = compute_subindex(ioa_z, zscore_weights[DIM_IOA])
        opi = compute_subindex(op_z, zscore_weights[DIM_OP])
        tqi = compute_subindex(tq_z, zscore_weights[DIM_TQ])

        p_tsi_z = compute_p_tsi_z(ioai, opi, tqi)
        p_tsi_5 = compute_p_tsi_scoring(inputs.dimension_scores, inputs.weight_set)

        tii = None
        if inputs.previous_p_tsi_5 is not None:
            tii = compute_tii(p_tsi_5, inputs.previous_p_tsi_5, record_key)

        values: dict[str, Any] = {
            "scr_raw_material": raw_ratios["SCR_RAW"],
            "scr_finished_product": raw_ratios["SCR_FINISHED"],
            "scr_glaze": raw_ratios["SCR_GLAZE"],
            "psi_energy": raw_ratios["PSI_ENERGY"],
            "psi_material": raw_ratios["PSI_MATERIAL"],
            "psi_throughput": raw_ratios["PSI_THROUGHPUT"],
            "ocr_flexural": raw_ratios["OCR_FLEXURAL"],
            "ocr_breaking_load": raw_ratios["OCR_BREAKING"],
            "ocr_surface": raw_ratios["OCR_SURFACE"],
            "ioai": ioai, "opi": opi, "tqi": tqi,
            "p_tsi_z": p_tsi_z, "p_tsi_5": p_tsi_5, "tii": tii,
        }
        return CalculationResult(
            engine=self.engine_name, engine_version=self.engine_version,
            calc_run_id="", context=context, values=values,
        )

    def validate_outputs(self, result: CalculationResult) -> None:
        for key in ("p_tsi_z", "p_tsi_5"):
            value = result.values[key]
            if math.isnan(value):
                raise EngineError(ErrorCategory.CALCULATION_ERROR, f"'{key}' is NaN")

    def persist(self, result: CalculationResult) -> dict[str, Any]:
        row = {
            "calc_run_id": result.calc_run_id,
            "plant_id": result.context.plant_id,
            "lot_id": result.context.lot_id,
            "period_start": result.context.period_start,
            "period_end": result.context.period_end,
            **result.values,
        }
        return {"table": "fact_ptsa_state", "row": row}
