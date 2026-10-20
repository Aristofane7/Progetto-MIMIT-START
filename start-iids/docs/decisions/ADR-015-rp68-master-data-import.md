# ADR-015 — RP6.8 master data import: what's real and loadable now, what's blocked

**Status:** ACCEPTED, 2026-09-01 — issue #7 progress, not closure

## Context

Issue #7 asks for the real product master data import: the 22 RP6.8 clusters,
the 13,251-product catalog with cluster assignments, and (eventually) the lot
↔ product mapping. `RP6.8 Report di Product Analysis_30-04-25.pdf` (repo
root) is the only RP6.8 artifact present in this repository — it is a
narrative report, not a data export.

Re-reading the full report text (not just the earlier partial extraction)
confirms three things worth recording precisely, because they determine what
can honestly be loaded as *real* data today versus what remains blocked:

1. **The p.13 cluster dashboard table is a complete, verifiable transcription
   source.** It lists, for each of the 22 clusters (`0`-`21`): product count,
   percentage of portfolio, and dominant Forma/Dimensione/Spessore/Scivolosità
   R/Effetto/Colore with purity %. Summing the 22 `product_count` values gives
   **exactly 13,251** — the same total the report states in sec. 2.3. That
   exact match is used below as a transcription guard, not asserted from
   authority.
2. **One cluster's dashboard entry is internally inconsistent in the source
   document itself.** Cluster 11 lists `Spessore: R9` (R9 is a Scivolosità R
   value, not a thickness), `Scivolosità R: PIETRA` (PIETRA is an Effetto
   value), `Effetto: CHIARO` (CHIARO is a Colore value), and no Colore value
   at all. This is consistent with a column-shift rendering defect in the
   report's own dashboard for this one cluster, not a transcription or OCR
   error on our side (every other cluster's values are internally consistent
   with their attribute's known vocabulary, and the product-count sum above
   only closes exactly if the transcription is otherwise accurate). We do
   **not** guess-correct it.
3. **The full 13,251-product cluster-assignment export is explicitly named as
   an existing deliverable the report does not include.** Sec. 3.7: *"Il
   dataset completo con assegnazioni di cluster per ciascuno dei 13.251
   prodotti analizzati rappresenta la base informativa..."* — this file is not
   in this repository. It is an external blocker: someone who holds RP6.8's
   raw deliverables must supply it. It cannot be reconstructed from the PDF.

There is also a minor, second-order discrepancy worth flagging without
blocking anything: the p.13 table gives cluster 13 as 494 products (3.7%),
while the sec. 3.3 narrative text cites 492 products for the same cluster.
The dashboard table's value is used (it is the structured deliverable, and it
is the one whose total closes to 13,251).

## Decision

1. `data/reference/rp68_cluster_master.csv` holds the 22 real clusters,
   transcribed verbatim from the report, with the cluster-11 defect and the
   cluster-13 discrepancy recorded in a `data_quality_flag` column rather than
   silently resolved.
2. `scripts/import_rp68_product_master_data.py` is the importer:
   - `load_cluster_master_csv` / `build_cluster_insert_sql` load the 22
     clusters into `dim_product_cluster` under a real `cluster_version`
     (`RP68_2025_04`), refusing to load if the product-count sum or cluster
     count guard fails (protects against a corrupted or hand-edited CSV ever
     being mistaken for a verified one).
   - Cluster 11's Spessore/Scivolosità R/Effetto/Colore are loaded as `NULL`,
     never as the shifted (wrong-domain) values from the source table.
   - The per-cluster CQS/Balance/Coherence/Separation/Business-Relevance
     columns in `dim_product_cluster` are left `NULL` for all 22 clusters:
     RP6.8 sec. 3.2 reports these four scores **once**, for the whole 22-
     cluster solution (Balance=0.811, Coherence=0.721, Separation=0.623,
     Business Relevance=1.000, CQS=0.780 — already the golden values in
     `tests/unit/test_product_cqs.py`), not per cluster. Writing that single
     aggregate figure into 22 per-cluster rows would misrepresent it as a
     per-cluster score the report does not provide.
   - `load_product_master_csv` / `build_product_insert_sql` are the
     ready-to-run importer for the RP6.8 sec. 3.7 product export, once
     supplied: required-field and cluster-FK validation mirror the
     `DataQualityFinding`/`Severity.BLOCKER` pattern used elsewhere
     (`src/engines/errors.py`), rejecting rather than guessing at bad rows.
     Exercised today only against `tests/fixtures/rp68_product_master_fixture.csv`,
     a clearly-labeled non-real fixture (`FIXTURE-PROD-*` IDs).
3. `data/reference/rp68_master_seed.sql` is the generated, committed SQL for
   the 22 real clusters (regenerate via
   `python3 -m scripts.import_rp68_product_master_data`) — small enough, and
   real enough, to commit directly rather than gitignore like the synthetic
   dataset (ADR-014).
4. Scope: this closes the **cluster-level** part of issue #7. It does **not**
   close #7 — the 13,251-product catalog and the lot↔product mapping remain
   blocked on the external file (point 3 above) and on real MES lot codes
   (P0-04) respectively.

## Consequences

- `dim_product_cluster` can now be seeded with real `cluster_id 0-21` data,
  distinct from both the RP6.8 range assumed in ADR-014 (`1`-`22`, which this
  ADR corrects to the report's actual `0`-`21`) and the synthetic range
  (`9001+`).
- The moment the real product export lands, `python3 -m
  scripts.import_rp68_product_master_data --products-csv <file> --sql-out
  <out>` validates and loads it against the already-real cluster set with no
  further code changes.
- No governance rule is bypassed: nothing here touches an `APPROVED`
  coefficient/weight set, and the cluster-11/-13 data-quality notes travel
  with the data rather than being silently smoothed over.
