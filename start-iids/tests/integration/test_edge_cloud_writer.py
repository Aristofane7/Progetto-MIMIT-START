"""Integration test: a collected Edge batch lands in the raw/staging schema
(migration 0011) and rejections reach audit_data_quality (issue #3, ADR-021).
"""
import glob
import pathlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.ingestion.contracts import load_contract
from src.ingestion.edge.cloud_writer import write_batch_to_staging
from src.ingestion.edge.collector import collect

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = ROOT / "sql" / "migrations"
CONTRACT_PATH = ROOT / "config" / "source_mappings" / "mes_production_v1.yaml"


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


def test_accepted_records_land_in_staging_with_a_batch_receipt(engine):
    contract = load_contract(CONTRACT_PATH)
    raw = [
        {"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 10},
        {"lot_code": "L2", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 20},
    ]
    batch = collect(contract, raw)

    with engine.begin() as conn:
        write_batch_to_staging(conn, "BATCH-001", contract, batch)

    with engine.connect() as conn:
        receipt = conn.execute(
            text("SELECT * FROM raw_ingestion_batch WHERE batch_id = 'BATCH-001'")
        ).mappings().one()
        staged = conn.execute(
            text("SELECT dedup_key, payload_json FROM stg_ingestion_record WHERE batch_id = 'BATCH-001'")
        ).mappings().all()

    assert receipt["record_count"] == 2
    assert receipt["rejected_count"] == 0
    assert receipt["contract_id"] == "MES_PRODUCTION_V1"
    assert len(staged) == 2
    assert "L1|P1" in staged[0]["dedup_key"] or "L1|P1" in staged[1]["dedup_key"]


def test_rejected_records_reach_audit_data_quality(engine):
    contract = load_contract(CONTRACT_PATH)
    raw = [{"lot_code": "L1", "product_code": None, "start_time": "2026-01-01T00:00:00"}]
    batch = collect(contract, raw)

    with engine.begin() as conn:
        write_batch_to_staging(conn, "BATCH-002", contract, batch)

    with engine.connect() as conn:
        findings = conn.execute(
            text("SELECT * FROM audit_data_quality WHERE dataset_name = :d"),
            {"d": contract.contract_id},
        ).mappings().all()
    assert len(findings) == 1
    assert findings[0]["severity"] == "BLOCKER"


def test_restaging_the_same_batch_is_rejected_by_the_unique_constraint(engine):
    """sec. 33 idempotence backstop at the storage layer, not just in-batch."""
    contract = load_contract(CONTRACT_PATH)
    raw = [{"lot_code": "L1", "product_code": "P1", "start_time": "2026-01-01T00:00:00", "output_m2": 10}]
    batch = collect(contract, raw)

    with engine.begin() as conn:
        write_batch_to_staging(conn, "BATCH-003", contract, batch)

    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError), engine.begin() as conn:
        write_batch_to_staging(conn, "BATCH-004", contract, batch)
