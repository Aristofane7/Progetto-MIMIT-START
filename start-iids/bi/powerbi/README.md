# START IIDS — Power BI semantic model (issue #8, ADR-016)

`START_IIDS.SemanticModel/` is a TMDL-format Power BI semantic model project.
It defines the **model only** (tables, relationships, display-aggregation
measures) — the three report pages from spec sec. 38.1-38.3 are not shipped
as pre-built visuals here; see `../../docs/powerbi/report_pages_spec.md` for
the exact visual-by-visual spec to build them against this model in Power BI
Desktop. See ADR-016 for why (a hand-authored report-layout JSON file cannot
be validated without a Power BI Desktop instance, and a subtly-invalid one is
worse than an explicit, precise spec for a human to build from).

## What it reads

Every table ultimately reads `mv_intelligent_industry_state` (sec. 26.2) —
**nothing else** — per ADR-006 ("BI is not a calculation engine") and issue
#8's explicit constraint. No measure recomputes EEA+/P-TSA; they are all
plain `SUM`/`AVERAGE`/`MAX` display aggregations (sec. 39).

## Opening it

Power BI Desktop (2024.06+) can open a TMDL semantic-model project directly:
File → Open → select the `START_IIDS.SemanticModel` folder. (Tabular Editor 3
or the Fabric/Power BI XMLA endpoint also read TMDL directly, if your Desktop
version predates folder-based project support.)

## Switching from synthetic to real data — no model rework

Four expression parameters (`definition/expressions.tmdl`) control the
source, editable from Power BI Desktop's Power Query "Manage Parameters":

| Parameter | Local (default) | SQL |
|---|---|---|
| `DataSourceMode` | `"Local"` | `"SQL"` |
| `LocalCsvFolder` | path to the folder from `scripts/export_mv_intelligent_industry_state.py` | *(unused)* |
| `SqlServer` | *(unused)* | your SQL Server / Azure SQL host |
| `SqlDatabase` | *(unused)* | the database exposing `mv_intelligent_industry_state` |

Generate (or refresh) the local CSVs from repo root:

```bash
python3 -m scripts.export_mv_intelligent_industry_state --out-dir data/synthetic/powerbi
```

By default this builds the synthetic demo dataset (ADR-014). Once real data
lands (issues #3/#7), point `--db-url` at the real database instead — the
CSV shape is identical, so no table/measure/relationship changes are needed;
or switch `DataSourceMode` to `"SQL"` and query the real database live.

## Known scope limits (see ADR-016)

- `DimPlant`/`DimLine`/`DimProduct` are id-only: the view/API don't expose
  friendly names (`plant_name`, `product_name`, ...) — only `DimProcess`
  has descriptive attributes, added as a passthrough for the Factory page's
  Process-level drill-down (sec. 38.1).
- `DimCluster` is id-only too; the real dominant-attribute/CQS values for the
  22 RP6.8 clusters exist (`data/reference/rp68_cluster_master.csv`, ADR-015)
  but are not part of the exposed read surface this model is scoped to.
- "Trend vs baseline" (sec. 38.1) is `tsi_norm` itself, which is already
  baseline-relative by construction (sec. 12) — `dim_baseline`'s underlying
  values aren't exposed via the view/API.
