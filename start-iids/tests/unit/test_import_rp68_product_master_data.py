"""Unit tests for the RP6.8 product master importer (issue #7, ADR-015).

Exercised only against `tests/fixtures/rp68_product_master_fixture.csv` — a
small, clearly-labeled FIXTURE, never the real 13,251-product export (which
does not exist in this repository, see ADR-015).
"""
from pathlib import Path

from src.engines.errors import Severity
from scripts.import_rp68_product_master_data import (
    build_product_insert_sql,
    load_cluster_master_csv,
    load_product_master_csv,
)

ROOT = Path(__file__).resolve().parents[2]
CLUSTER_CSV = ROOT / "data" / "reference" / "rp68_cluster_master.csv"
FIXTURE_CSV = ROOT / "tests" / "fixtures" / "rp68_product_master_fixture.csv"


def _known_cluster_ids() -> set[int]:
    return {r.cluster_id for r in load_cluster_master_csv(CLUSTER_CSV)}


def test_valid_rows_are_accepted():
    accepted, findings = load_product_master_csv(FIXTURE_CSV, _known_cluster_ids())
    accepted_ids = {row["product_id"] for row in accepted}
    assert accepted_ids == {"FIXTURE-PROD-0001", "FIXTURE-PROD-0002"}
    assert len(findings) == 2  # unknown cluster_id row + missing product_id row


def test_unknown_cluster_id_is_rejected_as_blocker():
    _, findings = load_product_master_csv(FIXTURE_CSV, _known_cluster_ids())
    rejected = [f for f in findings if f.check_code == "unknown_cluster_id"]
    assert len(rejected) == 1
    assert rejected[0].severity == Severity.BLOCKER
    assert rejected[0].observed_value == "999"


def test_missing_required_field_is_rejected_as_blocker():
    _, findings = load_product_master_csv(FIXTURE_CSV, _known_cluster_ids())
    rejected = [f for f in findings if f.check_code == "missing_required_field"]
    assert len(rejected) == 1
    assert rejected[0].severity == Severity.BLOCKER


def test_build_product_insert_sql_only_covers_accepted_rows():
    accepted, _ = load_product_master_csv(FIXTURE_CSV, _known_cluster_ids())
    statements = build_product_insert_sql(accepted)
    assert len(statements) == 2
    assert all("INSERT INTO dim_product" in s for s in statements)
