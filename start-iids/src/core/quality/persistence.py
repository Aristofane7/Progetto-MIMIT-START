"""Persist audit trail rows. Spec ref: sec. 29 (data quality), sec. 44/45
(lineage), sec. 49 ("an error must be persisted, never silently swallowed").

`src/engines/errors.py::DataQualityFinding` and the "IIDS is a rebuildable
read-optimization view, full lineage always resolves back to `audit_lineage`"
rule (sec. 45) both describe *what* must be recorded; this module is *how* —
a thin, explicit INSERT, no ORM, matching the SQLAlchemy Core style already
used by `src/api/repository.py`. Never called from `src/api/` (read-only).
"""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.engines.errors import DataQualityFinding


def record_finding(conn: Connection, dq_id: int, finding: DataQualityFinding) -> None:
    conn.execute(
        text(
            """
            INSERT INTO audit_data_quality
                (dq_id, dataset_name, record_key, check_code, severity, passed,
                 observed_value, expected_rule, calc_run_id)
            VALUES
                (:dq_id, :dataset_name, :record_key, :check_code, :severity, :passed,
                 :observed_value, :expected_rule, :calc_run_id)
            """
        ),
        {
            "dq_id": dq_id,
            "dataset_name": finding.dataset_name,
            "record_key": finding.record_key,
            "check_code": finding.check_code,
            "severity": finding.severity.value,
            "passed": finding.passed,
            "observed_value": finding.observed_value,
            "expected_rule": finding.expected_rule,
            "calc_run_id": finding.calc_run_id,
        },
    )


def record_lineage(
    conn: Connection,
    lineage_id: int,
    *,
    target_table: str,
    target_pk: str,
    source_table: str,
    source_pk: str,
    calc_run_id: str | None = None,
    transformation_id: str | None = None,
) -> None:
    conn.execute(
        text(
            """
            INSERT INTO audit_lineage
                (lineage_id, target_table, target_pk, source_table, source_pk,
                 transformation_id, calc_run_id)
            VALUES
                (:lineage_id, :target_table, :target_pk, :source_table, :source_pk,
                 :transformation_id, :calc_run_id)
            """
        ),
        {
            "lineage_id": lineage_id,
            "target_table": target_table,
            "target_pk": target_pk,
            "source_table": source_table,
            "source_pk": source_pk,
            "transformation_id": transformation_id,
            "calc_run_id": calc_run_id,
        },
    )
