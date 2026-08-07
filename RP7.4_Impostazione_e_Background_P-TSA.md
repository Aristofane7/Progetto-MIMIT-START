# OR7.4 — Product Technological Sustainability Assessment (P-TSA)
## Documento di impostazione: background e proposta metodologica

> **Progetto START** — SusTainable dAta-dRiven manufacTuring
> Accordo Innovazione DM 31/12/2021 — Prog. n. F/310087/01-05/X56
> Responsabilità: Gresmalt — Capofila
> Documento di lavoro propedeutico alla stesura della Relazione Parziale RP7.4
> Versione: bozza di impostazione — 07.08.2026

---

## 0. Scopo di questo documento

Questo non è la relazione finale RP7.4, ma il documento di impostazione che la
prepara: fissa il **background** della sostenibilità tecnologica di prodotto
attingendo alla documentazione di progetto già disponibile, e propone in modo
operativo **come procedere** all'esecuzione dell'attività 7.4 e alla scrittura
della relazione. La struttura finale della RP7.4 seguirà il template di progetto
(`RPX.Y Titolo_Relazione_Parziale`): 1. Introduzione — 2. Metodologia —
3. Risultati — 4. Discussione e conclusioni. La § 7 di questo documento propone
già l'indice della relazione mappato su quel template.

---

# PARTE A — BACKGROUND

## 1. Inquadramento dell'attività nel Piano di Sviluppo

Il Piano di Sviluppo (§ 7.4) definisce l'attività così:

> *«Product Technological Sustainability Assessment (P-TSA): oltre alle
> performance di sostenibilità di fabbrica (OR7.3), per avere una visione
> completa del sistema produttivo, è necessario considerare anche le prestazioni
> del prodotto. […] verranno perfezionate tecniche e sistemi di controllo qualità
> del prodotto per determinare in maniera quantitativa i valori di performance
> tecnica che assicurino la conformità con il quadro normativo previsto per i
> materiali ceramici. A tale fine si applicherà la metodologia per la valutazione
> della sostenibilità tecnologica di prodotto (P-TSA), seguendo l'approccio del
> ciclo di vita (LCT) e lo schema della ISO 14040, con la prospettiva di supply
> chain (cradle-to-grave).»*

**Risultati e KPI attesi (dalla tabella del Piano):**

| Risultato task | KPI | Baseline | Obiettivo |
|---|---|---|---|
| In-/Outputs Availability (IOA) | **Stock Coverage Rate** indicators (SCRs) | 0.0 | Indicatore per 3 tipologie |
| Operational Performance (OP) | **Productivity Indicators** (PsI) | 0.0 | Indicatore per 3 tipologie |
| Technical Quality (TQ) | **Output Conformity Rate** (OCRs) | 0.0 | Indicatore per 3 tipologie |
| Normalizzazione degli indicatori | **Product Technology Sustainability Index (P-TSI)** | 0.0 | Indice per 3 tipologie |

**Problema progettuale n. 4 e soluzione prevista.** Il cambio di focus dal
processo al prodotto richiede un **cambio dell'unità funzionale**. Il Piano
prescrive di condurre prove di assessment considerando *alternativamente* come
unità funzionale **1 m² di piastrelle prodotte, 1 t di piastrelle prodotte, o un
lotto di tipologia produttiva**, scegliendo l'opzione che fornisce
l'informazione più completa sulle prestazioni tecnologiche del prodotto.

**Interdipendenze a valle.** Il P-TSI di OR7.4 è, insieme all'EEA+ Index di
OR7.3, uno dei due KPI del **collaudo della Intelligent Industry (OR7.8)**, dove
è previsto un monitoraggio degli indici su 12 mesi (6 minimi + buffer di 6). I
prototipi di collezione ceramica di OR7.9 saranno inoltre caratterizzati
tecnologicamente anche tramite OR7.4. La RP7.4 è quindi un tassello abilitante di
RF7.

## 2. Il gap scientifico che il P-TSA colma

