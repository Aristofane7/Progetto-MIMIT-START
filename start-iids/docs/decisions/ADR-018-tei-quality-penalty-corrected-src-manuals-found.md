# ADR-018 — SRC-TEI/EFA/EcoFA/SFA manuals found; TEI-J quality penalty corrected

**Status:** ACCEPTED, 2026-09-01 — issue #4 progress on ADR-011 items 1-3; item 4 untouched

## Context

ADR-011 was written on the premise that "the corresponding manual's full text
is not available as machine-readable content in this corpus, only referenced
PDF filenames: `SRC-TEI`, `SRC-EFA`, `SRC-ECO`, `SRC-SFA`". That premise was
wrong — all four are present at the repo root as real, readable PDFs:

- `Manuale operativo – Modulo TEI‑J (beta) per EEA+.pdf`
- `Manuale operativo – Modulo EFA‑J (beta) per EEA+.pdf`
- `Manuale operativo – Modulo EcoFA‑J (beta) per EEA+.pdf`
- `Manuale operativo – Modulo SFA‑J (beta) per EEA+.pdf`

This is the same situation issue #7 found with the RP6.8 report: a primary
source assumed unavailable was sitting in the repository the whole time.
Reading all four against the current `src/engines/{tei,efa,ecofa,sfa}/formulas.py`
gives a materially different picture than ADR-011 assumed.

## What the manuals confirm

**EFA-J, EcoFA-J, SFA-J formulas already match their manuals exactly** —
`compute_resource_intake`/`compute_waste_exergy`/`compute_impact_equivalent`/
`compute_circularity_credit`/`compute_f_env` (EFA), `compute_economic_input`/
`compute_value_added`/`compute_fixed_assets`/`compute_f_econ` (EcoFA), and
`compute_stakeholder_value`/`compute_co2_exergy`/`compute_daly_diagnostic`/
`compute_lost_hours_exergy`/`compute_training_credit_exergy`/`compute_f_soc`
(SFA, including the DALY-stays-diagnostic-only rule, ADR-010) all reproduce
their manual's §3-§9 formulas verbatim, double-counting guards included. No
code change needed there — these three modules' docstrings already correctly
said "DOC", and now that claim is actually checked against the real source.

**TEI-J: two of three ADR-011 items were already right, one was wrong.**

- **Item 2 (MTO powder pricing) — confirmed correct.** Manual §3: `Ex_SDU =
  m_SDU · b_SD`. This module already prices `m_sdu_kg` with the `B_SDM`
  coefficient (same atomized-powder material). No code change; ADR-011's
  "pending confirmation" flag is resolved.
- **Item 3 (`B_TILE`) — confirmed correct.** Manual §3: `Ex_T = N_T^man · b_T`
  (the Power BI DAX example even names it `b_tile_MJex_per_pz`). This
  module's `Ex_T = N_T^man * b_tile` and its `B_TILE` coefficient code were
  already the right shape. No code change; ADR-011's flag is resolved.
- **Item 1 (quality penalty) — was wrong, now fixed.** Manual §4.4 (MTS) /
  §5.4 (MTO):

  ```
  Ex_qual = Σ_k κ_k · max(0, 1 - q_k / q̄_k) · Ex_exposed
  ```

  a **ratio** shortfall against a target/acceptability value. This module
  implemented `kappa * max(0, q_thr - q) * exposed_exergy_mj` — an
  **absolute-difference** shortfall. The two are only equivalent if `q` is
  already normalized to `[0, 1]` with `q_target = 1`, which sec. 14.2's
  minimal MTS/MTO dataset never guaranteed. Fixed in
  `src/engines/tei/formulas.py::compute_quality_penalty`.

## Decision

1. `compute_quality_penalty` now implements `kappa * max(0, 1 - q/q_target) *
   exposed_exergy_mj`, raises `PHYSICAL_RANGE_ERROR` if `q_target <= 0` (it's
   now a ratio denominator, not a subtraction reference), and documents the
   still-open generalization to the manual's multi-parameter sum (needs a
   `Quality` fact table per manual §8.3, which this schema doesn't have —
   not fabricated here, left as a named follow-up).
2. `TEIEngine.engine_version` bumped `1.0.0` → `1.1.0` (Appendix M: any
   formula change requires a version increment).
3. New tests (`tests/unit/test_tei_engine.py`) cover the ratio formula, the
   zero-shortfall case, missing-input handling, the new `q_target <= 0`
   guard, and an engine-level test that a quality shortfall actually reduces
   `f_tech`. There was no prior numeric test to preserve as "old" per
   Appendix M's process — no existing fixture ever set `q_mts`/`q_mto`, so
   the ARCH placeholder's wrong math was never actually exercised with real
   numbers.
4. ADR-011 items 1-3 are superseded by this ADR at the **formula** level.
   Item 4 (cluster-trend thresholds) is untouched: none of the four manuals
   discuss sales/trend classification, so it remains a genuine business-
   policy decision only the project owner can make.

## What this does NOT resolve

Per Appendix M, a confirmed formula is not an approved coefficient. All four
manuals' own example coefficient tables (TEI Annesso A5, EFA Annesso A,
EcoFA Annesso A3, SFA Annesso A) are explicitly labeled placeholder/
structure-only values ("valori segnaposto" / "…", "popolare con i dati
ufficiali") — the actual authoritative numeric library ("Tabella 2",
referenced by all four manuals as the primary source) is not part of this
corpus, the same kind of external blocker issue #7 hit with the RP6.8
product export. `B_TILE`, `B_SDM`, `KAPPA_MTS`, `KAPPA_MTO`, and every other
granular TEI/EFA/EcoFA/SFA coefficient therefore remain `DRAFT`/test-only —
this ADR fixes and confirms *formulas*, not coefficient governance. Getting
those to `APPROVED` needs the real Tabella 2 plus the project owner's
sign-off (sec. 11.3, the same process ADR-013 used for the RP7.3 aggregate
model).

## Consequences

- TEI-J's `f_tech` now differs from pre-fix runs whenever `q_mts`/`q_mto` are
  supplied and below target — no existing test or real calculation run
  depended on the old (wrong) math, so this is a pure correctness fix, not a
  breaking change to any committed result.
- Issue #4 stays open: the coefficient-value approval it ultimately asks for
  is still blocked on the real Tabella 2, exactly as issue #7's product
  catalog is blocked on RP6.8's raw export.
