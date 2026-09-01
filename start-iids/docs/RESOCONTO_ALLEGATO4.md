# Resoconto — Costruzione del sistema, stato di avanzamento e collocazione rispetto al Piano di Sviluppo (Allegato 4)

**Data:** 2026-09-01
**A cura di:** sessione di sviluppo Claude Code, branch `claude/start-intelligence-factory-9uoqet`
**Riferimento:** `START_Piano_di_Sviluppo_all4_integrato.pdf` (Allegato n. 4 al DM 31 dicembre 2021, Accordi per l'Innovazione — progetto START, capofila Gresmalt)

## Premessa

Questo documento risponde a tre domande: **come** è stato costruito `start-iids`, **dove** siamo arrivati (compreso cosa manca), e **come si colloca** rispetto al Piano di Sviluppo ufficiale del progetto START (Allegato 4), che articola il progetto in 8 Obiettivi Realizzativi (OR1-OR8) affidati a 5 soggetti proponenti (Libera Università di Bolzano, Università della Calabria, Università degli Studi di Sassari, SACMI, Gresmalt) su 36 mesi.

**Punto chiave:** `start-iids` non è un tentativo di implementare l'intero progetto START. È l'implementazione informatica (Digital Shadow, sez. 34 della specifica implementativa) di un sottoinsieme preciso e verificabile del Piano di Sviluppo — sostanzialmente **OR6 (Gresmalt, ricerca) e OR7 (Gresmalt, sviluppo sperimentale)**, limitatamente alle attività che sono codice/dati/modelli e non impianti fisici, laboratorio, hardware o organizzazione di progetto. Il resto del Piano (OR1-5, OR8, e le parti fisiche di OR6-7) appartiene ad altri partner o ad attività non software, ed è correttamente fuori dal perimetro di questo repository.

---

## 1. Come è stato costruito il sistema

### 1.1 Principio architetturale
`start-iids` implementa un **Digital Shadow** (non un Digital Twin): flusso di dati a senso unico dal sistema fisico al sistema digitale, mai il contrario — nessun endpoint di scrittura verso macchine/PLC (ADR-001), garantito strutturalmente e da un guard CI che intercetta pattern di scrittura vietati.

### 1.2 Stratificazione dati (ADR-004, sez. 6/61 della specifica)
`raw_*` (append-only) → `stg_*` (parsing/cast/naming) → `dim_*`/`fact_*`/`bridge_*` (core semantico) → `mart_*`/`mv_*` (output BI/motori) → `audit_*` (qualità, lineage, calc run). Ogni motore legge solo dal core, mai da `raw_*`, e nessuno strato salta un passaggio.

### 1.3 Ingestione dati (data contract pattern, sez. 27)
Ogni sorgente esterna (MES/ERP/HR/SCADA/LIMS) è descritta da un contratto dati YAML dichiarativo (`src/ingestion/contracts.py`): campi sorgente→target, chiave di deduplica, regole di scarto. Nessun motore di business codifica un mapping di campo al suo interno. Su questa base sono stati costruiti: un collector Edge generico (`src/ingestion/edge/collector.py`, sez. 34.1: acquisizione/validazione/filtro/dedup) e uno scrittore Cloud verso staging (`src/ingestion/edge/cloud_writer.py`, sez. 34.2).

### 1.4 Motori di calcolo (Stage 4-6)
- **TEI-J / EFA-J / EcoFA-J / SFA-J**: quattro motori per-lotto di impronta tecnologica/ambientale/economica/sociale, ciascuno con interfaccia `CalculationEngine` comune, versione (`engine_version`) e coefficienti tracciati (`dim_coefficient_set`).
- **EEA+ (Extended Exergy Accounting)**: aggregazione delle quattro impronte in un indice termodinamico unico (`TSI_norm`, e la variante reale `TSI_abs`/`TSI_rel`/`Phi`/`Psi`/`SA_w`), a livello sia di lotto che di aggregato fabbrica/anno.
- **P-TSA (Product Technological Sustainability Assessment)**: SCR/PsI/OCR → z-score → AHP → P-TSI → TII, a livello di prodotto.
- Ogni calcolo è riproducibile (`audit_calc_run`, `make_calc_run_id`) e non distruttivo (nessuna riscrittura in-place di una versione approvata).

### 1.5 Intelligenza di prodotto e workflow (Stage 5, 7)
Cluster prodotto (SCD2, sez. 19.6 — nessun re-clustering automatico, solo importazione/approvazione su richiesta), performance/trend cluster, e uno state machine per il workflow di design prodotto (progetto→opzione→prototipo→test→decisione).

### 1.6 Qualità dati e audit (sez. 29.3, ADR-017)
Ogni record scartato produce un `DataQualityFinding` persistito (`audit_data_quality`), mai silenziosamente perso. Query di rilevamento blocker provate contro inserimenti reali, non solo verificate come SQL sintatticamente valido.

### 1.7 Integrazione e BI (Stage 8)
Vista integrata `mv_intelligent_industry_state`, API di sola lettura (FastAPI), e un modello semantico Power BI (TMDL) con misure di sola visualizzazione — mai un calcolo di business duplicato in DAX.

### 1.8 Governance
21 ADR (`docs/decisions/`) tracciano ogni decisione architetturale e ogni item aperto/risolto. 251 test (unit/integration/regression), 95% di copertura, CI verde.

---

## 2. Dove siamo arrivati (compreso cosa manca)

- **27/30 criteri di accettazione v1** (spec sez. 57) **DONE**; 3 **PARTIAL**.
- Modello aggregato EEA+/TSI validato su **66 punti dati reali** (RP7.3); coefficienti e pesi **APPROVATI** dal responsabile di progetto (ADR-013).
- P-TSA (z-score e scoring/AHP) validato sui dati reali pubblicati nel report RP7.4 (ADR-020).
- Formule TEI-J/EFA-J/EcoFA-J/SFA-J verificate contro i manuali operativi reali; EFA/EcoFA/SFA già corrette, TEI-J corretta (ADR-018).
- 22 cluster prodotto reali RP6.8 caricati (ADR-015).
- Infrastruttura Edge/Cloud generica (sez. 34) costruita e testata; 5 contratti dati (1 reale, 4 draft con placeholder `TBD_*`).

**Cosa manca — tutti blocchi esterni confermati, non gap di codice** (vedi anche `docs/EXTERNAL_INPUT_REQUEST.md`):
1. Nomi reali di campi/tabelle MES/SCADA/ERP/HR/LIMS (P0-03, issue #3) — verificato assente da RP6.6/RP6.7/RP7.1/RP7.2 (ADR-021).
2. Export reale dei 13.251 prodotti con assegnazione cluster (P0-04, issue #7).
3. Valori approvati della libreria di coefficienti granulari per-lotto ("Tabella 2", issue #4).
4. Le 3 pagine report Power BI (passaggio GUI, issue #8).
5. Un ambiente di staging reale per la validazione finale (issue #9).

---

## 3. Collocazione rispetto al Piano di Sviluppo (Allegato 4)

### 3.1 Vista d'insieme per Obiettivo Realizzativo

| OR | Titolo | Proponente | Relazione con `start-iids` |
|---|---|---|---|
| OR1 | Digital Twin / IA etica / data hub / chatbot | UNIBZ | **Fuori perimetro** — ricerca concettuale (Axiomatic Design, ontologia, linee guida etiche, prototipo data hub Azure, chatbot) di un altro ente; non un artefatto software di questo repository |
| OR2 | Modelli qualità materiali ceramici (NDT + ML) | UNICAL | **Fuori perimetro** — richiede campioni fisici di laboratorio, sensori NDT (termografia, ultrasuoni), dati sperimentali di materiali; non digitalizzabile in un repository dati/software |
| OR3 | Involucro edilizio intelligente | UNISS | **Fuori perimetro** — prototipo edilizio fisico, monitoraggio microclimatico; dominio applicativo diverso (edificio, non fabbrica) |
| OR4 | Framework AI per Intelligent Industry | SACMI | **Fuori perimetro** — mappatura use case e algoritmi su impianti SACMI reali; risultato è un framework di riferimento, non codice eseguibile qui |
| OR5 | Applicazione AI su impianto pilota | SACMI | **Fuori perimetro** — richiede un impianto pilota reale, sensoristica di linea, dati di produzione live |
| **OR6** | **Modellazione soluzioni tecnologiche per Intelligent Industry** | **Gresmalt (RI)** | **Nucleo di `start-iids`** — vedi 3.2 |
| **OR7** | **Validazione in ambiente operativo** | **Gresmalt (SS)** | **Nucleo di `start-iids`** per le parti data/software — vedi 3.3 |
| OR8 | Misurazione risultati progetto, coordinamento | Gresmalt (SS) | **Fuori perimetro** — project management (SharePoint, Teams, sito web, stakeholder engagement, analisi input-output regionale); non software di dominio |

`start-iids` implementa quindi la parte **data-driven e di calcolo** di OR6 e OR7 — non le parti fisiche (adeguamento linee, prototipazione collezioni, laboratorio) né le parti gestionali (OR8) né il lavoro degli altri 4 partner.

### 3.2 OR6 — Modellazione di soluzioni tecnologiche (Gresmalt, Ricerca Industriale)

| Task | Deliverable atteso (Piano) | Corrispondente in `start-iids` | Stato |
|---|---|---|---|
| 6.1 Impronta tecnologica | TFA+ v.alpha | Motore **TEI-J** (`src/engines/tei/`) | Formula confermata sul manuale reale (ADR-018); coefficienti granulari `DRAFT` — valori attendono issue #4 |
| 6.2 Impronta ambientale | EFA+ v.alpha | Motore **EFA-J** | Formula confermata esatta (ADR-018) |
| 6.3 Impronta sociale | SFA+ v.alpha | Motore **SFA-J** | Formula confermata esatta (ADR-018) |
| 6.4 Impronta economica | EcoFA+ v.alpha | Motore **EcoFA-J** | Formula confermata esatta (ADR-018) |
| 6.5 Modellazione termodinamica (EEA+) | EEA+ v.alpha | `src/engines/eea/aggregate.py`, TSI | **Oltre l'alpha atteso a 24 mesi**: validato su 66 dati reali RP7.3, coefficienti/pesi `APPROVED` (ADR-012/013) — livello di maturità che il Piano colloca in OR7.3 |
| 6.6 Architettura Edge-to-Cloud | E2C v.alpha | `src/ingestion/edge/`, migrazione `0011` | Infrastruttura generica costruita e testata (ADR-021); connessione a sorgenti reali bloccata da P0-03, esattamente come da Piano ("velocità di elaborazione query" resta non misurabile senza dati reali) |
| 6.7 Progettazione Intelligent Factory | Architettura di implementazione | Stratificazione raw→staging→core→mart (ADR-004) + vista integrata | Il disegno architetturale esiste; l'"architettura di implementazione" completa (convergenza MES/ERP/BI reali) resta legata a P0-03/P0-04 |
| 6.8 Data-driven product analysis | Algoritmo k-means, N cluster 15÷20 | `src/product/clustering/catalog.py` | **Non lo stesso deliverable**: il repository implementa un catalogo SCD2 di cluster *importati* (sez. 19.6 vieta esplicitamente il re-clustering automatico in v1) — un k-means calcolato su dati di vendita reali non è tra gli obiettivi di questo v1 e comunque richiederebbe l'export prodotti (P0-04) |
| 6.9 Data-driven product design (Design Thinking) | Protocollo DT v.alpha | Workflow design prodotto (progetto/opzione/prototipo/test/decisione) | Schema e state machine `DONE`; la componente creativa/DT vera e propria (incrocio trend moda/arredamento) non è nel perimetro di questo repository |
| 6.10 Modellazione Intelligent Industry (BI) | Modello di simulazione, integrazione BI | `mv_intelligent_industry_state` + modello semantico Power BI (ADR-016) | Vista e modello semantico `DONE`; le pagine report (GUI) restano un passaggio manuale (issue #8) |

### 3.3 OR7 — Validazione in ambiente operativo (Gresmalt, Sviluppo Sperimentale)

| Task | Deliverable atteso (Piano) | Corrispondente in `start-iids` | Stato |
|---|---|---|---|
| 7.1 UAT piattaforma E2C | Collaudo v.beta in produzione | Collector + writer Edge/Cloud testati su schema reale (in-memory) | **Bloccato allo stesso punto del Piano**: UAT reale richiede P0-03 |
| 7.2 Performance testing Intelligent Factory | Rollout riuscito | — | **Fuori perimetro**: richiede infrastruttura di rete/server reale (issue #9) |
| 7.3 Assessment termodinamico della fabbrica | Collaudo EEA+ v.beta, dati reali | Aggregato EEA+/TSI su 66 punti reali RP7.3 | **Obiettivo di questo task già raggiunto** (ADR-012/013) — l'unico scarto è che il Piano lo prevede "N°3, 1 per unità produttiva su dati in tempo reale" e qui è su serie storica RP7.3, non streaming live (di nuovo, P0-03) |
| 7.4 Product Technological Sustainability Assessment | IOA/OP/TQ, P-TSI | Motore **P-TSA** (SCR/PsI/OCR/AHP/P-TSI/TII) | **Obiettivo raggiunto**: validato sui dati reali pubblicati nel report RP7.4 (ADR-020) — lo stesso report citato in nota 101 del Piano come fonte metodologica di questo task |
| 7.5 Data-Driven Product Quality Management | RFT/Defect Rate/IPR/Customer Rating | — | **Non implementato**: questi 4 KPI specifici non hanno un corrispondente nel repository (il meccanismo generico `audit_data_quality`/blocker rules copre la qualità dei *dati*, non ancora questi 4 KPI di qualità *di prodotto*); da considerare per un prossimo incremento una volta disponibili dati reali di scelta/reclamo |
| 7.6 Ingegnerizzazione Intelligent Factory | Adeguamento linee produttive | — | **Fuori perimetro** — lavoro fisico su impianti (attrezzature, non software) |
| 7.7 Data-driven design collezioni | Collaudo protocollo DT, prototipi fisici | — | **Fuori perimetro** — richiede laboratorio R&D e fornitori esterni |
| 7.8 Collaudo della Intelligent Industry | P-TSI + EEA+I su 6-12 mesi di produzione reale | — | **Bloccato**: è l'esatto traguardo finale che Stage 9 (`scripts/stage9_validation_checklist.py`, ADR-017) misura come non ancora raggiungibile senza P0-03/P0-04 e un deployment reale |
| 7.9 Test preindustriale collezioni | 120.000 m² piastrelle, conformità ISO | — | **Fuori perimetro** — produzione fisica e certificazione di laboratorio esterno |
| 7.10 Modello di business AI (AI-BM) | Business Model Canvas | — | **Fuori perimetro** — analisi strategica, non software |

### 3.4 Lettura d'insieme

Il Piano struttura il progetto come una progressione **OR6 (mesi 1-24, "alpha", ricerca)** → **OR7 (mesi 13-36, "beta", validazione su dati reali)**. `start-iids` ha già attraversato questa progressione per tre componenti (**EEA+/TSI aggregato**, **P-TSA**, e in parte le formule granulari TEI/EFA/EcoFA/SFA), portandole da "alpha" (formula soltanto) a un livello equivalente a "beta collaudata" grazie ai report RP7.3/RP7.4 reali reperiti e ai dati da essi derivati — con tanto di **approvazione formale del responsabile di progetto** sui coefficienti (ADR-013), esattamente la governance richiesta dal Piano (Appendix M della specifica implementativa).

Le componenti rimaste ad "alpha" o non raggiungibili da questo repository condividono tutte la stessa causa: **dipendono da un input fisico reale che l'ambiente di sviluppo non possiede** — un impianto (OR2/3/4/5/7.6/7.9), un accesso IT (E2C/OR6.6/7.1, P0-03), un export di terzi (product/cluster, P0-04), un giudizio umano (design estetico, DT/OR6.9/7.7; business strategy, OR7.10), o un processo organizzativo (OR8). Nessuna di queste è una lacuna di questo codice: sono, per costruzione, fuori dal perimetro di un repository software.

## Riferimenti
- `docs/ROADMAP.md` — stato dettagliato stage-per-stage e criterio-per-criterio
- `docs/decisions/ADR-001` ... `ADR-021` — log delle decisioni
- `docs/EXTERNAL_INPUT_REQUEST.md` — richiesta consolidata dei 5 input esterni mancanti
- `START_Piano_di_Sviluppo_all4_integrato.pdf` — Allegato 4, testo integrale del Piano di Sviluppo
