# ADR-003 — Lot as the central bridge

**Status:** ARCH proposed (spec sec. 61)

## Context
No single START document defines the operational hinge between the product and
factory domains explicitly as a table; the concept is implicit across RP7.3,
RP6.8, and RP7.4.

## Decision
`lot_id` (`fact_production_lot`) is the canonical hinge:
`Product ↔ Lot ↔ Process ↔ Factory`. A lot is associated with exactly one
`product_id` in v1; if a lot spans multiple products, introduce
`bridge_lot_product` via a new ADR rather than overloading `product_id`.

## Consequences
Every cross-domain join (EEA state, P-TSA state, IIDS view) keys off `lot_id`
(with `product_id` as a documented fallback grain for P-TSA when a lot-level test
does not exist).
