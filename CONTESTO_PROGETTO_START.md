# Contesto — Progetto START (MIMIT)

> Documento di sintesi generato dall'analisi dei 21 documenti del repository
> `Aristofane7/Progetto-MIMIT-START`. Serve come base di conoscenza condivisa
> per le attività successive. Ultima analisi: 2026-08-06.

---

## 1. Identità del progetto

| Voce | Dettaglio |
|---|---|
| **Acronimo** | **START** — *SusTainable dAta-dRiven manufacTuring* |
| **Programma** | DM 31 dicembre 2021 — **Accordi per l'Innovazione** (MIMIT) |
| **Durata** | 36 mesi |
| **KET (tecnologia abilitante)** | **Intelligenza Artificiale** |
| **Area di intervento** | Tecnologie di fabbricazione |
| **Settore applicativo** | Industria **ceramica** (piastrelle) |
| **Coordinatore / capofila** | **Gresmalt** — Resp. progetto: Davide Settembre Blundo (Innovation Program Manager) |

**Idea centrale.** Guidare la transizione dell'industria ceramica **da Industria 4.0 / Smart Factory → Intelligent Factory → Intelligent Industry**, usando l'AI per rendere la produzione più efficiente e sostenibile, dalla fabbrica fino all'impiego del prodotto (involucro edilizio) e con dati di ritorno per l'ottimizzazione continua del prodotto.

- **Smart Factory** = applica conoscenza già acquisita.
- **Intelligent Factory** = acquisisce autonomamente nuova conoscenza e si auto-ottimizza tramite AI.
- **Intelligent Industry** = estende l'intelligenza all'intera organizzazione e ai modelli di business data-driven.

---

## 2. Partenariato e Obiettivi Realizzativi (OR)

RI = Ricerca Industriale · SS = Sviluppo Sperimentale

| OR | Soggetto | Tipo | Oggetto | Risultato finale |
|---|---|---|---|---|
| **OR1** | Libera Università di Bolzano | RI | Concetto globale di **Digital Twin** (AI etica, human-centric, biointelligente) per la transizione. Metodi: Axiomatic Design, ontologie (Protégé/Genesys), data hub integrato. | Concetto globale gemello digitale |
| **OR2** | Università della Calabria | RI | Modelli **ML/ANN** per previsione e classificazione qualità materiali ceramici + diagnostica **non distruttiva (NDT)**: termografia, ultrasuoni, emissione acustica, imaging capacitivo. CNN/TCN, feature extraction, PCA/ICA. | Modelli predittivi qualità |
| **OR3** | Università di Sassari | RI | **Architectural Design 4.0+**: AI a supporto del confort ambientale indoor; involucro edilizio ceramico ventilato con sensori (IoT), efficienza energetica e benessere occupanti. | Soluzioni costruttive involucro ventilato |
| **OR4** | SACMI | RI | Framework di riferimento per il **deployment strutturato dell'AI** nel settore ceramico (use case, algoritmi, infrastruttura IoT, gestione dati). | Framework AI per la ceramica |
| **OR5** | SACMI | SS | Applicazione AI per la **sostenibilità del processo**: controllo supervisionato **predittivo** su indicatori energetici, in impianto pilota. | Sistema di controllo predittivo |
| **OR6** | **Gresmalt** | RI | **Modellazione** delle soluzioni tecnologiche per l'Intelligent Industry: le 4 impronte, architettura E2C, Intelligent Factory, product design. Metodo: **Abductive Design Thinking**. | Quadro operativo Intelligent Industry |
| **OR7** | **Gresmalt** | SS | **Validazione in ambiente operativo** (pilota/pre-industriale): collaudo E2C e performance testing Intelligent Factory. Trade-off & compliance analysis. | Documento finale di collaudo |
| **OR8** | **Gresmalt** | SS | **Project management**, misurazione risultati, analisi scostamenti, disseminazione. | Piano di Coordinamento |

> **Il repository contiene principalmente i deliverable di OR6 e OR7** (report RP6.x e RP7.x), più i manuali dei moduli software e il paper scientifico.

---

## 3. Il cuore metodologico: le 4 impronte e il modello EEA+

### 3.1 La "footprint family" a 4 dimensioni (OR6.1–6.4)

Framework unitario che misura la sostenibilità come incidenza (positiva/negativa) di un'entità su 4 pilastri. Tutti i report condividono: paradigma costruttivista; modello causale **input → activity → output → outcome → impact** (Vacchi et al. 2021); 5 dimensioni (**efficienza, produttività, efficacia, impatto, valore creato**); dati aziendali **MES → ERP → Business Intelligence** + bilanci; validazione sugli stabilimenti Gresmalt (2017–2022).

| Report | Impronta | Strumento (versione alpha) |
|---|---|---|
| RP6.1 (30/07/23) | Tecnologica | **TFA+** — Technological Footprint Assessment Plus |
| RP6.2 (31/10/23) | Ambientale | **EFA+** — Environmental Footprint Assessment Plus |
| RP6.3 (31/01/24) | Sociale | **SFA+** — Social Footprint Assessment Plus (SO-LCA, Ethics by Design/Doing/Use, DALY) |
| RP6.4 (30/04/24) | Economica | **EcoFA+ / EcFA+** — Economic Footprint Assessment Plus |

