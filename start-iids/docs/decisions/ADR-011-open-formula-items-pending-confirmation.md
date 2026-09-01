# ADR-011 — Open formula items pending project-owner / SRC-manual confirmation

**Status:** OPEN — implemented as best-effort ARCH placeholders, flagged in code

This ADR tracks implementation choices made where the implementation spec names
an input/output and a source manual, but the corresponding manual's full text is
not available as machine-readable content in this corpus (only referenced PDF
filenames: `SRC-TEI`, `SRC-EFA`, `SRC-ECO`, `SRC-SFA`, `SRC-RP74`). Per the
project's own governance rule (spec Appendix M — "Qualsiasi modifica di formula
richiede: ADR + source reference + test old + test new + migration/version
increment + approval"), none of the following should be treated as production
sign-off; each is implemented defensively (fails closed / never silently guesses)
and documented in-line at its point of use.

## 1. TEI-J quality penalty (sec. 14.7)
`src/engines/tei/formulas.py::compute_quality_penalty` implements a shortfall
penalty `kappa * max(0, q_thr - q) * exposed_exergy`. The manual's exact
algebraic form is referenced but not transcribed in the spec beyond naming its
three inputs (`q`, `q_thr`, `kappa`). **Action required:** confirm against
SRC-TEI before using in a production sign-off calculation.

## 2. TEI-J MTO powder pricing (sec. 14.5)
The minimal MTO dataset carries `m_SDU` (powder used) while the loss formula
names `Ex_SDM`. This implementation prices `m_sdu_kg` using the `B_SDM`
coefficient (same atomized-powder material). **Action required:** confirm this
identification against SRC-TEI.

## 3. TEI-J specific exergy per manufactured tile (`B_TILE`)
`Ex_T = N_T_man * b_tile` requires a specific-exergy-per-tile coefficient not
named explicitly in sec. 14. `B_TILE` is introduced as a new `TEI`-domain
coefficient code, to be populated in an APPROVED `dim_coefficient` set.

## 4. Cluster performance trend thresholds (sec. 20.2)
`src/product/sales/cluster_performance.py` classifies GROWTH/STABLE/DECLINE at
±5% period-over-period growth. The spec defines the enum but not the numeric
thresholds. **Action required:** project-owner approval of the actual thresholds.

## 5. P-TSA z-score golden regression (sec. 43.2)
The published z-score P-TSI reference values (T1=-0.047, T2=-0.115, T3=+0.162)
cannot be reproduced without RP7.4's underlying per-type indicator matrix and
population statistics, which are not part of this corpus. Per spec sec. 64
("Non fabbricare input per far tornare i valori"), `tests/regression/
test_ptsa_golden_reference.py::test_zscore_p_tsi_matches_rp74_published_values`
is marked `skip` rather than backed by fabricated inputs. **Action required:**
obtain the RP7.4 dataset (or an IT-equivalent) as a `tests/fixtures/` file.

## Process to close each item
Per Appendix M: source reference from the actual manual text → old test (this
placeholder's test) → new test (against the real formula) → version bump on the
affected engine (`engine_version`) → project-owner approval → new ADR entry
superseding this one for that item.
