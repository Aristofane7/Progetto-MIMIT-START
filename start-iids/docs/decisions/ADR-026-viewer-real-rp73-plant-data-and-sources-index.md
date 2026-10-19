# ADR-026 — Viewer: real RP7.3 plant-level data and a discovered sources index

**Status:** ACCEPTED — extends ADR-023/ADR-024

## Context
By 2026-10-19 the project's partial reports ("relazioni parziali", RP) had
moved forward in several parallel development branches not yet merged to
`main`, including a real-data update to the RP7.3 aggregate model (D020's
partial production year 2025, ADR-025, ported into this branch from
`claude/sleepy-pasteur-yddrv2`) and new finished RP deliverables (RP 7.5,
RP 7.8, among others listed in ADR-025's consequences). The user asked for
two concrete updates to the HTML viewer: surface the real RP7.3 data, and
reference the relazioni now deposited in the repository.

## Decision

### 1. ADR-025 ported and renumbered
The D020 partial-year reconciliation (homologous same-window baseline,
option A) was developed in a sibling branch under the number "ADR-015",
which collides with this branch's own ADR-015 (RP6.8 master data import —
an unrelated decision). It is renumbered **ADR-025** here; every code/test/SQL
comment referencing it was updated accordingly. The migration scripts
(`scripts/apply_adr015_d020_partial_year.py`,
`scripts/load_d020_real_period_data.py`) keep their original filenames —
renaming them would invalidate the traceability of the already-generated
beta-1.2/beta-1.3 log, which bakes the original label into generated Excel
cells (see the numbering note at the end of ADR-025's own file).

One pre-existing regression (`test_ex_useful_from_report_matches_psi_times_ex_ref_from_log`)
exercised a cross-check between the live `Ex_ref`/`Psi` and a value
transcribed from the *original* (full-year) RP7.3 report's Tabella 4. Since
D020/2025 is now a 7-month partial period, that cell's extensive quantities
are no longer on the same footing as the full-year transcription — exactly
the comparability caveat ADR-025 itself documents — and the regenerated
RV.2 report replaced the Ex_useful column with Ψ reported directly, so there
is no updated full-year-equivalent figure to re-anchor the check on. The
D020/2025 case is excluded from this one parametrized test with a comment
pointing back to ADR-025, rather than silently changed.

### 2. A real plant-level panel in the viewer, kept separate from synthetic data
`scripts/build_html_viewer.py::_load_real_plant_data()` runs the exact same
production path as the golden regression
(`tests/regression/test_rp73_calculation_log.py`) —
`load_rp73_reference_data`/`load_rp73_calculation_log` +
`compute_aggregate_state` against the `APPROVED` coefficient/weight sets —
for the 3 real plants (D020/D060/D240, 2022-2025) and exposes it as
`DATA.real_plants`. The Fabbrica tab renders it as its own card, explicitly
labeled as plant/year-level real data, **never merged or averaged together**
with the synthetic per-lot rows shown above it in the same tab (sec. 39: BI
is not a calculation engine; mixing two different granularities would also
misrepresent both). D020/2025's partial period is visually flagged (row
highlight + a "parziale (N mesi)" label) and the accompanying note repeats
ADR-025's comparability caveat: intensive ratios (Φ/Ψ/TSI) are comparable,
extensive quantities (SA_w, Ex_ref) are not.

### 3. A sources index discovered by filename, not hand-maintained
`_discover_sources()` scans the repository root for `RP*`/`Attività*`
`.pdf`/`.docx` files (excluding the literal template placeholder) and lists
them in the Guida tab. This was chosen over a hand-written list for the same
reason the glossary and the Edificio placeholder are grounded in real
artifacts rather than authored prose: a static list would drift out of sync
or imply a document exists when it does not. The scope of this ADR brought
in only the single-file RP7.3/7.5/7.8 deliverables from the sibling branch
that developed ADR-025 (no path collisions with this repository); several
other in-progress branches (RP 7.6, a draft RP 7.9, RP 8.6's own docx
rebuild, "Attività 7.10") were deliberately **not** merged here — they carry
their own scratch project scaffolding (own `README.md`/`.gitignore`/scripts)
that would collide with or shadow this repository's own root files, and are
a separate consolidation decision, not an HTML-viewer update.

## Tests
Full suite re-run after the port: 274 passed (up from 263; +9 from the
ported RP7.3/D020 real-data tests, +2 new viewer tests for `real_plants`/
`sources`), 0 skipped. `_load_real_plant_data()` and `_discover_sources()`
verified directly (9 plant/year rows, D020/2025 flagged partial; sources
list matches the repository root's actual `RP*` files).
