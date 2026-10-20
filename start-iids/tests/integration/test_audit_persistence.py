"""Stage 9 checklist items "Lineage PASS" / "Data quality PASS" (spec sec.
65): DataQualityFinding objects and lineage edges must actually reach
audit_data_quality/audit_lineage, not just exist as schema (sec. 49: "an
error must be persisted, never silently swallowed")."""
import glob
import pathlib

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

from src.core.quality.persistence import record_finding, record_lineage
from src.engines.errors import DataQualityFinding, Severity

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parents[2] / "sql" / "migrations"


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


def test_data_quality_finding_round_trips(engine):
    finding = DataQualityFinding(
        dataset_name="fact_production_lot",
        record_key="LOT-1",
        check_code="missing_required_field",
        severity=Severity.BLOCKER,
        passed=False,
        observed_value=None,
        expected_rule="lot_id must not be blank",
        calc_run_id="RUN-1",
    )
    with engine.begin() as conn:
        record_finding(conn, dq_id=1, finding=finding)

    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM audit_data_quality WHERE dq_id = 1")).mappings().one()
    assert row["severity"] == "BLOCKER"
    assert row["passed"] == 0
    assert row["record_key"] == "LOT-1"
    assert row["expected_rule"] == "lot_id must not be blank"


def test_engine_error_to_finding_persists_through_the_same_path(engine):
    from src.engines.errors import EngineError, ErrorCategory

    err = EngineError(ErrorCategory.MISSING_COEFFICIENT, "EL_EX not found", record_key="LOT-2")
    finding = err.to_finding(dataset_name="fact_eea_state", calc_run_id="RUN-2")

    with engine.begin() as conn:
        record_finding(conn, dq_id=2, finding=finding)

    with engine.connect() as conn:
        row = conn.execute(text("SELECT * FROM audit_data_quality WHERE dq_id = 2")).mappings().one()
    assert row["check_code"] == "MISSING_COEFFICIENT"
    assert row["calc_run_id"] == "RUN-2"


def test_lineage_resolves_a_mart_row_back_to_its_source_fact(engine):
    """sec. 45: mv_intelligent_industry_state is a rebuildable read-optimization
    view, not the system of record -- lineage must resolve any of its rows back
    to the core fact tables that produced it."""
    with engine.begin() as conn:
        record_lineage(
            conn, lineage_id=1,
            target_table="mv_intelligent_industry_state", target_pk="LOT-1",
            source_table="fact_production_lot", source_pk="LOT-1",
            calc_run_id="RUN-1",
        )
        record_lineage(
            conn, lineage_id=2,
            target_table="mv_intelligent_industry_state", target_pk="LOT-1",
            source_table="fact_eea_state", source_pk="1",
            calc_run_id="RUN-1", transformation_id="mv_intelligent_industry_state",
        )

    with engine.connect() as conn:
        sources = conn.execute(
            text(
                "SELECT source_table, source_pk FROM audit_lineage "
                "WHERE target_table = :t AND target_pk = :pk ORDER BY source_table"
            ),
            {"t": "mv_intelligent_industry_state", "pk": "LOT-1"},
        ).all()
    assert [(r.source_table, r.source_pk) for r in sources] == [
        ("fact_eea_state", "1"),
        ("fact_production_lot", "LOT-1"),
    ]
