-- Additive columns for the plant/year aggregate thermoeconomic model (ADR-012):
-- Ex_ref, SA_w (AHP-weighted SA), Phi, Psi, TSI_abs.
--
-- These are nullable and additive: existing lot/process-grain rows populated by
-- the granular TEI/EFA/EcoFA/SFA engines are unaffected and simply carry NULL
-- here. `tsi_norm` (already on this table) keeps the sec. 18.2 simple-ratio
-- semantics; `tsi_abs`/`tsi_rel` below is the fuller, RP7.3-verified variant —
-- see ADR-012 for why both exist. `tsi_rel` reuses the existing `tsi_norm`
-- column's slot conceptually but is NOT the same formula, so it gets its own
-- column rather than overloading `tsi_norm`.

ALTER TABLE fact_eea_state ADD COLUMN ex_ref_gj NUMERIC(28,8);
ALTER TABLE fact_eea_state ADD COLUMN sa_w_gj NUMERIC(28,8);
ALTER TABLE fact_eea_state ADD COLUMN phi NUMERIC(28,10);
ALTER TABLE fact_eea_state ADD COLUMN psi NUMERIC(28,10);
ALTER TABLE fact_eea_state ADD COLUMN tsi_abs NUMERIC(28,10);
ALTER TABLE fact_eea_state ADD COLUMN tsi_rel NUMERIC(28,10);
ALTER TABLE fact_eea_state ADD COLUMN weight_set_id VARCHAR(64) REFERENCES dim_weight_set(weight_set_id);
