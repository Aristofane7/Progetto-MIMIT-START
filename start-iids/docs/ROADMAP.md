# ROADMAP — START Intelligent Industry Digital Shadow (IIDS)

Status snapshot of this implementation against the deployment stages (spec sec. 53)
and the v1 acceptance criteria (spec sec. 57). "This repository" = what agents can
verify by running `pytest` here; it does not include live connections to a real
plant's MES/SCADA/ERP/HR/LIMS systems, which requires IT-provided source mappings
(open item P0-03) and infrastructure this codebase does not own.

## Stage status

| Stage | Scope | Status |
|---|---|---|
| 0 — Foundation | repo layout, CI, feature flags, unit library | **DONE** |
| 1 — Master data | plant/line/process/equipment/product/cluster DDL | **DONE** (schema + loaders); real 13.251-product / 22-cluster CSV import is a data-loading exercise for whoever owns the RP6.8 export, not a code gap |
| 2 — Lot bridge | production lot / lot-process / product mapping | **DONE** (schema); real MES lot codes need contract mapping (P0-04) |
| 3 — Process observation | E2C/MES ingestion, canonical units | **PARTIAL** — data contract mechanism done (`src/ingestion/contracts.py`), one example contract (`MES_PRODUCTION_V1`); no live Edge/MES/SCADA connector is implemented (needs IT source mappings, P0-03) |
| 4 — EEA engines | TEI → EFA → EcoFA → SFA → EEA aggregation | **DONE** (formulas + engines + tests) + an aggregate plant/year path (`src/engines/eea/aggregate.py`, ADR-012) validated against 66 real data points from `data/reference/RP7.3_calculation_log.xlsx`. Coefficients (`COEFF_RP73_PROVISIONAL_2026`, real project data) and AHP weights (`EEA_AHP_RP73_1`) are loaded but `DRAFT` — source explicitly labeled provisional (P0-02 partially resolved: real data now exists, formal APPROVED sign-off still open) |
| 5 — Product intelligence | sales, cluster performance, trend | **DONE** (schema + CQS + trend classification + SCD2 catalog) |
| 6 — P-TSA | SCR/PsI/OCR/z-score/AHP/P-TSI/TII | **DONE** (engine + tests); z-score golden regression blocked on RP7.4 dataset (ADR-011 item 5) |
| 7 — Product Design workflow | project/option/prototype/test/decision | **DONE** (schema + state machine + decision enum) |
| 8 — Integrated mart | IIDS view, read-only API | **DONE** (`mv_intelligent_industry_state`, FastAPI read-only endpoints) |
| 9 — Validation | regression, audit, performance, UAT | **PARTIAL** — unit/integration/regression test suite in place; performance/UAT against real infrastructure is out of this repository's scope |

## Acceptance criteria (spec sec. 57) — status

1. Physical data via E2C or equivalent fixture — **PARTIAL** (contract mechanism ready, no live connector)
2. Data associated with plant — DONE
3. Data associated with line/process — DONE
4. Lot associated with product — DONE
5. Product associated with cluster — DONE
6. Historical state reconstructable — DONE (historical-replay repository queries, sec. 46)
7-10. TEI/EFA/EcoFA/SFA operational — DONE
11. EEA aggregates four contributions — DONE
12. TSI_norm computable with coherent baseline — DONE, and the fuller real RP7.3 `TSI_abs`/`TSI_rel`/`Phi`/`Psi`/`SA_w` variant (ADR-012) reproduces 66 real logged values (`tests/regression/test_rp73_calculation_log.py`)
13. Sales associable to product — DONE
14. Cluster performance available — DONE
15. Trend linkable to cluster — DONE
16. P-TSA computes SCR/PsI/OCR — DONE
17. P-TSI z computed — DONE
18. P-TSI scoring/AHP computed — DONE
19. TII computed on the appropriate (P_TSI_5) variant — DONE
20. Design project traceable end-to-end — DONE (schema + workflow validator)
21. Prototype test linked — DONE (schema: `fact_quality_test.prototype_id`)
22. Design decision auditable — DONE
23. IIDS view available — DONE
24. BI drill-down functioning — **NOT STARTED** (Power BI semantic model is a BI-tool artifact, sec. 38, out of this Python/SQL repository's scope; the read-only API + view provide the data it would consume)
25. No automatic actuation — DONE (structural: no write routes exist; CI greps for forbidden patterns)
26. Coefficient/version tracked — DONE (`dim_coefficient_set`, `dim_weight_set`)
27. calc_run reproducible — DONE (`audit_calc_run`, `make_calc_run_id`)
28. Data quality visible — DONE (`audit_data_quality`, blocker queries)
29. P0 unit conversion validated — DONE (`test_units_energy.py`)
30. Golden regression tests approved — **PARTIAL**: CQS (sec. 19.5), the P-TSA AHP-formula self-consistency check, and — the strongest evidence so far — 66 real, non-fabricated RP7.3 EEA+/TSI data points (`f_env`/`f_econ`/`f_soc`/`f_tech`/`SA_raw`/`Ex_ref`/`TSI_abs`/`TSI_rel`, ADR-012) all pass; the P-TSA z-score targets remain blocked on a real fixture (see ADR-011). "Approved" in the governance sense (sec. 61 decision log) still requires project-owner sign-off — these are test-suite passes, not formal approvals

## What was deliberately NOT built (FUTURE / out of scope, per spec)

- ARIMA forecasting, logistic success model, portfolio optimizer (sec. 36, ADR-009)
- Any actuation / Digital Twin closed loop (sec. 3, ADR-001)
- Live Edge/MES/SCADA/ERP/HR/LIMS connectors (require IT-provided field mappings, P0-03)
- Power BI semantic model artifact itself (sec. 38 — BI-tool-side work)
- Re-clustering pipeline running on a schedule (sec. 19.6 — cluster versions are imported on request)

## Next steps for whoever continues this work

1. Get the RP7.3 historical series consolidated, then have the project owner
   formally promote `COEFF_RP73_PROVISIONAL_2026` and `EEA_AHP_RP73_1` from
   `DRAFT` to `APPROVED` (never skip the review, never do this in code).
2. Resolve the `Psi`/`Ex_useful` open item (ADR-012) with the project owner —
   currently a reported, not derived, input.
3. Get IT to supply real MES/SCADA/ERP/HR/LIMS field names and complete
   `audit_source_mapping` + per-source YAML contracts (P0-03).
4. Resolve the five ADR-011 open items (TEI-J quality penalty, MTO powder
   pricing, `B_TILE`, cluster-trend thresholds, P-TSA z-score fixture) with the
   actual SRC-TEI/EFA/EcoFA/SFA/RP74 manual text and an owner sign-off.
5. Build the Power BI semantic model against `mv_intelligent_industry_state` /
   the read-only API (sec. 38).
6. Run the Stage 9 checklist (spec sec. 65) against a staging environment with
   real data before declaring v1 production-ready.
