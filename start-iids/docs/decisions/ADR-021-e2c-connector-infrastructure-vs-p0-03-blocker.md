# ADR-021 — E2C connector infrastructure built; P0-03 (real source field names) confirmed a genuine external blocker

**Status:** ACCEPTED — infrastructure implemented; P0-03 itself remains OPEN pending real IT-provided field/table names

## Context
Issue #3 ("[P0-03] Connettori live E2C/MES/SCADA/ERP/HR/LIMS + source mapping
reali") had been closed as completed, linked to a merged PR that (per its own
description, ADR-014) is the unrelated synthetic Power BI dataset work and
explicitly does not close #3. The issue was reopened.

Before assuming P0-03 was another "hidden in the repo" case like the ones
resolved by ADR-018/ADR-020, the following documents were read in full for
real SAP/MES/SCADA/HR/LIMS table/field/tag names:
- `RP6.6 Report di progettazione dell'Architettura Edge to Cloud_30-09-24.pdf`
- `RP 7.1 Report di collaudo piattaforma E2C_30-04-25.pdf`
- `RP6.7 Report di Progettazione della Intelligent Factory_30-09-24.pdf`
- `RP 7.2 Performance testing della Intelligent Factory_30-04-25.pdf`

All four are architecture-design and UAT/performance narratives. They use only
generic system-class names ("MES", "ERP", "BI", "SCADA") and never a real
vendor table, column, or tag name. Implementation spec sec. 34.3's benchmark
table is itself a verbatim citation of RP6.6's own table, so it adds nothing.
Unlike the SRC-TEI-EFA-EcoFA-SFA / RP7.3 / RP7.4 cases, this is a genuine
external blocker: the real endpoints, credentials, and field names have to
come from IT/plant systems this environment has no access to (spec sec. 64 —
never fabricate input to force a match).

## Decision
Build everything sec. 34 (Edge→Cloud) and ADR-004 (raw→staging→core→mart)
allow without live access, and leave the rest explicitly blocked:

1. **Generic Edge collector** (`src/ingestion/edge/collector.py`) — implements
   sec. 34.1's acquisition/preprocessing/validation/filtering/buffering/
   transmission on top of the existing `src/ingestion/contracts.py` mechanism
   (`validate_record`, `compute_dedup_key`). Source-agnostic: any iterable of
   raw dicts in, a `CollectedBatch` (accepted, renamed to contract target
   fields; rejected, as `DataQualityFinding`s, sec. 29.3 — never silently
   dropped) out.
2. **Source-agnostic Cloud staging landing** — migration `0011_ingestion_raw_staging.sql`
   adds `raw_ingestion_batch` (one receipt row per batch) and
   `stg_ingestion_record` (one JSON-payload row per accepted record, `UNIQUE
   (contract_id, dedup_key)` — sec. 33 idempotence enforced at the storage
   layer, not just in-batch) per ADR-004's explicit sanction to introduce
   `raw_*`/`stg_*` tables "per-source as real connectors are built."
   `src/ingestion/edge/cloud_writer.py::write_batch_to_staging` lands a
   `CollectedBatch` there and persists every rejection via
   `src/core/quality/persistence.py::record_finding`.
3. **Four new draft data contracts** (`config/source_mappings/`):
   `erp_economic_v1.yaml`, `hr_social_v1.yaml`,
   `scada_process_observation_v1.yaml`, `lims_quality_v1.yaml`. Source-side
   field names are explicit `TBD_*` placeholders (never guessed real names,
   sec. 64) but target fields are grounded exactly in what the already-built
   consumers need: `EcoFAPeriodFlows`/`SFAPeriodFlows` engine inputs,
   `fact_process_observation`, `fact_quality_test` columns — the same
   "pre-shaped but source-blocked" pattern the pre-existing
   `MES_PRODUCTION_V1` contract already established.

## What remains blocked (P0-03 itself)
- Real SAP/MES/SCADA/HR/LIMS endpoint addresses, credentials, and table/field
  names — must come from IT/plant systems, not from this corpus.
- `audit_source_mapping` population with real mappings — needs the above.
- Promotion from `stg_ingestion_record` into specific `dim_*`/`fact_*` core
  rows — deliberately not implemented here; it is a per-contract mapping that
  needs each source's complete real field list, which the `TBD_*` contracts
  don't have yet. Writing stops at the layer sec. 61 says is safe to reach
  without it.

## Consequences
Once real field names are provided, closing P0-03 is: replace `TBD_*` with
real source field names in the four draft YAML contracts (plus
`mes_production_v1.yaml`'s own remaining placeholders, if any), point
`collect()`'s `raw_records` at the real endpoint/cursor, and add the
staging→core promotion step per source. No schema or engine-code change is
needed for that — the contract-driven design (sec. 27) already isolates the
mapping from the business logic.

## Tests
- `tests/unit/test_edge_collector.py` — 5 tests (accept+rename, blocker
  rejection not silently dropped, in-batch dedup, preprocess hook, mixed
  batch).
- `tests/integration/test_edge_cloud_writer.py` — 3 tests against an
  in-memory SQLite schema built from all migrations: staging + receipt
  creation, rejections reaching `audit_data_quality`, and duplicate-batch
  rejection via the storage-level `UNIQUE` constraint (`IntegrityError`).
- `tests/unit/test_draft_source_contracts.py` — all 4 draft contracts load,
  and each one's target fields exactly match its downstream consumer's
  expected field set.