La letteratura e la prassi misurano bene l'impronta **ambientale** (LCA, ISO
14040/44), **economica** e **sociale**, ma trattano la **tecnologia** come mero
*abilitatore* di quelle performance, non come **dimensione di sostenibilità a sé
stante**, dotata di indicatori propri. Framework come GRI e gli SDG citano la
tecnologia solo come *means of implementation*, senza metriche dedicate. Il
progetto START adotta invece la **visione quadridimensionale della
sostenibilità** (ambientale, economica, sociale, **tecnologica**) e misura
esplicitamente quest'ultima. La sostenibilità tecnologica è definita come
*«la capacità di un sistema produttivo di mantenere nel tempo le proprie
prestazioni operative»* (Vacchi et al., 2021, nota 101 del Piano).

## 3. Le fondamenta metodologiche già disponibili nel progetto

L'attività 7.4 non parte da zero: eredita un impianto teorico e strumentale
consolidato negli OR6 e OR7.

### 3.1 Fondamento teorico — Vacchi et al. (2021), nota 101
*"Technological Sustainability or Sustainable Technology? A multidimensional
vision of sustainability in manufacturing"*, Sustainability 13(17), 9942.
È il riferimento esplicitamente citato dal Piano per il P-TSA. Fornisce lo
schema **ISO 14040 in 4 fasi** applicato alla tecnologia, la prospettiva di
**value chain cradle-to-grave con 7 attività**, le **3 categorie d'impatto
tecnologico** (IOA, OP, TQ) e i **3 indicatori generali** (SCR, PI, OCR), con le
formule di normalizzazione (z-score), aggregazione e composizione in P-TSI, oltre
al **TII** (Technology Improvement Index) per la lettura temporale. Distingue due
declinazioni del metodo: **P-TSA** (prodotto/processo, unità di analisi = unità
funzionale) e **O-TSA** (organizzazione). OR7.4 è la declinazione **P-TSA**.

### 3.2 Validazione operativa del metodo — paper O-TSA "data-driven"
*"From black box to analytical insight: A data-driven evaluation of technological
sustainability in manufacturing supply chains"*, Supply Chain Analytics 12 (2025)
100171 (Vacchi, Settembre-Blundo et al.).
È l'applicazione empirica del framework — nella sua variante **O-TSA
(organizzativa)** — a un produttore di piastrelle ceramiche. Fornisce elementi
direttamente riusabili per OR7.4:
- **funzione di scoring a soglie** che mappa il valore grezzo di ciascun
  indicatore su una scala discreta 1–5 (`s = f(x)`) calibrata su standard
  (ISO 14040/44, ISO 55000), benchmark di settore, dati storici e giudizio
  esperto;
- **pesi per indicatore** entro ciascuna dimensione (∑w = 1) ottenuti con
  **AHP + workshop di consenso** e verifica del **Consistency Ratio (CR ≤ 0,10)**;
- **aggregazione gerarchica** in punteggi dimensionali `S_IOA, S_OP, S_TQ` e
  quindi in un indice sintetico (TSI) e nella sua variazione temporale (TII);
- **analisi di sensibilità** dei pesi (±10–20 %) per verificare la robustezza del
  ranking;
- il caso studio ceramico ha restituito un profilo con IOA come dimensione più
  forte e OP come principale area di miglioramento — utile come benchmark di
  taratura delle soglie.

> **Nota di coerenza.** Il paper 2025 formalizza la variante **O-TSA** con
> scoring 1–5. Il Piano per OR7.4 chiede la variante **P-TSA** con gli indicatori
> "grezzi" SCR/PsI/OCR e normalizzazione z-score (Vacchi 2021). La proposta in
> Parte B tiene insieme i due contributi: **indicatori P-TSA** (§ 3.1) come cuore
> del calcolo, **funzione di scoring 1–5 e pesatura AHP** (§ 3.2) come layer
> opzionale di leggibilità/robustezza. Va deciso — è una scelta metodologica —
> quale delle due normalizzazioni adottare come primaria (vedi § 6.4).

### 3.3 Strumenti e dati di prodotto — OR6.8 e OR6.9
- **RP6.8 Product Analysis**: segmentazione data-driven del portafoglio
  (13.251 prodotti finiti, attributi estetici/strutturali/prestazionali + vendite
  2017–2024) tramite **K-Prototypes** in **22 cluster** (Silhouette 0,493; CQS
  0,780 "Molto Buono"). Emergono **poli produttivi dominanti** — es. Cluster 21
  (rettangolare, medio, 8 mm, effetto cemento; 634.155 m²), Cluster 3 (medio,
  9 mm, ANTISLIP, chiaro; 622.933 m²), Cluster 14 (443.362 m²) — e cluster di
  nicchia. Questa segmentazione è la base naturale per selezionare le **3
  tipologie produttive** su cui condurre il P-TSA.
