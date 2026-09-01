"""Generate a temporary, clearly-tagged SYNTHETIC_DEMO dataset (ADR-014).

Unblocks Power BI semantic model development (issue #8) without waiting for
real master data (issue #7) or live connectors (issue #3). Every row is tagged
so it can never be mistaken for real data — see ADR-014 for the full rule set.

This script must NEVER be imported by, or run as part of, any production code
path (no calculation engine, no API route imports this module).

Usage::

    python3 -m scripts.generate_synthetic_demo_data --sql-out data/synthetic/seed.sql --csv-dir data/synthetic/csv
"""
from __future__ import annotations

import argparse
import csv
import random
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from src.product.clustering.cqs import ClusterScoreComponents, compute_cqs
from src.product.sales.cluster_performance import classify_trend

SEED = 42
SOURCE_SYSTEM = "SYNTHETIC_DEMO"
CLUSTER_VERSION = "SYNTHETIC_DEMO_V1"
COEFFICIENT_SET_ID = "SYN_COEFF_SET"
WEIGHT_SET_ID = "SYN_WEIGHT_SET"
BASELINE_ID = "SYN_BASELINE_2025"

PLANTS = [
    ("SYN01", "Synthetic Demo Plant 1", "MTS"),
    ("SYN02", "Synthetic Demo Plant 2", "MTO"),
]

PROCESS_CATALOG = [
    ("SYN-PROC-MILL", "Milling (synthetic)", "MILLING", "MTS"),
    ("SYN-PROC-PRESS", "Pressing (synthetic)", "PRESSING", "MTO"),
    ("SYN-PROC-DRY", "Drying (synthetic)", "DRYING", "MTO"),
    ("SYN-PROC-GLAZE", "Glazing (synthetic)", "GLAZING_DECORATION", "MTO"),
    ("SYN-PROC-KILN", "Kiln firing (synthetic)", "KILN_FIRING", "MTO"),
]

CLUSTER_DEFS = [
    (9001, "Large format, matte", ClusterScoreComponents(0.80, 0.75, 0.60, 0.90)),
    (9002, "Small format, glossy", ClusterScoreComponents(0.70, 0.65, 0.55, 0.60)),
    (9003, "Wood-effect, textured", ClusterScoreComponents(0.85, 0.80, 0.70, 0.75)),
]


@dataclass
class Dataset:
    tables: dict[str, list[dict]] = field(default_factory=dict)

    def add(self, table: str, row: dict) -> None:
        self.tables.setdefault(table, []).append(row)


def _quantize(rng: random.Random, low: float, high: float) -> float:
    return round(rng.uniform(low, high), 4)


