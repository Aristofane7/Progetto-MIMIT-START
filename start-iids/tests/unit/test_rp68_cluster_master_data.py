"""Regression guard on the transcribed RP6.8 cluster master data (issue #7,
ADR-015) — `data/reference/rp68_cluster_master.csv` is hand-transcribed from
the RP6.8 report and must never silently drift from the published numbers.
"""
from pathlib import Path

from scripts.import_rp68_product_master_data import (
    EXPECTED_CLUSTER_COUNT,
    EXPECTED_PRODUCT_TOTAL,
    REAL_CLUSTER_VERSION,
    build_cluster_insert_sql,
    load_cluster_master_csv,
)

ROOT = Path(__file__).resolve().parents[2]
CLUSTER_CSV = ROOT / "data" / "reference" / "rp68_cluster_master.csv"


def test_cluster_csv_has_22_clusters_summing_to_13251_products():
    rows = load_cluster_master_csv(CLUSTER_CSV)
    assert len(rows) == EXPECTED_CLUSTER_COUNT
    assert sum(r.product_count for r in rows) == EXPECTED_PRODUCT_TOTAL
    assert sorted(r.cluster_id for r in rows) == list(range(EXPECTED_CLUSTER_COUNT))


def test_cluster_11_source_defect_fields_are_null_not_guessed():
    rows = load_cluster_master_csv(CLUSTER_CSV)
    cluster_11 = next(r for r in rows if r.cluster_id == 11)
    # Forma/Dimensione survive (plausible); the three fields affected by the
    # documented column-shift defect in the source dashboard must be NULL.
    assert cluster_11.dim_fields["dominant_shape"] is not None
    assert cluster_11.dim_fields["dominant_dimension"] is not None
    assert cluster_11.dim_fields["dominant_thickness"] is None
    assert cluster_11.dim_fields["dominant_slip_class"] is None
    assert cluster_11.dim_fields["dominant_effect"] is None
    assert cluster_11.dim_fields["dominant_colour"] is None


def test_build_cluster_insert_sql_produces_one_statement_per_cluster():
    rows = load_cluster_master_csv(CLUSTER_CSV)
    statements = build_cluster_insert_sql(rows)
    assert len(statements) == EXPECTED_CLUSTER_COUNT
    assert all("INSERT INTO dim_product_cluster" in s for s in statements)
    assert all(REAL_CLUSTER_VERSION in s for s in statements)


def test_corrupted_csv_is_rejected(tmp_path):
    bad = tmp_path / "bad.csv"
    good_rows = CLUSTER_CSV.read_text().splitlines()
    # Drop the last data row so the product_count total no longer matches.
    bad.write_text("\n".join(good_rows[:-1]) + "\n")
    try:
        load_cluster_master_csv(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError on a truncated/corrupted cluster CSV")
