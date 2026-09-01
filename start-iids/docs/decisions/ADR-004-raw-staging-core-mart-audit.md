# ADR-004 — Raw → Staging → Core → Mart → Audit layering

**Status:** ARCH proposed (spec sec. 61)

## Decision
All data flows through five layers (sec. 6): `raw_*` (append-only, immutable),
`stg_*` (parsing/casting/naming), `dim_*`/`fact_*`/`bridge_*` (semantic core),
`mart_*`/`mv_*` (BI/engine outputs), `audit_*` (quality, lineage, calc runs).

## Consequences
No engine or API ever reads directly from `raw_*`; no layer skips a step. This
repository currently ships the `core` DDL (`sql/migrations/`) and one `mart`
artifact (`mv_intelligent_industry_state`); `raw_*`/`stg_*` tables are introduced
per-source as real connectors are built (see ROADMAP.md).
