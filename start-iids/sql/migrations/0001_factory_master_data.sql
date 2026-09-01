-- Factory / Organization Shadow — master data.
-- Spec ref: sec. 10.1-10.4. Reference SQL (PostgreSQL-compatible logical contract);
-- translate types for Azure SQL without changing semantics, PK/FK or constraints.

CREATE TABLE dim_plant (
    plant_id            VARCHAR(32) PRIMARY KEY,
    plant_name          VARCHAR(255) NOT NULL,
    site_code           VARCHAR(64) UNIQUE,
    active_from         DATE,
    active_to           DATE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_line (
    line_id             VARCHAR(64) PRIMARY KEY,
    plant_id            VARCHAR(32) NOT NULL REFERENCES dim_plant(plant_id),
    line_name           VARCHAR(255) NOT NULL,
    area_type           VARCHAR(16),
    active_from         DATE,
    active_to           DATE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    CHECK (area_type IN ('MTS','MTO','OTHER') OR area_type IS NULL)
);

CREATE TABLE dim_process (
    process_id          VARCHAR(64) PRIMARY KEY,
    process_name        VARCHAR(255) NOT NULL,
    process_family      VARCHAR(64) NOT NULL,
    mts_mto_class       VARCHAR(16),
    sequence_group      VARCHAR(64),
    CHECK (mts_mto_class IN ('MTS','MTO','OTHER') OR mts_mto_class IS NULL)
);

-- process_family seed values are ARCH (spec sec. 10.3) and must be mapped to real
-- processes by the plant during Stage 1 onboarding; see scripts/seed_reference_data.py.

CREATE TABLE dim_equipment (
    equipment_id        VARCHAR(64) PRIMARY KEY,
    line_id             VARCHAR(64) NOT NULL REFERENCES dim_line(line_id),
    process_id          VARCHAR(64) REFERENCES dim_process(process_id),
    equipment_name      VARCHAR(255),
    asset_class         VARCHAR(128),
    source_asset_code   VARCHAR(128),
    active_from         DATE,
    active_to           DATE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE
);
