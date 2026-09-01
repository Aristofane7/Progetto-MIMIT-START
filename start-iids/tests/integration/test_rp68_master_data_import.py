"""End-to-end check that the real RP6.8 cluster master data (ADR-015) loads
cleanly into the actual schema, and that the product importer's FK guard
holds against it using the non-real test fixture.
"""
import glob
import pathlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from scripts.import_rp68_product_master_data import (
    REAL_CLUSTER_VERSION,
    build_cluster_insert_sql,
    build_product_insert_sql,
    load_cluster_master_csv,
    load_product_master_csv,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "sql" / "migrations"
CLUSTER_CSV = ROOT / "data" / "reference" / "rp68_cluster_master.csv"
FIXTURE_CSV = ROOT / "tests" / "fixtures" / "rp68_product_master_fixture.csv"


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    with engine.begin() as conn:
        conn.execute(text("PRAGMA foreign_keys=ON"))
        for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
            conn.connection.driver_connection.executescript(pathlib.Path(path).read_text())
    return engine


def test_real_cluster_seed_loads_into_dim_product_cluster(engine):
    cluster_rows = load_cluster_master_csv(CLUSTER_CSV)
    statements = build_cluster_insert_sql(cluster_rows)
    with engine.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        count = conn.execute(
            text("SELECT COUNT(*) FROM dim_product_cluster WHERE cluster_version = :v"),
            {"v": REAL_CLUSTER_VERSION},
        ).scalar()
    assert count == 22


def test_fixture_products_load_against_real_clusters_with_fk_integrity(engine):
    cluster_rows = load_cluster_master_csv(CLUSTER_CSV)
    known_ids = {r.cluster_id for r in cluster_rows}
    with engine.begin() as conn:
        for stmt in build_cluster_insert_sql(cluster_rows):
            conn.execute(text(stmt))

    accepted, findings = load_product_master_csv(FIXTURE_CSV, known_ids)
    assert len(findings) == 2  # unknown cluster_id + missing product_id, both rejected before insert

    with engine.begin() as conn:
        for stmt in build_product_insert_sql(accepted):
            conn.execute(text(stmt))
        loaded = conn.execute(
            text("SELECT product_id, cluster_id FROM dim_product ORDER BY product_id")
        ).all()
    assert [row.product_id for row in loaded] == ["FIXTURE-PROD-0001", "FIXTURE-PROD-0002"]
