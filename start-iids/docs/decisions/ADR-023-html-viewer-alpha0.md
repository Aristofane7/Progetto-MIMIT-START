# ADR-023 — HTML self-contained viewer as the v1 "alpha 0" BI deliverable

**Status:** ACCEPTED

## Context
Issue #8's Power BI report pages (sec. 38.1-38.4, `docs/powerbi/report_pages_spec.md`,
ADR-016) are stuck on a genuine environment blocker: building them requires
opening Power BI Desktop, a GUI-only, licensed tool this repository cannot
run or validate headlessly. The semantic model (`bi/powerbi/`) is real and
correct, but nobody can turn the spec into actual report pages without that
software.

The sibling project VOLT (raw-material supply chain digital shadow, same
programme) solved an analogous problem with a single self-contained HTML
file: a Python build script queries the data, embeds it as
`const DATA = {...}`, and emits one file with no CDN dependency — buildable,
testable, and shippable (by email, by attaching to a chat, by opening
directly in a browser) without any BI platform license.

## Decision
Adopt the same pattern for START, scoped to what `start-iids` actually
covers (fabbrica ceramica + prodotto — not VOLT's upstream supply chain, and
not OR3's building envelope, per the user's own framing of scope):

1. **`bi/html_viewer/template.html`** — the static shell (CSS + vanilla JS,
   zero CDN dependencies), with a `/*__DATA__*/` placeholder inside
   `const DATA = /*__DATA__*/;`.
2. **`scripts/build_html_viewer.py`** — reuses
   `build_synthetic_engine`/`DIMENSION_QUERIES` from
   `export_mv_intelligent_industry_state.py` (no duplicated engine-building
   logic), queries `mv_intelligent_industry_state` plus the channel/quality
   aggregates, computes every displayed number itself (sec. 39 / ADR-006:
   **BI is not a calculation engine** — the JS in the template only renders
   numbers already computed in Python, exactly the same constraint the Power
   BI model's DAX measures follow), and writes the final single HTML file.
3. **Tabs**: Panoramica, Fabbrica (sec. 38.1), Prodotto (sec. 38.2), Canale
   distributivo (ADR-022), Integrata (sec. 38.3-38.4), Edificio, Qualità &
   Build — mapped directly onto the same field list
   `docs/powerbi/report_pages_spec.md` already worked out, so the two
   deliverables stay in sync rather than diverging into separate specs.
4. **Edificio tab**: a structural placeholder, not a fabricated dataset.
   `start-iids` has zero building/envelope data — that is OR3's domain
   (Università degli Studi di Sassari), a different partner in the Piano di
   Sviluppo (Allegato 4). The tab lists OR3's own 4 real tasks (3.1-3.4:
   involucro ventilato, comfort indoor, controllo predittivo, multiperformance)
   each with an honest "dati non disponibili — dominio OR3/UNISS" note, ready
   to receive real fields once that partner shares data (sec. 64 — never
   fabricate input to fill a gap).
5. **Canale distributivo tab**: new, not from the spec — see ADR-022. The
   user asked directly to evaluate a dedicated distribution-channel
   monitoring module, symmetric to how VOLT tracks upstream supplier
   concentration risk; this ADR wires it into the same viewer rather than a
   separate artifact.
6. **The Power BI semantic model is not replaced.** `bi/powerbi/` (ADR-016)
   stays exactly as built and stays the documented path for when a licensed
   Power BI Desktop/Service environment and real live data (issues #3/#7) are
   both available. This HTML viewer is the practical, always-buildable
   deliverable in the meantime — the "Qualità & Build" tab says so
   explicitly, so nobody mistakes it for a permanent replacement.

## Consequences
- `python3 -m scripts.build_html_viewer` produces a viewer against the
  synthetic dataset (ADR-014) with zero setup; `--db-url`/`--label` point it
  at real data later with no template rework, mirroring
  `export_mv_intelligent_industry_state.py`'s own `--db-url` pattern.
- Every number in the viewer traces back to the same `mv_intelligent_industry_state`
  view and the same aggregation rules already reviewed for the Power BI
  model — no second, divergent source of truth.
- The known gaps already documented for Power BI (`fact_quality_test`/product
  type not in the model, sec. 38.2) apply identically here — carried over
  verbatim rather than silently re-introduced.

## Tests
`tests/unit/test_build_html_viewer.py` — the build produces valid HTML with
a parseable embedded JSON payload whose row/cluster/channel counts match a
small fixture database, and the template's `/*__DATA__*/` marker check fails
loudly if the template is ever edited to remove it.
