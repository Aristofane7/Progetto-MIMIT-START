# ADR-002 — Dual-domain architecture: Factory Shadow + Product Shadow

**Status:** APPROVED by architecture (spec sec. 61)

## Context
START's results split naturally into a factory/process perspective (EEA+/TSI,
RP6.5/RP7.3) and a product/portfolio perspective (Product Analysis, Product
Design, P-TSA/P-TSI — RP6.8/RP6.9/RP7.4).

## Decision
Model two coupled domains, `DS_F(t)` (Factory/Organization Shadow) and `DS_P(t)`
(Product/Portfolio Information Shadow), converging through
`Product ↔ Lot ↔ Process` (ADR-003) into a single conceptual `IIDS(t)`.

## Consequences
Schema, engines, and marts are organized per-domain; the integrated view
(`mv_intelligent_industry_state`) is the only place the two domains are joined for
read purposes.
