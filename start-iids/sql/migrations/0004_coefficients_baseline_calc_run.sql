-- Coefficient registry, baseline management, calculation-run auditability.
-- Spec ref: sec. 11-13.

CREATE TABLE dim_coefficient_set (
    coefficient_set_id      VARCHAR(64) PRIMARY KEY,
    description             VARCHAR(255),
    reference_year          INTEGER,
    status                  VARCHAR(16) NOT NULL,
    approved_by             VARCHAR(255),
    approved_at             TIMESTAMP,
    CHECK (status IN ('DRAFT','APPROVED','RETIRED'))
);

CREATE TABLE dim_coefficient (
    coefficient_id          VARCHAR(128) NOT NULL,
    coefficient_set_id      VARCHAR(64) NOT NULL REFERENCES dim_coefficient_set(coefficient_set_id),
    domain                  VARCHAR(16) NOT NULL,
    code                    VARCHAR(128) NOT NULL,
    description             VARCHAR(255),
    coefficient_value       NUMERIC(28,12) NOT NULL,
    coefficient_unit        VARCHAR(64) NOT NULL,
    source                  VARCHAR(512),
    source_year             INTEGER,
    boundary                VARCHAR(32),
    method                  VARCHAR(32),
    confidence              VARCHAR(8),
    valid_from              DATE,
    valid_to                DATE,
    PRIMARY KEY (coefficient_id, coefficient_set_id),
    CHECK (domain IN ('EFA','ECOFA','SFA','TEI','PTSA'))
);
-- Rules (sec. 11.3): no production coefficient may be NULL; manual placeholder
-- values must never be loaded with status='APPROVED'; baseline and current runs
-- must share the same coefficient_set_id; a modification always creates a new
-- version (never retro-edit an APPROVED set); confidence uses A/B/C.

CREATE TABLE dim_baseline (
    baseline_id                 VARCHAR(64) PRIMARY KEY,
    baseline_name               VARCHAR(255) NOT NULL,
    baseline_year               INTEGER NOT NULL,
    plant_id                    VARCHAR(32) REFERENCES dim_plant(plant_id),
    functional_unit             VARCHAR(64) NOT NULL,
    coefficient_set_id          VARCHAR(64) NOT NULL REFERENCES dim_coefficient_set(coefficient_set_id),
    start_date                  DATE,
    end_date                    DATE,
    status                      VARCHAR(16) NOT NULL,
    notes                       TEXT,
    CHECK (status IN ('DRAFT','APPROVED','RETIRED'))
);
-- RP7.3 fixes 2017 as the Smart Factory vs Intelligent Factory reference baseline.

CREATE TABLE dim_weight_set (
    weight_set_id         VARCHAR(64) PRIMARY KEY,
    methodology           VARCHAR(64),
    version               VARCHAR(32),
    status                VARCHAR(16),
    consistency_ratio     NUMERIC(12,8),
    approved_by           VARCHAR(255),
    approved_at           TIMESTAMP
);

CREATE TABLE dim_weight (
    weight_set_id         VARCHAR(64) NOT NULL REFERENCES dim_weight_set(weight_set_id),
    dimension_code        VARCHAR(64) NOT NULL,
    metric_code           VARCHAR(64),
    weight_value          NUMERIC(18,12) NOT NULL,
    PRIMARY KEY (weight_set_id, dimension_code, metric_code)
);

CREATE TABLE audit_calc_run (
    calc_run_id              VARCHAR(128) PRIMARY KEY,
    engine                   VARCHAR(32) NOT NULL,
    engine_version           VARCHAR(64) NOT NULL,
    code_commit              VARCHAR(64),
    baseline_id              VARCHAR(64) REFERENCES dim_baseline(baseline_id),
    coefficient_set_id       VARCHAR(64) REFERENCES dim_coefficient_set(coefficient_set_id),
    weight_set_id            VARCHAR(64),
    period_start             TIMESTAMP NOT NULL,
    period_end               TIMESTAMP NOT NULL,
    scenario                 VARCHAR(16),
    status                   VARCHAR(16) NOT NULL,
    started_at               TIMESTAMP NOT NULL,
    completed_at             TIMESTAMP,
    input_record_count       BIGINT,
    rejected_record_count    BIGINT,
    data_quality_score       NUMERIC(12,8),
    error_message            TEXT,
    CHECK (engine IN ('EFA','ECOFA','SFA','TEI','EEA','PTSA','PRODUCT_CLUSTER')),
    CHECK (status IN ('RUNNING','SUCCESS','FAILED','REJECTED'))
);
-- Reproducibility chain (sec. 13.2): result -> calc_run_id -> engine_version ->
-- git commit -> input window -> baseline -> coefficient set -> weight set -> data quality.
