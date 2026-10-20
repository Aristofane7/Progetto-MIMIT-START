# ADR-019 — Psi / Ex_useful resolved via the primary RP7.3 report

**Status:** ACCEPTED, 2026-09-01 — closes issue #5 / ADR-012's open item

## Context

ADR-012 flagged one open item: `Psi = Ex_useful / Ex_ref` is logged directly
in `RP7.3_calculation_log.xlsx`, but no sheet in the corpus examined at the
time defined `Ex_useful` or a coefficient to derive it from production
output. Issue #5 asked to confirm the formula with the project owner/RP7.3
authors, obtain or approve the missing coefficient, and implement
`compute_ex_useful` — explicitly forbidding reverse-engineering a coefficient
just to make the numbers match (spec sec. 64).

This is the same pattern as issues #4 and #7: a primary source assumed
unavailable was sitting in the repository the whole time.
`RP7.3 Report di Assessment termodinamico della fabbrica.pdf` (repo root) is
the actual narrative report for Activity 7.3 — the two xlsx files ADR-012
used are its underlying data, not the report itself, and nobody had read the
PDF when ADR-012 was written.

## What the report confirms

**Sec. 2.3 ("Componente exergetica")**, verbatim:

> *"Il throughput exergetico dei vettori energetici è calcolato secondo la
> Eq. (18). L'exergia del combustibile è trattata come exergia chimica
> (b_fuel ≈ 42 MJ/Nm³), tenendo l'efficienza di conversione all'interno di Ψ
> e non nel denominatore Ex_ref = Ex_el + Ex_fuel. L'efficienza exergetica di
> secondo principio è Ψ = Ex_useful/Ex_ref (Eq. 17, destra)."*

Two things follow directly:

1. **`Ex_ref = Ex_el + Ex_fuel` is now confirmed by a second, independent
   primary source** (Eq. 18) — not just the calculation log. This is exactly
   what `compute_ex_ref_mj` already implements; no code change needed, only
   a stronger source citation.
2. **The conversion efficiency that would turn `Ex_useful` into a derived
   quantity is *deliberately* kept inside Ψ, not factored out as a
   coefficient**, in this (beta) version of the methodology. This is not an
   omission ADR-012 needed to chase down — it is how the RP7.3 authors
   designed the beta model.

**Sec. 4.5 ("Conclusioni") / "Significato più ampio e prospettive"** confirms
this is intentional, not an accident, by naming the decomposition as future
work: *"Il percorso verso la versione release riguarderà il consolidamento
della libreria dei coefficienti su dati primari ed EPD, l'estensione del
calcolo a granularità di linea e di lotto..."* — i.e. deriving `Ex_useful`
from a production coefficient is explicitly release-version scope, not
something missing from the beta this repository implements.

**Tabella 4 ("Bilancio exergetico")** gives the real `Ex_el`, `Ex_fuel`,
`Ex_ref`, `Ex_useful`, and `Ψ` for all 9 plant-years (D020/D060/D240 ×
2023-2025) — the same underlying numbers as `RP7.3_calculation_log.xlsx`
(e.g. D020/2023's `Ψ=0.154` matches the log's `R009`), now with the
`Ex_useful` column explicitly labeled, closing exactly the semantic gap
ADR-012 hit.

**Tabella 3 ("Risultati AHP")** independently reproduces the exact AHP
weights already in `config/weights/eea_ahp_rp73.yaml`
(env=0.3661, econ=0.1451, soc=0.0955, tech=0.3934, CR=0.0169) — a second,
free cross-check that those weights were transcribed correctly.

## Decision

1. `compute_ex_useful` is **not** implemented. Per the source's own
   methodology (sec. 2.3/4.5), there is no coefficient to derive it from in
   the beta version — implementing one now would mean inventing what the
   RP7.3 authors themselves say doesn't exist yet, exactly what issue #5 and
   spec sec. 64 forbid.
2. `compute_psi_efficiency` stays a documented pass-through of a directly
   reported `Psi` value — now confirmed correct by design, not merely
   "not yet disproven." Docstring updated to cite this ADR instead of
   describing an open question.
3. `tests/regression/test_rp73_calculation_log.py` gains
   `test_ex_useful_from_report_matches_psi_times_ex_ref_from_log`,
   transcribing Tabella 4's `Ex_useful` values (`EX_USEFUL_GJ_TABELLA4`) and
   asserting `Psi * Ex_ref` (both already validated against the calculation
   log) reproduces them for all 9 real plant-years — cross-source proof that
   the log's `Psi` was never fabricated, using two independently-formatted
   real artifacts rather than one.
4. `compute_ex_ref_mj`'s docstring now cites Eq. 18 of this report alongside
   the calculation log.

## Consequences

- Issue #5 closes without needing to interrupt the project owner for a
  confirmation the primary source already gives in writing.
- The `Ex_useful`-from-production-coefficient work RP7.3 sec. 4.5 describes
  remains a legitimate, named future item — for the "release" version, not
  this beta implementation. If/when that coefficient is defined and
  approved, `compute_ex_useful` should be added then, under a new ADR, per
  Appendix M.
- No governance rule is bypassed: no coefficient was invented, and nothing
  here needed project-owner sign-off (there is no new value or formula being
  approved — only a "no such derivation exists yet" fact confirmed from a
  primary text already in this repository).