**Innovazione chiave:** conversione di tutte le grandezze in **Gigajoule (GJ)** → indicatori **adimensionali e direttamente confrontabili** tra le 4 impronte. Integrazione via SAW / MCDA. Le impronte confluiscono nell'ambiente di Intelligent Industry (aggancio a OR4.2 di SACMI).

### 3.2 Modellazione termodinamica della sostenibilità (RP6.5 + Annesso + Paper)

Cambio di paradigma dalla contabilità monetaria alla **termoeconomia** (thermoeconomics): unisce termodinamica ed economia.
- **Exergia** = massimo lavoro utile estraibile (qualità dell'energia); **entropia** = degrado/inefficienza.
- I 4 principi della termodinamica reinterpretati in chiave gestionale (equità, conservazione risorse, minimizzazione sprechi, miglioramento continuo).
- Metodo abduttivo: 16 proposizioni → 2 teoremi → **Gestione Termoeconomica (TM)**.
- **EEA+ = Extended Exergy Accounting Plus**, fondato sull'approccio sistemico **SYMΞX / SYMNX (Systemic Exergy Management)**. Ogni risorsa caratterizzata dai 4 contributi (EFA+, EcoFA+, SFA+, TFA+) normalizzati in GJ e sommati in modo pesato.
- Calcolo exergia: `Ex_gas = η_comb × HHV_metano` (η≈0.9; HHV≈39.8 MJ/Nm³); `Ex_ele = 3.6 × kWh`; rapportati alla produzione (m² piastrelle).
- Indicatore sintetico finale: **TSI** — *Thermodynamic/Technological Sustainability Index*.
- **Paper**: *"Thermoeconomics meets business science"* (Fernández-Miguel, Settembre-Blundo, Vacchi, García-Muiña — Global Journal of Flexible Systems Management, 2024). Dimensioni TM: thermophysics, thermobusiness, thermosocial, thermo-technological.

### 3.3 I moduli operativi "-J" per EEA+ (manuali beta)

Suffisso **-J** = grandezze espresse in **Joule** (implementazione tool-agnostica: Excel `SOMMA.PRODOTTO`, Python `pandas`, Power BI `DAX/SUMX`). Ogni modulo converte le proprie grandezze in exergia con coefficienti versionati (fonte, anno, perimetro, confidenza A–C), confronta con **baseline** e produce un contributo in GJ; regola trasversale: evitare il **doppio conteggio**.

| Modulo | Impronta | Converte in Joule | Output |
|---|---|---|---|
| **TEI-J** | Tecnologica | KPI tecnologici MTS (spray-dryer) e MTO (forming/kiln/finishing): OEE, scarti, qualità, invenduto | `f_tech` |
| **EFA-J** | Ambientale | Materiali, energia, acqua, rifiuti, emissioni, imballi, circolarità | `f_env` |
| **EcoFA-J** | Economica | Voci economiche non fisiche (servizi terzi, logistica, licenze), Valore Aggiunto, immobilizzi (€→MJ) | `f_econ` |
| **SFA-J** | Sociale | Valore per stakeholder, salute/sicurezza (ore perse, CO₂/DALY), formazione, turnover | `f_soc` |

I quattro contributi (`f_env + f_econ + f_soc + f_tech`, in GJ) → **Sustainability Accounting (SA)** di EEA+ → **TSI**. Perimetro gate-to-gate; unità funzionale = piastrella equivalente/kg. Documentati nella **Attività 7.3 — Assessment termodinamico della fabbrica**.

---

## 4. Architettura tecnologica (OR6.6, 6.7, 6.10 + collaudo OR7)

### 4.1 Architettura Edge-to-Cloud (E2C) — RP6.6
Infrastruttura ibrida a **due livelli**:
- **EDGE**: elaborazione locale near-sensor per real-time (anomaly detection, manutenzione predittiva, controllo qualità), bassa latenza, pre-filtraggio dati.
- **CLOUD**: storage storico, analisi predittiva a lungo termine, training/ricalibrazione modelli ML → feedback all'edge (ciclo continuo).
- Integrazione bidirezionale con **MES / ERP / BI** via connettori; data lake + pipeline di **semantizzazione ontologica**; Digital Twin su **Microsoft Power BI**; motore **RT-PSE** (Real-Time Production Simulation Engine); ambiente di collaudo **Digital (Grey) Shadow** (UNIBZ, OR1.3).

### 4.2 Intelligent Factory (RP6.7)
Evoluzione della Smart Factory con ML/analytics sull'E2C. Digital twin in Power BI; logica **make-to-stock** (impasto atomizzato) + 3 unità **make-to-order** (piastrelle finite). Alimenta gli strumenti di sostenibilità (TFA+/EFA+/SFA+/EcoFA+/EEA+).

### 4.3 Intelligent Industry (RP6.10)
Framework dinamico multilivello formalizzato matematicamente (tempo discreto), ciclo cognitivo chiuso (percezione → comprensione → conoscenza → giudizio → azione), 4 layer:
1. Fisico-Operativo · 2. Informativo (E2C) · 3. Cognitivo (Digital Twin, ottimizzazione multi-obiettivo throughput/OEE/qualità/sostenibilità) · 4. Sostenibilità (EEA+ e TSI nella funzione di costo).

### 4.4 Product Analysis & Data-driven Product Design (RP6.8, RP6.9 + Annesso)
- **Product Analysis (RP6.8)**: segmentazione data-driven di **13.251 prodotti** con **K-Prototypes** (dati misti) → **22 cluster**; qualità via Silhouette (0,493) e **CQS = 0,780** ("Molto Buono").
- **Data-driven Product Design (RP6.9)**: protocollo di **Product Design Thinking** data-driven a 3 strati (gemello informativo → analitico K-Prototypes/ARIMA → Design Thinking), con modello di ottimizzazione del portfolio (max E[NPV] − rischio).
- **Annesso**: Template operativo in 6 fasi (kick-off → lettura dati → sintesi parametri ceramici → ideazione/prototipazione → decisione GO/Stop/Re-iterate → chiusura/scheda), tracciabile (coerenza ISO 9001).

---

## 5. Collaudo e performance (OR7)

**RP7.1 — Collaudo piattaforma E2C** (beta, UAT in ambiente reale):
- Latenza EDGE **< 10 ms** in tutti i test; carico 100→5 ms, 2000→10 ms (1,5% errori); cloud 0,8–1,4 s.
- CPU EDGE da baseline 80% → 45% (target <50%); trasferimento dati da 30 s → 0,8 s; errori <1%.
- Feedback utenti: 87% maggiore confidenza, 92% prestazioni in linea/superiori.

**RP7.2 — Performance testing Intelligent Factory** (Digital Grey Shadow):
- Load testing, fault injection, interruzioni fornitura.
- Risultati: latenza EDGE **5 ms**; **−15% fermo macchina**; **+10% capacità produttiva**; **−8 min** attesa media/lotto; **+12% efficienza adattiva**.
- Interoperabilità MES-ERP-BI validata; infrastruttura "production-ready" per l'Attività 7.3 (assessment termodinamico).

---

## 6. Inventario documenti del repository

**Piano** · `START_Piano_di_Sviluppo_all4_integrato.pdf` (Allegato 4, 93 pp.) — documento master
**Impronte (OR6.1–6.4)** · RP6.1 tecnologica · RP6.2 ambientale · RP6.3 sociale · RP6.4 economica
**Termodinamica (OR6.5)** · RP6.5 Report modellazione termodinamica · RP6.5 Annesso (Guida) · Paper *Thermoeconomics meets business science*
**Architettura (OR6.6–6.7, 6.10)** · RP6.6 Architettura E2C · RP6.7 Intelligent Factory · RP6.10 Intelligent Industry
**Prodotto (OR6.8–6.9)** · RP6.8 Product Analysis · RP6.9 Data-driven Product Design + Annesso Protocollo
**Collaudo (OR7)** · RP7.1 Collaudo E2C · RP7.2 Performance testing
**Manuali moduli (beta, per EEA+)** · TEI-J · EFA-J · EcoFA-J · SFA-J
**Template** · `RPX.Y Titolo_Relazione_Parziale_data.docx` — modello di relazione parziale (struttura: Introduzione · Metodologia · Risultati · Discussione e Conclusioni)

---

## 7. Glossario acronimi

- **START** — SusTainable dAta-dRiven manufacTuring
- **OR / RI / SS** — Obiettivo Realizzativo / Ricerca Industriale / Sviluppo Sperimentale
- **RF** — Risultato Finale (di OR) · **RP** — Relazione Parziale (deliverable)
- **E2C** — Edge-to-Cloud · **MES/ERP/BI** — Manufacturing Execution System / Enterprise Resource Planning / Business Intelligence
- **EEA+** — Extended Exergy Accounting Plus · **SYMΞX/SYMNX** — Systemic Exergy Management
- **TFA+/EFA+/SFA+/EcoFA+** — Footprint Assessment Plus (Tecnologica/Ambientale/Sociale/Economica)
- **TEI-J/EFA-J/EcoFA-J/SFA-J** — moduli operativi in Joule per EEA+
- **TM** — Thermoeconomic Management · **SA** — Sustainability Accounting · **TSI** — Thermodynamic/Technological Sustainability Index
- **MTS/MTO** — Make-to-Stock / Make-to-Order
- **ANN/CNN/TCN/ML/DL** — reti neurali (artificiali/convoluzionali/temporali) / Machine / Deep Learning · **NDT** — Non-Destructive Testing
- **DALY** — Disability-Adjusted Life Year · **CQS** — Clustering Quality Score
- **DNSH** — Do No Significant Harm (Reg. UE 2020/852)
