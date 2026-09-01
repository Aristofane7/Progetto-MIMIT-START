"""Ensures the reference blocker-rule queries (sec. 29.3) are at least valid,
executable SQL against the migrated schema — a cheap guard against sql drift when
column names change."""
import glob
import pathlib
import re
import sqlite3

import pytest

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "migrations"
QUALITY_CHECKS_FILE = (
    pathlib.Path(__file__).resolve().parents[2] / "sql" / "quality_checks" / "blocker_rules.sql"
)


def _split_statements(sql_text: str) -> list[str]:
    # Strip line comments, then split on statement-terminating semicolons.
    without_comments = re.sub(r"--.*", "", sql_text)
    return [s.strip() for s in without_comments.split(";") if s.strip()]


@pytest.fixture()
def migrated_conn():
    con = sqlite3.connect(":memory:")
    for path in sorted(glob.glob(str(MIGRATIONS_DIR / "*.sql"))):
        con.executescript(pathlib.Path(path).read_text())
    yield con
    con.close()


def test_all_blocker_queries_execute_without_error(migrated_conn):
    statements = _split_statements(QUALITY_CHECKS_FILE.read_text())
    assert len(statements) >= 7
    for statement in statements:
        migrated_conn.execute(statement).fetchall()
