-- Intelligent Industry Digital Shadow — integrated read state.
-- Spec ref: sec. 26 (ARCH). Grain: period + plant + lot + product (sec. 26.1).
--
-- IMPORTANT (sec. 45): this is a rebuildable read-optimization view, NOT the
-- system of record. `IIDS(t) = Query(CoreData, t)` — the underlying fact tables
-- remain the single source of truth and full lineage always resolves back to
-- them (audit_lineage).
--
-- Portability note: this file uses a plain `CREATE VIEW` as the logical contract.
-- Whether it is physically realized as a PostgreSQL `MATERIALIZED VIEW` (with an
-- explicit `REFRESH MATERIALIZED VIEW` job) or as an Azure SQL indexed view / ETL
-- snapshot table is an infrastructure decision outside this contract's scope.
--
-- ARCH joins (not literally specified by the spec, only the field list in 26.2):
--   * cluster performance is matched to the lot's product cluster by period
--     containment (lot start falls inside the cluster-performance period);
--   * the design decision surfaced is the most recent one for a design option
--     referencing the product's current cluster/version (best-effort linkage —
--     sec. 23's bridge_design_process_requirement is the authoritative link once
--     a given lot is produced from an explicit design option in later stages).

CREATE VIEW mv_intelligent_industry_state AS
SELECT
    lot.start_ts                                   AS period_start,
    COALESCE(lot.end_ts, lot.start_ts)              AS period_end,
    lot.plant_id                                    AS plant_id,
    lp.line_id                                      AS line_id,
    lot.lot_id                                      AS lot_id,
    lot.product_id                                  AS product_id,
    prod.cluster_id                                 AS cluster_id,
    prod.cluster_version                            AS cluster_version,

    eea.f_env_gj                                    AS f_env_gj,
    eea.f_econ_gj                                   AS f_econ_gj,
    eea.f_soc_gj                                    AS f_soc_gj,
    eea.f_tech_gj                                   AS f_tech_gj,
    eea.sa_gj                                       AS sa_gj,
    eea.tsi_norm                                    AS tsi_norm,

    ptsa.ioai                                       AS ioai,
    ptsa.opi                                        AS opi,
    ptsa.tqi                                        AS tqi,
    ptsa.p_tsi_z                                    AS p_tsi_z,
    ptsa.p_tsi_5                                    AS p_tsi_5,
    ptsa.tii                                        AS tii,

    sales.sales_m2                                  AS sales_m2,
    cperf.trend_class                               AS cluster_trend,
    ctrend.alignment_score                          AS trend_alignment,

    design_opt.design_project_id                    AS design_project_id,
    design_opt.design_option_id                     AS design_option_id,
    latest_decision.decision_code                   AS design_decision,

    COALESCE(eea.data_quality_score, ptsa.data_quality_score) AS data_quality_score,
    eea_run.coefficient_set_id                      AS coefficient_set_id,
    ptsa_run.weight_set_id                          AS weight_set_id,
    eea_run.baseline_id                             AS baseline_id,
    COALESCE(eea.calc_run_id, ptsa.calc_run_id)     AS calc_run_id

FROM fact_production_lot lot
LEFT JOIN fact_lot_process lp
    ON lp.lot_id = lot.lot_id AND lp.sequence_no = 1
LEFT JOIN dim_product prod
    ON prod.product_id = lot.product_id
LEFT JOIN fact_eea_state eea
    ON eea.lot_id = lot.lot_id
LEFT JOIN audit_calc_run eea_run
    ON eea_run.calc_run_id = eea.calc_run_id
LEFT JOIN fact_ptsa_state ptsa
    ON ptsa.lot_id = lot.lot_id
LEFT JOIN audit_calc_run ptsa_run
    ON ptsa_run.calc_run_id = ptsa.calc_run_id
LEFT JOIN fact_product_sales sales
    ON sales.product_id = lot.product_id
   AND lot.start_ts >= sales.period_start
   AND lot.start_ts <  sales.period_end
LEFT JOIN fact_cluster_performance cperf
    ON cperf.cluster_id = prod.cluster_id
   AND cperf.cluster_version = prod.cluster_version
   AND lot.start_ts >= cperf.period_start
   AND lot.start_ts <  cperf.period_end
LEFT JOIN bridge_cluster_trend ctrend
    ON ctrend.cluster_id = prod.cluster_id
   AND ctrend.cluster_version = prod.cluster_version
LEFT JOIN fact_design_option design_opt
    ON design_opt.reference_cluster_id = prod.cluster_id
   AND design_opt.reference_cluster_version = prod.cluster_version
LEFT JOIN fact_design_decision latest_decision
    ON latest_decision.design_option_id = design_opt.design_option_id
   AND latest_decision.decision_ts = (
        SELECT MAX(d2.decision_ts)
        FROM fact_design_decision d2
        WHERE d2.design_option_id = design_opt.design_option_id
   );
