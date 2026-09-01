-- Lot bridge, process route, observations, quality tests.
-- Spec ref: sec. 8 (lot_id as canonical hinge), sec. 10.9-10.13.

CREATE TABLE fact_production_lot (
    lot_id              VARCHAR(128) PRIMARY KEY,
    product_id          VARCHAR(128) NOT NULL REFERENCES dim_product(product_id),
    plant_id            VARCHAR(32) NOT NULL REFERENCES dim_plant(plant_id),
    start_ts            TIMESTAMP NOT NULL,
    end_ts              TIMESTAMP,
    output_m2           NUMERIC(18,6),
    output_pcs          NUMERIC(18,3),
    output_kg           NUMERIC(18,6),
    quality_grade       VARCHAR(64),
    scenario            VARCHAR(16) NOT NULL,
    source_lot_code     VARCHAR(128),
    source_system       VARCHAR(64),
    ingestion_ts        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (scenario IN ('HISTORICAL','CURRENT'))
);
-- Rule (sec. 8.2): a lot is associated with exactly one product_id in v1. If a lot
-- spans multiple products, introduce bridge_lot_product via ADR — never overload
-- product_id.

CREATE TABLE fact_lot_process (
    lot_process_id      BIGINT PRIMARY KEY,
    lot_id              VARCHAR(128) NOT NULL REFERENCES fact_production_lot(lot_id),
    process_id          VARCHAR(64) NOT NULL REFERENCES dim_process(process_id),
    line_id             VARCHAR(64) NOT NULL REFERENCES dim_line(line_id),
    equipment_id        VARCHAR(64) REFERENCES dim_equipment(equipment_id),
    sequence_no         INTEGER NOT NULL,
    start_ts            TIMESTAMP NOT NULL,
    end_ts              TIMESTAMP,
    input_qty           NUMERIC(18,6),
    output_qty          NUMERIC(18,6),
    qty_unit            VARCHAR(32),
    source_system       VARCHAR(64),
    UNIQUE (lot_id, sequence_no)
);

CREATE TABLE dim_variable (
    variable_code       VARCHAR(128) PRIMARY KEY,
    description         VARCHAR(255) NOT NULL,
    domain              VARCHAR(32) NOT NULL,
    canonical_unit      VARCHAR(32),
    aggregation_rule    VARCHAR(16),
    expected_min        NUMERIC(24,8),
    expected_max        NUMERIC(24,8),
    accounting_owner    VARCHAR(16),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (aggregation_rule IN ('SUM','AVG','MIN','MAX','LAST','NONE')),
    CHECK (accounting_owner IN ('EFA','ECOFA','SFA','TEI','PTSA','DIAGNOSTIC') OR accounting_owner IS NULL)
);
-- accounting_owner does NOT restrict which engine may read the raw datum; it only
-- means the equivalent accounting entry must not be duplicated (sec. 10.11, sec. 30).

CREATE TABLE fact_process_observation (
    observation_id      BIGINT PRIMARY KEY,
    lot_process_id      BIGINT REFERENCES fact_lot_process(lot_process_id),
    equipment_id        VARCHAR(64) REFERENCES dim_equipment(equipment_id),
    variable_code       VARCHAR(128) NOT NULL REFERENCES dim_variable(variable_code),
    source_ts           TIMESTAMP NOT NULL,
    ingestion_ts        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    value_num           NUMERIC(28,10),
    value_text          VARCHAR(512),
    original_unit       VARCHAR(32),
    canonical_value     NUMERIC(28,10),
    canonical_unit      VARCHAR(32),
    source_system       VARCHAR(64) NOT NULL,
    quality_flag        VARCHAR(32) NOT NULL DEFAULT 'VALID',
    confidence          VARCHAR(8),
    UNIQUE (source_system, variable_code, source_ts, equipment_id, lot_process_id)
);
-- The UNIQUE constraint is the idempotence/dedup key referenced in sec. 33.

CREATE TABLE fact_quality_test (
    quality_test_id         BIGINT PRIMARY KEY,
    lot_id                  VARCHAR(128) REFERENCES fact_production_lot(lot_id),
    prototype_id            VARCHAR(128),
    test_code               VARCHAR(128) NOT NULL,
    measured_value          NUMERIC(24,8),
    measured_text           VARCHAR(512),
    unit                    VARCHAR(32),
    acceptance_threshold    NUMERIC(24,8),
    threshold_operator      VARCHAR(8),
    pass_flag               BOOLEAN,
    test_ts                 TIMESTAMP NOT NULL,
    source_system           VARCHAR(64),
    method_reference        VARCHAR(255)
);
