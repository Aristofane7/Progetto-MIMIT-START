-- P-TSA / P-TSI persisted results.
-- Spec ref: sec. 25.

CREATE TABLE fact_ptsa_state (
    ptsa_state_id            BIGINT PRIMARY KEY,
    calc_run_id              VARCHAR(128) NOT NULL REFERENCES audit_calc_run(calc_run_id),
    period_start             TIMESTAMP NOT NULL,
    period_end               TIMESTAMP NOT NULL,
    product_type_id          VARCHAR(64) REFERENCES dim_ptsa_type(product_type_id),
    product_id               VARCHAR(128) REFERENCES dim_product(product_id),
    lot_id                   VARCHAR(128) REFERENCES fact_production_lot(lot_id),
    plant_id                 VARCHAR(32) REFERENCES dim_plant(plant_id),

    scr_raw_material         NUMERIC(20,8),
    scr_finished_product     NUMERIC(20,8),
    scr_glaze                NUMERIC(20,8),

    psi_energy               NUMERIC(20,8),
    psi_material              NUMERIC(20,8),
    psi_throughput           NUMERIC(20,8),

    ocr_flexural             NUMERIC(20,8),
    ocr_breaking_load        NUMERIC(20,8),
    ocr_surface              NUMERIC(20,8),

    ioai                     NUMERIC(20,8),
    opi                      NUMERIC(20,8),
    tqi                      NUMERIC(20,8),

    p_tsi_z                  NUMERIC(20,8),
    p_tsi_5                  NUMERIC(20,8),
    tii                      NUMERIC(20,8),

    weight_set_id            VARCHAR(64) REFERENCES dim_weight_set(weight_set_id),
    data_quality_score       NUMERIC(12,8)
);
-- Rule (sec. 24.10): tii is computed on p_tsi_5 by default (tii_base_variant =
-- P_TSI_5), never automatically on the z-score variant, whose denominator can be
-- zero or negative.
