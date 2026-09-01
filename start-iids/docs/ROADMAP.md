# ROADMAP — START Intelligent Industry Digital Shadow (IIDS)

**Last updated:** 2026-09-01 — v1 technical backbone merged into `main`
([PR #1](https://github.com/Aristofane7/Progetto-MIMIT-START/pull/1), squash
commit `39f2c7f`).

Status snapshot of this implementation against the deployment stages (spec sec. 53)
and the v1 acceptance criteria (spec sec. 57). "This repository" = what agents can
verify by running `pytest` here; it does not include live connections to a real
plant's MES/SCADA/ERP/HR/LIMS systems, which requires IT-provided source mappings
(open item P0-03) and infrastructure this codebase does not own.

## At a glance

- **27 / 30** v1 acceptance criteria (spec sec. 57) — **DONE**
- **3 / 30** — **PARTIAL** (E2C live connector, full golden-regression approval,
  BI drill-down — semantic model shipped, report pages need GUI authoring)
- **235 tests passing** (0 skipped — the last skip, P-TSA z-score, is
  resolved by ADR-020), 95% coverage on `src/`, CI green on `main`
- Stage 9 self-check (ADR-017): `python3 -m scripts.stage9_validation_checklist`
  reports **12 PASS / 5 PARTIAL / 4 BLOCKED** out of 21 checklist items (spec
  sec. 65) — a live, re-runnable number, not a hand-maintained assertion
- The real SRC-TEI/EFA/EcoFA/SFA manuals (repo-root PDFs) were found and read
  (ADR-018): EFA/EcoFA/SFA formulas confirmed exact; TEI-J's quality-penalty
  formula was wrong and is now fixed against the real manual text
- The RP7.3 narrative report (repo-root PDF) was found and read (ADR-019):
  `Psi`/`Ex_useful` confirmed as intentionally a directly-reported input in
  the beta methodology, closing that ADR-012 open item
- Real RP7.3 aggregate EEA+/TSI model (ADR-012) **validated against 66 real,
  non-fabricated data points**; its coefficient/weight sets are **APPROVED**
  by the project owner (ADR-013, 2026-09-01)
- The 22 real RP6.8 product clusters are loaded (ADR-015); the 13,251-product
  export with cluster assignment (issue #7) remains an external blocker, not
  a code gap — see `data/reference/README.md`
- Nothing in `src/` writes to the physical system — enforced structurally and
  by a CI guard (ADR-001)

## Stage status

| Stage | Scope | Status |
|---|---|---|
| 0 — Foundation | repo layout, CI, feature flags, unit library | **DONE** |
| 1 — Master data | plant/line/process/equipment/product/cluster DDL | **PARTIAL** — schema + loaders done; the 22 real RP6.8 clusters are now loaded (`data/reference/rp68_cluster_master.csv`, ADR-015); the 13.251-product export with cluster assignment (RP6.8 sec. 3.7) is an external blocker — not in this repository, not reconstructable from the report, needs whoever holds the raw RP6.8 deliverables |
| 2 — Lot bridge | production lot / lot-process / product mapping | **DONE** (schema); real MES lot codes need contract mapping (P0-04) |
| 3 — Process observation | E2C/MES ingestion, canonical units | **PARTIAL** — data contract mechanism done (`src/ingestion/contracts.py`), one example contract (`MES_PRODUCTION_V1`); no live Edge/MES/SCADA connector is implemented (needs IT source mappings, P0-03) |
| 4 — EEA engines | TEI → EFA → EcoFA → SFA → EEA aggregation | **DONE** (formulas + engines + tests) + an aggregate plant/year path (`src/engines/eea/aggregate.py`, ADR-012) validated against 66 real data points from `data/reference/RP7.3_calculation_log.xlsx`. Coefficients (`COEFF_RP73_PROVISIONAL_2026`) and AHP weights (`EEA_AHP_RP73_1`) are `APPROVED` as of 2026-09-01 (ADR-013) — P0-02 **resolved for the aggregate model**. The 4 real SRC-TEI/EFA/EcoFA/SFA manuals (repo root PDFs) were found and read (ADR-018): EFA/EcoFA/SFA formulas already matched exactly; TEI-J's quality-penalty formula was wrong (absolute-difference vs the manual's ratio shortfall) and is now fixed (`engine_version` 1.1.0). Granular coefficient *values* (`B_TILE`, `B_SDM`, `KAPPA_MTS`, etc.) remain `DRAFT`/test-only — the real coefficient library ("Tabella 2") every manual points to is not part of this corpus, an external blocker like issue #7's product export, not a code gap |
| 5 — Product intelligence | sales, cluster performance, trend | **DONE** (schema + CQS + trend classification + SCD2 catalog) |
| 6 — P-TSA | SCR/PsI/OCR/z-score/AHP/P-TSI/TII | **DONE** (engine + tests); z-score golden regression now real, validated against the RP7.4 report's own Tabelle 3-7 (ADR-020, issue #6) |
| 7 — Product Design workflow | project/option/prototype/test/decision | **DONE** (schema + state machine + decision enum) |
| 8 — Integrated mart | IIDS view, read-only API | **DONE** (`mv_intelligent_industry_state`, FastAPI read-only endpoints); Power BI semantic model **PARTIAL** — TMDL model + measures + CSV/SQL data-source switch shipped (`bi/powerbi/`, ADR-016); the 3 report pages (sec. 38.1-38.3) are a GUI-authoring step against the shipped model + `docs/powerbi/report_pages_spec.md` |
| 9 — Validation | regression, audit, performance, UAT | **PARTIAL** — unit/integration/regression suite in place; audit persistence (`audit_data_quality`/`audit_lineage`) and blocker-rule detection now proven with real inserts, not just schema (ADR-017); `scripts/stage9_validation_checklist.py` reports live status against issue #9's 21-item checklist (12 PASS/5 PARTIAL/4 BLOCKED); performance/UAT against real infrastructure remain out of this repository's scope by construction |

## Acceptance criteria (spec sec. 57) — status

1. Physical data via E2C or equivalent fixture — **PARTIAL** (contract mechanism ready, no live connector)
2. Data associated with plant — DONE
3. Data associated with line/process — DONE
4. Lot associated with product — DONE
5. Product associated with cluster — DONE
6. Historical state reconstructable — DONE (historical-replay repository queries, sec. 46; proven across multiple time points, not just one, in `test_factory_shadow_historical_replay_across_two_periods`, ADR-017)
7-10. TEI/EFA/EcoFA/SFA operational — DONE; formulas cross-checked against the real SRC-TEI/EFA/EcoFA/SFA manuals (ADR-018) — EFA/EcoFA/SFA matched exactly, TEI-J's quality-penalty formula was corrected
11. EEA aggregates four contributions — DONE
12. TSI_norm computable with coherent baseline — DONE, and the fuller real RP7.3 `TSI_abs`/`TSI_rel`/`Phi`/`Psi`/`SA_w` variant (ADR-012) reproduces 66+9 real logged values (`tests/regression/test_rp73_calculation_log.py`); `Psi`/`Ex_useful` confirmed by design, not a stopgap (ADR-019)
13. Sales associable to product — DONE
14. Cluster performance available — DONE
15. Trend linkable to cluster — DONE
16. P-TSA computes SCR/PsI/OCR — DONE
17. P-TSI z computed — DONE, validated against the real RP7.4 report data (ADR-020)
18. P-TSI scoring/AHP computed — DONE, validated against the real RP7.4 report data (ADR-020)
19. TII computed on the appropriate (P_TSI_5) variant — DONE
20. Design project traceable end-to-end — DONE (schema + workflow validator)
21. Prototype test linked — DONE (schema: `fact_quality_test.prototype_id`)
22. Design decision auditable — DONE
23. IIDS view available — DONE
24. BI drill-down functioning — **PARTIAL**: the Power BI semantic model (`bi/powerbi/`, ADR-016) is real and openable — `FactShadowState` + 6 conformed dimensions, display-aggregation-only measures, a `DataSourceMode` parameter switching between the ADR-014 synthetic export and a live SQL connection with no model rework. The 3 report pages/drill-down visuals themselves (sec. 38.1-38.4) are specified field-by-field in `docs/powerbi/report_pages_spec.md` but not yet built — that's a Power BI Desktop GUI step this repository can't execute or validate headlessly. Full real-data demonstration still waits on issues #3/#7 — see [issue #8](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/8)
25. No automatic actuation — DONE (structural: no write routes exist; CI greps for forbidden patterns)
26. Coefficient/version tracked — DONE (`dim_coefficient_set`, `dim_weight_set`)
27. calc_run reproducible — DONE (`audit_calc_run`, `make_calc_run_id`)
28. Data quality visible — DONE (`audit_data_quality`, blocker queries; `src/core/quality/persistence.py` now actually writes findings, and the blocker queries are proven to detect real violations rather than just parse as SQL, ADR-017)
29. P0 unit conversion validated — DONE (`test_units_energy.py`)
30. Golden regression tests approved — **PARTIAL**: CQS (sec. 19.5); 66+9 real, non-fabricated RP7.3 EEA+/TSI data points (`f_env`/`f_econ`/`f_soc`/`f_tech`/`SA_raw`/`Ex_ref`/`TSI_abs`/`TSI_rel`/`Ex_useful`, ADR-012/ADR-019) all pass against coefficient/weight sets formally `APPROVED` (ADR-013, 2026-09-01); the P-TSA z-score AND scoring/AHP targets now both pass against the real RP7.4 report data (ADR-020, issue #6) — the only remaining gap is that the granular per-lot TEI/EFA/EcoFA/SFA coefficient *values* (formulas confirmed, ADR-018) are still unapproved test-only placeholders pending the real Tabella 2 library

## What was deliberately NOT built (FUTURE / out of scope, per spec)

- ARIMA forecasting, logistic success model, portfolio optimizer (sec. 36, ADR-009)
- Any actuation / Digital Twin closed loop (sec. 3, ADR-001)
- Live Edge/MES/SCADA/ERP/HR/LIMS connectors (require IT-provided field mappings, P0-03)
- The 3 Power BI report pages' actual visual layout (sec. 38.1-38.3) —
  a GUI-authoring step in Power BI Desktop against the semantic model in
  `bi/powerbi/` (ADR-016) and the spec in `docs/powerbi/report_pages_spec.md`;
  not something this repository can produce or validate headlessly
- Re-clustering pipeline running on a schedule (sec. 19.6 — cluster versions are imported on request)

## Next steps for whoever continues this work

1. ~~Promote `COEFF_RP73_PROVISIONAL_2026` and `EEA_AHP_RP73_1` from `DRAFT` to
   `APPROVED`~~ — **done, ADR-013 (2026-09-01)**. If the RP7.3 historical
   series is later consolidated with different values, that must land under a
   new `coefficient_set_id`/`weight_set_id` (sec. 11.3 point 4), never as an
   in-place edit of the approved set.
2. ~~Resolve the `Psi`/`Ex_useful` open item (ADR-012)~~ — **done, ADR-019**:
   the primary RP7.3 report (repo root PDF, not examined before) confirms
   `Ex_useful`'s coefficient-based derivation is deliberately deferred to a
   future "release" version of the methodology, not missing from this beta —
   `Psi` stays a directly reported input by design. No coefficient invented,
   no project-owner sign-off needed (nothing new was approved).
3. Get IT to supply real MES/SCADA/ERP/HR/LIMS field names and complete
   `audit_source_mapping` + per-source YAML contracts (P0-03).
3b. ~~Load the 22 real RP6.8 clusters~~ — **done, ADR-015**. Obtain the real
    13,251-product cluster-assignment export (RP6.8 sec. 3.7, not in this
    repository) and run `python3 -m scripts.import_rp68_product_master_data
    --products-csv <file>` — the importer is ready and FK-validated against
    the real cluster set, only the input file is missing (issue #7).
4. ~~Resolve ADR-011 items 1-3 (TEI-J quality penalty, MTO powder pricing,
   `B_TILE`) against the actual SRC-TEI manual text~~ — **done, ADR-018**: the
   4 real manuals were found at the repo root; TEI-J's formula is fixed,
   EFA/EcoFA/SFA confirmed correct. Still open: get the project owner's
   sign-off on actual coefficient *values* once the real "Tabella 2" library
   (referenced by all 4 manuals, not part of this corpus) is available —
   confirming a formula is not approving a value (sec. 11.3). ADR-011 item 4
   (cluster-trend thresholds) remains genuinely open — no manual answers a
   business-policy question like that. Item 5 (P-TSA z-score/RP7.4 dataset)
   is separately resolved — see next point.
4b. ~~Obtain the RP7.4 dataset for the P-TSA z-score golden regression
    (ADR-011 item 5)~~ — **done, ADR-020**: the RP7.4 report (repo root PDF)
    contains the full raw SCR/PsI/OCR matrix and real per-dimension scores;
    `test_zscore_p_tsi_matches_rp74_published_values` is un-skipped and
    passing (issue #6).
5. ~~Build the Power BI semantic model against `mv_intelligent_industry_state`~~
   — **done, ADR-016**: `bi/powerbi/START_IIDS.SemanticModel/` (TMDL), built
   and testable today against the synthetic dataset via
   `scripts/export_mv_intelligent_industry_state.py`. Remaining: open it in
   Power BI Desktop and build the 3 report pages per
   `docs/powerbi/report_pages_spec.md` (sec. 38.1-38.4) — a GUI step: not
   executable from this repository. Swap `DataSourceMode`/`SqlServer`/
   `SqlDatabase` to real data once #3/#7 land, no model rework needed.
6. Run the Stage 9 checklist (spec sec. 65) against a staging environment with
   real data before declaring v1 production-ready. `python3 -m
   scripts.stage9_validation_checklist` (ADR-017) tracks live status of what
   this repository alone can verify (10/21 PASS today) — re-run it as #3-#7
   land; it will not, and cannot, turn UAT/performance items green, since
   those need a real deployment and real users.
7. Get the project owner's explicit sign-off on `config/baselines/rp73_baseline_2022.yaml`
   (currently `DRAFT`) — a gap ADR-017 found: the RP7.3 aggregate model has used
   this baseline since ADR-012, but it was never a governed artifact the way
   the coefficient/weight sets are (ADR-013).
