"""Materialize `mv_intelligent_industry_state` (+ conformed dimension slices)
to CSV, for the Power BI semantic model's local/dev data source (issue #8,
ADR-016).

By default this builds an ephemeral SQLite database from the migrations, the
view, and the synthetic demo dataset (ADR-014) — so the semantic model has
real, joined rows to develop against without a live database. Point
`--db-url` at any SQLAlchemy-reachable database (including a real one, once
issues #3/#7 land) to export real data instead: the output shape is
identical either way, so the Power BI model needs no rework (ROADMAP, Stage
8, Next steps #5).

No business logic is computed here — this only runs the already-committed
view and groups already-computed columns for dimension distincts (sec. 39 /
ADR-006: BI is not a calculation engine, and neither is this export step).

Usage::

    python3 -m scripts.export_mv_intelligent_industry_state --out-dir data/synthetic/powerbi
    python3 -m scripts.export_mv_intelligent_industry_state --db-url sqlite:///real.db --out-dir out/
"""
from __future__ import annotations

import argparse
import csv
import glob
import pathlib

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from scripts.generate_synthetic_demo_data import build_synthetic_dataset

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT / "sql" / "migrations"
VIEWS_DIR = ROOT / "sql" / "views"

FACT_COLUMNS = None  # SELECT * — the view's column list is the single source of truth.

DIMENSION_QUERIES = {
    "dim_plant": "SELECT DISTINCT plant_id FROM mv_intelligent_industry_state WHERE plant_id IS NOT NULL",
    "dim_line": "SELECT DISTINCT plant_id, line_id FROM mv_intelligent_industry_state WHERE line_id IS NOT NULL",
    "dim_process": (
        "SELECT DISTINCT process_id, process_name, process_family "
        "FROM mv_intelligent_industry_state WHERE process_id IS NOT NULL"
    ),
    "dim_product": (
        "SELECT DISTINCT product_id, cluster_id, cluster_version "
        "FROM mv_intelligent_industry_state WHERE product_id IS NOT NULL"
    ),
    "dim_cluster": (
        "SELECT DISTINCT cluster_id, cluster_version FROM mv_intelligent_industry_state "
        "WHERE cluster_id IS NOT NULL"
    ),
}


def build_synthetic_engine() -> Engine:
    """An ephemeral, migrations+view+synthetic-seeded engine — the default
    local data source, per ADR-014's "start now against synthetic data" rule.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
            conn.connection.driver_connection.executescript(pathlib.Path(path).read_text())
        for path in sorted(glob.glob(str(VIEWS_DIR / "*.sql"))):
            conn.connection.driver_connection.executescript(pathlib.Path(path).read_text())

        dataset = build_synthetic_dataset()
        for table, rows in dataset.tables.items():
            for row in rows:
                columns = ", ".join(row.keys())
                placeholders = ", ".join(f":{k}" for k in row)
                conn.execute(text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"), row)
    return engine


def export(engine: Engine, out_dir: pathlib.Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    with engine.connect() as conn:
        fact_rows = conn.execute(text("SELECT * FROM mv_intelligent_industry_state")).mappings().all()
    counts["fact_shadow_state"] = _write_csv(out_dir / "fact_shadow_state.csv", fact_rows)

    with engine.connect() as conn:
        for name, query in DIMENSION_QUERIES.items():
            rows = conn.execute(text(query)).mappings().all()
            counts[name] = _write_csv(out_dir / f"{name}.csv", rows)

    return counts


def _write_csv(path: pathlib.Path, rows) -> int:
    rows = list(rows)
    if not rows:
        path.write_text("")
        return 0
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(dict(r) for r in rows)
    return len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db-url", default=None,
                         help="SQLAlchemy URL to export from. Omit to use an ephemeral "
                              "synthetic-seeded SQLite database (ADR-014).")
    parser.add_argument("--out-dir", type=pathlib.Path, default=pathlib.Path("data/synthetic/powerbi"))
    args = parser.parse_args()

    engine = create_engine(args.db_url) if args.db_url else build_synthetic_engine()
    counts = export(engine, args.out_dir)
    for name, count in counts.items():
        print(f"{name}: {count} rows -> {args.out_dir / (name + '.csv')}")


if __name__ == "__main__":
    main()
