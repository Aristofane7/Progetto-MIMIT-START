# ADR-007 — TII computed only on the P-TSI scoring/AHP variant

**Status:** ARCH safety rule (spec sec. 61), APPLIED

## Context
`P-TSI_z` (z-score method) is signed and can be zero or negative by construction;
a ratio `P-TSI_z(t) / P-TSI_z(t-1)` is not well-defined in general.

## Decision
`TII_{t-1,t} = (P_TSI_5(t) / P_TSI_5(t-1) - 1) * 100`, always on `P_TSI_5` (the
1-5 scoring/AHP variant, positive and ratio-compatible). `tii_base_variant =
P_TSI_5` is recorded implicitly by never exposing a z-score TII function.

## Consequences
`src/engines/ptsa/formulas.py::compute_tii` takes only `P_TSI_5` values and
rejects a non-positive previous-period value; there is intentionally no
`compute_tii_zscore` function anywhere in the codebase (see
`tests/unit/test_ptsa_engine.py::test_engine_never_exposes_a_zscore_tii_function`).
