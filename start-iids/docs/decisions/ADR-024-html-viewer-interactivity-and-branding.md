# ADR-024 — HTML viewer: interactivity, glossary, real "scenario" scope, and START branding

**Status:** ACCEPTED — extends ADR-023

## Context
After the first alpha-0 HTML viewer (ADR-023), the user asked for four
concrete improvements: more interactivity including "scenario analysis",
every integrated metric/indicator shown by full name (not just acronyms
like `IOAI`/`TQI`/`SA`), inline field explanations, and a dedicated
"guida all'uso" (user guide) page. The user also provided the real START
project logo (a green pyramid-in-square mark) and asked to adopt the same
color palette.

## Decision

### 1. Branding
The viewer's header now uses the real START logo (inline SVG, no external
asset) and a green (`#67C271`) brand palette replacing the placeholder
teal, with a light header to match the logo's own white background rather
than the previous dark bar.

### 2. Glossary (not just acronyms)
`GLOSSARY` in `scripts/build_html_viewer.py` is the single source of truth
for every metric's full name, unit, and plain-language definition —
grounded in the implementation spec sections and engine docstrings
(`src/engines/eea/formulas.py` sec. 18, `src/engines/ptsa/formulas.py`
sec. 24), never invented. Where the spec itself never expands an acronym
(`TII`, sec. 24.10), the glossary describes it by formula/purpose instead
of guessing words behind the letters. The template's `gl(key, {short})`
helper renders a short or full label with a hover tooltip pulled from this
same dict, so there is exactly one place to fix a definition. Compact
contexts (KPI tiles, table headers) use the short form with tooltip;
wider contexts (the period-comparison table, the Integrata columns, the
new Guida tab) show the full name.

### 3. "Scenario analysis" — grounded in what's real, not invented
The user's request was modeled on the sibling project VOLT, which
simulates supply-chain disruption scenarios (S1-S4) with impact curves.
**This domain has no equivalent model** — no disruption/what-if model for
a ceramic factory exists in the spec or this corpus, and inventing one
would violate sec. 64 ("non fabbricare input per far tornare i valori").
Instead, "scenario" here means two things genuinely supported by existing
data:

1. **CURRENT/HISTORICAL toggle** — `fact_production_lot.scenario` (sec. 46,
   already `CHECK IN ('HISTORICAL','CURRENT')` since migration `0003`) is
   now passed through `mv_intelligent_industry_state` (mirroring the
   `channel_id` passthrough pattern, ADR-022) and exposed as a filter chip
   on the Fabbrica page.
2. **Period comparison** — a "Confronta due periodi" control lets the user
   pick any two `period_start` values from the real data and shows
   SA/TSI_norm/footprint deltas between them (percentage change, computed
   client-side as a plain average+ratio over already-computed columns —
   the same kind of arithmetic a Power BI `AVERAGE` measure would do, not
   a new calculation, sec. 39).

The Guida tab states this distinction explicitly so nobody mistakes it for
a disruption simulator.

### 4. "Guida all'uso" tab
A new tab explains: what the tool is, how to navigate each page, what
synthetic vs. real data provenance means (tied to the existing
`dataset_label`/`data_note` mechanism), the honest scope of "scenario"
above, a table of known gaps (mirroring ADR-023/report_pages_spec.md's own
"known gaps" sections, not re-litigated separately), and the full glossary
table.

## Tests
`tests/integration/test_build_html_viewer.py` — extended: every metric
acronym shown in the template resolves to a glossary entry with a
non-empty full name and description; the `scenario` passthrough only ever
takes the two real values (`CURRENT`/`HISTORICAL`), never a fabricated one.
