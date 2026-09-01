"""End-to-end check that the synthetic demo dataset (ADR-014) flows through the
full schema into `mv_intelligent_industry_state` and the read-only API —
proving the Power BI semantic model has something real to query against.
"""
import glob
import pathlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from scripts.generate_synthetic_demo_data import (
    CLUSTER_VERSION,
    COEFFICIENT_SET_ID,
    SOURCE_SYSTEM,
    WEIGHT_SET_ID,
    build_synthetic_dataset,
)
from src.api.app import app, configure_repository
from src.api.repository import IIDSRepository

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "sql" / "migrations"
VIEWS_DIR = ROOT / "sql" / "views"


def _insert(conn, table: str, row: dict) -> None:
    columns = ", ".join(row.keys())
    placeholders = ", ".join(f":{k}" for k in row)
    conn.execute(text(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"), row)


@pytest.fixture()
def seeded_engine():
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
        # Insertion order matters for FK integrity; the generator already
        # builds tables in a dependency-safe order.
        for table, rows in dataset.tables.items():
            for row in rows:
                _insert(conn, table, row)
    return engine


def test_synthetic_rows_are_tagged_and_non_colliding():
    dataset = build_synthetic_dataset()
    for lot in dataset.tables["fact_production_lot"]:
        assert lot["source_system"] == SOURCE_SYSTEM
        assert lot["plant_id"].startswith("SYN")
    for cluster in dataset.tables["dim_product_cluster"]:
        assert cluster["cluster_version"] == CLUSTER_VERSION
        assert cluster["cluster_id"] >= 9001
    for coeff_set in dataset.tables["dim_coefficient_set"]:
        assert coeff_set["coefficient_set_id"] == COEFFICIENT_SET_ID
        assert coeff_set["status"] == "DRAFT"
    for weight_set in dataset.tables["dim_weight_set"]:
        assert weight_set["weight_set_id"] == WEIGHT_SET_ID
        assert weight_set["status"] == "DRAFT"


def test_mv_intelligent_industry_state_returns_synthetic_rows(seeded_engine):
    with seeded_engine.connect() as conn:
        rows = conn.execute(text("SELECT * FROM mv_intelligent_industry_state")).mappings().all()
    assert len(rows) >= 24  # 12 products x 2 lots each
    for row in rows:
        assert row["plant_id"].startswith("SYN")
        assert row["tsi_norm"] is not None
        assert row["p_tsi_5"] is not None
        assert row["process_name"] is not None  # ADR-016: Factory-page Process drill-down


def test_api_serves_synthetic_lot_state(seeded_engine):
    from fastapi.testclient import TestClient

    configure_repository(IIDSRepository(seeded_engine))
    client = TestClient(app)

    with seeded_engine.connect() as conn:
        any_lot_id = conn.execute(text("SELECT lot_id FROM fact_production_lot LIMIT 1")).scalar()

    resp = client.get(f"/api/v1/shadow/lot/{any_lot_id}", params={"at": "2027-01-01T00:00:00Z"})
    assert resp.status_code == 200
    assert resp.json()["state"]["tsi_norm"] is not None
