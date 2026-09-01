# ADR-017 — Stage 9 validation: what a repo-only pass can and cannot close

**Status:** ACCEPTED, 2026-09-01 — issue #9 progress, not closure

## Context

Issue #9 (spec sec. 65) asks for the final v1 checklist to be run on a
staging environment with real data before declaring the system production-
ready. Its own body already marks most items as depending on #3/#4/#5/#6/#7.
Two things were worth doing regardless of that:

1. Turn the manual checklist into something **re-runnable and truthful**
   instead of a hand-ticked markdown list a future edit could silently let
   drift from what the code actually does — the same failure mode as the
   "178 tests" number that had to be corrected earlier in this project's
   history.
2. **Actually look**, rather than assume, at what today's tests prove for
   each item. Two real, previously-invisible gaps turned up from doing this:
   - `DataQualityFinding`/lineage objects were only ever Python dataclasses
     in memory — nothing wrote them to `audit_data_quality`/`audit_lineage`,
     despite sec. 49's "an error must be persisted, never silently
     swallowed." Schema existed; the write path didn't.
   - `blocker_rules.sql`'s only test proved the seven queries are
     *syntactically valid SQL* — not that any of them actually flags a real
     violation. A rule with an always-false WHERE clause would have passed
     that test forever.
   - No `dim_baseline`-shaped config artifact existed for the baseline the
     RP7.3 aggregate model has used since ADR-012 (`baseline_year = 2022`,
     confirmed by the workbook's own sheets and validated against 66 real
     values) — unlike the coefficient/weight sets, which got that treatment
     under ADR-013. "Baseline APPROVED" (checklist item 8) had nothing to
     check.

## Decision

1. `src/core/quality/persistence.py` adds `record_finding`/`record_lineage` —
   thin, explicit SQLAlchemy Core inserts (no ORM, matching
   `src/api/repository.py`'s style). Proven by
   `tests/integration/test_audit_persistence.py`, including a lineage test
   that resolves a `mv_intelligent_industry_state` row back to its source
   fact tables (sec. 45's own definition of what lineage must do).
2. `tests/integration/test_blocker_rules_detect_violations.py` seeds real
   violating and clean rows for three of the seven blocker rules and asserts
   the query actually distinguishes them — on top of, not instead of, the
   existing syntax-only test.
3. `tests/integration/test_api_shadow_endpoints.py` gained a genuine
   multi-period historical-replay test (two `fact_eea_state` rows for the
   same plant at different periods, three distinct `at` values) — the
   existing tests only ever had one state to return, so "Historical replay
   PASS" had never actually been exercised against more than one point in
   time.
4. `config/baselines/rp73_baseline_2022.yaml` records the RP7.3 aggregate
   model's baseline as a governed artifact, status **DRAFT** — this ADR does
   **not** approve it. ADR-013's approval named only
   `COEFF_RP73_PROVISIONAL_2026` and `EEA_AHP_RP73_1`; a baseline sign-off is
   the project owner's decision to make separately, the same rule ADR-013
   itself operates under.
5. `scripts/stage9_validation_checklist.py` runs issue #9's 21-item checklist
   as actual pytest invocations and config-file reads, printing PASS/PARTIAL/
   BLOCKED with the specific evidence or blocking issue for each — never a
   hardcoded assertion. A subset of items (`gate=True`) are checks this
   repository alone should always be able to keep passing (schema, unit
   library, EEA regression, design workflow, IIDS view, replay, lineage,
   data quality, security/no-actuation); a regression there fails the
   script's exit code. Items genuinely blocked by #3/#4/#5/#6/#7, or (for
   UAT) structurally outside what a repository can execute, never gate.

## Consequences

- Running `python3 -m scripts.stage9_validation_checklist` gives a live,
  accurate count today: 10 PASS, 7 PARTIAL, 4 BLOCKED out of 21 — a
  materially stronger and more honest position than before this pass, but
  still explicitly not the "staging environment with real data" run issue #9
  asks for.
- Nothing here approves anything on the project owner's behalf: the new
  baseline artifact is DRAFT, exactly like a freshly-authored coefficient or
  weight set would be before sign-off (sec. 11.3).
- UAT and full performance validation remain permanently out of a
  code-repository's reach regardless of how many of #3-#7 land — they need
  real users and a real deployment, which is Stage 9's own point.
