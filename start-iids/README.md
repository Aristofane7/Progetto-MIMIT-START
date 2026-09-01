# START Intelligent Industry Digital Shadow (IIDS)

Implementazione di riferimento del **Digital Shadow della Intelligent Industry** per il progetto
START (DM 31/12/2021 — Prog. n. F/310087/01-05/X56), come specificato in
`docs/sources/START_Intelligent_Industry_Digital_Shadow_Implementation_Spec_v1.0.md`.

## Cos'è, cosa non è

- **È** un Digital Shadow: flusso automatico `Physical → Digital`, con analisi, previsione,
  simulazione e raccomandazione a supporto della decisione umana.
- **Non è** un Digital Twin bidirezionale: nessuna scrittura automatica verso PLC/SCADA, nessun
  endpoint di attuazione. Vedi `docs/decisions/ADR-001-digital-shadow-no-actuation.md`.

## Struttura del repository

```text
docs/            architettura, dizionario dati, ADR, documenti sorgente
config/          feature flags, source mapping, variabili, baseline, coefficienti, pesi AHP
sql/
  migrations/    DDL di riferimento (contratto logico, portabile su Azure SQL)
  views/         viste materializzate (es. mv_intelligent_industry_state)
  quality_checks/regole di data quality / blocker
src/
  ingestion/     collettori Edge→Cloud, contratti dati per sorgente (MES/ERP/HR/LIMS)
  core/          unità di misura, entity resolution, lot linking, data quality
  engines/       motori di calcolo: tei, efa, ecofa, sfa, eea, ptsa
  product/       clustering prodotto, vendite, trend
  design/        workflow di Product Design (fasi A-F)
  marts/         costruzione della vista integrata IIDS
  api/           API read-only (nessun endpoint di scrittura/attuazione)
tests/           unit, integration, regression, data_contracts, fixtures
```

## Regola P0 — unità di energia

Unità di calcolo interna: **MJ**. Unità di reporting: **GJ**. Conversione: `gj = mj / 1000.0`
(MAI `/ 1e9`, che è valida solo per J→GJ). Vedi `src/core/units/energy.py` e
`tests/unit/test_units_energy.py`.

## Avvio rapido

```bash
pip install -e ".[dev]"
pytest
```

## Pipeline aggregata EEA+/TSI (dati reali RP7.3)

`data/reference/` contiene i file reali del progetto: raccolta dati 2023-2025,
log di calcolo di riferimento e matrice AHP. La pipeline che li consuma è
descritta in `docs/decisions/ADR-012-...`:

```bash
python3 -m src.run_all                       # stampa il log su stdout
python3 -m src.run_all --output out.csv       # scrive il log su file
pytest tests/regression/test_rp73_calculation_log.py  # verifica contro i valori reali pubblicati
```

Il coefficient set (`COEFF_RP73_PROVISIONAL_2026`) e il weight set
(`EEA_AHP_RP73_1`) sono `APPROVED` (sign-off del 2026-09-01, vedi
`docs/decisions/ADR-013-...`); la loro copertura è però limitata al modello
aggregato annuale/impianto — i coefficienti granulari usati dai motori
per-lotto restano `DRAFT` (vedi ADR-011), e l'input `Psi`/`Ex_useful` resta un
dato riportato, non derivato.

## Dati master reali RP6.8 (cluster di prodotto)

`data/reference/rp68_cluster_master.csv` contiene i 22 cluster reali,
trascritti dal report `RP6.8 Report di Product Analysis_30-04-25.pdf`
(conteggio prodotti verificato: somma esatta a 13.251). Vedi
`docs/decisions/ADR-015-...` per la nota di qualità dati su un cluster con
un difetto nella tabella sorgente, e per lo stato del blocco esterno
sull'export completo dei 13.251 prodotti (issue #7):

```bash
python3 -m scripts.import_rp68_product_master_data                 # rigenera data/reference/rp68_master_seed.sql (22 cluster reali)
python3 -m scripts.import_rp68_product_master_data --products-csv <file>  # + carica l'export prodotti reale, quando disponibile
pytest tests/unit/test_rp68_cluster_master_data.py tests/integration/test_rp68_master_data_import.py
```

## Dataset sintetico temporaneo (sviluppo modello Power BI)

In attesa dei dati master reali (issue #7) e dei connettori live (issue #3),
`scripts/generate_synthetic_demo_data.py` genera un dataset **chiaramente
etichettato come sintetico** (`source_system='SYNTHETIC_DEMO'`, plant `SYN01`/
`SYN02`, cluster `9001+`) per sviluppare il modello semantico Power BI (issue
#8) contro `mv_intelligent_industry_state`. Vedi `docs/decisions/ADR-014-...`
per le regole (mai coefficienti `APPROVED`, mai usato per la Validazione
Stage 9, mai citato come risultato di calcolo):

```bash
python3 -m scripts.generate_synthetic_demo_data   # scrive data/synthetic/{seed.sql,csv/}
pytest tests/integration/test_synthetic_demo_data.py  # verifica il flusso end-to-end
```

`data/synthetic/` non è versionato (rigenerabile in un comando, seed fisso).

## Stato di avanzamento

Vedi `docs/ROADMAP.md` per lo stato Stage 0–9 e la checklist dei 30 criteri di accettazione
(sec. 57 della specifica).

## Governance

Ogni scelta architetturale non direttamente presente nei documenti START è tracciata come ADR in
`docs/decisions/`. Nessun agente deve introdurre logiche di calcolo alternative senza una ADR
esplicita approvata dal responsabile di progetto.
