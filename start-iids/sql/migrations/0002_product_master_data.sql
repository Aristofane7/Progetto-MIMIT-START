-- Product / Portfolio Information Shadow — master data.
-- Spec ref: sec. 10.5-10.8.
-- Rule (sec. 10.6): commercial performance never enters cluster classification.
-- OR6.8 clusters on intrinsic attributes only; sales are joined ex post
-- (see fact_product_sales / fact_cluster_performance in 0006).

CREATE TABLE dim_product_cluster (
    cluster_id                  INTEGER NOT NULL,
    cluster_version             VARCHAR(64) NOT NULL,
    dominant_shape              VARCHAR(128),
    dominant_dimension          VARCHAR(128),
    dominant_thickness          VARCHAR(128),
    dominant_slip_class         VARCHAR(128),
    dominant_effect             VARCHAR(128),
    dominant_colour             VARCHAR(128),
    balance_score               NUMERIC(12,8),
    coherence_score             NUMERIC(12,8),
    separation_score            NUMERIC(12,8),
    business_relevance_score    NUMERIC(12,8),
    cqs                         NUMERIC(12,8),
    valid_from                  DATE,
    valid_to                    DATE,
    is_current                  BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (cluster_id, cluster_version)
);
-- The initial version must load the 22 clusters documented in OR6.8 (SRC-RP68).

CREATE TABLE dim_product (
    product_id              VARCHAR(128) PRIMARY KEY,
    product_name            VARCHAR(255),
    cluster_id              INTEGER,
    cluster_version         VARCHAR(64),
    shape                   VARCHAR(128),
    dimension_class         VARCHAR(64),
    format_mm               VARCHAR(64),
    thickness_mm            NUMERIC(12,4),
    slip_class              VARCHAR(64),
    surface_effect          VARCHAR(128),
    finish                  VARCHAR(128),
    colour_class            VARCHAR(128),
    mass_kg_m2              NUMERIC(14,6),
    product_status          VARCHAR(32),
    source_product_code     VARCHAR(128),
    valid_from              DATE,
    valid_to                DATE,
    is_current              BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (cluster_id, cluster_version)
        REFERENCES dim_product_cluster(cluster_id, cluster_version)
);

CREATE TABLE dim_ptsa_type (
    product_type_id         VARCHAR(64) PRIMARY KEY,
    description             VARCHAR(255),
    thickness_mm            NUMERIC(12,4),
    mass_kg_m2              NUMERIC(14,6),
    declared_unit           VARCHAR(64),
    epd_reference           VARCHAR(255),
    default_plant_id        VARCHAR(32) REFERENCES dim_plant(plant_id),
    valid_from              DATE,
    valid_to                DATE
);
-- Initial load: T1 = 7.4 mm, T2 = 8.2 mm, T3 = 20.0 mm (spec sec. 10.7).

CREATE TABLE bridge_product_ptsa_type (
    product_id          VARCHAR(128) NOT NULL REFERENCES dim_product(product_id),
    product_type_id     VARCHAR(64) NOT NULL REFERENCES dim_ptsa_type(product_type_id),
    valid_from          DATE NOT NULL,
    valid_to            DATE,
    mapping_method      VARCHAR(64),
    mapping_confidence  VARCHAR(8),
    PRIMARY KEY (product_id, product_type_id, valid_from)
);
