# ADR-022 — Distribution channel dimension

**Status:** ACCEPTED — schema and concentration metric built; real per-channel volumes remain an external blocker

## Context
Requested directly (not from the implementation spec's fixed field list): the
distribution channel (B2B/B2C) is a monitoring point for concentration risk
on the sales side, symmetric to the raw-material supplier concentration risk
the sibling project VOLT tracks upstream. `fact_product_sales` had no channel
attribute at all before this ADR — a genuine schema gap, not a hidden field.

The Piano di Sviluppo (Allegato 4) itself already names Gresmalt's real
channel split at OR7.5 ("Data-Driven Product Quality Management"): *"Il
calcolo del Customer Rating (CR) potrebbe risultare complesso per la diversa
tipologia di cientela di Gresmalt: B2C (business-to-consumer) e B2B
(business-to-business)... Verranno creati due indicatori distinti (B2C-CR e
B2B-CR)"*. OR2.1 separately lists "canali distributivi" among the factors
that make production use-cases vary. So B2B/B2C is not a fabricated
taxonomy — it is the one the project's own plan already commits to.

## Decision
1. **`dim_distribution_channel`** (migration `0012`): `channel_id`,
   `channel_name`, `channel_type` (`B2B`/`B2C`). Seeded with exactly the 2
   real channel types named above — reference data, like the unit library or
   the 22 real RP6.8 clusters, not fabricated business data.
2. **`fact_product_sales.channel_id`**: nullable FK to the new dimension.
   Nullable because real per-sale channel tagging is not yet available
   (below) — existing/future rows without it still load.
3. **`mv_intelligent_industry_state`**: `channel_id`/`channel_type` surfaced
   via the same kind of passthrough join already used for `process_id` et
   al. (ADR-016) — not in spec sec. 26.2's field list, added because there
   was no field to expose this monitoring point without it.
4. **`src/product/sales/channel_concentration.py::compute_channel_concentration`**:
   a Herfindahl-Hirschman-style concentration index (sum of squared channel
   shares of sales) over a dict of `{channel_id: sales_value}`. Returns
   `None` (not a misleading `0.0` or a `ZeroDivisionError`) when there is
   nothing to concentrate. This is the same kind of over-dependency signal
   VOLT computes for supplier/raw-material concentration, applied downstream
   to sales channels.
5. Synthetic demo dataset (`scripts/generate_synthetic_demo_data.py`,
   ADR-014) now assigns a `channel_id` to every synthetic sales row, and the
   Power BI CSV export (`scripts/export_mv_intelligent_industry_state.py`)
   now also exports `dim_distribution_channel.csv` — so the new dimension is
   visible end-to-end (schema → view → synthetic dataset → export) without
   waiting for real data.

## What remains blocked
Real per-channel sales volumes: which invoices/orders belong to B2B vs B2C
(and any finer split Gresmalt's ERP actually tracks — e.g. distributor,
GDO, e-commerce, if those exist as distinct channels rather than sub-types
of B2B/B2C). This is the same class of external blocker as P0-03/P0-04 —
not fabricatable, and not resolved by this ADR.

## Tests
`tests/unit/test_channel_concentration.py` — even split, full concentration,
the uneven-split HHI arithmetic, and both `None`-returning guard cases (no
channels, zero total).
