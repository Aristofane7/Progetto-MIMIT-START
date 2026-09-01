"""Import real RP6.8 product master data (issue #7).

Two independent pieces, at two different levels of readiness:

1. **Cluster master (`dim_product_cluster`) — ready now.** The 22 real
   clusters, their sizes and dominant-attribute profiles are transcribed
   verbatim from `RP6.8 Report di Product Analysis_30-04-25.pdf` (sec. 3.3,
   p.13 dashboard) into `data/reference/rp68_cluster_master.csv`. Every
   `product_count` was cross-checked to sum to exactly 13,251 (the report's
   own total, sec. 2.3) as a transcription guard. One cluster (11) has a
   documented source-data defect (a column-shift in the report's own
   dashboard table) and is loaded with the affected fields left NULL rather
   than guessed — see `data_quality_flag` in the CSV and ADR-015.

2. **Product master (`dim_product`) — tooling ready, blocked on input.**
   RP6.8 sec. 3.7 states a full per-product cluster-assignment export for all
   13,251 products exists as a deliverable, but that file is not present in
   this repository (ADR-015). `load_product_master_csv` / `--products-csv`
   below is the ready-to-run importer for that export once supplied — it is
   exercised today only against `tests/fixtures/rp68_product_master_fixture.csv`,
   a small non-real fixture used purely to prove the validation logic.

Usage::

    python3 -m scripts.import_rp68_product_master_data --sql-out data/reference/rp68_master_seed.sql
    python3 -m scripts.import_rp68_product_master_data --products-csv <real_export.csv> --sql-out out.sql
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

from src.engines.errors import DataQualityFinding, Severity

REAL_CLUSTER_VERSION = "RP68_2025_04"
EXPECTED_CLUSTER_COUNT = 22
EXPECTED_PRODUCT_TOTAL = 13251

DEFAULT_CLUSTER_CSV = Path("data/reference/rp68_cluster_master.csv")

# Required for a product master row to be loadable at all (sec. 27-style
# reject_if_missing policy, mirroring src/ingestion/contracts.py).
PRODUCT_REQUIRED_FIELDS = ("product_id", "cluster_id")

CLUSTER_COLUMNS_TO_DIM = {
    "dominant_shape": "dominant_shape",
    "dominant_dimension": "dominant_dimension",
    "dominant_thickness": "dominant_thickness",
    "dominant_slip_class": "dominant_slip_class",
    "dominant_effect": "dominant_effect",
    "dominant_colour": "dominant_colour",
}

PRODUCT_COLUMNS_TO_DIM = (
    "product_id", "product_name", "cluster_id", "shape", "dimension_class",
    "format_mm", "thickness_mm", "slip_class", "surface_effect", "finish",
    "colour_class", "mass_kg_m2", "product_status", "source_product_code",
)


@dataclass(frozen=True)
class ClusterRow:
    cluster_id: int
    product_count: int
    dim_fields: dict[str, str | None]


def load_cluster_master_csv(path: Path = DEFAULT_CLUSTER_CSV) -> list[ClusterRow]:
    """Load and sanity-check the verified RP6.8 cluster table.

    Raises ``ValueError`` if the transcription guards fail — a corrupted or
    hand-edited CSV must never be silently loaded into a "real" table.
    """
    rows: list[ClusterRow] = []
    with path.open(newline="") as f:
        for raw in csv.DictReader(f):
            cluster_id = int(raw["cluster_id"])
            dim_fields = {
                dim_col: (raw[csv_col] or None)
                for csv_col, dim_col in CLUSTER_COLUMNS_TO_DIM.items()
            }
            rows.append(
                ClusterRow(cluster_id=cluster_id, product_count=int(raw["product_count"]), dim_fields=dim_fields)
            )

    if len(rows) != EXPECTED_CLUSTER_COUNT:
        raise ValueError(f"expected {EXPECTED_CLUSTER_COUNT} clusters, got {len(rows)}")
    ids = sorted(r.cluster_id for r in rows)
    if ids != list(range(EXPECTED_CLUSTER_COUNT)):
        raise ValueError(f"expected cluster_id 0..{EXPECTED_CLUSTER_COUNT - 1}, got {ids}")
    total = sum(r.product_count for r in rows)
    if total != EXPECTED_PRODUCT_TOTAL:
        raise ValueError(
            f"cluster product_count sums to {total}, expected {EXPECTED_PRODUCT_TOTAL} "
            "(RP6.8 sec. 2.3) — the CSV may be corrupted or hand-edited"
        )
    return rows


def build_cluster_insert_sql(rows: list[ClusterRow], cluster_version: str = REAL_CLUSTER_VERSION) -> list[str]:
    statements = []
    for row in rows:
        columns = ["cluster_id", "cluster_version", *row.dim_fields.keys(), "is_current"]
        values = [row.cluster_id, cluster_version, *row.dim_fields.values(), True]
        statements.append(f"INSERT INTO dim_product_cluster ({', '.join(columns)}) "
                           f"VALUES ({', '.join(_sql_literal(v) for v in values)});")
    return statements


def load_product_master_csv(
    path: Path, known_cluster_ids: set[int]
) -> tuple[list[dict], list[DataQualityFinding]]:
    """Validate a product master export against the loaded cluster set.

    Returns accepted rows plus BLOCKER findings for rejected ones (missing
    required field, or a `cluster_id` not present in `known_cluster_ids`).
    Never raises on bad data — that is the caller's/importer's decision to
    make once findings are reviewed (sec. 29.3).
    """
    accepted: list[dict] = []
    findings: list[DataQualityFinding] = []
    with path.open(newline="") as f:
        for raw in csv.DictReader(f):
            record_key = raw.get("product_id") or raw.get("source_product_code") or "<unknown>"
            missing = [field for field in PRODUCT_REQUIRED_FIELDS if not raw.get(field)]
            if missing:
                findings.append(DataQualityFinding(
                    dataset_name="rp68_product_master", record_key=record_key,
                    check_code="missing_required_field", severity=Severity.BLOCKER,
                    passed=False, expected_rule=f"required fields present: {missing}",
                ))
                continue
            cluster_id = int(raw["cluster_id"])
            if cluster_id not in known_cluster_ids:
                findings.append(DataQualityFinding(
                    dataset_name="rp68_product_master", record_key=record_key,
                    check_code="unknown_cluster_id", severity=Severity.BLOCKER,
                    passed=False, observed_value=str(cluster_id),
                    expected_rule=f"cluster_id in loaded {REAL_CLUSTER_VERSION} set",
                ))
                continue
            accepted.append({col: raw.get(col) or None for col in PRODUCT_COLUMNS_TO_DIM})
    return accepted, findings


def build_product_insert_sql(rows: list[dict], cluster_version: str = REAL_CLUSTER_VERSION) -> list[str]:
    statements = []
    for row in rows:
        columns = [*PRODUCT_COLUMNS_TO_DIM, "cluster_version", "is_current"]
        values = [*row.values(), cluster_version, True]
        statements.append(f"INSERT INTO dim_product ({', '.join(columns)}) "
                           f"VALUES ({', '.join(_sql_literal(v) for v in values)});")
    return statements


def _sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clusters-csv", type=Path, default=DEFAULT_CLUSTER_CSV)
    parser.add_argument("--cluster-version", default=REAL_CLUSTER_VERSION)
    parser.add_argument("--products-csv", type=Path, default=None,
                         help="Real 13,251-product export (RP6.8 sec. 3.7). Not shipped in this repo — "
                              "omit to load only the 22 real clusters.")
    parser.add_argument("--sql-out", type=Path, default=Path("data/reference/rp68_master_seed.sql"))
    args = parser.parse_args()

    cluster_rows = load_cluster_master_csv(args.clusters_csv)
    statements = build_cluster_insert_sql(cluster_rows, args.cluster_version)
    print(f"Loaded {len(cluster_rows)} real RP6.8 clusters "
          f"(sum product_count={sum(r.product_count for r in cluster_rows)}).")

    if args.products_csv is not None:
        known_ids = {r.cluster_id for r in cluster_rows}
        products, findings = load_product_master_csv(args.products_csv, known_ids)
        for finding in findings:
            print(f"REJECTED {finding.record_key}: {finding.check_code} ({finding.expected_rule})")
        statements += build_product_insert_sql(products, args.cluster_version)
        print(f"Loaded {len(products)} products, rejected {len(findings)}.")
    else:
        print("No --products-csv supplied — the real 13,251-product export (RP6.8 sec. 3.7) "
              "is an external blocker, see ADR-015. Only cluster master data was loaded.")

    args.sql_out.parent.mkdir(parents=True, exist_ok=True)
    with args.sql_out.open("w") as f:
        f.write("-- Generated by scripts/import_rp68_product_master_data.py — see ADR-015.\n")
        f.write(f"-- Real RP6.8 master data, cluster_version = {args.cluster_version}.\n\n")
        f.write("\n".join(statements) + "\n")
    print(f"Wrote {len(statements)} INSERT statements to {args.sql_out}")


if __name__ == "__main__":
    main()