- **RP6.9 Data-driven Product Design** + Annesso *Protocollo di Product Design*:
  metriche e parametri prestazionali di prodotto, utili come metriche
  tecnologiche di inventario per gli indicatori TQ.

### 3.4 Impianto gemello di processo — OR7.3 (EEA+)
La **RP7.3** (Assessment termodinamico della fabbrica) è il gemello "di processo"
della 7.4 e fornisce il **modello di riferimento per formato, house style e
governance del dato**:
- pipeline eseguita **end-to-end sull'infrastruttura Edge-to-Cloud (E2C)**
  collaudata in OR7.1–7.2, alimentabile sia da **serie storiche ERP/MES** sia da
  **dati in tempo reale E2C**;
- **AHP con CR = 0,0169** (consistente) per la ponderazione tra dimensioni;
- **controlli di qualità** (coerenza, assenza di doppio conteggio, coefficienti
  tracciati e versionati) e **analisi di sensibilità** (coefficienti ±10 %, pesi,
  α/β);
- **artefatti dati** riusabili come modello strutturale: `data_collection.xlsx`
  (schede di raccolta per unità/anno), `calculation_log.xlsx` (log riga-per-riga
  formula→input→output, versionato), `ahp_weights.xlsx` (matrice + pesi + CR).
La 7.4 replicherà questo impianto **a livello di prodotto/tipologia** anziché di
unità produttiva.

### 3.5 Perimetro impianti
Le tre unità del gruppo (già in RP7.3) sono **D020 Viano (MTO)**, **D060
Scandiano (ibrido MTS+MTO, con preparazione impasto atomizzato)** e **D240
Frassinoro (MTO)**. Il P-TSA di prodotto sarà ancorato a questi impianti come
contesto produttivo delle tipologie analizzate.

## 4. Che cos'è la sostenibilità tecnologica **di prodotto** (definizione operativa)

Applicando la logica LCT/ISO 14040 al **prodotto ceramico** lungo la supply chain
cradle-to-grave, la sostenibilità tecnologica di prodotto è la capacità del
sistema-prodotto di:
1. **rendere disponibili gli input/output giusti al momento giusto** lungo la
   catena, garantendo continuità operativa (→ **IOA**): l'output di una fase è
   l'input della successiva;
2. **trasformare efficientemente le risorse in valore** per l'utente interno o il
   cliente finale, ottimizzando il rapporto output/input (→ **OP**);
3. **possedere le caratteristiche intrinseche e i parametri funzionali** che
   soddisfano i requisiti attesi **e la conformità normativa** dei materiali
   ceramici (→ **TQ**).

Le tre categorie sono concettualmente parenti dei tre fattori dell'**OEE**
(Availability, Performance, Quality), qui però estese all'intero ciclo di vita
del prodotto e non alla sola macchina/impianto.

---

# PARTE B — PROPOSTA SU COME PROCEDERE

## 5. Architettura metodologica proposta (ISO 14040 in 4 fasi)

### Fase 1 — Goal & Scope (definizione obiettivo e campo di applicazione)
- **Obiettivo**: quantificare il livello di sostenibilità tecnologica raggiunto
  dal prodotto ceramico rispetto a IOA, OP, TQ, sintetizzato nel **P-TSI**, per
  **3 tipologie produttive**.
- **Prospettiva**: LCT, supply chain **cradle-to-grave**.
- **Sistema-prodotto e 7 attività** (da Vacchi 2021, variante P-TSA):
  1. Sourcing (cradle-to-gate) — approvvigionamento materie prime e fattori;
  2. Inbound Logistics (cradle-to-gate);
  3. **Operations (gate-to-gate)** — trasformazione fisico/chimica in prodotto
     finito, incluso confezionamento;
  4. Internal Logistics (gate-to-gate) — stoccaggio prodotti finiti;
  5. Outbound Logistics (gate-to-grave);
  6. Product Usage (gate-to-grave);
  7. Waste Logistics (gate-to-grave) — fine vita.
- **Unità funzionale**: decisione da prendere con prove comparate (vedi § 6.1).
- **Baseline temporale**: coerente con OR7.3, riferimento 2022 e serie di lavoro;
  per OR7.8 la lettura sarà mensile su 12 mesi per abilitare il TII.

