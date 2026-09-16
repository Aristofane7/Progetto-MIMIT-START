# START IIDS — self-contained HTML viewer (issue #8, ADR-023)

A single-file, no-CDN-dependency HTML dashboard over `mv_intelligent_industry_state`
— the same pattern the sibling project VOLT uses for its Digital Shadow
viewer. Built to be the practical, always-buildable alternative to the Power
BI report pages (`bi/powerbi/`, ADR-016), whose GUI-authoring step this
repository cannot execute headlessly.

## What it reads

Same constraint as the Power BI model (ADR-006, sec. 39 — "BI is not a
calculation engine"): every number is computed once in
`scripts/build_html_viewer.py` from `mv_intelligent_industry_state` and the
`dim_distribution_channel`/`audit_data_quality` tables; the HTML/JS in
`template.html` only renders already-computed numbers.

## Building it

```bash
# against the synthetic demo dataset (ADR-014) — no setup needed
python3 -m scripts.build_html_viewer --out dist/start_iids_viewer.html

# against a real database, once available (issues #3/#7)
python3 -m scripts.build_html_viewer --db-url sqlite:///real.db \
    --label "Estrazione ERP 2026-XX-XX" --out out/viewer.html
```

Open the resulting file directly in any browser — no server needed.

## Pages

Overview, Guida all'uso (user guide + full glossary, ADR-024), Factory
(sec. 38.1, with a CURRENT/HISTORICAL scenario filter and a period-comparison
tool — both grounded in real fields, not a fabricated disruption model),
Product (sec. 38.2), Canale distributivo (ADR-022, requested directly — not
from the spec), Integrated (sec. 38.3-38.4), Edificio (a structural
placeholder for OR3/UNISS building-envelope data, never fabricated — see
ADR-023), and Qualità & Build (data quality findings + build provenance, so
nobody mistakes synthetic output for real data).

Every metric acronym (SA, TSI_norm, IOAI/OPI/TQI, P-TSI, TII, HHI, ...) is
shown with a hover tooltip and full definition, sourced from a single
`GLOSSARY` dict in `scripts/build_html_viewer.py` (ADR-024) — never a bare,
unexplained acronym.

## Relationship to the Power BI model

`bi/powerbi/` is not replaced. It remains the documented path for a licensed
Power BI environment with real live data. This viewer is the alpha-0
deliverable in the meantime, sharing the same field mapping
(`docs/powerbi/report_pages_spec.md`) so the two never diverge into
separate specs.
