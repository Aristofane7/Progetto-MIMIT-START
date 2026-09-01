# ADR-009 — ARIMA / portfolio optimizer / logistic success model disabled

**Status:** DOC/FUTURE (spec sec. 61, sec. 21.1, sec. 36)

## Decision
`config/features.yaml` hardcodes `arima_forecast`, `logistic_success_model`,
`portfolio_optimizer`, and `trend_forecast_rows` to `false`. No code in this
repository implements RP6.9's `V(C*) = Σ E[NPV(c)] - λ Risk(C*)` portfolio model,
its logistic success-probability regression, or an ARIMA forecaster. `DIM_TREND`
accepts a `FORECAST` `source_type` value at the schema level (for forward
compatibility) but no code path writes such rows while the flag is `false`.

## Consequences
Any future enablement requires a new ADR, a validated model, and an explicit
project-owner decision — never a silent flag flip.
