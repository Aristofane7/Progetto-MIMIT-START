# ADR-011 — Open formula items pending project-owner / SRC-manual confirmation

**Status:** PARTIALLY SUPERSEDED (items 1-3 by ADR-018, item 5 by ADR-020, 2026-09-01) — only item 4 (cluster-trend thresholds) remains genuinely open

This ADR tracks implementation choices made where the implementation spec names
an input/output and a source manual. **Update (ADR-018):** items 1-3 below were
written on the premise that the SRC-TEI manual "is not available as
machine-readable content in this corpus" — that premise was wrong; the manual
is a readable PDF at the repo root (`Manuale operativo – Modulo TEI‑J (beta)
per EEA+.pdf`). ADR-018 confirms items 2 and 3 were already implemented
correctly, and corrects item 1's formula. Per the project's own governance rule
(spec Appendix M — "Qualsiasi modifica di formula richiede: ADR + source
reference + test old + test new + migration/version increment + approval"),
resolving the *formula* is not the same as approving the *coefficient value* —
see ADR-018 for exactly what remains open (the real coefficient library,
"Tabella 2", is still not part of this corpus).

## 1. TEI-J quality penalty (sec. 14.7) — SUPERSEDED by ADR-018
~~`src/engines/tei/formulas.py::compute_quality_penalty` implements a shortfall
penalty `kappa * max(0, q_thr - q) * exposed_exergy`.~~ Corrected to the
manual's actual ratio-shortfall formula, `kappa * max(0, 1 - q/q_target) *
exposed_exergy` (Manuale TEI-J §4.4/5.4) — see ADR-018.

## 2. TEI-J MTO powder pricing (sec. 14.5) — CONFIRMED by ADR-018
Manual §3 confirms `Ex_SDU = m_SDU * b_SD`: pricing `m_sdu_kg` with the
`B_SDM` coefficient (same atomized-powder material) was already correct.

## 3. TEI-J specific exergy per manufactured tile (`B_TILE`) — CONFIRMED by ADR-018
Manual §3 confirms `Ex_T = N_T^man * b_T` (the manual's own Power BI example
names it `b_tile_MJex_per_pz`) — this module's `B_TILE` coefficient and
`Ex_T = N_T_man * b_tile` formula were already the right shape. Still `DRAFT`/
test-only as a coefficient *value*, pending the real Tabella 2 and
project-owner approval (ADR-018).

## 4. Cluster performance trend thresholds (sec. 20.2)
`src/product/sales/cluster_performance.py` classifies GROWTH/STABLE/DECLINE at
±5% period-over-period growth. The spec defines the enum but not the numeric
thresholds. **Action required:** project-owner approval of the actual thresholds.

## 5. P-TSA z-score golden regression (sec. 43.2) — RESOLVED by ADR-020
~~The published z-score P-TSI reference values... cannot be reproduced
without RP7.4's underlying per-type indicator matrix..., which are not part
of this corpus.~~ The repo-root PDF `RP 7.4 Report di Product Technological
Sustainability Assessment.pdf` (not examined when this item was written)
contains the full raw SCR/PsI/OCR matrix (Tabelle 3-5) and the real
per-dimension scoring data (Tabella 7). Transcribed into
`data/reference/RP7.4_indicator_matrix.csv` /
`RP7.4_dimension_scores.csv`; `test_zscore_p_tsi_matches_rp74_published_values`
is un-skipped and passing. See ADR-020.

## Process to close each item
Per Appendix M: source reference from the actual manual text → old test (this
placeholder's test) → new test (against the real formula) → version bump on the
affected engine (`engine_version`) → project-owner approval → new ADR entry
superseding this one for that item.
