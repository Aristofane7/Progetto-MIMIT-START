# RP7.3 reference data (provisional)

Real project data files, copied verbatim from the repository root, used to
validate and drive the ADR-012 aggregate EEA+/TSI model:

- `RP7.3_data_collection_20232025.xlsx` — plant master data (**per-year**
  production, ADR-025), annual energy consumption, pre-aggregated
  TEI/EFA/EcoFA/SFA module terms, coefficient library, and AHP pairwise matrix
  for D020/D060/D240, 2022 (baseline)-2025. Since **ADR-025** it also carries a
  `Periodo` sheet (activity window / `months_active` per plant/year) and a
  `Riferimento` sheet (homologous same-window baseline — option A — for
  D020/2025, the Jan-July period after D020's July 2025 cessation).
- `RP7.3_calculation_log.xlsx` — 93 logged reference results (`R001`-`R093`),
  **beta-1.3** (ADR-025, D020/2025 now the partial-period, homologous-baselined
  figures), the golden target of `tests/regression/test_rp73_calculation_log.py`.
- `RP7.3_D020_partial_year_data_collection.xlsx` — the **filled**
  data-collection sheet (delivered by the project owner 2026-10-19, ERP/MES/HSE)
  with the real measured D020 Jan-cessation 2025 and homologous 2022 Jan-July
  inputs now loaded into the model (ADR-025 §6).
- `ahp_weights.xlsx` — AHP pairwise comparison matrix and resulting weights for
  the `env`/`econ`/`soc`/`tech` dimensions.

The previous **beta-1.1** workbook and log are archived under
`tests/fixtures/rp73/` and pinned by
`tests/regression/test_rp73_calculation_log_beta_1_1_fixture.py`. The migration
is scripted: `python3 -m scripts.apply_adr015_d020_partial_year` builds the
ADR-025 structure (beta-1.2, provisional values); `python3 -m
scripts.load_d020_real_period_data` loads the real measured data (**beta-1.3**).
Both mirror copies (repo root and this folder) are kept in sync (identical md5).
(The script module names keep their original `adr015` label from the branch
where this was developed — see the numbering note in
`docs/decisions/ADR-025-d020-partial-year-2025.md`.)

**Data collection round: still labeled provisional by its own source.** Per
the `Istruzioni` sheet in the data collection file: *"I valori inseriti sono
provvisori e in corso di consolidamento con le serie storiche definitive."*

**Derived coefficient/weight sets: APPROVED (ADR-013, 2026-09-01).** The
project owner (Davide Settembre) has explicitly signed off on using
`config/coefficients/rp73_provisional_2026.yaml`
(`COEFF_RP73_PROVISIONAL_2026`) and `config/weights/eea_ahp_rp73.yaml`
(`EEA_AHP_RP73_1`) for current calculations — see `docs/decisions/ADR-013-...`
for the exact scope of that approval (it covers only these two sets, not the
granular per-lot coefficients tracked in ADR-011). See `docs/decisions/ADR-012-...`
for the full model derivation and the verified formulas.

**`Psi`/`Ex_useful`: resolved (ADR-019, issue #5).** The repo-root PDF
`RP7.3 Report di Assessment termodinamico della fabbrica.pdf` — the actual
narrative report these two xlsx files are the data for, not examined when
ADR-012 was first written — confirms `Ex_ref = Ex_el + Ex_fuel` (a second,
independent source for what was already implemented) and states that
`Ex_useful`'s decomposition via a production coefficient is deliberately
deferred to a future "release" version of the methodology, not missing from
this beta. `Psi` stays a directly reported input by design, not as a
stopgap — see ADR-019 and the added
`test_ex_useful_from_report_matches_psi_times_ex_ref_from_log` regression
test.

## RP7.4 P-TSA indicator matrix (issue #6, ADR-020)

- `RP7.4_indicator_matrix.csv` — the real SCR/PsI/OCR raw values for the 3
  product types (T1/T2/T3), transcribed verbatim from Tabelle 3-5 of
  `RP 7.4 Report di Product Technological Sustainability Assessment.pdf`
  (repo root). Metric codes match `IOA_METRICS`/`OP_METRICS`/`TQ_METRICS` in
  `src/engines/ptsa/formulas.py` exactly.
- `RP7.4_dimension_scores.csv` — the real per-dimension 1-5 scores
  (`S_IOA`/`S_OP`/`S_TQ`), `P-TSI(5)`, and `TII` per type, from Tabella 7.
- Together these un-skip `tests/regression/test_ptsa_golden_reference.py`'s
  z-score P-TSI golden regression (sec. 43.2's published -0.047/-0.115/
  +0.162) — see `docs/decisions/ADR-020-...` for how this was found.

## RP6.8 product cluster master data (issue #7, ADR-015)

- `rp68_cluster_master.csv` — the 22 real product clusters, transcribed
  verbatim from `RP6.8 Report di Product Analysis_30-04-25.pdf` (repo root),
  product counts cross-checked to sum to exactly 13,251. One cluster (11) has
  a documented source-data defect and one (13) a minor source discrepancy —
  see the `data_quality_flag` column and `docs/decisions/ADR-015-...`.
- `rp68_master_seed.sql` — generated INSERT statements for
  `dim_product_cluster` (`cluster_version = RP68_2025_04`). Regenerate with
  `python3 -m scripts.import_rp68_product_master_data`.
- **Not present, and not reconstructable from the PDF:** the full
  13,251-product export with per-product cluster assignment that RP6.8 sec.
  3.7 names as an existing deliverable. `scripts/import_rp68_product_master_data.py
  --products-csv <file>` is ready to validate and load it once supplied.
