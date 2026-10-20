# ADR-016 — Power BI semantic model: format, scope, and mv view extension

**Status:** ACCEPTED, 2026-09-01 — issue #8 progress, not closure

## Context

Issue #8 (spec sec. 38) asks for a Power BI semantic model plus three report
pages (Factory, Product, Integrated) with specific drill-down behavior,
consuming *only* `mv_intelligent_industry_state` and the read-only API
(never duplicating EEA+/P-TSA calculation logic in DAX — ADR-006, sec. 39).

Two format questions had to be settled before writing anything:

1. **How to ship a Power BI artifact from a code repository at all**, given
   this environment has no Power BI Desktop to open/validate a `.pbix`.
   Power BI's modern **PBIP/TMDL** project format is plain text
   (JSON + TMDL), designed for exactly this — git-tracked, diffable,
   openable directly in Power BI Desktop (2024.06+) or Tabular Editor.
2. **Whether to hand-author the report pages' visual-layout JSON
   (`.pbir`/report definition) as well as the semantic model.** Decided
   **no**: the model (TMDL) is a well-documented, mechanically-checkable
   text format — the same category of artifact as the SQL DDL already in
   this repo. The report-layout format is denser, more Desktop-version-
   coupled, and effectively impossible to validate without opening it in
   Desktop. A subtly-malformed `.pbir` would be a worse handoff than an
   explicit spec — the same judgment call as ADR-015 refusing to
   guess-correct the RP6.8 cluster-11 defect rather than risk silently
   wrong data.

## Decision

1. `bi/powerbi/START_IIDS.SemanticModel/` is a real, openable TMDL semantic
   model project: `FactShadowState` (one row per lot, straight from
   `mv_intelligent_industry_state`) plus five conformed dimensions
   (`DimPlant`, `DimLine`, `DimProcess`, `DimProduct`, `DimCluster`) and a
   standard calendar (`DimDate`). Every measure is a plain `SUM`/`AVERAGE`/
   `MAX` display aggregation (sec. 39) — none recomputes EEA+/P-TSA.
2. `docs/powerbi/report_pages_spec.md` is the sec. 38.1-38.4 visual-by-visual
   build spec — the report pages themselves are a GUI-authoring step for a
   human with Power BI Desktop, not hand-written JSON in this repo.
3. `sql/views/mv_intelligent_industry_state.sql` gains three passthrough
   columns — `process_id`, `process_name`, `process_family` (joining
   `dim_process` the same way `line_id` already does) — because sec. 38.1's
   required "Plant→Line→Lot→Process" drill-down has no field to reach
   without them. This is additive to sec. 26.2's "campi minimi" ("minimum
   fields" — a floor, not a ceiling) and does not touch any calculation
   logic; it is a small, spec-driven passthrough, not scope creep, and it is
   covered by an existing test assertion
   (`tests/integration/test_synthetic_demo_data.py`).
4. `scripts/export_mv_intelligent_industry_state.py` materializes the view
   (+ dimension distincts) to CSV — the model's default **local** data
   source, built from the ADR-014 synthetic dataset by default, or from any
   real database via `--db-url` once issues #3/#7 land. The semantic model's
   `DataSourceMode` parameter switches between this and a live SQL Server/
   Azure SQL connection with no table/measure/relationship changes — the
   same "start on synthetic, swap to real with no model rework" promise
   ADR-014 and the ROADMAP already made.
5. `DimCluster` and `FactShadowState` both carry a computed `ClusterKey`
   (`cluster_id & "|" & cluster_version`) as the actual relationship key,
   because `cluster_id` alone is only unique within one `cluster_version`
   (`dim_product_cluster`'s real primary key is the pair, sec. 19.6 SCD2).
   Today's real (`0`-`21`) and synthetic (`9001+`) ranges happen not to
   collide, but relying on that would be exactly the kind of silent
   assumption this project's governance style (ADR-011, ADR-015) exists to
   avoid.
6. Known, documented gaps (not silently patched around in DAX): no
   `dim_baseline` values, `fact_quality_test`, or `dim_ptsa_type` data reach
   `mv_intelligent_industry_state`, so "trend vs baseline" reuses `tsi_norm`'s
   own baseline-relative definition (sec. 12) and "technical tests"/"product
   type" (sec. 38.2) cannot yet be built. `DimPlant`/`DimLine`/`DimProduct`/
   `DimCluster` are id-only — no friendly names are in the exposed read
   surface. All recorded in `docs/powerbi/report_pages_spec.md` and
   `bi/powerbi/README.md`.

## Consequences

- The semantic model is real, versioned, and immediately usable against the
  synthetic dataset today; swapping to real data is a two-parameter change.
- No governance rule is bypassed: nothing here computes a sustainability
  metric outside `src/engines/`, and the mart-view extension is a passthrough
  column, not new business logic.
- The report pages remain a to-do for a human with Power BI Desktop — this
  ADR deliberately does not claim otherwise.
