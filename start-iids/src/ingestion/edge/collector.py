"""Generic Edge collector (spec sec. 34.1, issue #3, ADR-021).

Edge responsibilities per sec. 34.1 — acquisition, preprocessing, technical
validation, filtering, buffering, transmission of relevant data — mapped onto
this module as:

- **acquisition**: `raw_records`, any iterable of dicts (a DB cursor, a REST
  page, a CSV reader, ...) — deliberately pluggable, since a real live source
  (SAP/MES/SCADA/HR/LIMS endpoint) is P0-03, not part of this corpus (ADR-021).
- **preprocessing**: the optional `preprocess` hook (unit conversion, field
  renaming upstream of the contract) — sec. 27's own rule ("nessun agente deve
  codificare mapping direttamente dentro il business engine") means this stays
  a caller-supplied, contract-adjacent step, never engine code.
- **technical validation + filtering**: `validate_record` (already implemented
  in `src/ingestion/contracts.py`) — a record with a BLOCKER finding is
  rejected, never silently passed on (sec. 29.3).
- **buffering + dedup**: an in-memory batch, deduplicated by the contract's own
  `dedup_key` (sec. 33 idempotence) before anything is returned.
- **transmission**: the returned `CollectedBatch` is what a cloud-side writer
  (`src/ingestion/edge/cloud_writer.py`) lands into staging.

No network or database code lives here on purpose — this module is the part
of sec. 34 that is genuinely implementable without a live source.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from src.engines.errors import DataQualityFinding
from src.ingestion.contracts import DataContract, compute_dedup_key, validate_record


@dataclass(frozen=True)
class CollectedBatch:
    contract_id: str
    accepted: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[DataQualityFinding] = field(default_factory=list)


def collect(
    contract: DataContract,
    raw_records: Iterable[dict[str, Any]],
    *,
    preprocess: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> CollectedBatch:
    """Run one batch of raw records through acquisition -> ... -> transmission.

    Returns every accepted record renamed onto the contract's `target` field
    names (never partially applied — a rejected record contributes nothing to
    `accepted`), plus a `DataQualityFinding` per rejection (sec. 29.3).
    """
    accepted: list[dict[str, Any]] = []
    rejected: list[DataQualityFinding] = []
    seen_keys: set[tuple[Any, ...]] = set()

    for raw in raw_records:
        record = preprocess(raw) if preprocess else raw
        findings = validate_record(record, contract)
        if findings:
            rejected.extend(findings)
            continue

        dedup_key = compute_dedup_key(record, contract)
        if dedup_key in seen_keys:
            continue  # idempotent re-ingestion (sec. 33) — a no-op, not an error
        seen_keys.add(dedup_key)

        renamed = {spec.target: record.get(name) for name, spec in contract.fields.items()}
        # The timestamp field (sec. 27) isn't necessarily also listed under
        # `fields` (e.g. MES_PRODUCTION_V1 declares it only in `timestamp:`) —
        # carry it through under its own name so it survives into the target
        # record even when it has no separate FieldSpec/target of its own.
        if contract.timestamp.field not in contract.fields and contract.timestamp.field not in renamed:
            renamed[contract.timestamp.field] = record.get(contract.timestamp.field)
        accepted.append(renamed)

    return CollectedBatch(contract_id=contract.contract_id, accepted=accepted, rejected=rejected)
