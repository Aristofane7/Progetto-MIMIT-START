"""Stage 9 checklist "Data quality PASS" (spec sec. 65) needs more than
"the blocker queries are syntactically valid SQL" (already covered by
test_quality_check_queries_are_valid_sql.py) -- it needs proof they actually
flag a real violation and stay silent on clean data. A vacuously-true-or-
false WHERE clause would pass the syntax-only test and still be useless.
"""
import glob
import pathlib
import re
import sqlite3

import pytest

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "migrations"
QUALITY_CHECKS_FILE = (
    pathlib.Path(__file__).resolve().parents[2] / "sql" / "quality_checks" / "blocker_rules.sql"
)


def _statement(index: int) -> str:
    without_comments = re.sub(r"--.*", "", QUALITY_CHECKS_FILE.read_text())
    statements = [s.strip() for s in without_comments.split(";") if s.strip()]
    return statements[index]


@pytest.fixture()
def conn():
    con = sqlite3.connect(":memory:")
    for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
        con.executescript(pathlib.Path(path).read_text())
    yield con
    con.close()


def test_rule3_flags_a_blank_lot_id(conn):
    conn.execute(
        "INSERT INTO dim_plant (plant_id, plant_name) VALUES ('D060', 'Plant D060')"
    )
    conn.execute(
        "INSERT INTO dim_product_cluster (cluster_id, cluster_version) VALUES (1, 'V1')"
    )
    conn.execute(
        "INSERT INTO dim_product (product_id, cluster_id, cluster_version) VALUES ('P1', 1, 'V1')"
    )
    conn.execute(
        "INSERT INTO fact_production_lot (lot_id, product_id, plant_id, start_ts, scenario) "
        "VALUES ('', 'P1', 'D060', '2026-01-01', 'CURRENT')"
    )
    assert conn.execute(_statement(2)).fetchall() != []  # rule 3: blank/missing lot_id


def test_rule3_is_silent_on_a_clean_lot(conn):
    conn.execute(
        "INSERT INTO dim_plant (plant_id, plant_name) VALUES ('D060', 'Plant D060')"
    )
    conn.execute(
        "INSERT INTO dim_product_cluster (cluster_id, cluster_version) VALUES (1, 'V1')"
    )
    conn.execute(
        "INSERT INTO dim_product (product_id, cluster_id, cluster_version) VALUES ('P1', 1, 'V1')"
    )
    conn.execute(
        "INSERT INTO fact_production_lot (lot_id, product_id, plant_id, start_ts, scenario) "
        "VALUES ('LOT-1', 'P1', 'D060', '2026-01-01', 'CURRENT')"
    )
    assert conn.execute(_statement(2)).fetchall() == []


def test_rule4_flags_a_coefficient_under_a_non_approved_set(conn):
    conn.execute(
        "INSERT INTO dim_coefficient_set (coefficient_set_id, status) VALUES ('SET-1', 'DRAFT')"
    )
    conn.execute(
        "INSERT INTO dim_coefficient (coefficient_id, coefficient_set_id, domain, code, "
        "coefficient_value, coefficient_unit) VALUES ('C1', 'SET-1', 'EFA', 'EL_EX', 1.0, 'MJ/kWh')"
    )
    assert conn.execute(_statement(3)).fetchall() != []  # rule 4: not APPROVED


def test_rule4_is_silent_once_the_set_is_approved(conn):
    conn.execute(
        "INSERT INTO dim_coefficient_set (coefficient_set_id, status) VALUES ('SET-1', 'APPROVED')"
    )
    conn.execute(
        "INSERT INTO dim_coefficient (coefficient_id, coefficient_set_id, domain, code, "
        "coefficient_value, coefficient_unit) VALUES ('C1', 'SET-1', 'EFA', 'EL_EX', 1.0, 'MJ/kWh')"
    )
    assert conn.execute(_statement(3)).fetchall() == []


def test_rule6_flags_a_lot_referencing_a_nonexistent_product(conn):
    # No PRAGMA foreign_keys=ON here: the point of this reference query (sec.
    # 29.3) is to catch exactly the drift FK enforcement is supposed to
    # prevent -- e.g. a bulk load path, or a target engine, where it wasn't on.
    conn.execute(
        "INSERT INTO dim_plant (plant_id, plant_name) VALUES ('D060', 'Plant D060')"
    )
    conn.execute(
        "INSERT INTO fact_production_lot (lot_id, product_id, plant_id, start_ts, scenario) "
        "VALUES ('LOT-1', 'GHOST-PRODUCT', 'D060', '2026-01-01', 'CURRENT')"
    )
    assert conn.execute(_statement(5)).fetchall() != []  # rule 6: referential integrity
