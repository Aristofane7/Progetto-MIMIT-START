# ADR-013 — RP7.3 coefficient set and AHP weight set promoted to APPROVED

**Status:** APPROVED, effective 2026-09-01

## Decision

The project owner (Davide Settembre) has explicitly approved, on 2026-09-01,
the use of the following two governed parameter sets in current calculations:

| Set | ID | Was | Now |
|---|---|---|---|
| Coefficient set | `COEFF_RP73_PROVISIONAL_2026` | DRAFT | **APPROVED** |
| AHP weight set | `EEA_AHP_RP73_1` | DRAFT | **APPROVED** |

This satisfies spec sec. 11.3's requirement that a coefficient/weight set must
be explicitly reviewed and approved before it may feed a production
calculation — the approval is recorded in-line in each YAML file
(`config/coefficients/rp73_provisional_2026.yaml`,
`config/weights/eea_ahp_rp73.yaml`) via `approved_by`/`approved_at`, mirroring
`dim_coefficient_set.approved_by/approved_at` and `dim_weight_set.
approved_by/approved_at` in the reference schema.

## Scope of this approval — read carefully

This approval covers **exactly** the six coefficients in
`COEFF_RP73_PROVISIONAL_2026` (`EL_EX`, `GAS_EX`, `IMP_CO2`, `ECO_VA`,
`ECO_IN`, `LAB_H`) and the four AHP dimension weights in `EEA_AHP_RP73_1`
(`env`, `econ`, `soc`, `tech`) — i.e. the plant/year **aggregate** EEA+/TSI
model (ADR-012). It does **not**:

- Approve any coefficient referenced only by the granular, per-lot/per-process
  TEI/EFA/EcoFA/SFA engines (`B_RM`, `B_UW`, `B_SDM`, `B_TILE`, `KAPPA_MTS`,
  `Q_THR_MTS`, `KAPPA_MTO`, `Q_THR_MTO`, `PCI_GAS`, `F_EX_GAS`, etc.) — those
  remain unapproved placeholders used only in unit tests (ADR-011 is
  unaffected by this ADR).
- Resolve the `Psi`/`Ex_useful` open item (ADR-012) — `Psi` is still a directly
  reported input, not a derived value, regardless of coefficient/weight
  approval status.
- Constitute a statement that the underlying RP7.3 2023-2025 data collection
  is final. The source workbook's own `Istruzioni` sheet still calls that data
  "provvisori e in corso di consolidamento con le serie storiche definitive."
  The project owner has approved *using today's values* for current
  calculations, not that they are immutable. Per sec. 11.3 point 4, any future
  *value* change (not just a status change) must land under a **new**
  `coefficient_set_id`/`weight_set_id` — never edit these two in place.

## Consequences

- `src/run_all.py` no longer needs to (and no longer does) locally re-wrap a
  DRAFT set as APPROVED for its own run — it loads
  `COEFF_RP73_PROVISIONAL_2026` / `EEA_AHP_RP73_1` exactly as any production
  caller would, through `CoefficientSet.get` / `WeightSet.
  get_dimension_weight`.
- `tests/regression/test_rp73_calculation_log.py` now calls
  `src/engines/eea/aggregate.py::compute_aggregate_state` directly (the same
  production-safe function `run_all.py` uses) instead of bypassing the
  approval gate via `raw_value`/`raw_dimension_weight`.
- `CoefficientSet.raw_value` / `WeightSet.raw_dimension_weight` remain in the
  codebase as general-purpose tools for validating a *future* still-DRAFT
  set's numbers before it, too, is promoted — they are no longer needed for
  this specific dataset.
