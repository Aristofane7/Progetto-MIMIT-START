# ADR-006 — BI is not a calculation engine

**Status:** ARCH proposed (spec sec. 61)

## Decision
All EEA+/P-TSA/TEI/EFA/EcoFA/SFA formulas execute in the Python/SQL engines under
`src/engines/`; results are persisted (`fact_eea_state`, `fact_ptsa_state`) before
any BI tool touches them. Power BI/BusinessObjects may only perform display-level
aggregation (sec. 39) — never re-implement a formula in DAX in parallel with
Python.

## Consequences
Auditability and single-source-of-truth: a number shown on a dashboard always
traces back to one `calc_run_id`, never to an independently-computed DAX measure.
