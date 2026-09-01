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

**Status: provisional.** Per the `Istruzioni` sheet in the data collection file:
*"I valori inseriti sono provvisori e in corso di consolidamento con le serie
storiche definitive."* The derived coefficient set
(`config/coefficients/rp73_provisional_2026.yaml`) and weight set
(`config/weights/eea_ahp_rp73.yaml`) are loaded with `status: DRAFT` accordingly
— per spec sec. 11.3, a DRAFT set must never feed a production calc-run. See
`docs/decisions/ADR-012-...` for full derivation and the verified formulas.
