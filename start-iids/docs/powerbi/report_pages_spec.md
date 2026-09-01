# Power BI report pages — build spec (spec sec. 38.1-38.4, issue #8)

This maps every visual sec. 38.1-38.4 asks for onto a concrete field/measure
from `bi/powerbi/START_IIDS.SemanticModel` (ADR-016). It is written to be
built in Power BI Desktop's report designer against that model — it is not a
substitute for opening Desktop, because a hand-authored `.pbir`/report-layout
JSON file cannot be validated without an actual Desktop instance to open it
in, and a subtly-invalid one would be a worse handoff than this spec (see
ADR-016). Every field below already exists in the model; nothing here
requires a new measure beyond what's in `FactShadowState.tmdl`.

Global constraints that apply to every page (non-negotiable, sec. 3.2/39):

- No visual/button ever writes back to the physical system — every field is
  from a read model built on `mv_intelligent_industry_state`.
- No DAX measure recomputes EEA+/P-TSA — every measure listed is `SUM`/
  `AVERAGE`/`MAX` (see `FactShadowState.tmdl` for the exact DAX).
- Show `'Freshness — EEA'` / `'Freshness — PTSA'` / `'Freshness — Sales'`
  and `'Data Quality Score (avg)'` somewhere visible on every page (sec.
  31.3, sec. 29) — a card visual in a fixed header area is sufficient.

## 38.1 — Factory page

| Visual | Type | Fields |
|---|---|---|
| SA | Card | `'SA (avg GJ)'` |
| TSI_norm | Card + line chart over time | `'TSI norm (avg)'` by `DimDate[Date]` |
| f_env / f_econ / f_soc / f_tech | Stacked column or 4 cards | `'f_env (avg GJ)'`, `'f_econ (avg GJ)'`, `'f_soc (avg GJ)'`, `'f_tech (avg GJ)'` |
| Trend vs baseline | Line chart | `'TSI norm (avg)'` by `DimDate[Date]`, reference line at `1.0` (TSI_norm is already baseline-relative by construction, sec. 12 — there is no separate baseline series to plot; a constant `1.0` reference line is the "baseline" sec. 38.1 asks to compare against) |
| Drill-down Plant→Line→Lot→Process | Matrix or decomposition tree | Rows hierarchy: `DimPlant[plant_id]` → `DimLine[line_id]` → `FactShadowState[lot_id]` → `DimProcess[process_name]`; Values: `'SA (avg GJ)'`, `'TSI norm (avg)'` |

Slicers: `DimPlant[plant_id]`, `DimDate[Calendar]` hierarchy.

## 38.2 — Product page

| Visual | Type | Fields |
|---|---|---|
| Cluster | Slicer/table | `DimCluster[cluster_id]`, `DimCluster[cluster_version]` |
| Sales trend | Line chart | `'Sales (sum m2)'` by `DimDate[Date]`, split by `FactShadowState[cluster_trend]` |
| P-TSI | Card + gauge (1-5 scale) | `'P-TSI (avg, 1-5)'` |
| IOAI | Card | `'IOAI (avg)'` |
| OPI | Card | `'OPI (avg)'` |
| TQI | Card | `'TQI (avg)'` |
| Technical tests | *(not modeled)* | `fact_quality_test` / prototype test results are not part of `mv_intelligent_industry_state` — out of this model's scope; note as a known gap rather than fabricate a field |
| Product type | Table | `FactShadowState[product_id]` (the mart view carries no separate `product_type`/`dim_ptsa_type` join — same gap as above) |

Slicers: `DimProduct[product_id]`, `DimCluster[cluster_id]`.

## 38.3 — Integrated page

Selector: a single slicer bound to `FactShadowState[product_id]` /
`DimCluster[cluster_id]` / `FactShadowState[lot_id]` (a "field parameter" in
Power BI, or three synced slicers if field parameters aren't available in
the Desktop version in use) drives all three columns below via the model's
existing relationships — no extra table or logic needed.

| Column | Fields |
|---|---|
| Market | `DimCluster[cluster_id]`, `'Sales (sum m2)'`, `FactShadowState[cluster_trend]`, `FactShadowState[trend_alignment]` |
| Product | `'P-TSI (avg, 1-5)'`, `'IOAI (avg)'`, `'OPI (avg)'`, `'TQI (avg)'` |
| Factory | `'TSI norm (avg)'`, `'f_env (avg GJ)'`, `'f_econ (avg GJ)'`, `'f_soc (avg GJ)'`, `'f_tech (avg GJ)'` |

## 38.4 — Drill-down (why)

Two drillthrough pages, both landing on a single-lot detail page (filters
context passed via Power BI's standard drillthrough mechanism — no DAX
needed beyond the page-level filter):

1. **TSI → footprint → driver → process → observation.**
   `'TSI norm (avg)'` visual → drillthrough on `FactShadowState[lot_id]` →
   detail page showing `f_env_gj`/`f_econ_gj`/`f_soc_gj`/`f_tech_gj` (the
   footprints) broken down by `DimProcess[process_name]` (the driver/process
   level). The model's read surface stops at lot+process grain — a true
   "observation" (a single `fact_process_observation` row, sec. 26) is one
   level below what `mv_intelligent_industry_state` exposes; link out via
   `FactShadowState[calc_run_id]` as the last drillthrough field so a user
   can cross-reference `audit_calc_run`/`fact_process_observation` in the
   source system if they have direct DB access. Do not attempt to reach
   observation grain by adding a second data source to this model — that
   would violate the "only `mv_intelligent_industry_state` and the read-only
   API" constraint (issue #8).
2. **P-TSI → dimension → metric → product/lot → source record.**
   `'P-TSI (avg, 1-5)'` visual → drillthrough on `FactShadowState[product_id]`
   → detail page showing `ioai`/`opi`/`tqi` (the dimensions) at
   `FactShadowState[lot_id]` grain (the metric/product-lot level); the last
   field is `FactShadowState[calc_run_id]`, the same cross-reference pattern
   as above (a "source record" one level below `fact_ptsa_state` is outside
   this model's read surface).

## Known gaps carried over from ADR-016 / the model's own scope

- No `dim_baseline` values are exposed (only `baseline_id` as an FK), so
  "trend vs baseline" uses `tsi_norm`'s own baseline-relative definition
  rather than a literal two-series comparison.
- No `fact_quality_test` / `dim_ptsa_type` data is in `mv_intelligent_industry_state`,
  so "technical tests" and "product type" (sec. 38.2) cannot be built from
  this model as-is; flagged here rather than invented.
- `DimPlant`/`DimLine`/`DimProduct`/`DimCluster` show ids, not names, for
  the same reason (see `bi/powerbi/README.md`).

These are legitimate follow-ups for whoever next extends
`mv_intelligent_industry_state` — not something to silently patch around in
DAX (that would reintroduce exactly the risk sec. 39 exists to prevent).
