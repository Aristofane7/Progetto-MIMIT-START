# RP7.3 reference data (provisional)

Real project data files, copied verbatim from the repository root, used to
validate and drive the ADR-012 aggregate EEA+/TSI model:

- `RP7.3_data_collection_20232025.xlsx` — plant master data, annual energy
  consumption, pre-aggregated TEI/EFA/EcoFA/SFA module terms, coefficient
  library, and AHP pairwise matrix for D020/D060/D240, 2022 (baseline)-2025.
- `RP7.3_calculation_log.xlsx` — 93 logged reference results (`R001`-`R093`)
  used as the golden regression target in
  `tests/regression/test_rp73_calculation_log.py`.
- `ahp_weights.xlsx` — AHP pairwise comparison matrix and resulting weights for
  the `env`/`econ`/`soc`/`tech` dimensions.

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
