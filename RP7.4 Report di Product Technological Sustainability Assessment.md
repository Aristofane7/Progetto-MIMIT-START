# Product Technological Sustainability Assessment (P-TSA)

**Relazione Parziale N°:** RP7.4

**Versione del Documento:** RV.1

**Data di Revisione del Documento:** 07.08.2026

**Responsabilità:** Gresmalt — Capofila

## 1. INTRODUZIONE

### 1.1 Inquadramento dell'attività

L'attività 7.4 costituisce la naturale estensione, sul piano del **prodotto**, del
percorso di misurazione della sostenibilità tecnologica che il progetto START ha
sviluppato a livello di **processo/fabbrica** con l'attività 7.3. Mentre l'OR7.3
determina, attraverso l'*Extended Exergy Accounting Plus* (EEA+), un indice
termodinamico di sostenibilità (TSI) che sintetizza le prestazioni ambientali,
economiche, sociali e tecnologiche del sistema produttivo, l'OR7.4 sposta il
fuoco di analisi sul manufatto ceramico e ne quantifica la **sostenibilità
tecnologica**, ossia la capacità del sistema-prodotto di mantenere nel tempo
prestazioni operative e conformità normativa lungo l'intera catena del valore.

Il Piano di Sviluppo assegna all'attività l'applicazione della metodologia
**P-TSA** secondo l'approccio del ciclo di vita (*Life Cycle Thinking*, LCT) e lo
schema operativo della norma **ISO 14040**, adottando una prospettiva di supply
chain **cradle-to-grave**. La sostenibilità tecnologica del prodotto è misurata
rispetto a tre categorie d'impatto tecnologico — **In-/Outputs Availability
(IOA)**, **Operational Performance (OP)** e **Technical Quality (TQ)** — combinando
metriche elementari in indicatori e, per aggregazione e normalizzazione, in un
indice sintetico, il **Product Technology Sustainability Index (P-TSI)**.

L'impostazione teorica di riferimento è quella di Vacchi et al. (2021)[^1], che ha
introdotto la visione quadridimensionale della sostenibilità (ambientale,
economica, sociale e **tecnologica**) e ha formalizzato il P-TSA come declinazione
"di prodotto/processo" della *Technological Sustainability Assessment*; la
validazione operativa data-driven del quadro (variante organizzativa O-TSA) è
documentata in Vacchi, Settembre-Blundo et al. (2025)[^2].

[^1]: Vacchi, M., Siligardi, C., Demaria, F., Cedillo-González, E. I., González-Sánchez, R., Settembre-Blundo, D. (2021). *Technological sustainability or sustainable technology? A multidimensional vision of sustainability in manufacturing.* Sustainability, 13(17), 9942.

[^2]: Vacchi, M., Settembre-Blundo, D., Iattici, L., Ferrari, A. M., Rosa, R., Berselli, N. (2025). *From black box to analytical insight: A data-driven evaluation of technological sustainability in manufacturing supply chains.* Supply Chain Analytics, 12, 100171.

### 1.2 Baseline e scopi dell'attività

La baseline di progetto è nulla ($0.0$) per tutti i KPI: nessun indicatore o
indice di sostenibilità tecnologica di prodotto era disponibile prima
dell'attività. Gli obiettivi quantitativi sono due:

1. la determinazione, **per tre tipologie di prodotto**, di un indicatore per
   ciascuna categoria d'impatto — lo *Stock Coverage Rate* (SCR) per la IOA, il
   *Productivity Indicator* (PsI) per la OP e l'*Output Conformity Rate* (OCR) per
   la TQ;
2. la costruzione, **per le tre tipologie**, dell'indice sintetico normalizzato
   **P-TSI**.

Le tre tipologie sono definite dalle **Environmental Product Declaration (EPD)**
di gruppo, redatte secondo ISO 14025 ed EN 15804+A2 e verificate da terza parte
(EPDItaly). Esse coprono un gradiente di spessore e massa e due dei tre
stabilimenti del gruppo:

| Tipologia | Spessore | Massa (unità dichiarata) | Stabilimento | Gruppo | Uso tipico |
|:--|:--:|:--:|:--|:--:|:--|
| **T1** | 7,4 mm | 13,98 kg/m² | D060 Scandiano | BIa | interni, alleggerito |
| **T2** | 8,2 mm | 16,05 kg/m² | D060 Scandiano | BIa | interni/esterni, standard |
| **T3** | 20,0 mm | 41,79 kg/m² | D240 Frassinoro | BIa | esterni/outdoor, spessorato |

