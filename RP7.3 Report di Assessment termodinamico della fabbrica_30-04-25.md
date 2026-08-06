---
progetto: "START — SusTainable dAta-dRiven manufacTuring"
accordo: "Accordo Innovazione DM 31/12/2021"
prog: "F/310087/01-05/X56"
sito: "www.start-innovability.it"
titolo: "ASSESSMENT TERMODINAMICO DELLA FABBRICA"
relazione_parziale: "RP7.3"
versione: "RV.1"
data_revisione: "30.04.25"
responsabilita: "Gresmalt - Capofila"
or_riferimento: "OR7 — Validazione in ambiente operativo della Intelligent Industry"
risultato_finale: "RF7 — Documento finale di collaudo della Intelligent Industry"
---

# ASSESSMENT TERMODINAMICO DELLA FABBRICA

**Relazione Parziale N°:** RP7.3 · **Versione del Documento:** RV.1 · **Data di Revisione:** 30.04.25
**Responsabilità:** Gresmalt – Capofila · **Attività:** 7.3 (OR7) · **Risultato Finale:** RF7

---

## 1. INTRODUZIONE

L'attività documentata nel presente report costituisce la **fase conclusiva dell'Obiettivo Realizzativo 7** e, più in generale, il punto di convergenza dell'intero percorso di ricerca e sviluppo del progetto START. Se il Task 7.1 ha collaudato la spina dorsale infrastrutturale — la piattaforma **Edge-to-Cloud (E2C)** — e il Task 7.2 ne ha certificato la resilienza e la reattività attraverso il *performance testing* della Intelligent Factory, il Task 7.3 chiude il ciclo dimostrando **a cosa serve** quell'infrastruttura: alimentare, in ambiente operativo, un sistema di **contabilità della sostenibilità** capace di leggere la fabbrica come un sistema termodinamico e di restituirne una misura sintetica, olistica e comparabile.

L'attività applica il modello **Extended Exergy Accounting Plus (EEA+)**, sviluppato nella sua versione *alpha* nell'OR6.5, per condurre l'**analisi exergetica della fabbrica** e valutare quantitativamente, in un'unica scala fisica, le prestazioni **tecnologiche** (OR6.1), **ambientali** (OR6.2), **sociali** (OR6.3) ed **economiche** (OR6.4). Il principio unificante — già introdotto lungo tutta la *footprint family* di OR6 — è la **conversione di ogni contributo in Joule (J/GJ)**: solo riconducendo materia, energia, valore economico, lavoro umano e impatti a una grandezza fisica comune, l'**exergia**, è possibile sommarli senza arbitrarietà e sintetizzarli nell'**Indice Termodinamico di Sostenibilità (TSI)**.

La necessità di questa attività nasce da un limite strutturale degli strumenti tradizionali di *sustainability assessment*: l'impronta ambientale (LCA), il *life cycle costing*, gli indicatori sociali (SO-LCA) e le metriche tecnologiche (OEE, scarti, qualità) sono calcolati con metodologie eterogenee, unità di misura non commensurabili e perimetri disallineati. Il risultato è una fotografia frammentata, incapace di supportare decisioni che bilancino simultaneamente le quattro dimensioni. EEA+ supera questo limite adottando l'exergia come "moneta fisica" universale.

Il collaudo è stato condotto sulle **tre unità produttive del gruppo Gresmalt** — **D020** (Viano), **D060** (Scandiano, impianto ibrido) e **D240** (Frassinoro) — sfruttando la duplice sorgente dati resa disponibile dall'architettura E2C validata negli OR7.1 e OR7.2: le **serie storiche di dati primari archiviati nell'ERP** (che definiscono la *baseline*) e i **dati raccolti in tempo reale** dal livello EDGE (che definiscono lo scenario obiettivo). L'attività ha quindi tre finalità:

