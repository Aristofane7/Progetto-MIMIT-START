# ADR-025 — D020 partial production year 2025 (option A, homologous reference)

**Status:** APPROVED by project owner (Davide Settembre), 2026-10-19

## Context

Plant **D020 (Viano)** produced for only part of 2025 and **ceased production in
July 2025** (reconversion to a logistics hub; confirmed by RP7.5 §1.2 and the
RP7.8 collaudo). From 2026 the production perimeter is D060 + D240.

The RP7.3 aggregate model (ADR-012) treated 2025 for every plant as a full year
baselined on the fixed annual 2022 row. Feeding D020's ~7 months of 2025 against
a 12-month 2022 reference would make the module contributions (`f_i`, extensive
differences in MJ) collapse artificially, i.e. the shorter exercise would read as
a large "improvement" purely because fewer months were produced.

The data-collection workbook also carried a **single** `produzione_m2` per plant
(identical for every year), so there was no way to weight a partial year by its
real output.

## Decision — option A (homologous reference)

1. **Per-year production.** The `Unita` sheet is now `(plant, year,
   produzione_m2, descrizione)`. `rp73_reference_data.py` exposes
   `production_m2(plant, year)` (with a legacy single-value fallback for the
   archived beta-1.1 workbook).

2. **Activity window.** A new optional `Periodo` sheet records
   `(plant, year, period_start, period_end, months_active)`. D020/2025 =
   `2025-01-01 .. 2025-07-31`, `months_active = 7`; everything else = 12.

3. **Homologous baseline (option A).** A new optional `Riferimento` sheet
   overrides a plant/year's module baseline with the **same calendar window of
   the reference year**. For D020/2025 the baseline is **2022 Jan–July**, not the
   annual 2022 row. The annual 2022 row is **kept unchanged** and still baselines
   D020's 2023 and 2024. Options **B** (per-m² normalization) and **C** (drop
   D020/2025) were considered and rejected.

4. **Duration guard.** `compute_aggregate_state` raises a
   `TEMPORAL_MISMATCH` blocker if a plant/year's window length differs from its
   baseline's (e.g. a 7-month current period against a 12-month annual baseline
   with no homologous override). A matching SQL diagnostic was added to
   `sql/quality_checks/blocker_rules.sql`. This operationalizes the rule that
   extensive quantities must only be compared over equal-length windows.

5. **Comparability of the result.** Because reference and current period use the
   same window, the **intensive ratios are invariant**: D020/2025 `TSI_abs`,
   `Φ`, `Ψ` and `TSI_rel` are unchanged vs. beta-1.1 (`TSI_abs = 0.118`,
   `Φ = 0.072`, `Ψ = 0.164`, `TSI_rel = 1.361`). The **extensive** quantities
   (`f_env/f_econ/f_soc/f_tech`, `SA_raw`, `SA_w`, `Ex_ref`, production) scale to
   the ~7-month window (e.g. `Ex_ref` 184,300 → 115,556 GJ) and are **not
   comparable** with the full-year plants. The Group mean, previously weighted by
   a constant production, now uses per-year production, so D020/2025 weighs by its
   real period output (Group `TSI_rel` 1.3415 → 1.3394; ordering D240 > D060 >
   D020 and the 1.32–1.36 interval unchanged).

6. **Source of the 2025/2022 period values — provisional, non-golden.** The real
   measured period data were **not available** when this ADR was applied. The
   values currently in the workbook are provisional, generated **only to exercise
   the model** (project owner, 2026-10-19). They are the Jan–July share of a
   seasonal monthly production profile (`FRAC = 0.627`, **not** a flat 7/12
   month-fraction, which would be forbidden reproportioning — spec sec. 64). The
   exact missing inputs are itemized in
   `data/reference/RP7.3_D020_partial_year_data_collection.xlsx`; they are to be
   replaced by real measured values for D020 **Jan–cessation 2025** and the
   **homologous 2022 Jan–July** window before project close. Until then these six
   D020/2025 numbers are not a golden acceptance data point.

   **Update (2026-10-19): real data delivered and loaded.** The project owner
   supplied the measured D020 period data (ERP/MES/HSE consolidation; cessation
   **2025-07-31**; both windows Jan 1 → Jul 31, 212 days). They replaced the
   provisional values via `python3 -m scripts.load_d020_real_period_data`; the log
   is now **beta-1.3**. D020 is confirmed MTO-only (`loss_MTS = qual_MTS = 0`).
   Result (real): D020/2025 `TSI_abs = 0.1212`, `TSI_rel = 1.398`,
   `Ex_ref = 114,990 GJ`, `Ψ = 0.164`; Group `TSI_rel = 1.345`; ordering by
   `TSI_abs` still D240 > D060 > D020. Note for RP7.3 RV.2: with real data the
   per-plant `TSI_rel` interval widens to ≈ 1.32–1.40 (D020's 1.398 is the
   highest, i.e. D020 improved most vs. its 2023 baseline), so the previous
   "1.32–1.36" wording must be corrected.

7. **Governance unchanged.** The APPROVED `COEFF_RP73_PROVISIONAL_2026` /
   `EEA_AHP_RP73_1` sets are **untouched** (only data changed, not coefficients —
   sec. 11.3 point 4). The previous golden log (`beta-1.1`) and its workbook are
   archived under `tests/fixtures/rp73/` and pinned by
   `tests/regression/test_rp73_calculation_log_beta_1_1_fixture.py` for
   traceability; the live `RP7.3_calculation_log.xlsx` is bumped to **beta-1.2**
   and remains the golden target of
   `tests/regression/test_rp73_calculation_log.py`. The migration is scripted and
   reproducible: `python3 -m scripts.apply_adr015_d020_partial_year`.

## Consequences

- The model now represents partial production years correctly without letting a
  shorter exercise masquerade as efficiency, and weights the Group mean by real
  per-year output.
- Both mirror copies (repo root + `data/reference/`) of the workbook and the log
  are updated to beta-1.2.
- Downstream documents that consume RP7.3 values must be regenerated once the
  real period data land: **RP7.8** (Intelligent Industry collaudo — Group
  `TSI_abs`/`TSI_rel`, KPI table) and **RP8.6** (impact assessment, if it uses
  D020 2025 EEA+ quantities). **RP7.4** is unaffected (T1/T2 on D060, T3 on D240).
- Closure is pending the real measured period data (criterion in the instruction
  §8); the structural change, guards, tests, and governance are complete.

**Nota di numerazione (questa integrazione, 2026-10-19):** questa decisione è
stata sviluppata in un branch parallelo dove era numerata "ADR-015"; qui prende
il numero ADR-025, il successivo libero in questo branch. Gli script
`scripts/apply_adr015_d020_partial_year.py` e i riferimenti `ADR-015` interni al
loro output Excel (celle/commenti generati) mantengono il nome/numero
originale — non sono stati rinominati per non invalidare la tracciabilità del
log beta-1.2/beta-1.3 già generato; ogni altro riferimento in commenti di
codice, test e SQL è stato aggiornato a ADR-025.
