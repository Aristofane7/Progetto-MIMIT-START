# ADR-014 — Temporary synthetic demo dataset (Power BI development enabler)

**Status:** APPROVED by project owner (Davide Settembre), 2026-09-01 — explicitly temporary

## Context

Issues [#7](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/7) (real
master data import) and [#3](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/3)
(live E2C/MES/SCADA connectors) block a fully real, end-to-end demonstration of
`mv_intelligent_industry_state` and the read-only API. Both require inputs
(RP6.8 product export, IT field mappings) that are not available yet. Building
the Power BI semantic model ([#8](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/8))
does not need to wait for them — it needs *some* data flowing through the
existing schema/view so pages, relationships and measures can be built and
verified against a real query surface.

The project owner explicitly approved proceeding with a **synthetic** dataset
for this purpose only.

## Decision

1. A deterministic generator (`scripts/generate_synthetic_demo_data.py`, fixed
   seed) produces a small, internally consistent dataset spanning
   `dim_plant` → `fact_ptsa_state` / `fact_cluster_performance`, sized to
   exercise every join in `mv_intelligent_industry_state`.
2. **Every** synthetic row is tagged so it can never be mistaken for real data:
   - `source_system = 'SYNTHETIC_DEMO'` on every fact table that has the column;
   - plant IDs `SYN01`/`SYN02` (never a real site code like `D020`/`D060`/`D240`);
   - product/lot IDs prefixed `SYN-`;
   - `cluster_version = 'SYNTHETIC_DEMO_V1'` with `cluster_id` in the `9001+`
     range, clear of the real RP6.8 range (`1`-`22`);
   - the coefficient set (`SYN_COEFF_SET`) and weight set (`SYN_WEIGHT_SET`)
     backing the synthetic `audit_calc_run` rows are **`DRAFT`** and must
     **never** be promoted to `APPROVED` — sec. 11.3 already blocks a DRAFT set
     from a real engine run; here there is no real engine run at all (see next
     point).
3. `fact_eea_state` / `fact_ptsa_state` values for the synthetic dataset are
   **randomized within plausible ranges**, not computed by
   `src/engines/eea` / `src/engines/ptsa`. They exist only to make dashboard
   visuals non-empty. They must never be cited as a calculation result, a
   golden-regression data point, or evidence toward acceptance criteria #7,
   #11, #12, #16-#19 (spec sec. 57) — those remain gated on real data (issues
   #3, #4, #6, #7).
4. Scope: unblocks **only** issue #8 (Power BI semantic model development).
   It does **not** close #7 (real master data) or #3 (live connectors), and it
   must not be used as an input to #9 (Stage 9 validation), which explicitly
   requires real data (spec sec. 65).
5. Removal: the dataset lives under `data/synthetic/` (generated, gitignored
   the same way as other build output would be — the generator script itself
   is the source of truth) so it can be dropped in one step before any
   production/staging load. `scripts/generate_synthetic_demo_data.py` must
   never be imported by, or run as part of, any production code path.

## Consequences

- Power BI development can start immediately against
  `mv_intelligent_industry_state` populated with synthetic rows.
- No governance rule from sec. 11.3, ADR-011, ADR-012, or ADR-013 is bypassed:
  the synthetic dataset does not touch any APPROVED coefficient/weight set,
  and does not claim to be a calculation result.
- When #7/#3 land, the synthetic dataset is deleted and regenerated data (real)
  takes its place; no code in `src/engines/` or `src/api/` needs to change,
  since both already treat `mv_intelligent_industry_state` as a read surface
  over whatever rows exist in the core tables.