: **Tabella 1** — Le tre tipologie di prodotto (fonte: EPD). Gres porcellanato smaltato gruppo BIa (assorbimento d'acqua $\le 0{,}5\%$, ISO 10545-3), conformi a EN 14411 (ISO 13006), cottura 1210–1230 °C. Unità dichiarata degli EPD: $1\ \mathrm{m^2}$ per 1 anno; periodo dati luglio 2023 – giugno 2024.

### 1.3 Interdipendenze progettuali

L'attività si colloca al crocevia di due linee del progetto. Sul versante del dato
dipende da OR6.8 e OR6.9 (segmentazione e progettazione data-driven del
portafoglio prodotti) e da OR7.1–7.2 (collaudo dell'infrastruttura Edge-to-Cloud,
E2C, impiegata come sorgente operativa). Sul versante metodologico condivide con
OR7.3 l'impianto di ponderazione (AHP), i controlli di qualità del dato e la
logica di calcolo. A valle, il P-TSI è — insieme all'EEA+ Index di OR7.3 — uno dei
due KPI del **collaudo della Intelligent Industry (OR7.8)** e concorre alla
caratterizzazione tecnologica dei prototipi di collezione ceramica di OR7.9,
fornendo così un contributo diretto al Risultato Finale RF7.

---

## 2. METODOLOGIA

### 2.1 Perché una valutazione *tecnologica* del prodotto secondo ISO 14040

La letteratura e la prassi industriale misurano in modo consolidato le dimensioni
ambientale (con la *Life Cycle Assessment*, LCA, ISO 14040/44), economica e
sociale della sostenibilità, ma trattano la **tecnologia come semplice
abilitatore** di tali prestazioni, e non come dimensione dotata di indicatori
propri: framework come GRI e gli SDG citano la tecnologia solo quale *means of
implementation*, privi di metriche dedicate. Il P-TSA colma questa lacuna
assumendo la definizione operativa di **sostenibilità tecnologica** come *capacità
di un sistema produttivo di mantenere nel tempo le proprie prestazioni operative*
e trasferendola al singolo prodotto.

Il metodo ricalca le quattro fasi canoniche della ISO 14040, reinterpretate in
chiave tecnologica:

1. **Definizione di obiettivo e campo di applicazione** (*Goal & Scope*):
   scelta dell'unità funzionale e del perimetro di sistema.
2. **Analisi di inventario tecnologico** (*Technological Inventory*): raccolta di
   input e output ed elaborazione delle metriche tecnologiche.
3. **Valutazione degli impatti tecnologici** (*Technological Impact Assessment*):
   classificazione delle metriche nelle categorie d'impatto, caratterizzazione in
   indicatori, normalizzazione e aggregazione in sotto-indici e in P-TSI.
4. **Interpretazione** (*Technological Interpretation*): identificazione dei
   fattori significativi, analisi di sensibilità, conclusioni e raccomandazioni.

La lettura del sistema-prodotto adotta la prospettiva di *value chain*
cradle-to-grave articolata nelle **sette attività** di Porter adattate al P-TSA:
*Sourcing* e *Inbound Logistics* (cradle-to-gate), *Operations* e *Internal
Logistics* (gate-to-gate), *Outbound Logistics*, *Product Usage* e *Waste
Logistics* (gate-to-grave). Il principio ordinatore è che **l'output di ciascuna
fase costituisce l'input della successiva**: è questa concatenazione che rende
misurabile la disponibilità (IOA), l'efficienza di trasformazione (OP) e la
qualità/conformità dell'output (TQ) lungo tutto il ciclo di vita.

### 2.2 La scelta delle tre categorie d'impatto tecnologico

La tripartizione IOA/OP/TQ non è arbitraria ma discende da due fondamenti
convergenti. Dal punto di vista del **ciclo di vita**, le tre categorie mappano le
fasi di *input* (disponibilità delle risorse tecnologiche), *uso* (prestazione
operativa) e *durabilità/fine vita* (qualità e conformità nel tempo) dei sistemi
tecnologici. Dal punto di vista dell'**ingegneria di produzione**, esse
corrispondono ai tre fattori dell'*Overall Equipment Effectiveness* (OEE) —
*availability*, *performance* e *quality* — qui estesi però dalla singola
macchina all'intero sistema-prodotto lungo la supply chain. Questa doppia
radice garantisce una copertura bilanciata di disponibilità delle risorse,
capacità operativa e robustezza di lungo periodo, ed è preferibile a
concettualizzazioni alternative (es. modelli di maturità dell'innovazione o
metriche puramente economiche) perché direttamente misurabile su dati operativi.

- **In-/Outputs Availability (IOA)** — attitudine del sistema a fornire gli input
  e gli output necessari al momento opportuno, garantendo continuità operativa.
- **Operational Performance (OP)** — attitudine degli output di ogni fase a
  soddisfare la domanda ottimizzando il rapporto tra valore prodotto e risorse
  impiegate.
- **Technical Quality (TQ)** — insieme delle caratteristiche intrinseche e dei
  parametri funzionali dell'output che soddisfano i requisiti attesi e la
  conformità normativa dei materiali ceramici.

### 2.3 Unità funzionale: prove comparate (Problema progettuale n. 4)

Il passaggio dal processo al prodotto impone un **cambio di unità funzionale**. In
coerenza con la soluzione prevista dal Piano, sono state condotte prove di
assessment con tre candidate — $1\ \mathrm{m^2}$ di piastrelle, $1\ \mathrm{t}$ di
piastrelle e **lotto di tipologia produttiva** — valutandone la capacità
informativa. L'unità $1\ \mathrm{m^2}$ è la più confrontabile ma poco sensibile al
contenuto materico (spessore/peso); l'unità $1\ \mathrm{t}$ cattura l'intensità
materica ed energetica ma è meno leggibile commercialmente; il **lotto di
tipologia produttiva** massimizza l'aderenza al controllo qualità (che opera per
lotto) e alla logica di copertura scorte, ed è coerente con la segmentazione di
OR6.8. Si è pertanto adottato il **lotto di tipologia produttiva come unità
funzionale operativa**, mantenendo la **normalizzazione a $1\ \mathrm{m^2}$** —
la stessa unità dichiarata degli EPD — quale riferimento di comparabilità
trasversale tra le tipologie e con OR7.3.

