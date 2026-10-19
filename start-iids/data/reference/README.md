# RP7.3 reference data (provisional)

Real project data files, copied verbatim from the repository root, used to
validate and drive the ADR-012 aggregate EEA+/TSI model:

- `RP7.3_data_collection_20232025.xlsx` — plant master data (**per-year**
  production, ADR-015), annual energy consumption, pre-aggregated
  TEI/EFA/EcoFA/SFA module terms, coefficient library, and AHP pairwise matrix for
  D020/D060/D240, 2022 (baseline)-2025. Since **ADR-015** it also carries a
  `Periodo` sheet (activity window / `months_active` per plant/year) and a
  `Riferimento` sheet (homologous same-window baseline — option A — for D020/2025,
  which is the Jan–July period after D020's July 2025 cessation).
- `RP7.3_calculation_log.xlsx` — 93 logged reference results (`R001`-`R093`),
  **beta-1.3** (ADR-015, D020/2025 now the partial-period, homologous-baselined
  figures), the golden target of `tests/regression/test_rp73_calculation_log.py`.
- `RP7.3_D020_partial_year_data_collection.xlsx` — the **filled** data-collection
  sheet (delivered by the project owner 2026-10-19, ERP/MES/HSE) with the real
  measured D020 Jan–cessation 2025 and homologous 2022 Jan–July inputs now loaded
  into the model (ADR-015 §6).
- `ahp_weights.xlsx` — AHP pairwise comparison matrix and resulting weights for
  the `env`/`econ`/`soc`/`tech` dimensions.

The previous **beta-1.1** workbook and log are archived under
`tests/fixtures/rp73/` and pinned by
`tests/regression/test_rp73_calculation_log_beta_1_1_fixture.py`. The migration is
scripted: `python3 -m scripts.apply_adr015_d020_partial_year` builds the ADR-015
structure (beta-1.2, provisional values); `python3 -m scripts.load_d020_real_period_data`
loads the real measured data (**beta-1.3**). Both mirror copies (repo root and
this folder) are kept in sync (identical md5).

**Data collection round: still labeled provisional by its own source.** Per
the `Istruzioni` sheet in the data collection file: *"I valori inseriti sono
provvisori e in corso di consolidamento con le serie storiche definitive."*

**Derived coefficient/weight sets: APPROVED (ADR-013, 2026-09-01).** The
project owner (Davide Settembre) has explicitly signed off on using
`config/coefficients/rp73_provisional_2026.yaml`
(`COEFF_RP73_PROVISIONAL_2026`) and `config/weights/eea_ahp_rp73.yaml`
(`EEA_AHP_RP73_1`) for current calculations — see `docs/decisions/ADR-013-...`
for the exact scope of that approval (it covers only these two sets, not the
granular per-lot coefficients tracked in ADR-011, and it does not resolve the
`Psi`/`Ex_useful` open item). See `docs/decisions/ADR-012-...` for the full
model derivation and the verified formulas.