def build_synthetic_dataset(seed: int = SEED) -> Dataset:
    rng = random.Random(seed)
    ds = Dataset()

    # --- dim_plant / dim_line / dim_process / dim_equipment ---
    for plant_id, plant_name, area_type in PLANTS:
        ds.add("dim_plant", {
            "plant_id": plant_id, "plant_name": plant_name, "site_code": f"{plant_id}-SITE",
            "is_active": True,
        })
        line_id = f"{plant_id}-L1"
        ds.add("dim_line", {
            "line_id": line_id, "plant_id": plant_id, "line_name": f"{plant_name} Line 1",
            "area_type": area_type, "is_active": True,
        })

    for process_id, process_name, process_family, mts_mto_class in PROCESS_CATALOG:
        ds.add("dim_process", {
            "process_id": process_id, "process_name": process_name,
            "process_family": process_family, "mts_mto_class": mts_mto_class,
        })

    equipment_ids: dict[str, list[str]] = {}
    for plant_id, _, _ in PLANTS:
        line_id = f"{plant_id}-L1"
        equipment_ids[plant_id] = []
        for process_id, *_ in PROCESS_CATALOG:
            eq_id = f"{line_id}-EQ-{process_id.split('-')[-1]}"
            ds.add("dim_equipment", {
                "equipment_id": eq_id, "line_id": line_id, "process_id": process_id,
                "equipment_name": f"{process_id} equipment", "is_active": True,
            })
            equipment_ids[plant_id].append(eq_id)

    # --- dim_product_cluster ---
    for cluster_id, label, components in CLUSTER_DEFS:
        cqs = compute_cqs(components)
        ds.add("dim_product_cluster", {
            "cluster_id": cluster_id, "cluster_version": CLUSTER_VERSION,
            "dominant_shape": label, "balance_score": components.balance,
            "coherence_score": components.coherence, "separation_score": components.separation,
            "business_relevance_score": components.business_relevance, "cqs": round(cqs, 6),
            "is_current": True,
        })

    # --- dim_product ---
    products = []
    for i in range(1, 13):
        cluster_id = CLUSTER_DEFS[i % len(CLUSTER_DEFS)][0]
        product_id = f"SYN-PROD-{i:04d}"
        products.append((product_id, cluster_id))
        ds.add("dim_product", {
            "product_id": product_id, "product_name": f"Synthetic product {i:04d}",
            "cluster_id": cluster_id, "cluster_version": CLUSTER_VERSION,
            "mass_kg_m2": _quantize(rng, 18.0, 24.0), "product_status": "ACTIVE",
            "is_current": True,
        })

    # --- governance rows (all DRAFT, never to be promoted — ADR-014 point 2) ---
    ds.add("dim_coefficient_set", {
        "coefficient_set_id": COEFFICIENT_SET_ID, "description": "Synthetic demo only — never approve",
        "reference_year": 2025, "status": "DRAFT",
    })
    ds.add("dim_weight_set", {
        "weight_set_id": WEIGHT_SET_ID, "methodology": "AHP", "version": "0.0-synthetic",
        "status": "DRAFT",
    })
    ds.add("dim_baseline", {
        "baseline_id": BASELINE_ID, "baseline_name": "Synthetic demo baseline",
        "baseline_year": 2025, "functional_unit": "m2", "coefficient_set_id": COEFFICIENT_SET_ID,
        "status": "DRAFT",
    })

    # --- fact_production_lot / fact_lot_process / calc runs / EEA & P-TSA state ---
    calc_run_seq = 0
    lot_seq = 0
    start_date = date(2025, 1, 6)

    for product_id, cluster_id in products:
        plant_id, _, _ = PLANTS[lot_seq % len(PLANTS)]
        line_id = f"{plant_id}-L1"
        for _lot_n in range(2):
            lot_seq += 1
            lot_id = f"SYN-LOT-{lot_seq:05d}"
            lot_start = datetime.combine(start_date + timedelta(days=7 * lot_seq), datetime.min.time())
            lot_end = lot_start + timedelta(hours=8)
            output_m2 = _quantize(rng, 500.0, 3000.0)

            ds.add("fact_production_lot", {
                "lot_id": lot_id, "product_id": product_id, "plant_id": plant_id,
                "start_ts": lot_start, "end_ts": lot_end, "output_m2": output_m2,
                "scenario": "CURRENT", "source_lot_code": lot_id, "source_system": SOURCE_SYSTEM,
            })

            process_id = PROCESS_CATALOG[lot_seq % len(PROCESS_CATALOG)][0]
            equipment_id = equipment_ids[plant_id][lot_seq % len(equipment_ids[plant_id])]
            ds.add("fact_lot_process", {
                "lot_process_id": lot_seq, "lot_id": lot_id, "process_id": process_id,
                "line_id": line_id, "equipment_id": equipment_id, "sequence_no": 1,
                "start_ts": lot_start, "end_ts": lot_end, "output_qty": output_m2,
                "qty_unit": "m2", "source_system": SOURCE_SYSTEM,
            })

            # EEA state — randomized, NOT engine-computed (ADR-014 point 3).
            calc_run_seq += 1
            eea_run_id = f"SYN_CALC_EEA_{calc_run_seq:05d}"
            ds.add("audit_calc_run", {
                "calc_run_id": eea_run_id, "engine": "EEA", "engine_version": "synthetic-0.0",
                "baseline_id": BASELINE_ID, "coefficient_set_id": COEFFICIENT_SET_ID,
                "period_start": lot_start, "period_end": lot_end, "scenario": "CURRENT",
                "status": "SUCCESS", "started_at": lot_start,
            })
            f_env = _quantize(rng, 50, 500)
            f_econ = _quantize(rng, 50, 500)
            f_soc = _quantize(rng, 20, 200)
            f_tech = _quantize(rng, -50, 300)
            ds.add("fact_eea_state", {
                "eea_state_id": calc_run_seq, "calc_run_id": eea_run_id, "plant_id": plant_id,
                "line_id": line_id, "lot_id": lot_id, "period_start": lot_start, "period_end": lot_end,
                "scenario": "CURRENT", "f_env_gj": f_env, "f_econ_gj": f_econ, "f_soc_gj": f_soc,
                "f_tech_gj": f_tech, "sa_gj": round(f_env + f_econ + f_soc + f_tech, 4),
                "tsi_norm": _quantize(rng, 0.85, 1.25), "data_quality_score": 0.5,
            })

            # P-TSA state — randomized, NOT engine-computed (ADR-014 point 3).
            ptsa_run_id = f"SYN_CALC_PTSA_{calc_run_seq:05d}"
            ds.add("audit_calc_run", {
                "calc_run_id": ptsa_run_id, "engine": "PTSA", "engine_version": "synthetic-0.0",
                "baseline_id": BASELINE_ID, "coefficient_set_id": COEFFICIENT_SET_ID,
                "weight_set_id": WEIGHT_SET_ID, "period_start": lot_start, "period_end": lot_end,
                "scenario": "CURRENT", "status": "SUCCESS", "started_at": lot_start,
            })
            ds.add("fact_ptsa_state", {
                "ptsa_state_id": calc_run_seq, "calc_run_id": ptsa_run_id,
                "period_start": lot_start, "period_end": lot_end, "product_id": product_id,
                "lot_id": lot_id, "plant_id": plant_id,
                "ioai": _quantize(rng, -1.0, 1.0), "opi": _quantize(rng, -1.0, 1.0),
                "tqi": _quantize(rng, -1.0, 1.0), "p_tsi_z": _quantize(rng, -0.3, 0.3),
                "p_tsi_5": _quantize(rng, 2.5, 4.5), "weight_set_id": WEIGHT_SET_ID,
                "data_quality_score": 0.5,
            })

    # --- fact_product_sales / fact_cluster_performance ---
    sales_id = 0
    cluster_perf_id = 0
    cluster_sales: dict[tuple[int, int], list[float]] = {}
    periods = [(date(2025, 1, 1), date(2025, 7, 1)), (date(2025, 7, 1), date(2026, 1, 1))]

    for period_idx, (period_start, period_end) in enumerate(periods):
        for product_id, cluster_id in products:
            sales_id += 1
            sales_m2 = _quantize(rng, 1000, 8000)
            ds.add("fact_product_sales", {
                "product_sales_id": sales_id, "product_id": product_id,
                "period_start": period_start, "period_end": period_end,
                "sales_m2": sales_m2, "revenue_eur": round(sales_m2 * rng.uniform(8, 15), 2),
                "source_system": SOURCE_SYSTEM,
            })
            cluster_sales.setdefault((cluster_id, period_idx), []).append(sales_m2)

    previous_avg: dict[int, float] = {}
    for period_idx, (period_start, period_end) in enumerate(periods):
        for cluster_id, _, _ in CLUSTER_DEFS:
            values = cluster_sales.get((cluster_id, period_idx), [])
            if not values:
                continue
            cluster_perf_id += 1
            avg = sum(values) / len(values)
            trend_class = classify_trend(avg, previous_avg.get(cluster_id))
            previous_avg[cluster_id] = avg
            ds.add("fact_cluster_performance", {
                "cluster_perf_id": cluster_perf_id, "cluster_id": cluster_id,
                "cluster_version": CLUSTER_VERSION, "period_start": period_start,
                "period_end": period_end, "product_count": len(values),
                "sales_total_m2": round(sum(values), 4), "sales_m2_per_product": round(avg, 4),
                "trend_class": trend_class,
            })

    # --- dim_trend / bridge_cluster_trend ---
    for i, (cluster_id, label, _components) in enumerate(CLUSTER_DEFS, start=1):
        trend_id = f"SYN-TREND-{i:03d}"
        ds.add("dim_trend", {
            "trend_id": trend_id, "trend_category": "AESTHETIC", "trend_value": label,
            "source_type": "SCENARIO", "source_name": SOURCE_SYSTEM,
        })
        ds.add("bridge_cluster_trend", {
            "cluster_id": cluster_id, "cluster_version": CLUSTER_VERSION, "trend_id": trend_id,
            "alignment_score": _quantize(rng, 0.4, 0.95),
        })

    return ds


