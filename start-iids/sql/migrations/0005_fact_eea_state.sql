-- EEA+ / TSI persisted results.
-- Spec ref: sec. 18.3.

CREATE TABLE fact_eea_state (
    eea_state_id           BIGINT PRIMARY KEY,
    calc_run_id            VARCHAR(128) NOT NULL REFERENCES audit_calc_run(calc_run_id),
    plant_id               VARCHAR(32) NOT NULL REFERENCES dim_plant(plant_id),
    line_id                VARCHAR(64) REFERENCES dim_line(line_id),
    lot_id                 VARCHAR(128) REFERENCES fact_production_lot(lot_id),
    period_start           TIMESTAMP NOT NULL,
    period_end             TIMESTAMP NOT NULL,
    scenario               VARCHAR(16) NOT NULL,
    f_env_mj               NUMERIC(28,8),
    f_econ_mj              NUMERIC(28,8),
    f_soc_mj               NUMERIC(28,8),
    f_tech_mj              NUMERIC(28,8),
    sa_mj                  NUMERIC(28,8),
    f_env_gj               NUMERIC(28,8),
    f_econ_gj              NUMERIC(28,8),
    f_soc_gj               NUMERIC(28,8),
    f_tech_gj              NUMERIC(28,8),
    sa_gj                  NUMERIC(28,8),
    tsi_norm               NUMERIC(28,10),
    data_quality_score     NUMERIC(12,8)
);
-- Rule (sec. 18.4): tsi_norm is populated only when a baseline is available,
-- SA_historical != 0, and perimeter/FU/coefficient set match; otherwise tsi_norm
-- is NULL and the corresponding audit_data_quality row is flagged NON_COMPARABLE.
