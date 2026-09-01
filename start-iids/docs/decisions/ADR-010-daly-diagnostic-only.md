# ADR-010 — DALY is diagnostic only

**Status:** DOC (spec sec. 61, sec. 17.4)

## Decision
`compute_daly_diagnostic` (`src/engines/sfa/formulas.py`) is computed and reported
in `CalculationResult.values["daly_diagnostic"]` for visibility, but is never
added into `f_soc` and is never persisted onto `fact_eea_state` (see
`SFAEngine.persist`, and `tests/unit/test_sfa_engine.py::
test_daly_is_diagnostic_only_and_excluded_from_f_soc`).

## Consequences
DALY→Joule remains an open item (P1-04) until a mapping is formally approved;
until then no formula anywhere may add a DALY-derived term into a persisted
sustainability accounting value.