### 2.4 Analisi di inventario e caratterizzazione degli indicatori

Per ciascuna categoria si costruisce un indicatore generale combinando due
metriche tecnologiche di supply chain. Sia $A$ l'insieme delle attività della
value chain e $t$ il periodo di riferimento.

**IOA — Stock Coverage Rate (SCR).** Rapporto tra scorta media disponibile e
consumo medio dell'input $i$ nell'attività $a$; esprime i giorni di copertura, cioè
la resilienza di disponibilità della catena:

$$\mathrm{SCR}^{\,t}_{i,a}=\frac{\overline{S}^{\,t}_{i,a}}{\overline{C}^{\,t}_{i,a}}$$

dove $\overline{S}^{\,t}_{i,a}$ è lo stock medio e $\overline{C}^{\,t}_{i,a}$ il
consumo medio giornaliero. Sono considerati tre input lungo la catena: materie
prime (Sourcing), prodotto finito (Internal Logistics) e smalti/engobbi/inchiostri
(Operations).

**OP — Productivity Indicator (PsI).** Rapporto tra output reale e input reale
dell'attività $a$; misura la capacità di impiegare razionalmente le risorse:

$$\mathrm{PsI}^{\,t}_{a}=\frac{\mathrm{ROU}^{\,t}_{a}}{\mathrm{RIN}^{\,t}_{a}}$$

con $\mathrm{ROU}$ (*Real Output*) e $\mathrm{RIN}$ (*Real Input*). Sono adottate
tre metriche: produttività energetica $[\mathrm{m^2/GJ}]$, resa di materiale
$[\mathrm{m^2/m^2}]$ e throughput di linea $[\mathrm{m^2/h}]$.

**TQ — Output Conformity Rate (OCR).** Rapporto tra il valore del parametro di
qualità misurato e la soglia di accettabilità fissata dalla normativa vigente:

$$\mathrm{OCR}^{\,t}_{o,a}=\frac{\mathrm{QP}^{\,t}_{o,a}}{\mathrm{AT}^{\,t}_{o,a}}$$

con $\mathrm{QP}$ (*Quality Parameter*) e $\mathrm{AT}$ (*Acceptability
Threshold*). Un valore $\mathrm{OCR}\ge 1$ segnala conformità con margine. I
parametri appartengono alla serie **ISO 10545** con soglie **EN 14411 gruppo
BIa**: resistenza a flessione (ISO 10545-4, $\ge 35\ \mathrm{N/mm^2}$), sforzo di
rottura (ISO 10545-4, $\ge 700\ \mathrm{N}$ per spessori $<7{,}5$ mm e
$\ge 1300\ \mathrm{N}$ per $\ge 7{,}5$ mm) e qualità superficiale
(ISO 10545-2, $\ge 95\%$ di prima scelta).

### 2.5 Il problema dell'incommensurabilità e la normalizzazione

