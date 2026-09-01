# ADR-008 — Product clustering, sales joined ex post

**Status:** DOC (spec sec. 61, sec. 10.6, sec. 19.2)

## Decision
K-Prototypes clustering (RP6.8, 22 clusters, `k` explored 10-25, `n_init=15`
exploratory / `50` final, `max_iter=100`, `random_state=42`, Cao/Huang init) runs
on intrinsic product attributes only. Sales volumes are never a clustering
feature; they are joined ex post via `fact_product_sales` /
`fact_cluster_performance`.

## Consequences
`dim_product_cluster` and `dim_product` carry no sales columns. Re-clustering is
not scheduled automatically (sec. 19.6) — a new `cluster_version` is imported on
request and never overwrites history (`src/product/clustering/catalog.py`).
