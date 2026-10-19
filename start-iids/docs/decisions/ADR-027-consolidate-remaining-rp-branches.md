# ADR-027 — Consolidate the remaining RP deliverable branches

**Status:** ACCEPTED — extends ADR-026

## Context
After ADR-025/ADR-026 (RP7.3 RV.2/D020), four more development branches held
finished or in-progress "Relazione Parziale" deliverables not yet on `main`:
`claude/wizardly-fermi-vyp490` (RP 7.6), `claude/rp-7-9-ceramiche-report-og91dw`
(RP 7.9, still a draft), `claude/assessment-impatto-start-2gpd8z` (RP 8.6,
a from-scratch rebuild as its own small project), and
`claude/attivita-7-10-relazione-9ltbw8` (Attività 7.10, also its own small
project). None of these touch `start-iids/` engine code.

## Decision
Each branch's actual deliverable content was brought in with
`git checkout <branch> -- <paths>`, never a full branch merge, to avoid two
specific hazards found by inspecting their diffs first:

1. **Resurrected deletions.** All four were forked before `main` deleted two
   superseded RP6.9 files (`RP6.9 Annesso_Protocollo...`/`RP6.9 Report di
   Data-driven Product Design...`); a full merge would have resurrected them.
   Only the genuinely new files were taken.
2. **Root-level scratch-project collisions.** `claude/attivita-7-10-relazione-9ltbw8`
   is its own small, from-scratch project (own `README.md`, `.gitignore`,
   `requirements.txt`, `scripts/`, `src/`) built directly at the repository
   root. Taking it as-is would have planted a second, unrelated `README.md`/
   `.gitignore` at the root (this repository currently has none of its own —
   so there would be no overwrite, but adopting a mini-pipeline's own
   housekeeping files as if they described the whole repository would still
   be misleading) and a `docs/`/`scripts/`/`src/` sitting loose next to this
   repository's actual `start-iids/` tree. Its deliverable content (the
   `.docx`/`.md` report, figures, format-reference template) was moved into
   a new `Attivita_7.10/` folder instead — the same isolation pattern
   `claude/assessment-impatto-start-2gpd8z` already used on its own
   (`RP8.6/`), which needed no changes at all.

`RP 7.6` and `RP 7.9` are single loose files at the repository root, the
same pattern as the RP7.3/7.5/7.8 files ADR-026 already added — no
isolation needed. RP 7.9's filename is still `...draft.docx`: it is listed,
not hidden, but flagged.

`scripts/build_html_viewer.py::_discover_sources()` (ADR-026) is extended to
also look one directory level into any root entry whose name matches the
RP/Attività pattern (covering `RP8.6/` and `Attivita_7.10/`), still never
into `start-iids/` itself, and to flag any filename containing "draft" so
the Guida tab shows "(bozza)" next to it rather than presenting it as
equivalent to a finished relazione. Two known non-deliverable template files
(the root blank RP template, `Attivita_7.10/docs/assets/rp_format_reference.docx`)
are excluded by name, the same way the blank RP template already was.

## Consequences
- The sources index in the viewer's Guida tab now lists RP 7.6, RP 7.9
  (flagged as draft), RP 8.6 (the rebuilt `.docx`), and Attività 7.10,
  alongside everything ADR-026 already added.
- `RP8.6/` and `Attivita_7.10/` each carry their own throwaway
  pipeline (requirements.txt, ad hoc scripts) — out of scope for this ADR to
  harmonize with `start-iids/`'s own tooling; they are deliverable archives,
  not part of this repository's tested codebase.
- The competing, independent RP7.4 rebuild found in
  `claude/product-sustainability-assessment-ueb7dp` was deliberately **not**
  brought in: this repository's RP7.4 work is already resolved against the
  real report data (ADR-020), and that branch's own synthetic dataset/pipeline
  would just be a second, unreconciled source of truth for the same
  deliverable.