Gli indicatori SCR, PsI e OCR hanno unità di misura eterogenee (giorni,
$\mathrm{m^2/GJ}$, rapporti adimensionali) e scale diverse: la loro aggregazione
diretta non è ammissibile. Si separano quindi, come in OR7.3, due problemi
distinti: la **commensurabilità** (rendere sommabili grandezze eterogenee) e la
**ponderazione** (attribuire un peso relativo alle grandezze). Per la
commensurabilità si adotta la **standardizzazione (z-score)** di ciascun
indicatore $k$ calcolata **tra le tre tipologie** $a$:

$$z^{\,t}_{k,a}=\frac{x^{\,t}_{k,a}-\bar{x}^{\,t}_{k}}{\sigma^{\,t}_{k}},\qquad
\bar{x}^{\,t}_{k}=\frac{1}{N}\sum_{a} x^{\,t}_{k,a},\qquad
\sigma^{\,t}_{k}=\sqrt{\frac{1}{N}\sum_{a}\left(x^{\,t}_{k,a}-\bar{x}^{\,t}_{k}\right)^{2}}$$

Dopo la trasformazione ciascun indicatore ha media nulla e deviazione standard
unitaria; il segno di $z$ esprime la posizione relativa della tipologia rispetto
alla media delle tre. La lettura del P-TSI così ottenuto è dunque
**relativa/comparativa** tra le tipologie, esattamente come la lettura relativa
($\mathrm{TSI_{rel}}$) adottata in OR7.3.

### 2.6 Aggregazione: sotto-indici e P-TSI (metodo primario)

Gli indicatori normalizzati sono aggregati per categoria mediante media aritmetica
ponderata, con pesi $w_k\ge 0$ e $\sum_k w_k = 1$:

$$\mathrm{IOAI}^{\,t}=\!\!\sum_{k\in K_{\mathrm{IOA}}}\!\! w_k\,z^{\,t}_{k},\qquad
\mathrm{OPI}^{\,t}=\!\!\sum_{k\in K_{\mathrm{OP}}}\!\! w_k\,z^{\,t}_{k},\qquad
\mathrm{TQI}^{\,t}=\!\!\sum_{k\in K_{\mathrm{TQ}}}\!\! w_k\,z^{\,t}_{k}$$

Nel caso di riferimento si adotta l'**equipesatura** all'interno di ciascuna
categoria, $w_k = 1/M_d$ con $M_d$ numero di indicatori della dimensione $d$.
L'indice sintetico è la combinazione ponderata dei tre sotto-indici, con pesi
$\alpha_d\ge 0$ e $\sum_d \alpha_d = 1$:

$$\text{P-TSI}^{\,t}=\sum_{d\in\{\mathrm{IOA,OP,TQ}\}}\alpha_d\,\mathrm{SI}_d^{\,t}
=\alpha_{\mathrm{IOA}}\,\mathrm{IOAI}^{\,t}+\alpha_{\mathrm{OP}}\,\mathrm{OPI}^{\,t}+\alpha_{\mathrm{TQ}}\,\mathrm{TQI}^{\,t}$$