def _sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return f"'{value.isoformat()}'"
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def write_sql(dataset: Dataset, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("-- Generated by scripts/generate_synthetic_demo_data.py — see ADR-014.\n")
        f.write("-- SYNTHETIC DATA. Never mark the coefficient/weight sets below as APPROVED.\n\n")
        for table, rows in dataset.tables.items():
            for row in rows:
                columns = ", ".join(row.keys())
                values = ", ".join(_sql_literal(v) for v in row.values())
                f.write(f"INSERT INTO {table} ({columns}) VALUES ({values});\n")


def write_csv(dataset: Dataset, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for table, rows in dataset.tables.items():
        if not rows:
            continue
        # Rows in the same table may have heterogeneous keys (e.g. an EEA
        # audit_calc_run has no weight_set_id, a P-TSA one does) — union the
        # fieldnames so DictWriter doesn't choke on the first row's shape.
        fieldnames: list[str] = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
        with (directory / f"{table}.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sql-out", type=Path, default=Path("data/synthetic/synthetic_demo_seed.sql"))
    parser.add_argument("--csv-dir", type=Path, default=Path("data/synthetic/csv"))
    args = parser.parse_args()

    dataset = build_synthetic_dataset()
    write_sql(dataset, args.sql_out)
    write_csv(dataset, args.csv_dir)
    row_count = sum(len(rows) for rows in dataset.tables.values())
    print(f"Generated {row_count} synthetic rows across {len(dataset.tables)} tables "
          f"(SQL: {args.sql_out}, CSV: {args.csv_dir})")


if __name__ == "__main__":
    main()
