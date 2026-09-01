-- Cross-cutting governance: double-counting control, source mapping registry,
-- data quality findings, lineage.
-- Spec ref: sec. 28-30, 44.

CREATE TABLE dim_accounting_map (
    accounting_term_id      VARCHAR(128) PRIMARY KEY,
    source_category         VARCHAR(128),
    description             VARCHAR(255),
    owning_module           VARCHAR(16) NOT NULL,
    physical_driver_first   BOOLEAN NOT NULL DEFAULT TRUE,
    fallback_module         VARCHAR(16),
    notes                   TEXT,
    CHECK (owning_module IN ('EFA','ECOFA','SFA','TEI'))
);
-- Rule (sec. 30.3): if a physical driver exists (e.g. LOGISTICS_TKM -> EFA), it
-- always wins over the economic proxy (LOGISTICS_EUR -> EcoFA only if TKM absent).

CREATE TABLE audit_source_mapping (
    source_system        VARCHAR(64) NOT NULL,
    source_field         VARCHAR(128) NOT NULL,
    target_entity        VARCHAR(128) NOT NULL,
    target_field         VARCHAR(128) NOT NULL,
    transformation_rule  TEXT,
    unit_rule             VARCHAR(255),
    valid_from           DATE NOT NULL,
    valid_to             DATE,
    approved_by          VARCHAR(255),
    PRIMARY KEY (source_system, source_field, target_entity, valid_from)
);

CREATE TABLE audit_data_quality (
    dq_id                   BIGINT PRIMARY KEY,
    dataset_name            VARCHAR(128) NOT NULL,
    record_key              VARCHAR(512),
    check_code              VARCHAR(128) NOT NULL,
    severity                VARCHAR(16) NOT NULL,
    passed                  BOOLEAN NOT NULL,
    observed_value          VARCHAR(512),
    expected_rule           TEXT,
    calc_run_id             VARCHAR(128),
    created_at              TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (severity IN ('INFO','WARNING','ERROR','BLOCKER'))
);

CREATE TABLE audit_lineage (
    lineage_id            BIGINT PRIMARY KEY,
    target_table          VARCHAR(128) NOT NULL,
    target_pk             VARCHAR(512) NOT NULL,
    source_table          VARCHAR(128) NOT NULL,
    source_pk             VARCHAR(512) NOT NULL,
    transformation_id     VARCHAR(128),
    calc_run_id           VARCHAR(128),
    created_at            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
