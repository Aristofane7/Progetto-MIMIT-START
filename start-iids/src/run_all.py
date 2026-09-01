"""START IIDS — aggregate EEA+/TSI pipeline (ADR-012).

Usage::

    python3 -m src.run_all [--output PATH]

Reproduces `data/reference/RP7.3_calculation_log.xlsx`'s structure by re-running
the verified formulas (`src/engines/eea/aggregate.py`) over
`data/reference/RP7.3_data_collection_20232025.xlsx`, exactly as instructed by
that workbook's own `Istruzioni` sheet: *"Rigenerazione: sostituire i valori e
rieseguire python3 -m src.run_all (stessa struttura di calcolo)."*

The coefficient set (`COEFF_RP73_PROVISIONAL_2026`) and AHP weight set
(`EEA_AHP_RP73_1`) are `status: APPROVED` as of 2026-09-01 (ADR-013, signed off
by the project owner) — this script loads and uses them exactly as any other
production calculation would, through `CoefficientSet.get`/`WeightSet.
get_dimension_weight`, with no special-casing. The underlying RP7.3 data
collection round is still labeled "provisional" by its own source sheet
(future consolidation may supersede these six values with a new
coefficient_set_id, per sec. 11.3 point 4), but their current use is approved.

`Psi` (exergy efficiency) is read directly from the existing calculation log as
a reported input, pending resolution of the `Ex_useful` derivation (ADR-012
open item, unaffected by the coefficient/weight approval) — it is not
recomputed from scratch here.
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import UTC, datetime
from pathlib import Path

from src.core.coefficients import load_coefficient_set
from src.core.weights import load_weight_set
from src.engines.eea.aggregate import compute_aggregate_state
from src.ingestion.rp73_reference_data import load_rp73_calculation_log, load_rp73_reference_data

SCRIPT_VERSION = "run_all-1.0.0"
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "reference"
CONFIG_DIR = ROOT / "config"

FIELDNAMES = [
    "result_id", "report_table", "plant", "year", "variable",
    "output", "unit", "date", "script_version",
]


def run(output_path: Path | None = None) -> list[dict]:
    coefficient_set = load_coefficient_set(CONFIG_DIR / "coefficients" / "rp73_provisional_2026.yaml")
    weight_set = load_weight_set(CONFIG_DIR / "weights" / "eea_ahp_rp73.yaml")
    print(
        f"Using APPROVED coefficient set '{coefficient_set.coefficient_set_id}' "
        f"(approved_by={coefficient_set.approved_by}, approved_at={coefficient_set.approved_at}) "
        f"and weight set '{weight_set.weight_set_id}' "
        f"(approved_by={weight_set.approved_by}, approved_at={weight_set.approved_at}). See ADR-013.",
        file=sys.stderr,
    )

    reference_data = load_rp73_reference_data(DATA_DIR / "RP7.3_data_collection_20232025.xlsx")
    calculation_log = load_rp73_calculation_log(DATA_DIR / "RP7.3_calculation_log.xlsx")

    today = datetime.now(UTC).date().isoformat()
    rows: list[dict] = []
    tsi_abs_by_plant_baseline: dict[str, float] = {}

    for plant_id, year in reference_data.plant_years():
        psi = calculation_log[(plant_id, year, "Psi")]
        state = compute_aggregate_state(
            plant_id, year, reference_data, coefficient_set, weight_set, psi=psi,
        )
        if year == 2023:
            tsi_abs_by_plant_baseline[plant_id] = state.tsi_abs

        for variable in ("f_env_gj", "f_econ_gj", "f_soc_gj", "f_tech_gj", "sa_raw_gj",
                          "sa_w_gj", "ex_ref_gj", "phi", "psi", "tsi_abs"):
            rows.append({
                "result_id": f"RUN_ALL_{len(rows) + 1:03d}",
                "report_table": "AGGREGATE",
                "plant": plant_id,
                "year": year,
                "variable": variable,
                "output": round(getattr(state, variable), 6),
                "unit": "GJ" if variable.endswith("_gj") else "adim",
                "date": today,
                "script_version": SCRIPT_VERSION,
            })

    for plant_id, tsi_abs_2023 in tsi_abs_by_plant_baseline.items():
        if (plant_id, 2025) not in reference_data.energy:
            continue
        psi_2025 = calculation_log[(plant_id, 2025, "Psi")]
        state_2025 = compute_aggregate_state(
            plant_id, 2025, reference_data, coefficient_set, weight_set, psi=psi_2025,
        )
        tsi_rel = state_2025.tsi_abs / tsi_abs_2023
        rows.append({
            "result_id": f"RUN_ALL_{len(rows) + 1:03d}",
            "report_table": "AGGREGATE",
            "plant": plant_id,
            "year": 2025,
            "variable": "tsi_rel",
            "output": round(tsi_rel, 6),
            "unit": "adim",
            "date": today,
            "script_version": SCRIPT_VERSION,
        })

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {output_path}", file=sys.stderr)

    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=None,
        help="CSV output path (default: print to stdout only)",
    )
    args = parser.parse_args()
    rows = run(args.output)
    if args.output is None:
        writer = csv.DictWriter(sys.stdout, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
