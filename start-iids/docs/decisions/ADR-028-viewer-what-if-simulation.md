# ADR-028 — "Simulazione" tab: a what-if sandbox over real, already-validated formulas

**Status:** ACCEPTED — amends ADR-024's "no disruption model" scope

## Context
The user asked for the HTML viewer to also support simulations, as the
sibling project VOLT's Digital Shadow does with its supply-chain disruption
scenarios (S1-S4, pre-authored impact curves). ADR-024 had deliberately
**not** built a VOLT-style scenario model, because no approved
disruption/shock taxonomy exists in the spec or the data for a ceramic
factory, and inventing impact magnitudes would violate sec. 64 ("non
fabbricare input per far tornare i valori"). That reasoning still holds for
a *canned scenario catalogue* — this ADR does not reintroduce one. What it
adds instead is a narrower, honest capability: a **what-if sandbox**, where
the user explicitly declares a hypothetical percentage/absolute change to a
real, already-displayed number, and the tool recomputes the *same*, already
real, documented downstream formula — nothing about the shape or magnitude
of the "shock" is invented by the tool.

## Decision

### What is allowed to run client-side, and what is not
ADR-006 (sec. 39: "BI is not a calculation engine") constrains this
viewer's JavaScript to rendering already-computed numbers, with one
existing exception already accepted for the period-comparison feature
(ADR-024): plain arithmetic over already-computed columns (an average, a
ratio) is not treated as "a new calculation", the same way a spreadsheet's
`AVERAGE`/`=A/B` isn't. The simulation tab stays inside that same boundary
by construction — every formula it runs client-side is a **single-line,
already-public arithmetic identity, already in `DATA.glossary`**, applied to
numbers the build already computed:
- `SA = f_env + f_econ + f_soc + f_tech` (sec. 18.1, plain sum, no weights)
- `TSI_norm = SA_current / SA_baseline` (sec. 18.2, plain ratio)
- `Φ = SA_w / Ex_ref` (ADR-012, plain ratio — `SA_w` itself, which needs the
  AHP weight set, is taken as given from the real payload, never
  recomputed from footprints client-side)
- `TSI_abs = α·Φ + β·Ψ` (α=β=0.5, ADR-012)
- `TSI_rel = TSI_abs(current) / TSI_abs(baseline)` (ADR-012)

What stays firmly server-side, never duplicated in JS: the TEI-J/EFA-J/
EcoFA-J/SFA-J loss/circularity formulas, `Ex_ref`'s dependency on the
`APPROVED` coefficient set, and the AHP weighting that produces `SA_w` in
the first place. The simulation only perturbs the *inputs* to the five
formulas above (the four footprints, `Ψ`, `Ex_ref`), never re-derives those
inputs' own upstream calculation.

### Two simulation panels, each on real data
1. **Fabbrica/Prodotto (dati sintetici di lotto).** Baseline = the average
   footprints/SA/TSI_norm of the rows currently shown (same averaging
   `avgOf()` already does elsewhere). Sliders apply a ±50% delta to each of
   the four footprints; `SA_sim`/`TSI_norm_sim` recompute live.
2. **Impianto reale — RP7.3 (D020/D060/D240).** Baseline = one real
   plant/year row from `DATA.real_plants` (ADR-026), picked by the user.
   Sliders apply a delta to `Ψ` (±0.05 absolute, its real range is ~0.15-0.18)
   and to `Ex_ref` (±30%, a stand-in for an energy-price/consumption shock);
   `Φ_sim`/`TSI_abs_sim` recompute, and `TSI_rel_sim` too when the same
   plant's real 2023 `TSI_abs` is available as baseline.

Both panels are visually marked with a persistent "SIMULAZIONE — valori
ipotetici, non osservati" banner (distinct styling from every other tab,
which shows only real/synthetic-but-labeled data) and the Guida tab explains
the distinction from VOLT explicitly: VOLT's curves are pre-authored and
simulate the scenario's *shape* over time; here the user supplies the
hypothetical delta directly and the tool is transparent about which five
formulas it reruns.

## Consequences
- No change to `scripts/build_html_viewer.py`'s payload shape is required —
  the simulation reads `DATA.rows`/`DATA.real_plants`, already present.
- `tests/integration/test_build_html_viewer.py` is unchanged; the simulation
  logic lives entirely in `template.html` and has no server-side
  computation to unit-test. Manual verification: headless browser
  screenshot of both panels with non-zero slider deltas, confirming the
  recomputed values move and the baseline values don't.
