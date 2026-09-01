"""Cloud-side staging write path for a collected Edge batch (spec sec. 34.2,
ADR-004, ADR-021).

Lands a `CollectedBatch` (src/ingestion/edge/collector.py) into the
source-agnostic `raw_ingestion_batch`/`stg_ingestion_record` tables
(migration 0011) and persists every rejection as an `audit_data_quality`
finding (sec. 29.3, via `src/core/quality/persistence.py` — never silently
dropped). Promotion from staging into a specific `dim_*`/`fact_*` core table
is deliberately NOT done here: it is a per-contract mapping that needs each
source's complete real field list (P0-03), which this corpus does not have
yet (ADR-021) — writing here stops at the layer sec. 61's raw->staging->core
rule says is safe to reach without it.
"""
from __future__ import annotations

import json

from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.core.quality.persistence import record_finding
from src.ingestion.contracts import DataContract
from src.ingestion.edge.collector import CollectedBatch


def write_batch_to_staging(
    conn: Connection, batch_id: str, contract: DataContract, batch: CollectedBatch,
) -> None:
    """One `raw_ingestion_batch` receipt row, one `stg_ingestion_record` row per
    accepted record, and one `audit_data_quality` row per rejected finding."""
    conn.execute(
        text(
            "INSERT INTO raw_ingestion_batch "
            "(batch_id, contract_id, source_system, record_count, rejected_count) "
            "VALUES (:batch_id, :contract_id, :source_system, :record_count, :rejected_count)"
        ),
        {
            "batch_id": batch_id, "contract_id": contract.contract_id,
            "source_system": contract.source_system,
            "record_count": len(batch.accepted), "rejected_count": len(batch.rejected),
        },
    )

    # A dedup key field not in `contract.fields` (e.g. the bare timestamp
    # field) survives into the accepted record under its own source name —
    # see collect()'s same fallback.
    dedup_key_target_names = [
        contract.fields[k].target if k in contract.fields else k for k in contract.dedup_key
    ]
    for i, record in enumerate(batch.accepted):
        # dedup_key was computed on the source-named record in collect(); the
        # record here is already target-renamed, so re-key on the same values
        # via each dedup key field's target name.
        target_dedup_key = tuple(record.get(t) for t in dedup_key_target_names)
        conn.execute(
            text(
                "INSERT INTO stg_ingestion_record "
                "(stg_record_id, batch_id, contract_id, dedup_key, payload_json) "
                "VALUES (:stg_record_id, :batch_id, :contract_id, :dedup_key, :payload_json)"
            ),
            {
                "stg_record_id": hash((batch_id, i)) & 0x7FFFFFFFFFFF,
                "batch_id": batch_id, "contract_id": contract.contract_id,
                "dedup_key": "|".join(str(v) for v in target_dedup_key),
                "payload_json": json.dumps(record, default=str),
            },
        )

    for i, finding in enumerate(batch.rejected):
        record_finding(conn, dq_id=hash((batch_id, "reject", i)) & 0x7FFFFFFFFFFF, finding=finding)