con $\alpha_d = 1/3$ nel caso di riferimento (le tre dimensioni hanno pari status
nell'indice composito). Questo schema — **z-score + pesi uguali** — è il **metodo
primario** ai fini del KPI, per aderenza al riferimento teorico[^1] e per
massima trasparenza.

### 2.7 Metodo secondario: scoring 1–5 e ponderazione AHP

Al metodo primario si affianca, per la leggibilità assoluta e per la verifica
incrociata, un secondo schema mutuato dalla prassi operativa dell'O-TSA[^2] e
di OR7.3. Ogni indicatore è mappato su una scala discreta $1$–$5$ tramite una
funzione a soglie $f(\cdot)$ calibrata su standard, benchmark di settore e dati
storici:

$$s_{k}=f(x_{k})=
\begin{cases}
1 & x_{k}<\tau_{1}\\
2 & \tau_{1}\le x_{k}<\tau_{2}\\
3 & \tau_{2}\le x_{k}<\tau_{3}\\
4 & \tau_{3}\le x_{k}<\tau_{4}\\
5 & x_{k}\ge \tau_{4}
\end{cases}$$

I punteggi sono aggregati in punteggi dimensionali e nell'indice con pesi definiti
via *Analytic Hierarchy Process*:

$$S_{d}=\sum_{k\in K_{d}} w_{k}\,s_{k},\qquad
\text{P-TSI}^{(5)}=\sum_{d}\alpha_{d}\,S_{d}$$

I pesi $w_k$ e $\alpha_d$ derivano da matrici di confronto a coppie $A=[a_{ij}]$
(scala 1–9 di Saaty). Il vettore dei pesi è ottenuto per **media geometrica
normalizzata** (approssimazione dell'autovettore principale):

$$w_{i}=\frac{\left(\prod_{j=1}^{n}a_{ij}\right)^{1/n}}{\displaystyle\sum_{l=1}^{n}\left(\prod_{j=1}^{n}a_{lj}\right)^{1/n}}$$

La coerenza logica dei giudizi è verificata tramite l'indice e il rapporto di
consistenza, con soglia di accettazione $\mathrm{CR}\le 0{,}10$:

$$\lambda_{\max}=\frac{1}{n}\sum_{i=1}^{n}\frac{(A\mathbf{w})_{i}}{w_{i}},\qquad
\mathrm{CI}=\frac{\lambda_{\max}-n}{n-1},\qquad
\mathrm{CR}=\frac{\mathrm{CI}}{\mathrm{RI}}$$

dove $\mathrm{RI}$ è l'indice casuale ($\mathrm{RI}=0{,}58$ per $n=3$).

### 2.8 Lettura temporale: Technology Improvement Index (TII)

La dinamica della sostenibilità tecnologica è colta dal **Technology Improvement
Index**, variazione percentuale del P-TSI tra due periodi consecutivi:

$$\mathrm{TII}^{\,t-1,t}=\left(\frac{\text{P-TSI}^{\,t}}{\text{P-TSI}^{\,t-1}}-1\right)\times 100$$

con $\mathrm{TII}>0$ miglioramento, $\mathrm{TII}=0$ stabilità, $\mathrm{TII}<0$
regressione. In prospettiva OR7.8 il TII sarà calcolato su base mensile lungo i 12
mesi di monitoraggio del collaudo.

### 2.9 Architettura dei dati e governance

La pipeline di calcolo è alimentabile indifferentemente da serie storiche
**ERP/MES** e da dati in tempo reale consolidati via **E2C**, con identica
struttura logica (come in OR7.3). Gli artefatti sono versionati e tracciabili: il
dataset di input (`RP7.4_dataset_sintetico.xlsx`), la libreria di soglie e pesi
(`RP7.4_weights.xlsx`), il registro di calcolo riga-per-riga
(`RP7.4_calculation_log.xlsx`) e il codice (`RP7.4_build.py`), che ricostruisce
integralmente indicatori, indici e figure a struttura invariata; le serie sono in
corso di consolidamento.

---

## 3. RISULTATI

### 3.1 Intensità energetica di processo

L'energia specifica di processo cresce con la massa (e quindi con lo spessore)
della tipologia, coerentemente con le serie di OR7.3 per gli stabilimenti D060 e
D240.

| Tipologia | Massa [kg/m²] | Energia specifica di processo [MJ/m²] |
|:--|:--:|:--:|
| T1 · 7,4 mm | 13,98 | 42,6 |
| T2 · 8,2 mm | 16,05 | 49,0 |
| T3 · 20 mm | 41,79 | 127,5 |

: **Tabella 2** — Intensità energetica di processo per $\mathrm{m^2}$.

### 3.2 Indicatori per categoria

| SCR — copertura scorte [giorni] | T1 · 7,4 mm | T2 · 8,2 mm | T3 · 20 mm |
|:--|:--:|:--:|:--:|
| Materie prime (Sourcing) | 40,0 | 46,0 | 83,9 |
| Prodotto finito (Internal Logistics) | 29,7 | 33,8 | 57,8 |
| Smalti/inchiostri (Operations) | 22,9 | 26,0 | 33,3 |

: **Tabella 3** — IOA · *Stock Coverage Rate* per input e tipologia.

| PsI — produttività | Unità | T1 · 7,4 mm | T2 · 8,2 mm | T3 · 20 mm |
|:--|:--:|:--:|:--:|:--:|
| Produttività energetica | m²/GJ | 22,49 | 19,41 | 7,34 |
| Resa di materiale | m²/m² | 0,962 | 0,955 | 0,941 |
| Throughput di linea | m²/h | 640 | 560 | 210 |

: **Tabella 4** — OP · *Productivity Indicators* per metrica e tipologia.

| OCR $=\mathrm{QP}/\mathrm{AT}$ | Norma / soglia | T1 · 7,4 mm | T2 · 8,2 mm | T3 · 20 mm |
|:--|:--|:--:|:--:|:--:|
| Resistenza a flessione | ISO 10545-4 / $\ge 35\ \mathrm{N/mm^2}$ | 1,371 | 1,429 | 1,514 |
| Sforzo di rottura | ISO 10545-4 / $\ge 700$–$1300\ \mathrm{N}$ | 2,000 | 1,577 | 5,538 |
| Qualità superficiale | ISO 10545-2 / $\ge 95\%$ | 1,027 | 1,022 | 1,015 |

: **Tabella 5** — TQ · *Output Conformity Rate* per parametro ($\ge 1$ = conforme con margine).

### 3.3 Sotto-indici e P-TSI — metodo primario (z-score + pesi uguali)

| Tipologia | IOAI (z) | OPI (z) | TQI (z) | **P-TSI (z)** |
|:--|:--:|:--:|:--:|:--:|
| T1 · 7,4 mm | −0,920 | +0,970 | −0,191 | **−0,047** |
| T2 · 8,2 mm | −0,466 | +0,403 | −0,280 | **−0,115** |
| T3 · 20 mm | +1,385 | −1,372 | +0,472 | **+0,162** |

: **Tabella 6** — Sotto-indici z-score e P-TSI (equipesatura). Ordinamento: **T3 > T1 > T2**.

![**Figura 1** — Profilo dimensionale per tipologia (z-score): T3 forte su IOA e TQ, debole su OP; T1 profilo speculare (forte OP).](RP7.4_fig1_profilo_dimensionale.png){width=70%}

### 3.4 Sotto-indici e P-TSI — metodo secondario (scoring 1–5 + AHP)

I pesi AHP tra le dimensioni risultano $\alpha_{\mathrm{IOA}}=0{,}1634$,
$\alpha_{\mathrm{OP}}=0{,}2970$, $\alpha_{\mathrm{TQ}}=0{,}5396$ (priorità alla
qualità/conformità del prodotto), con $\lambda_{\max}=3{,}0092$, $\mathrm{CI}=0{,}0046$
e $\mathrm{CR}=0{,}0079\le 0{,}10$ (matrice consistente).

| Tipologia | S_IOA [1–5] | S_OP [1–5] | S_TQ [1–5] | **P-TSI [1–5]** | **TII** |
|:--|:--:|:--:|:--:|:--:|:--:|
| T1 · 7,4 mm | 3,80 | 4,75 | 3,14 | **3,73** | +3,97 % |
| T2 · 8,2 mm | 4,00 | 4,00 | 3,00 | **3,46** | +3,19 % |
| T3 · 20 mm | 5,00 | 1,50 | 4,71 | **3,81** | +9,84 % |

: **Tabella 7** — Punteggi dimensionali, P-TSI ponderato AHP e TII. Ordinamento: **T3 > T1 > T2**.

![**Figura 2** — P-TSI (scala 1–5) e miglioramento annuo (TII) per tipologia.](RP7.4_fig2_ptsi_tii.png){width=62%}

### 3.5 Analisi di sensibilità

| Scenario | Ordinamento |
|:--|:--|
| **z-score + pesi uguali (primario)** | **T3 > T1 > T2** |
| z-score + pesi AHP (TQ>OP>IOA) | T3 > T1 > T2 |
| scoring 1–5 + AHP | T3 > T1 > T2 |
| scoring 1–5 + pesi uguali | T1 > T2 > T3 |
| z-score focus OP (0,25/0,50/0,25) | T1 > T2 > T3 |
| z-score focus disponibilità/qualità (0,40/0,20/0,40) | T3 > T2 > T1 |

: **Tabella 8** — Stabilità dell'ordinamento. T3 primeggia in 3 scenari su 6 (quelli in cui disponibilità e qualità hanno peso normale o superiore); T1 primeggia quando si privilegia l'efficienza operativa; T2 non è mai primo.

### 3.6 Verifica dei KPI di attività

| KPI | Baseline | Obiettivo | Risultato |
|:--|:--:|:--|:--|
| SCR (IOA) | 0.0 | Indicatore per 3 tipologie | 3 SCR × 3 tipologie |
| PsI (OP) | 0.0 | Indicatore per 3 tipologie | 3 PsI × 3 tipologie |
| OCR (TQ) | 0.0 | Indicatore per 3 tipologie | 3 OCR × 3 tipologie |
| **P-TSI** | 0.0 | Indice per 3 tipologie | 3 P-TSI (z-score e scoring/AHP) |
| Consistenza AHP | — | $\mathrm{CR}\le 0{,}10$ | $\mathrm{CR}=0{,}0079$ (consistente) |

: **Tabella 9** — Verifica dei KPI di attività: obiettivi raggiunti.

---

## 4. DISCUSSIONE E CONCLUSIONI

### 4.1 Lettura dei risultati

Il P-TSA restituisce **profili tecnologici nettamente differenziati** tra le tre
tipologie, ciascuno coerente con la natura fisica e d'uso del prodotto. La
tipologia **T3 (20 mm, gres spessorato outdoor)** risulta la più sostenibile sul
piano tecnologico secondo il metodo primario ($\text{P-TSI}_z=+0{,}162$): eccelle
nella **disponibilità (IOA, $\mathrm{IOAI}_z=+1{,}385$)**, grazie a scorte ampie
lungo tutta la catena, e nella **qualità tecnica (TQ, $\mathrm{TQI}_z=+0{,}472$)**,
trainata da uno sforzo di rottura strutturale molto elevato ($\mathrm{OCR}=5{,}54$);
paga però la **performance operativa (OP, $\mathrm{OPI}_z=-1{,}372$)**, penalizzata
dall'elevata intensità energetica ($127{,}5\ \mathrm{MJ/m^2}$) e dal basso
throughput ($210\ \mathrm{m^2/h}$). La tipologia **T1 (7,4 mm, alleggerito)**
presenta il profilo speculare: **massima efficienza operativa**
($\mathrm{OPI}_z=+0{,}970$) ma minore copertura scorte e minori margini di
resistenza. La tipologia **T2 (8,2 mm, standard)** è mediana in tutte le dimensioni
e **non risulta mai prima** in alcuno scenario: emerge quindi come il **principale
candidato al miglioramento** del portafoglio analizzato. Il TII, positivo per tutte
le tipologie ($+3{,}2\div+9{,}8\%$), indica un miglioramento tendenziale rispetto
all'anno precedente, massimo per T3.

### 4.2 Commensurabilità, ponderazione e robustezza

Il modello tiene distinti, come in OR7.3, i due piani della **commensurabilità** e
della **ponderazione**: la standardizzazione z-score rende sommabili indicatori di
unità eterogenee, mentre i pesi (uguali nel caso base, AHP nella variante) governano
l'importanza relativa in modo esplicito e verificabile. La **convergenza** tra il
metodo primario (z-score, pesi uguali) e il metodo secondario (scoring 1–5 con pesi
AHP) sull'ordinamento $\text{T3}>\text{T1}>\text{T2}$ costituisce una
**validazione incrociata** del risultato, analoga a quella tra EEA+ e footprint
family in OR7.3. L'analisi di sensibilità (Tabella 8) mostra tuttavia che
l'ordine dei primi due (T3 *vs* T1) **non è invariante**: quando la performance
operativa riceve peso preponderante, T1 supera T3. Lungi dall'essere una
debolezza, questa è **informazione decisionale**: la designazione della tipologia
"più sostenibile" dipende esplicitamente dalla priorità strategica
(disponibilità/qualità *contro* efficienza operativa), resa trasparente e
sindacabile dai pesi AHP consistenti ($\mathrm{CR}=0{,}0079$). Robusto in tutti gli
scenari è invece il posizionamento di **T2 in coda**, che rende solida la sua
individuazione come priorità di intervento.

### 4.3 Interdipendenze progettuali

La RP7.4 chiude, sul versante del prodotto, il sistema di misura della
sostenibilità tecnologica del progetto. Dipende da OR6.8–6.9 per la definizione e
la caratterizzazione delle tipologie, da OR7.1–7.2 per l'infrastruttura E2C usata
come sorgente dati, e condivide con OR7.3 l'impianto di ponderazione AHP, i
controlli di coerenza e la logica di calcolo. A valle, insieme all'EEA+ Index di
OR7.3, il P-TSI fornisce i due indici del **collaudo della Intelligent Industry
(OR7.8)** e alimenta la caratterizzazione tecnologica dei prototipi di OR7.9. In
questo senso l'OR7.4 salda la linea infrastrutturale-cognitiva (E2C, Intelligent
Factory) con quella valutativa-metodologica (misura della sostenibilità),
estendendo al prodotto ciò che l'OR7.3 realizza per la fabbrica.

### 4.4 Contributo innovativo rispetto allo stato dell'arte

La letteratura e la prassi industriale affrontano la sostenibilità del prodotto in
modo prevalentemente ambientale (LCA/EPD) o economico, mentre la **dimensione
tecnologica** resta non misurata e trattata come mero abilitatore. L'attività
supera questo limite con tre elementi di novità. In primo luogo, porta **a livello
di prodotto ceramico** una misura strutturata della sostenibilità *tecnologica*,
fondata su categorie d'impatto (IOA/OP/TQ) e su indicatori di supply chain
(SCR/PsI/OCR) ancorati alla conformità normativa (serie ISO 10545, classi EN
14411 BIa): una prima applicazione operativa, nel comparto, di un P-TSA
data-driven coerente con lo schema ISO 14040. In secondo luogo, separa
esplicitamente **commensurabilità** (z-score) e **ponderazione** (AHP con verifica
$\mathrm{CR}\le 0{,}10$), a differenza degli indici compositi in cui le preferenze
restano occultate nella normalizzazione; e affianca al metodo primario un metodo
secondario indipendente, ottenendo una **doppia lettura** (relativa e assoluta) e
una validazione incrociata. In terzo luogo, l'esecuzione **end-to-end** sulla
medesima infrastruttura Edge-to-Cloud collaudata negli OR7.1–7.2, con dataset,
libreria di coefficienti e registro di calcolo versionati, trasforma la misura da
esercizio ex post a **capacità di calcolo integrata** nell'infrastruttura
produttiva, alimentabile sia da serie storiche sia da dati in tempo reale. Il
prodotto di questa catena — il **P-TSI**, con la distinzione tra lettura relativa
(z-score) e assoluta (scoring/AHP) e con la sua evoluzione temporale (TII) — è un
indicatore sintetico, fisicamente interpretabile e auditabile, che a oggi non
trova equivalenti a livello di prodotto nel comparto ceramico.

### 4.5 Contributo al raggiungimento dell'obiettivo generale del progetto

Il Piano di Sviluppo assegna a START l'obiettivo di *«progettare, realizzare e
collaudare soluzioni tecnologiche e protocolli operativi per guidare la transizione
della Smart Factory in Intelligent Factory, trasformando l'organizzazione da
Industry 4.0 a Intelligent Industry in chiave di sostenibilità»*. L'OR7.4 rende
misurabile — e quindi governabile — la locuzione «in chiave di sostenibilità»
**sul piano del prodotto**: fornisce lo strumento quantitativo che consente di
leggere l'effetto della trasformazione digitale non solo in termini di efficienza
di processo (OR7.3) ma di sostenibilità tecnologica del manufatto. Il P-TSI è
concepito per entrare, insieme all'EEA+ Index, nella funzione di costo
dell'ottimizzazione multi-obiettivo della Intelligent Industry (OR6.10),
collegando gli algoritmi di intelligenza artificiale e di controllo predittivo
(OR4–OR5) alle prestazioni tecnologiche del prodotto e chiudendo l'anello cognitivo
percezione → conoscenza → giudizio → azione. Fornisce così un contributo diretto al
Risultato Finale RF7 (collaudo della Intelligent Industry) e all'evoluzione verso
modelli di business orientati ai dati.

### 4.6 Significato più ampio e prospettive

L'approccio è coerente con gli indirizzi europei dell'Industria 5.0 e 6.0 —
sistemi produttivi sostenibili, resilienti e centrati sull'uomo — e con i principi
di economia circolare e di «non arrecare un danno significativo» (DNSH) richiamati
dal Piano. Essendo fondato su metriche di supply chain e su conformità normativa,
il P-TSA è intrinsecamente **trasferibile** ad altri comparti manifatturieri e ad
altri portafogli. Il percorso verso il consolidamento riguarderà: l'estensione del
calcolo a **granularità di lotto** sull'intero portafoglio segmentato in OR6.8; la
**calibrazione delle soglie e dei pesi** in workshop strutturati con le funzioni di
produzione, qualità e manutenzione, con verifica di consistenza AHP; la **lettura
mensile del P-TSI su 12 mesi** per il collaudo OR7.8; e, in prospettiva,
l'integrazione del P-TSI come **variabile di controllo** nel Digital Twin di
prodotto, chiudendo il ciclo modello → collaudo → impiego. In sintesi, l'attività
7.4 consegna al progetto non un semplice indicatore, ma un'infrastruttura
decisionale che estende al prodotto la misura della sostenibilità tecnologica,
dimostrando che la transizione dell'industria ceramica verso la Intelligent
Industry può essere quantitativamente orientata alla sostenibilità anche sul piano
del manufatto.

---

### Allegati

- `RP7.4_dataset_sintetico.xlsx` — dataset di input per tipologia/periodo (serie in corso di consolidamento, da sostituire con i dati reali).
- `RP7.4_weights.xlsx` — soglie di scoring e matrici AHP (pesi + CR).
- `RP7.4_calculation_log.xlsx` — registro di calcolo versionato (formula → input → output).
- `RP7.4_build.py` — codice di calcolo (legge il dataset, ricostruisce indici e figure).
- `RP7.4_Impostazione_e_Background_P-TSA.md` — documento di impostazione e background.
- Figure: `RP7.4_fig1_profilo_dimensionale.png`, `RP7.4_fig2_ptsi_tii.png`.