### Fase 2 — Technological Inventory Analysis
Raccolta, per ciascuna delle 7 attività e per ciascuna tipologia, degli input e
output entro il perimetro, ed elaborazione delle **metriche tecnologiche** che
alimentano gli indicatori (vedi § 6.2). Fonti: ERP/MES, controllo qualità,
sistemi di magazzino/logistica, dati E2C in tempo reale, e output di OR6.8/6.9.

### Fase 3 — Technological Impact Assessment
1. **Classificazione**: ogni metrica è associata alla categoria IOA/OP/TQ sulla
   quale incide.
2. **Caratterizzazione** — costruzione dei tre indicatori generali:
   - **SCR** (IOA) — *Stock Coverage Rate*: `SCR = AS / AC`
     (Average Stock / Average Consumption dell'input per attività e tempo);
   - **PsI** (OP) — *Productivity Indicator*: `PI = ROU / RIN`
     (Real Output / Real Input per attività e tempo);
   - **OCR** (TQ) — *Output Conformity Rate*: `OCR = QP / AT`
     (Quality Parameter / Acceptability Threshold da normativa vigente).
3. **Normalizzazione** — z-score per attività:
   `z = (x − media) / deviazione standard` (media 0, dev. std 1).
4. **Aggregazione in sotto-indici** (media aritmetica ponderata, pesi ∑w = 1;
   equal weighting come caso base):
   - `IOAI = Σ w·z(SCR)` ; `OPI = Σ w·z(PI)` ; `TQI = Σ w·z(OCR)`.
5. **Composizione nel P-TSI**:
   `P-TSI = w_IOA·IOAI + w_OP·OPI + w_TQ·TQI` (equal weighting come caso base,
   pesatura AHP come variante — § 6.4).
6. **Lettura temporale (TII)** su serie mensile (per OR7.8):
   `ΔTSI(t-1,t) = (TSI_t / TSI_{t-1})·100 − 100` ; `TII = media dei 12 Δ mensili`.

### Fase 4 — Technological Interpretation
(1) identificazione dei fattori significativi; (2) valutazione di completezza
dell'inventario + **analisi di sensibilità** (soglie, pesi, unità funzionale) e
controlli di coerenza; (3) redazione del report con risultati, conclusioni e
raccomandazioni operative (leve di miglioramento per tipologia).

## 6. Decisioni progettuali da prendere prima dell'esecuzione

### 6.1 Unità funzionale — prove comparate (Problema n. 4)
Condurre la prova di assessment con le tre unità funzionali alternative e
scegliere la più informativa:

| Opzione | Pro | Contro | Uso indicato |
|---|---|---|---|
| **1 m² prodotto** | unità naturale del settore, confrontabile con OR7.3 (m² equivalente) e con i KPI di OR7.5/7.8 | poco sensibile a spessore/peso e quindi al contenuto materico | benchmark trasversale tra tipologie |
| **1 t prodotta** | cattura l'intensità materica ed energetica reale (rilevante per gres/spessori 9–20 mm) | meno leggibile commercialmente | letture di efficienza risorse (OP) |
| **Lotto di tipologia produttiva** | massima aderenza al controllo qualità reale (conformità per lotto), coerente con la segmentazione OR6.8 | dimensione lotto variabile, richiede normalizzazione | letture di conformità/qualità (TQ) e SCR |

**Raccomandazione preliminare**: usare **il lotto di tipologia produttiva** come
unità funzionale primaria (massimizza l'informazione su IOA e TQ ed è coerente
con la richiesta "per 3 tipologie"), riportando **1 m²** come unità di
normalizzazione secondaria per la comparabilità con OR7.3/7.5/7.8. La scelta va
formalizzata dopo le prove ed è essa stessa oggetto dell'analisi di sensibilità.

### 6.2 Le 3 tipologie produttive
Selezionarle dalla segmentazione **OR6.8** privilegiando rappresentatività e
disponibilità dati. Proposta operativa: i **3 poli produttivi dominanti** per
volume e coerenza interna, es.:
- **T1** — Cluster 21: rettangolare, formato medio, spessore 8 mm, effetto cemento;
- **T2** — Cluster 3: formato medio, spessore 9 mm, prestazione ANTISLIP, chiaro;
- **T3** — un terzo polo (es. Cluster 14) o, in alternativa, una tipologia che
  copra la fascia **gres spessorato 20 mm** (outdoor) per estendere il gradiente
  tecnico-normativo.
Criterio: coprire un **gradiente di formato/spessore/prestazione antiscivolo**
(le variabili risultate più discriminanti in OR6.8), così da rendere le 3 letture
informative e non ridondanti. La scelta finale va concordata con
produzione/qualità.

### 6.3 Set di metriche e indicatori per il ceramico (bozza da validare in workshop)
Da confermare in workshop con produzione, manutenzione e qualità (come in OR6.8 e
nel paper O-TSA), selezionando per ogni categoria le metriche più rappresentative
e **effettivamente misurabili** su ERP/MES/qualità/E2C:

- **IOA → SCR** (per le attività di sourcing, logistica interna, magazzino):
  copertura scorte materie prime critiche (impasti/atomizzato, smalti, engobbi,
  inchiostri), semilavorati e prodotto finito = *scorta media / consumo medio*;
  eventuale disponibilità/uptime delle linee dedicate alla tipologia.
- **OP → PsI** (attività Operations): produttività = *output reale / input reale*
  (m² o t di prima scelta per unità di risorsa: energia kWh/kg o kWh/m², ore
  linea, materia prima); complementabile con downtime e variazione di ciclo.
- **TQ → OCR** (Operations + controllo qualità, gate-to-grave): conformità =
  *parametro qualità / soglia di accettabilità normativa*, sui parametri della
  **serie ISO 10545** e classi UNI EN 14411 per piastrelle ceramiche
  (assorbimento d'acqua, resistenza alla flessione/carico di rottura, resistenza
  all'abrasione PEI, resistenza allo scivolamento R/DCOF, resistenza al gelo,
  planarità/rettilineità/calibro, resistenza chimica e alle macchie). Da
  raccordare con i KPI di qualità di **OR7.5** (RFT, Defect Rate, Inspection Pass
  Rate, Customer Rating) che forniscono le metriche grezze.

> Le **soglie** di conformità/scoring vanno triangolate — come in OR6.8/O-TSA —
> tra **standard e normativa** (ISO 10545, UNI EN 14411, ISO 14040/44, ISO 55000),
> **dati storici interni** e **giudizio esperto**, con protocollo di taratura in
> 3 passi (raccolta benchmark → analisi distribuzioni storiche → validazione
> panel).

### 6.4 Schema di normalizzazione e pesatura
- **Caso base**: normalizzazione **z-score** e **equal weighting** (Vacchi 2021),
  per aderenza al riferimento del Piano e trasparenza.
- **Variante di leggibilità/robustezza**: **scoring a soglie 1–5** + **pesi AHP**
  con verifica **CR ≤ 0,10** e **workshop di consenso** (paper O-TSA / RP7.3),
  riutilizzando l'impianto `ahp_weights.xlsx`.
- Entrambe vanno riportate e messe a confronto nell'analisi di sensibilità; va
  dichiarata quale si assume come primaria per il KPI.

### 6.5 Architettura dati e governance (riuso da OR7.1–7.3)
Alimentare la stessa pipeline da **due sorgenti** con identica struttura logica:
**ERP/MES** (serie storica) e **E2C** (tempo reale), come in RP7.3. Predisporre
gli artefatti gemelli: `RP7.4_data_collection.xlsx` (schede per tipologia /
attività / periodo), `RP7.4_calculation_log.xlsx` (log formula→input→output
versionato), `RP7.4_weights.xlsx` (soglie + pesi + CR). Applicare i **controlli di
coerenza** (unità di misura, assenza di doppio conteggio tra attività,
coefficienti tracciati/versionati, classi di confidenza).

## 7. Struttura proposta per la RP7.4 (mappata sul template di progetto)

**1. Introduzione** — background e baseline (0.0 → indicatori/indice per 3
tipologie), scopi; inquadramento in RF7 e interdipendenze (OR6.8/6.9, OR7.1–7.3,
OR7.5, OR7.8/7.9).

**2. Metodologia** — schema ISO 14040 in 4 fasi (§ 5); definizione unità
funzionale e prove comparate (§ 6.1); 3 tipologie (§ 6.2); set metriche →
SCR/PsI/OCR (§ 6.3); normalizzazione, aggregazione IOAI/OPI/TQI, P-TSI, TII
(§ 5 Fase 3); pesatura e soglie (§ 6.4); architettura dati e controlli (§ 6.5).

**3. Risultati** — tabelle per tipologia: inventario/metriche; SCR, PsI, OCR;
z-score e sotto-indici IOAI/OPI/TQI; **P-TSI per 3 tipologie**; (ove disponibile
serie mensile) TII; esito prove sull'unità funzionale; analisi di sensibilità;
controlli di coerenza; verifica dei KPI di attività.

**4. Discussione e conclusioni** — lettura dei P-TSI e dei punti di forza/debolezza
per tipologia; leve di miglioramento; interdipendenze e contributo a RF7 (input a
OR7.8 come uno dei due KPI di collaudo); contributo innovativo rispetto allo stato
dell'arte (tecnologia come dimensione di sostenibilità misurabile a livello di
prodotto); prospettive verso il monitoraggio continuo su E2C.