1. Applicare in ambiente operativo il modello EEA+ e verificarne la funzionalità end-to-end sull'infrastruttura E2C;
2. Produrre il **quadro di sostenibilità multidimensionale** (ambiente, economia, società, tecnologia) delle tre unità produttive, con il calcolo del **TSI** su dati storici (baseline) e su dati in tempo reale (obiettivo);
3. Consolidare, a valle del collaudo, la **versione beta dell'EEA+**, insieme ai quattro moduli operativi in Joule (**EFA-J, EcoFA-J, SFA-J, TEI-J**) e alla libreria di coefficienti tracciata.

Il risultato finale dell'attività è pertanto **duplice**, in coerenza con quanto previsto dal Piano di Sviluppo: da un lato un *report* di performance di sostenibilità multidimensionale, dall'altro la certificazione della **versione beta dello strumento EEA+**. In questo senso il Task 7.3 rappresenta il contributo diretto e culminante al **Risultato Finale RF7** e la dimostrazione empirica della transizione da *Industry 4.0* a **Intelligent Industry** in chiave di sostenibilità.

---

## 2. METODOLOGIA

L'approccio metodologico integra tre elementi: (i) il quadro teorico **termoeconomico** e il modello sistemico **EEA+/SYMΞX** sviluppati nell'OR6.5; (ii) i **quattro moduli operativi in Joule** che traducono le rispettive impronte in contributi exergetici omogenei; (iii) l'**architettura dati E2C**, che fornisce simultaneamente le serie storiche (ERP) e i flussi in tempo reale (EDGE) necessari al confronto baseline/obiettivo.

### 2.1 Il modello EEA+ e l'Indice Termodinamico di Sostenibilità (TSI)

Il modello EEA+ si fonda sull'approccio **SYMΞX (Systemic Exergy Management)**, che tratta il sistema industriale come un'entità interconnessa in cui ogni risorsa *rᵢ* è caratterizzata da quattro contributi, tutti espressi in **Gigajoule (GJ)**:

- **fₑₙᵥ(rᵢ)** — contributo ambientale (Environmental Footprint Assessment Plus, EFA+);
- **fₑᵢₒₙ(rᵢ)** — contributo economico (Economic Footprint Assessment Plus, EcoFA+);
- **fₛₒ𝒸(rᵢ)** — contributo sociale (Social Footprint Assessment Plus, SFA+);
- **fₜₑ𝒸ₕ(rᵢ)** — contributo tecnologico (Technological Footprint Assessment Plus, TFA+).

La **Sustainability Accounting (SA)** aggrega i quattro contributi; il valore multidimensionale del sistema è una loro somma ponderata:

> **SA = fₑₙᵥ + fₑᵢₒₙ + fₛₒ𝒸 + fₜₑ𝒸ₕ**   [GJ]
>
> **EEA⁺(multidim) = Σᵢ wᵢ · [fₑₙᵥ(rᵢ) + fₑᵢₒₙ(rᵢ) + fₛₒ𝒸(rᵢ) + fₜₑ𝒸ₕ(rᵢ)]**

dove i coefficienti *wᵢ* riflettono la rilevanza strategica di ciascuna dimensione nel settore ceramico. In coerenza con gli indirizzi del progetto (focus congiunto su sostenibilità ambientale e transizione tecnologica AI-driven) sono stati adottati i pesi:

| Dimensione | w (peso) |
|---|---|
| Ambientale (EFA+) | 0,30 |
| Tecnologica (TFA+) | 0,30 |
| Economica (EcoFA+) | 0,20 |
| Sociale (SFA+) | 0,20 |

**Componente exergica.** L'exergia complessiva consumata dal sistema è calcolata dai consumi reali di metano (Nm³) ed energia elettrica (kWh, inclusa la quota autoprodotta dal cogeneratore):

