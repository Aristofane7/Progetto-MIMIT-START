# Richiesta di input esterni — START IIDS v1

**Data:** 2026-09-01
**A cura di:** sessione di sviluppo Claude Code, branch `claude/start-intelligence-factory-9uoqet`

## Scopo

Le 5 issue GitHub ancora aperte (#3, #4, #7, #8, #9) sono bloccate ciascuna da
un singolo input che questo ambiente di sviluppo non può produrre né
inventare (spec sez. 64 — "non fabbricare input per far tornare i valori").
Tutto il codice, schema e test che consumeranno questi input **sono già
pronti**: ogni voce sotto indica esattamente cosa serve, a chi va chiesto, e
cosa succede in automatico non appena arriva.

Questo documento sostituisce il girare issue per issue: è un'unica lista da
girare a chi di competenza.

## I 5 blocchi

### 1. Nomi reali di campi/tabelle IT (issue #3 — P0-03)
- **A chi chiedere:** referenti IT dei sistemi di stabilimento (SAP/MES/SCADA/HR/LIMS)
- **Cosa serve:** per ciascuna sorgente, il nome reale di tabella/endpoint e il
  nome reale di ogni campo elencato come `TBD_*` nei contratti dati:
  - `config/source_mappings/mes_production_v1.yaml` (esempio già presente)
  - `config/source_mappings/erp_economic_v1.yaml`
  - `config/source_mappings/hr_social_v1.yaml`
  - `config/source_mappings/scada_process_observation_v1.yaml`
  - `config/source_mappings/lims_quality_v1.yaml`
  - più le credenziali/endpoint di accesso (DB, REST, file drop — a seconda del sistema)
- **Verificato assente da:** RP6.6, RP6.7, RP 7.1, RP 7.2 (letti integralmente, ADR-021) — non è un dato "nascosto nel repo", va richiesto a chi gestisce quei sistemi
- **Cosa succede all'arrivo:** si sostituiscono i placeholder `TBD_*` con i nomi reali nei file YAML — nessuna modifica di schema o codice motore (ADR-021); il collector Edge (`src/ingestion/edge/collector.py`) e lo scrittore Cloud (`src/ingestion/edge/cloud_writer.py`) sono già pronti e testati

### 2. Libreria coefficienti reale "Tabella 2" + soglie di business (issue #4 — ADR-011)
- **A chi chiedere:** responsabile di progetto / autori dei manuali SRC-TEI/EFA/EcoFA/SFA
- **Cosa serve:**
  - i valori reali dei coefficienti granulari per-lotto citati da tutti e 4 i
    manuali come "Tabella 2" (es. `B_TILE`, `B_SDM`, `KAPPA_MTS`) — le
    *formule* sono già confermate sul testo reale dei manuali (ADR-018), manca
    solo il *valore* approvato
  - approvazione formale per Appendix M (fonte + firma responsabile)
  - una decisione di business sulle soglie di classificazione trend cluster
    (`GROWTH_THRESHOLD`/`DECLINE_THRESHOLD` in
    `src/product/sales/cluster_performance.py`) — non è nei manuali perché è
    una scelta gestionale, non tecnica
- **Cosa succede all'arrivo:** nuovo `coefficient_set_id` `APPROVED`, bump di
  `engine_version` sui motori coinvolti, nuovi test old/new (Appendix M) —
  processo già seguito per il modello aggregato RP7.3 (ADR-013)

### 3. Export reale dei 13.251 prodotti con assegnazione cluster (issue #7 — P0-04)
- **A chi chiedere:** chi detiene i deliverable grezzi di RP6.8 (sez. 3.7)
- **Cosa serve:** un CSV/export con un prodotto per riga, attributi prodotto e
  `cluster_id` di assegnazione (i 22 cluster reali sono già caricati, ADR-015)
- **Cosa succede all'arrivo:** import diretto con lo script già pronto e
  validato via foreign key:
  `python3 -m scripts.import_rp68_product_master_data --products-csv <file>`

### 4. Accesso a Power BI Desktop per le 3 pagine report (issue #8)
- **A chi chiedere:** chiunque abbia un ambiente Power BI Desktop disponibile
- **Cosa serve:** aprire `bi/powerbi/START_IIDS.SemanticModel/` (modello
  semantico TMDL già pronto, ADR-016) e costruire le 3 pagine report
  (Factory/Product/Integrated) seguendo la specifica campo-per-campo in
  `docs/powerbi/report_pages_spec.md` (sez. 38.1-38.4)
- **Perché non lo fa questo ambiente:** è un passaggio di autoring GUI in
  Power BI Desktop, non eseguibile né validabile in modo headless
- **Nota:** può partire già oggi sui dati sintetici/RP7.3 reali disponibili;
  il collegamento ai dati reali (blocchi 1 e 3) non richiede rilavorazione del
  modello, solo lo switch del parametro `DataSourceMode`

### 5. Ambiente di staging reale per la validazione finale (issue #9)
- **A chi chiedere:** chi gestisce l'infrastruttura di deployment (Postgres/Azure SQL)
- **Cosa serve:** un ambiente con dati reali (dipende dai blocchi 1 e 3) su
  cui eseguire l'intera checklist di accettazione v1
- **Cosa succede all'arrivo:** si rilancia
  `python3 -m scripts.stage9_validation_checklist` (ADR-017), che oggi segnala
  già in modo automatico 12 PASS / 5 PARTIAL / 4 BLOCKED su 21 voci; i
  restanti item di performance/UAT possono essere eseguiti solo lì

## Riepilogo

| # | Issue | Owner della richiesta | Blocca anche |
|---|---|---|---|
| 1 | [#3](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/3) | IT stabilimento | #8, #9 |
| 2 | [#4](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/4) | Responsabile di progetto | #9 |
| 3 | [#7](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/7) | Detentore deliverable RP6.8 | #8, #9 |
| 4 | [#8](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/8) | Chi ha Power BI Desktop | — |
| 5 | [#9](https://github.com/Aristofane7/Progetto-MIMIT-START/issues/9) | Gestore infrastruttura deployment | — |

Nessuno di questi 5 punti richiede ulteriore sviluppo software: il codice,
lo schema e i test che li consumeranno sono già scritti, testati e in attesa
solo del dato/accesso indicato.
