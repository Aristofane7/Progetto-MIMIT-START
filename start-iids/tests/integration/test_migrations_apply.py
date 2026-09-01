"""Migration ordering / FK integrity smoke test (Stage 0 DoD, spec sec. 53/62: "DB
clean install"). SQLite is used only as a syntax/FK-order gate; it is not the
target production engine (PostgreSQL-compatible or Azure SQL, sec. 5)."""
import glob
import pathlib
import sqlite3

import pytest

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "migrations"

EXPECTED_MINIMUM_VIABLE_TABLES = {
    # spec sec. 63 — first tranche
    "dim_plant",
    "dim_line",
    "dim_process",
    "dim_product_cluster",
    "dim_product",
    "fact_production_lot",
    "fact_lot_process",
    "fact_process_observation",
    "fact_quality_test",
    "fact_eea_state",
    "fact_product_sales",
    "fact_ptsa_state",
    # second tranche
    "dim_trend",
    "bridge_cluster_trend",
    "fact_design_project",
    "fact_design_option",
    "fact_prototype",
    "fact_design_decision",
    "bridge_design_process_requirement",
}


@pytest.fixture()
def migrated_conn():
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys=ON;")
    for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
        con.executescript(pathlib.Path(path).read_text())
    yield con
    con.close()


def test_migrations_run_in_order_without_fk_errors(migrated_conn):
    tables = {
        row[0]
        for row in migrated_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    missing = EXPECTED_MINIMUM_VIABLE_TABLES - tables
    assert not missing, f"minimum viable release tables missing: {missing}"


def test_no_actuation_tables_or_endpoints_in_schema(migrated_conn):
    tables = {
        row[0]
        for row in migrated_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    forbidden_markers = ("setpoint", "actuat", "plc_write", "command_execute")
    offending = [t for t in tables if any(marker in t.lower() for marker in forbidden_markers)]
    assert not offending, f"forbidden actuation-related tables found: {offending}"
