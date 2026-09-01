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
