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

## Pipeline aggregata EEA+/TSI (dati reali provvisori RP7.3)

`data/reference/` contiene i file reali (seppur provvisori) del progetto:
raccolta dati 2023-2025, log di calcolo di riferimento e matrice AHP. La
pipeline che li consuma è descritta in `docs/decisions/ADR-012-...`:

```bash
python3 -m src.run_all                       # stampa il log su stdout
python3 -m src.run_all --output out.csv       # scrive il log su file
pytest tests/regression/test_rp73_calculation_log.py  # verifica contro i valori reali pubblicati
```

Attenzione: il coefficient set e il weight set usati sono `DRAFT` (dati
provvisori, non ancora approvati) — `run_all.py` lo segnala esplicitamente e
non deve essere considerato un calcolo di produzione (sez. 11.3 della
specifica).

## Stato di avanzamento

Vedi `docs/ROADMAP.md` per lo stato Stage 0–9 e la checklist dei 30 criteri di accettazione
(sec. 57 della specifica).

## Governance

Ogni scelta architetturale non direttamente presente nei documenti START è tracciata come ADR in
`docs/decisions/`. Nessun agente deve introdurre logiche di calcolo alternative senza una ADR
esplicita approvata dal responsabile di progetto.
