-- Raw -> Staging landing for the Edge->Cloud collector (spec sec. 34, ADR-004,
-- ADR-021). Source-agnostic: every contract in config/source_mappings/ lands
-- here regardless of its (currently unknown, P0-03) real field list, so this
-- schema does not need to change once real field names arrive per source.
--
-- Layering (ADR-004): raw_* is the append-only batch receipt; stg_* holds one
-- parsed/validated record per row (still source-shaped, pre-promotion). No
-- engine or API reads from either directly (sec. 61) -- promotion into the
-- dim_*/fact_* core is a separate, per-contract step once a source's real
-- field list is complete enough to populate a core table's required columns.

CREATE TABLE raw_ingestion_batch (
    batch_id            VARCHAR(128) PRIMARY KEY,
    contract_id         VARCHAR(64) NOT NULL,
    source_system       VARCHAR(64) NOT NULL,
    ingested_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    record_count        INTEGER NOT NULL,
    rejected_count      INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE stg_ingestion_record (
    stg_record_id       BIGINT PRIMARY KEY,
    batch_id            VARCHAR(128) NOT NULL REFERENCES raw_ingestion_batch(batch_id),
    contract_id         VARCHAR(64) NOT NULL,
    dedup_key           VARCHAR(512) NOT NULL,
    payload_json        TEXT NOT NULL,
    promoted_to_core    BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE (contract_id, dedup_key)
);
-- The UNIQUE constraint is the storage-level backstop for sec. 33 idempotence;
-- the collector (src/ingestion/edge/collector.py) already deduplicates
-- in-batch before a row reaches here.