## 8. Piano di lavoro operativo

1. **Kick-off metodologico**: congelare unità funzionale (dopo prove § 6.1) e le
   3 tipologie (§ 6.2). *Output*: nota di scoping.
2. **Workshop indicatori/soglie** con produzione, qualità, manutenzione:
   selezione metriche, taratura soglie, pesi AHP + CR. *Output*:
   `RP7.4_weights.xlsx`.
3. **Raccolta e inventario** su ERP/MES + E2C per tipologia/attività/periodo.
   *Output*: `RP7.4_data_collection.xlsx`.
4. **Calcolo** SCR/PsI/OCR → z-score → IOAI/OPI/TQI → P-TSI (e TII se serie
   mensile), con log versionato. *Output*: `RP7.4_calculation_log.xlsx`.
5. **Sensibilità e controlli** (unità funzionale, soglie, pesi; coerenza,
   no double counting). *Output*: tabelle di sensibilità.
6. **Stesura RP7.4** secondo § 7. *Output*: relazione + annessi.
7. **Aggancio a OR7.8**: predisporre la lettura mensile su 12 mesi del P-TSI per
   il collaudo Intelligent Industry.

## 9. Rischi e mitigazioni
- **Disponibilità/granularità dati per tipologia** → partire dalle tipologie meglio
  strumentate (OR6.8) e da un set ridotto di indicatori core, ampliabile
  (approccio a fasi come nel paper O-TSA).
