# ADR-012 — Real RP7.3 aggregate model: Ex_ref, SA_w, Phi, Psi, TSI_abs, TSI_rel

**Status:** DOC (verified numerically against the project's own real data files), with one flagged open item

## Context

The repository root ships three real (though explicitly "provisional, being
consolidated") RP7.3 data artifacts that were not yet used by the v1
implementation:

- `RP7.3_data_collection_20232025.xlsx` — plant master data (D020, D060, D240),
  annual energy consumption (2022-2025), pre-aggregated module terms for
  TEI/EFA/EcoFA/SFA (`Moduli_TEI/EFA/EcoFA/SFA` sheets), a coefficient library
  (`Coefficienti`), and an AHP pairwise comparison matrix (`AHP`).
- `RP7.3_calculation_log.xlsx` — 93 logged results (`R001`-`R093`) reproducing
  the actual report-level calculation for each plant/year, including
  intermediate variables (`f_env`, `f_econ`, `f_soc`, `f_tech`, `SA_raw`, `SA_w`,
  `Ex_ref`, `Phi`, `Psi`, `TSI_abs`, `TSI_rel`) with formula strings, inputs, and
  outputs.
- `ahp_weights.xlsx` — the AHP pairwise matrix and its resulting weights/
  consistency check for the SA dimensions (`env`, `econ`, `soc`, `tech`).

The `Istruzioni` sheet in the data collection file explicitly instructs:
*"Rigenerazione: sostituire i valori e rieseguire `python3 -m src.run_all`
(stessa struttura di calcolo)"* — i.e. this is meant to drive an actual runnable
pipeline, not just be reference material.

## Verification performed

Every formula below was hand-verified against the real logged numbers (not
fabricated) before being implemented:

- `f_env`, `f_econ`, `f_soc` reproduce `R001-R003` (D020/2023) **exactly** using
  `src/engines/efa/formulas.py::compute_f_env`,
  `src/engines/ecofa/formulas.py::compute_f_econ`,
  `src/engines/sfa/formulas.py::compute_f_soc` **unchanged** — those pure
  functions already take pre-aggregated MJ terms and needed no modification.
- `f_tech` reproduces `R004` using `src/engines/tei/formulas.py::compute_f_tech`
  **unchanged**, confirming `loss_MTS + loss_MTO` is the correct combined loss
  term for that formula's first two arguments.
- `SA_raw = f_env + f_econ + f_soc + f_tech` reproduces `R005` exactly via the
  existing `compute_sa_mj`.
- `Ex_ref = Ex_el + Ex_fuel = (E_el_kWh * EL_EX) + (V_gas_Nm3 * GAS_EX)`
  (`EL_EX=3.6 MJ/kWh`, matching the spec's own `kwh_to_mj`; `GAS_EX=42 MJ/Nm3`)
  reproduces `R007` exactly (verified by hand for D020/2023: 39,140 + 156,560 =
  195,700 GJ).
- `Phi = SA_w / Ex_ref` reproduces `R008` (SA_w computed with the published,
  4-decimal-rounded AHP weights: env=0.3661, econ=0.1451, soc=0.0955,
  tech=0.3934 — these do not sum to exactly 1 due to that rounding, and are
  used as published rather than renormalized, to stay traceable to the source).
- `TSI_abs = alpha*Phi + beta*Psi` with `alpha=beta=0.5` reproduces `R010`
  exactly (0.5*0.0194 + 0.5*0.154 = 0.0867).
- `TSI_rel = TSI_abs(t) / TSI_abs(baseline)` reproduces `R031`/`R062`/`R093`
  (each plant's 2025-vs-2023 ratio) within the same rounding tolerance as above.
- Baseline year is **fixed at 2022** for every plant (not a rolling
  previous-year comparison) — confirmed by the `Moduli_*` sheets carrying a 2022
  row used identically as the `_ref` term for 2023, 2024, and 2025.

This **refines** the terse description in the implementation spec (sec. 18.2:
"TSI_norm = SA_current/SA_historical") with the actual RP7.3 methodology: TSI is
not a direct ratio of SA, but a ratio of `TSI_abs` — itself an AHP-weighted,
reference-exergy-normalized (`Phi`) blend with an exergy efficiency indicator
(`Psi`). The simple `SA_current/SA_historical` ratio (`compute_tsi_norm` in
`src/engines/eea/formulas.py`, ADR at the time this was written) remains
implemented as a documented, simpler fallback variant for when the fuller
Phi/Psi inputs are not available — it is not deleted, since sec. 18.2 is still
literally in the spec — but the aggregate/plant-year pipeline (`src/run_all.py`)
uses the fuller, verified `TSI_abs`/`TSI_rel` path as primary.

## Open item — Psi / Ex_useful (tracked alongside ADR-011)

`Psi = Ex_useful / Ex_ref` is logged directly in `RP7.3_calculation_log.xlsx`
(e.g. `R009=0.154`), but **no sheet in the available corpus defines
`Ex_useful`** or a coefficient to derive it from `produzione_m2` (`Unita`
sheet). Reverse-engineering a coefficient from `Psi * Ex_ref = Ex_useful` and
correlating it against `produzione_m2` would be fabricating an unapproved
coefficient to force a match — forbidden by spec sec. 64. Per this project's own
governance (Appendix L/M), `Psi` is therefore treated as a **directly reported
input** (sourced from the calculation log itself, which is legitimate SRC-RP73
data, not invented) until the `Ex_useful` derivation is confirmed with the
project owner. `compute_psi_efficiency` in `src/engines/eea/formulas.py` is a
thin pass-through with this caveat documented in its docstring; nothing computes
a `Psi` value from scratch in this codebase.

## Decision

1. `src/engines/eea/formulas.py` gains `compute_ex_ref`, `compute_sa_weighted`,
   `compute_phi`, `compute_psi_efficiency` (pass-through, see above),
   `compute_tsi_abs`, `compute_tsi_rel` — all pure, all guarded against a zero
   `Ex_ref`/baseline `TSI_abs` denominator (`CALCULATION_ERROR`, never silently
   coerced).
2. The AHP dimension weights (`env`/`econ`/`soc`/`tech`) are loaded through the
   same `WeightSet` abstraction as P-TSA's AHP weights (sec. 24.8/24.9), under a
   distinct `weight_set_id` (`EEA_AHP_RP73_1`) — never hardcoded in a formula.
3. `dim_coefficient` gains `EL_EX`, `GAS_EX`, `IMP_CO2`, `ECO_VA`, `ECO_IN`,
   `LAB_H` under a coefficient set loaded as **`DRAFT`**, not `APPROVED` — the
   source data explicitly says these are provisional ("in corso di
   consolidamento con le serie storiche definitive"). Per sec. 11.3, a `DRAFT`
   set must never feed a production calculation; it is used here only for
   regression testing and demonstration (`src/run_all.py`), clearly labeled as
   such. Promoting it to `APPROVED` requires an explicit project-owner sign-off
   once the historical series is consolidated.
4. `fact_eea_state` gains nullable `ex_ref_gj`, `sa_w_gj`, `phi`, `psi`,
   `tsi_abs` columns via a new, additive migration (`0010_...sql`) — existing
   lot/process-level rows populated by the granular TEI/EFA/EcoFA/SFA engines
   are unaffected and simply leave these columns NULL.