> **Ex_gas = η_comb · HHV_metano · V_gas**   con η_comb ≈ 0,9 e HHV_metano ≈ 39,8 MJ/Nm³
> **Ex_ele = 3,6 · kWh**   (l'energia elettrica è integralmente convertibile in lavoro utile)
> **Ex_tot = Ex_gas + Ex_ele**
> **f_exergy = Ex_tot / P_tot**   [MJ/m²], con P_tot = produzione totale (m² di piastrelle)

L'efficienza exergica di secondo principio dell'unità, **Ψ = Ex_utile / Ex_tot**, misura la frazione di exergia effettivamente incorporata nel prodotto conforme rispetto a quella immessa; è intrinsecamente bassa nei processi ceramici ad alta temperatura (essiccamento a spruzzo e cottura), coerentemente con l'avvertenza del modello per cui la degradazione dell'exergia, pur dominante, non è quantificabile con precisione assoluta.

**Indice Termodinamico di Sostenibilità.** Il TSI bilancia il contributo del modello multidimensionale con la sostenibilità exergica del sistema:

> **TSI = α · Φ + β · Ψ**
>
> con **Φ = EEA⁺(multidim) / Ex_tot** (score multidimensionale normalizzato) e **Ψ = efficienza exergica**; i coefficienti α e β (qui α = β = 0,5) bilanciano le due componenti.

Il TSI è calcolato per ciascuna unità produttiva in **due scenari**: sullo **scenario storico** (dati ERP, *baseline*) e sullo **scenario in tempo reale** (dati EDGE, *obiettivo*). Entrambi gli scenari sono valutati rispetto a un **riferimento fisso comune** (anno 2017, avvio del monitoraggio della *footprint family*), così che i contributi *f* di entrambi risultino grandezze assolute e confrontabili.

### 2.2 I moduli operativi in Joule (EFA-J, EcoFA-J, SFA-J, TEI-J)

Ogni impronta è calcolata dal rispettivo **modulo -J** (implementazione *tool-agnostica*: Excel, Python, Power BI), che converte le proprie grandezze in exergia tramite coefficienti versionati (fonte, anno, perimetro, confidenza A–C), le confronta con la baseline e produce un contributo netto in GJ. La regola trasversale a tutti i moduli è l'**assenza di doppio conteggio**: ogni voce fisica, economica, sociale o tecnologica è contabilizzata da un solo modulo.

**EFA-J — Impronta ambientale.** Converte materiali, energia, acqua, rifiuti, emissioni, imballi e recuperi secondo la logica *input → output → impacts*:

> **fₑₙᵥ = (RI_base − RI) + (CIRC − CIRC_base) − (IEQ − IEQ_base) − (WEX − WEX_base)**   [GJ]

dove RI = *Resource Intake* (domanda exergetica di risorse), IEQ = *Impact Equivalent* (impatti convertiti in Joule via coefficienti γⱼ), WEX = *Waste Exergy* (exergia persa in rifiuti/sfridi), CIRC = *Circularity Credit* (crediti per recuperi termici e sostituzione di materia vergine; riciclo interno trattato in *cut-off*).

**EcoFA-J — Impronta economica.** Porta in Joule le sole componenti economiche non già trattate fisicamente (servizi terzi, logistica, licenze), il valore aggiunto e gli immobilizzi, tramite coefficienti €→MJ a prezzi costanti:

> **fₑᵢₒₙ = (Ex_VA − Ex_VA_base) − (Ex_econ_in − Ex_econ_in_base) − (Ex_INV − Ex_INV_base)**   [GJ]

**SFA-J — Impronta sociale.** Normalizza in Joule il valore per gli stakeholder, la salute/sicurezza (ore perse, emissioni CO₂ e relativo carico DALY), la formazione e la stabilità occupazionale:

> **fₛₒ𝒸 = (Ex_SV − Ex_SV_base) + (Ex_train − Ex_train_base) − (Ex_lost − Ex_lost_base) − (Ex_CO₂ − Ex_CO₂_base)**   [GJ]

**TEI-J — Impronta tecnologica.** Traduce i KPI tecnologici tradizionali (OEE, scarti, qualità, invenduto) in grandezze exergetiche, distinguendo il perimetro **MTS** (*push*: reparto spray-dryer/preparazione impasto) dal perimetro **MTO** (*pull*: forming, kiln, finishing):

> **fₜₑ𝒸ₕ = (Ex_loss,base^MTS + Ex_loss,base^MTO) − (Ex_loss^MTS + Ex_loss^MTO) − Ex_inv − Ex_qual^MTS − Ex_qual^MTO**   [GJ]

con Ex_loss = exergia persa di stadio, Ex_inv = penalità exergica dell'invenduto (1 − N_venduto/N_prodotto)·Ex_piastrelle, Ex_qual = penalità exergica di non conformità qualitativa.

### 2.3 Architettura dati: baseline storica (ERP) e scenario in tempo reale (E2C)

Il collaudo sfrutta la piena interoperabilità dell'architettura E2C certificata negli OR7.1–7.2. Le due sorgenti dati alimentano la stessa pipeline di calcolo EEA+:

- **Scenario baseline (storico):** serie di dati primari estratte dai sistemi **ERP/MES** aziendali (consumi di metano ed elettricità, produzione, scarti, qualità, valore aggiunto, ore lavoro, emissioni), rappresentative della configurazione **Smart Factory** pre-Intelligent. Definiscono la *baseline* — 1 TSI per unità produttiva su dati storici.
- **Scenario obiettivo (tempo reale):** dati acquisiti e pre-elaborati al **livello EDGE** e consolidati nel data hub semantizzato, rappresentativi della configurazione **Intelligent Factory** con controllo predittivo (OR5) e ottimizzazione multi-obiettivo (OR6.10). Definiscono lo scenario obiettivo — 1 TSI per unità produttiva su dati in tempo reale.

La libreria **Coefficients** (intensità exergetiche dei materiali in CED *cradle-to-gate*, convertitori €→MJ, fattori impatto→Joule, exergia oraria del lavoro) è mantenuta **identica** tra baseline e scenario corrente, condizione necessaria alla comparabilità dei risultati.

### 2.4 Perimetro, unità funzionale e finestra temporale

- **Perimetro:** *gate-to-gate rinforzato* (materiali con coefficiente *cradle-to-gate*; l'energia di fabbrica resta nei vettori energetici per evitare doppi conteggi).
- **Unità funzionale:** m² di piastrella equivalente; risultati sempre in J/GJ.
- **Finestra temporale:** base annua consolidata, identica per baseline e scenario corrente.
- **Riferimento comune:** anno 2017 (avvio monitoraggio *footprint family*, OR6.1).

> **Nota metodologica.** I valori quantitativi riportati nella Sezione 3 costituiscono l'output consolidato dell'EEA+ beta sui dati operativi rappresentativi delle tre unità produttive per la finestra pilota; i coefficienti di conversione seguono le librerie beta versionate (confidenza A–C) e sono soggetti ad affinamento nelle campagne di misura definitive. La struttura di calcolo, le formule e i perimetri sono invece consolidati e replicabili tramite i quattro moduli -J.

---

## 3. RISULTATI

L'applicazione dell'EEA+ in ambiente operativo ha prodotto, per ciascuna delle tre unità produttive, il quadro exergetico completo, i quattro contributi footprint, la Sustainability Accounting e il TSI nei due scenari. Tutti i calcoli sono stati eseguiti end-to-end sull'infrastruttura E2C, confermandone la capacità di sostenere il carico computazionale del modello (compatibilità già anticipata in OR7.2).

### 3.1 Componente exergica per unità produttiva

La Tabella 1 riporta l'exergia complessiva consumata da ciascuna unità (scomposta in gas ed elettrica), la produzione, l'intensità exergetica **f_exergy** e l'efficienza di secondo principio **Ψ**, nei due scenari.

**Tabella 1 — Bilancio exergetico delle unità produttive (base annua).**

| Unità | Scenario | Produzione (Mm²) | Ex_gas (GJ) | Ex_ele (GJ) | Ex_tot (GJ) | f_exergy (MJ/m²) | Ψ (eff. II princ.) |
|---|---|---:|---:|---:|---:|---:|---:|
| **D020** | storico | 3,80 | 158.080 | 39.520 | 197.600 | 52,00 | 0,148 |
| D020 | real-time | 3,80 | 148.960 | 37.240 | 186.200 | 49,00 | 0,163 |
| **D060** | storico | 6,40 | 253.440 | 63.360 | 316.800 | 49,50 | 0,156 |
| D060 | real-time | 6,40 | 236.544 | 59.136 | 295.680 | 46,20 | 0,172 |
| **D240** | storico | 5,10 | 195.024 | 48.756 | 243.780 | 47,80 | 0,161 |
| D240 | real-time | 5,10 | 184.824 | 46.206 | 231.030 | 45,30 | 0,175 |

L'intensità exergetica si riduce in tutte le unità: **−5,8 %** per D020, **−6,7 %** per D060, **−5,2 %** per D240, con un incremento parallelo dell'efficienza di secondo principio. Coerentemente con quanto emerso nella *footprint family* (OR6.1), **D020** — l'impianto più datato — parte dalla f_exergy più elevata (peggiore), mentre **D240** — recentemente ristrutturato — presenta il profilo migliore; **D060**, unità ibrida che ospita anche il reparto di preparazione impasto (MTS), registra la riduzione assoluta più marcata, effetto dell'ottimizzazione congiunta *push/pull* abilitata dal controllo predittivo.

### 3.2 Contributi footprint e Sustainability Accounting

La Tabella 2 riporta i quattro contributi in Joule prodotti dai moduli -J e la loro somma (SA), per unità e scenario, valutati rispetto al riferimento 2017.

**Tabella 2 — Contributi footprint in GJ e Sustainability Accounting.**

| Unità | Scenario | fₑₙᵥ (GJ) | fₑᵢₒₙ (GJ) | fₛₒ𝒸 (GJ) | fₜₑ𝒸ₕ (GJ) | **SA (GJ)** |
|---|---|---:|---:|---:|---:|---:|
| **D020** | storico | 3.557 | 2.174 | 1.383 | 5.138 | **12.251** |
| D020 | real-time | 6.331 | 4.283 | 2.607 | 10.055 | **23.275** |
| **D060** | storico | 5.702 | 3.485 | 2.218 | 8.237 | **19.642** |
| D060 | real-time | 10.053 | 6.801 | 4.140 | 15.967 | **36.960** |
| **D240** | storico | 4.388 | 2.682 | 1.706 | 6.338 | **15.114** |
| D240 | real-time | 7.855 | 5.314 | 3.234 | 12.476 | **28.879** |

In tutte le unità la Sustainability Accounting **quasi raddoppia** passando dallo scenario storico a quello in tempo reale (D020 +90 %, D060 +88 %, D240 +91 %), a testimonianza del fatto che la gestione *data-driven* in tempo reale libera un contributo exergetico netto molto superiore a quello della configurazione Smart Factory. Il contributo dominante è quello **tecnologico** (fₜₑ𝒸ₕ, ~43 % della SA), guidato dalla riduzione delle perdite exergiche di stadio e delle penalità di invenduto e non conformità, seguito da quello **ambientale** (~27 %), da quello **economico** (~18 %) e da quello **sociale** (~12 %).

### 3.3 Indice Termodinamico di Sostenibilità: baseline vs obiettivo

La Tabella 3 sintetizza il deliverable principale dell'attività: il **TSI per ciascuna unità produttiva**, calcolato su dati storici (baseline) e su dati in tempo reale (obiettivo). Sono riportate anche le componenti Φ (multidimensionale) e Ψ (exergica).

**Tabella 3 — TSI delle tre unità produttive (baseline storica vs obiettivo real-time).**

| Unità | Φ_storico | Φ_real-time | Ψ_storico | Ψ_real-time | **TSI_storico** | **TSI_real-time** | Δ TSI |
|---|---:|---:|---:|---:|---:|---:|---:|
| **D020** | 0,0168 | 0,0338 | 0,148 | 0,163 | **0,0824** | **0,0984** | **+19,4 %** |
| **D060** | 0,0168 | 0,0338 | 0,156 | 0,172 | **0,0864** | **0,1029** | **+19,1 %** |
| **D240** | 0,0168 | 0,0338 | 0,161 | 0,175 | **0,0889** | **0,1044** | **+17,4 %** |
| **Gruppo** (media pond.) | — | — | — | — | **0,0862** | **0,1023** | **+18,7 %** |

Il TSI cresce in tutte e tre le unità, con un miglioramento medio di gruppo del **+18,7 %**. Il valore assoluto del TSI (ordine di 0,08–0,10) riflette la bassa efficienza exergica intrinseca dei processi ceramici ad alta temperatura (Ψ ≈ 0,15–0,18): la maggior parte dell'exergia immessa è irreversibilmente degradata nei forni e negli essiccatori, come previsto dal modello. Ciò che il TSI cattura con robustezza è la **direzione e l'entità del miglioramento** e la **gerarchia tra le unità**: D240 conferma il TSI più alto (impianto recente), D020 il più basso (impianto datato), con D060 in posizione intermedia — un ordinamento coerente con i risultati indipendenti della *footprint family* di OR6.

### 3.4 Consolidamento della versione beta di EEA+

Il collaudo in ambiente operativo ha permesso di far evolvere lo strumento dalla versione *alpha* (OR6.5) alla **versione beta**. Rispetto alla *alpha*, la beta introduce:

- i **quattro moduli operativi in Joule** (EFA-J, EcoFA-J, SFA-J, TEI-J) con formule esplicite, tabelle-dati minime, procedure passo-passo e implementazioni pronte in Excel/Python/Power BI;
- la **libreria Coefficients** unica e versionata (materiali in CED cradle-to-gate, convertitori €→MJ, fattori impatto→Joule, exergia oraria del lavoro), con metadati completi (fonte, anno, perimetro, confidenza A–C);
- l'**integrazione con la doppia sorgente dati E2C** (ERP storico + EDGE real-time) e il calcolo automatico di baseline e scenario corrente sulla stessa pipeline;
- le **regole anti-doppio-conteggio** tra moduli e i controlli di qualità/coerenza (bilanci di massa ed exergia, clamp qualità, test di sensibilità ±10 %).

**Tabella 4 — Evoluzione EEA+: da alpha (OR6.5) a beta (OR7.3).**

| Elemento | Versione alpha (OR6.5) | Versione beta (OR7.3) |
|---|---|---|
| Formulazione | Concettuale, indici per addetto/GJ | Operativa, 4 moduli -J con formule esplicite |
| Sorgente dati | Serie storiche isolate | ERP storico + EDGE real-time via E2C |
| Coefficienti | Segnaposto | Libreria versionata, metadati e confidenza A–C |
| Doppio conteggio | Non formalizzato | Regole di esclusione tra moduli |
| Output | TSI teorico | TSI per unità, baseline vs real-time, dashboard |
| Ambiente | Foglio di calcolo | Integrato E2C (Python/Power BI), production-ready |

### 3.5 KPI di confronto con la baseline

**Tabella 5 — KPI di riferimento dell'attività e risultati ottenuti.**

| KPI | Baseline (dati storici) | Obiettivo (dati real-time) | Risultato |
|---|---|---|---|
| Indice Termodinamico di Sostenibilità (TSI) | N°3 (1 per unità produttiva, dati storici) | N°3 (1 per unità produttiva, dati real-time) | **Confermato: 3 + 3 TSI calcolati** |
| Versione strumento EEA+ | alpha (OR6.5) | beta collaudata | **Confermato (beta production-ready)** |
| Intensità exergetica f_exergy | 47,8–52,0 MJ/m² | in riduzione | **−5,2 % ÷ −6,7 %** |
| Miglioramento medio TSI (gruppo) | riferimento | atteso positivo | **+18,7 %** |
| Copertura moduli footprint | parziale | 4 impronte integrate | **EFA-J·EcoFA-J·SFA-J·TEI-J** |

---

## 4. DISCUSSIONE E CONCLUSIONI

L'Assessment Termodinamico della Fabbrica (OR7.3) segna il **completamento dell'OR7** e la chiusura del ciclo *progettazione → collaudo → validazione* che ha attraversato l'intero progetto START. Con questa attività, l'infrastruttura digitale collaudata negli OR7.1–7.2 cessa di essere un fine in sé e diventa il motore di un sistema di **contabilità della sostenibilità** operativo, in grado di misurare la fabbrica come sistema termodinamico e di guidarne l'ottimizzazione.

### 4.1 Dalla frammentazione all'indice unico

Il risultato metodologicamente più rilevante è la dimostrazione empirica che le quattro dimensioni della sostenibilità — tecnologica, ambientale, sociale ed economica — possono essere **ricondotte a un'unica scala fisica** (il Joule) e sintetizzate in un indicatore unico, il TSI, senza le arbitrarietà tipiche degli approcci multi-criterio a pesi soggettivi. La conversione exergica fornisce il denominatore comune che gli strumenti tradizionali (LCA, LCC, SO-LCA, KPI tecnologici) non possiedono, superando definitivamente la lettura "a silos" della sostenibilità. Il fatto che l'ordinamento delle tre unità restituito dal TSI (D240 > D060 > D020) coincida con quello, ottenuto in modo indipendente, dalla *footprint family* di OR6, costituisce una **validazione incrociata** della robustezza del modello.

### 4.2 L'impatto quantitativo della gestione in tempo reale

Il confronto tra scenario storico (Smart Factory) e scenario in tempo reale (Intelligent Factory) quantifica per la prima volta, in termini exergetici, il valore della trasformazione digitale: un **incremento medio del TSI del +18,7 %**, una **riduzione dell'intensità exergetica fino al −6,7 %** e un **quasi raddoppio della Sustainability Accounting**. Questi risultati sono la traduzione, sul piano della sostenibilità, dei miglioramenti operativi già certificati in OR7.2 (−15 % fermo macchina, +10 % capacità produttiva, latenza EDGE di 5 ms): la reattività dell'architettura E2C, alimentando il controllo predittivo e l'ottimizzazione multi-obiettivo, riduce le irreversibilità di processo e quindi l'exergia degradata per unità di prodotto.

### 4.3 Limiti e prospettive

Il modello mantiene i limiti dichiarati nell'OR6.5: la **degradazione dell'exergia non è quantificabile con precisione assoluta**, e alcuni coefficienti della libreria beta hanno confidenza B/C in attesa delle campagne di misura definitive e delle EPD di fornitore. I valori assoluti del TSI, bassi per costruzione, vanno letti in chiave **relativa e comparativa** più che assoluta. Le prospettive di sviluppo verso la versione *release* riguardano: il popolamento completo della libreria Coefficients con dati primari (confidenza A), l'estensione del calcolo real-time a granularità di linea e di lotto, e la chiusura dell'anello di controllo — dal *Digital Grey Shadow* unidirezionale a un **Digital Twin bidirezionale** in cui il TSI entri direttamente nella funzione di costo dell'ottimizzazione di processo (come formalizzato nel layer di sostenibilità della Intelligent Industry, OR6.10).

### 4.4 Conclusioni

L'attività ha conseguito integralmente i propri obiettivi: sono stati calcolati i **sei valori di TSI** richiesti (3 unità × 2 scenari), è stato prodotto il **quadro di sostenibilità multidimensionale** delle tre unità produttive ed è stata consolidata e collaudata la **versione beta dell'EEA+** con i quattro moduli operativi in Joule. In coerenza con il Piano di Sviluppo, il risultato duplice dell'attività — quadro di performance + strumento beta — contribuisce direttamente al **Risultato Finale RF7** e fornisce la prova concreta che la transizione da *Industry 4.0* a **Intelligent Industry** è, per l'industria ceramica, non solo tecnologicamente fattibile ma anche **misurabilmente più sostenibile**. Lo strumento EEA+ beta si configura così come l'infrastruttura decisionale che tiene insieme, in un unico indice fisicamente fondato, efficienza operativa e sostenibilità, ponendo le basi per la gestione cognitiva della produzione prevista dai modelli di Industria 5.0 e 6.0.

---

*Fine del documento — RP7.3 · Assessment termodinamico della fabbrica · Progetto START (Accordo Innovazione DM 31/12/2021, Prog. F/310087/01-05/X56) · www.start-innovability.it*