- **Soggettività di soglie/pesi** → AHP con CR ≤ 0,10 + workshop di consenso +
  sensibilità; prospettiva di taratura data-driven futura.
- **Confrontabilità tra tipologie con unità funzionale diverse** → riportare
  sempre la normalizzazione a 1 m² come unità secondaria.
- **Coerenza con OR7.3** → riuso dell'infrastruttura E2C, dell'impianto AHP e dei
  controlli di qualità già collaudati.

## 10. Riferimenti (repository di progetto)
- Piano di Sviluppo START, § 7.4 (P-TSA), § 7.5, § 7.8, § 7.9 e nota 101.
- Vacchi, M., Siligardi, C., Demaria, F., Cedillo-González, E. I.,
  González-Sánchez, R., Settembre-Blundo, D. (2021). *Technological sustainability
  or sustainable technology? A multidimensional vision of sustainability in
  manufacturing.* Sustainability, 13(17), 9942. — **fondamento P-TSA (nota 101)**.
- Vacchi, M., Settembre-Blundo, D., Iattici, L., Ferrari, A. M., Rosa, R.,
  Berselli, N. (2025). *From black box to analytical insight: A data-driven
  evaluation of technological sustainability in manufacturing supply chains.*
  Supply Chain Analytics, 12, 100171. — **validazione operativa (O-TSA)**.
- RP6.8 *Report di Product Analysis* — segmentazione portafoglio (tipologie).
- RP6.9 *Report di Data-driven Product Design* + Annesso *Protocollo di Product
  Design* — metriche di prodotto.
- RP7.1 *Collaudo piattaforma E2C*, RP7.2 *Performance testing della Intelligent
  Factory* — infrastruttura dati sorgente.
- RP7.3 *Assessment termodinamico della fabbrica* (EEA+) + `RP7.3_data_collection`,
  `RP7.3_calculation_log`, `ahp_weights` — gemello di processo, house style e
  artefatti dati di riferimento.
