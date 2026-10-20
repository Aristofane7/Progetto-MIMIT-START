# ADR-020 — RP7.4 report found; P-TSA z-score golden regression un-skipped

**Status:** ACCEPTED, 2026-09-01 — closes issue #6 / ADR-011 item 5

## Context

ADR-011 item 5 and issue #6 both stated that the raw per-type indicator
matrix (9 SCR/PsI/OCR metrics × population statistics) behind RP7.4's
published z-score P-TSI values (T1=-0.047, T2=-0.115, T3=+0.162, spec sec.
43.2) was not part of this corpus, and that fabricating inputs to hit those
targets is forbidden (spec sec. 64). `test_zscore_p_tsi_matches_rp74_published_values`
was marked `skip` pending "IT/RP7.4 authors" supplying that dataset.

Same blind spot as issues #4, #5, and #7: nobody had opened
`RP 7.4 Report di Product Technological Sustainability Assessment.pdf`
(repo root) — the actual narrative report for Activity 7.4, present the
whole time. It contains exactly the missing data:

- **Tabella 1**: the three product types (T1=7.4mm, T2=8.2mm, T3=20mm; EPD-
  sourced, ISO 14025/EN 15804+A2).
- **Tabelle 3-5**: the real raw SCR (3 metrics), PsI (3 metrics), and OCR (3
  metrics) values for all three types — the exact 9×3 indicator matrix ADR-011
  said was missing.
- **Tabella 6**: the resulting z-scores (IOAI/OPI/TQI/P-TSI_z) per type —
  reproducing sec. 43.2's published targets exactly.
- **Tabella 7**: the scoring/AHP method's real per-dimension scores
  (S_IOA/S_OP/S_TQ), P-TSI(5), and TII per type, plus the AHP weights
  (α_IOA=0.1634, α_OP=0.2970, α_TQ=0.5396, CR=0.0079) — already the exact
  constants `RP74_ALPHA_IOA`/`RP74_ALPHA_OP`/`RP74_ALPHA_TQ`/
  `RP74_CONSISTENCY_RATIO` pinned in the (previously self-consistency-only)
  regression test, now independently confirmed correct.

## Decision

1. `data/reference/RP7.4_indicator_matrix.csv` — the 27 raw values from
   Tabelle 3-5, one row per (product_type_id, metric_code), transcribed
   verbatim. Metric codes match `IOA_METRICS`/`OP_METRICS`/`TQ_METRICS`
   already defined in `src/engines/ptsa/formulas.py` exactly — the engine's
   original metric taxonomy anticipated this data shape correctly.
2. `data/reference/RP7.4_dimension_scores.csv` — Tabella 7's `S_IOA`/`S_OP`/
   `S_TQ`/`P_TSI_5`/`TII_pct` per type.
3. `tests/regression/test_ptsa_golden_reference.py` is rewritten to:
   - compute population mean/stdev (sec. 24.5's N-divisor formula, matching
     RP7.4 sec. 2.5) for each of the 9 metrics across the 3 real product
     types, then z-scores, subindices, and `P-TSI_z`, via the existing
     `compute_zscore`/`compute_subindex`/`compute_p_tsi_z` — no new formula
     code needed, only real inputs;
   - un-skip `test_zscore_p_tsi_matches_rp74_published_values`, now backed
     by real data (`abs=5e-3` tolerance for the source table's own 2-3
     decimal rounding);
   - add `test_subindex_z_matches_rp74_tabella6`, checking the intermediate
     IOAI/OPI/TQI subindices too, not just the final P-TSI_z;
   - add `test_ahp_weighted_sum_matches_rp74_real_dimension_scores`, using
     Tabella 7's real `S_IOA`/`S_OP`/`S_TQ` instead of the old
     uniform-score back-solve;
   - keep the original `test_ahp_weighted_sum_formula_is_consistent_with_rp74_reference`
     as the "old test" of record per Appendix M, now explicitly noted as
     superseded in strength (not deleted — it still proves the arithmetic in
     a degenerate case).
4. ADR-011 item 5 is marked resolved (see that file).

## Consequences

- The P-TSA regression suite goes from 1 skipped test (with only a
  self-consistency probe backing the scoring method) to 18 passing tests
  backed by real RP7.4 data, covering both the z-score (primary KPI) and
  scoring/AHP (secondary) methods end-to-end, at both the subindex and
  final-index level.
- No coefficient or input was invented: every number in the two new CSVs is
  a direct transcription, cross-checked against the report's own downstream
  tables (Tabella 6/7) the same way ADR-015/ADR-019 cross-checked their
  sources.
- `docs/ROADMAP.md`'s "P-TSA z-score golden regression blocked on RP7.4
  dataset" note and acceptance criterion 30's "P-TSA z-score targets remain
  blocked" caveat are both stale as of this ADR — updated accordingly.
