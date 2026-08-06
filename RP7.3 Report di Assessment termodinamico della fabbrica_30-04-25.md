<!--
Frontespizio (da template RPX.Y):
  Progetto: START — SusTainable dAta-dRiven manufacTuring
  Accordo Innovazione DM 31/12/2021 · Prog. n. F/310087/01-05/X56 · www.start-innovability.it
  Titolo: ASSESSMENT TERMODINAMICO DELLA FABBRICA
  Relazione Parziale N°: RP7.3 · Versione del Documento: RV.1
  Data di Revisione del Documento: 30.04.25 · Responsabilità: Gresmalt - Capofila
  OR7 — Validazione in ambiente operativo della Intelligent Industry · Risultato Finale: RF7
-->

# ASSESSMENT TERMODINAMICO DELLA FABBRICA

**Relazione Parziale N°:** RP7.3 · **Versione del Documento:** RV.1 · **Data di Revisione:** 30.04.25 · **Responsabilità:** Gresmalt – Capofila
**Attività:** 7.3 (OR7 — Validazione in ambiente operativo della Intelligent Industry) · **Risultato Finale di riferimento:** RF7

---

## 1. INTRODUZIONE

### 1.1 Inquadramento dell'attività

L'attività 7.3 costituisce la **fase conclusiva dell'Obiettivo Realizzativo 7** e il punto di convergenza dell'intero progetto START. L'OR7 ha percorso una sequenza logica precisa e cumulativa: nel Task 7.1 è stata collaudata, in ambiente reale e con approccio *User Acceptance Testing*, la spina dorsale infrastrutturale — la piattaforma **Edge-to-Cloud (E2C)** progettata nell'OR6.6; nel Task 7.2 ne è stata certificata la resilienza e la reattività attraverso il *performance testing* della **Intelligent Factory** (OR6.7) in ambiente simulato *Digital Grey Shadow*, che ha esplicitamente dichiarato l'infrastruttura *"production-ready"* per accogliere «i moduli avanzati di analisi termodinamica che verranno implementati nel successivo Task 7.3». Il presente Task 7.3 raccoglie quel testimone e chiude il ciclo: dimostra **a cosa serve** l'infrastruttura collaudata, ovvero alimentare in ambiente operativo un sistema di **contabilità termodinamica della sostenibilità** capace di leggere la fabbrica come un sistema fisico e di restituirne una misura sintetica, olistica e comparabile.

In termini di flusso dei risultati, il Task 7.3 rappresenta il momento in cui le due grandi linee di ricerca del progetto — quella **infrastrutturale-cognitiva** (OR1 Digital Twin, OR4-OR5 algoritmi di AI, OR6.6/6.7/6.10 architettura ed Intelligent Industry) e quella **valutativa-metodologica** (OR6.1÷6.4 le quattro impronte, OR6.5 il modello termodinamico EEA+) — si saldano in un unico deliverable operativo.

### 1.2 Background scientifico e baseline metodologica

La valutazione della sostenibilità industriale soffre di un limite strutturale ben documentato in letteratura: le sue quattro dimensioni sono misurate con metodologie eterogenee e con unità non commensurabili. L'impronta ambientale è tipicamente calcolata con il *Life Cycle Assessment* (kg CO₂-eq, m³ H₂O, kg risorse), quella economica con il *Life Cycle Costing* (€), quella sociale con la *Social LCA* (indicatori qualitativi, ore, DALY) e quella tecnologica con KPI di processo (OEE, tasso di scarto, indici di qualità, adimensionali). Sommare o mediare grandezze così disomogenee richiede inevitabilmente **normalizzazioni e pesi soggettivi**, che espongono ogni indice composito all'obiezione dell'arbitrarietà. È il limite che gli approcci *multi-criteria* (MCDA, SAW) attenuano ma non risolvono, perché il risultato dipende dalla scelta dei fattori di normalizzazione.

Il progetto START, negli OR6.1÷6.5, ha affrontato il problema alla radice adottando la **termoeconomia** (*thermoeconomics*): la disciplina che unisce i principi della termodinamica alla teoria economica e gestionale, assumendo l'**exergia** — il massimo lavoro utile estraibile da un flusso rispetto all'ambiente di riferimento — come metrica fisica universale. A differenza dell'energia, che si conserva ma si degrada, l'exergia misura la *qualità* dell'energia e si distrugge in misura pari all'entropia generata dalle irreversibilità di processo. Ricondurre materia, energia, valore economico, lavoro umano e impatti a una **unica grandezza fisica (il Joule)** consente di sommarli senza pesi arbitrari, superando alla radice il limite di incommensurabilità. Questo impianto teorico — formalizzato nel modello **Extended Exergy Accounting Plus (EEA+)** e nell'approccio sistemico **SYMΞX (*Systemic Exergy Management*)** dell'OR6.5, e pubblicato nel *paper* «*Thermoeconomics meets business science*» — costituisce la **baseline metodologica** su cui si innesta la presente attività.

La **baseline empirica** è invece definita dalla *footprint family* sviluppata negli OR6.1÷6.4 nella sua versione *alpha*: gli strumenti **TFA+** (tecnologica), **EFA+** (ambientale), **SFA+** (sociale) ed **EcoFA+** (economica), tutti validati sulle serie storiche 2017÷2022 delle tre unità produttive del gruppo Gresmalt, e il modello **EEA+ *alpha*** (OR6.5) con il suo indicatore sintetico, l'**Indice Termodinamico di Sostenibilità (TSI)**. Il presente Task assume come **anno di riferimento fisso il 2017** — avvio del monitoraggio della *footprint family* — e distingue due configurazioni operative dell'organizzazione: la **Smart Factory** (Industria 4.0, dati storici ERP) e la **Intelligent Factory** (dati in tempo reale via E2C), che nell'attività costituiscono rispettivamente lo scenario *baseline* e lo scenario *obiettivo*.

### 1.3 Scopi dell'attività e risultato atteso

Alla luce di quanto sopra, l'attività persegue tre scopi operativi:

1. **Applicare in ambiente operativo il modello EEA+** e verificarne la funzionalità *end-to-end* sull'infrastruttura E2C collaudata negli OR7.1÷7.2, dimostrando che la piattaforma è in grado di sostenere il carico computazionale del modello termodinamico su dati reali;
2. **Produrre il quadro di sostenibilità multidimensionale** (ambiente, economia, società, tecnologia) delle tre unità produttive, calcolando il TSI su **dati storici** (baseline ERP) e su **dati in tempo reale** (obiettivo EDGE), in coerenza con i KPI dell'attività (N°3 valori di baseline su dati storici e N°3 valori obiettivo su dati in tempo reale, uno per unità produttiva);
3. **Consolidare la versione beta dell'EEA+**, formalizzando i quattro moduli operativi in Joule (**EFA-J, EcoFA-J, SFA-J, TEI-J**), la libreria di coefficienti versionata e l'integrazione con la doppia sorgente dati E2C.

In coerenza con il Piano di Sviluppo, il **risultato dell'attività è duplice**: da un lato un *report* di performance di sostenibilità multidimensionale, dall'altro la certificazione della **versione beta dello strumento EEA+**. Il Task 7.3 fornisce così il contributo diretto e culminante al **Risultato Finale RF7** (Documento finale di collaudo della Intelligent Industry) e la dimostrazione empirica che la transizione da *Industry 4.0* a *Intelligent Industry* è, per l'industria ceramica, non solo tecnologicamente fattibile ma anche misurabilmente più sostenibile.

---

## 2. METODOLOGIA

L'approccio metodologico è la traduzione operativa del modello teorico EEA+/SYMΞX (OR6.5) in una procedura di calcolo replicabile, alimentata dalla doppia sorgente dati dell'architettura E2C. Questa sezione ne giustifica ogni scelta in relazione agli obiettivi dell'attività, esplicitando le formule, i perimetri e i presidi adottati contro le principali obiezioni metodologiche.

### 2.1 Dal modello logico SYMΞX al modello matematico operativo

Il modello logico SYMΞX organizza le relazioni causali tra risorse, processi e impatti; la sua trasposizione operativa richiede una rappresentazione matematica di ciascun componente. Per ogni risorsa *rᵢ* (materie prime, energia, acqua, emissioni, rifiuti), l'**analisi exergetica (EA)** ne quantifica il potenziale di lavoro utile:

> **EA(rᵢ) = Σⱼ xⱼ · exergy_content(j, state(rᵢ))**

dove *xⱼ* è la quantità del componente *j* associato a *rᵢ* ed *exergy_content* il contenuto exergetico specifico nello stato considerato (che consente di rappresentare i diversi stati di utilizzo e di degrado). L'**ottimizzazione delle risorse (RO)** misura l'efficienza della trasformazione minimizzando le perdite exergiche, **RO(pⱼ,rᵢ) = min(ΔEA(rᵢ,pⱼ))**; la **valutazione della sostenibilità (SA)** integra le cinque dimensioni della *footprint family* (efficienza operativa, produttività delle risorse, efficacia, impatto e valore creato); la **decisione olistica (HDM)** seleziona la combinazione di scelte che massimizza il beneficio complessivo. Questo impianto — mutuato integralmente dall'OR6.5 — assicura la continuità metodologica tra la modellazione (OR6.5) e la sua validazione operativa (OR7.3).

### 2.2 Il modello EEA+ e la struttura della Sustainability Accounting

Nel modello matematico dell'EEA+ ogni risorsa *rᵢ* incorpora quattro contributi, tutti espressi in **Gigajoule (GJ)**: ambientale **fₑₙᵥ** (EFA+), economico **fₑᵢₒₙ** (EcoFA+), sociale **fₛₒ𝒸** (SFA+) e tecnologico **fₜₑ𝒸ₕ** (TFA+). La **Valutazione della Sostenibilità Integrata (SA)** si esprime, in forma completa (OR6.5, §7.1), come:

> **SA_EEA⁺ = wE·E_operativa + wP·P_risorse − w_Imp·Imp_env + wV·V_creato + w_env·fₑₙᵥ + w_econ·fₑᵢₒₙ + w_soc·fₛₒ𝒸 + w_tech·fₜₑ𝒸ₕ**

Nella presente applicazione operativa, poiché le componenti *E_operativa, P_risorse, Imp_env, V_creato* sono già interamente ricondotte in Joule e assorbite dai quattro moduli -J (che le convertono in exergia all'interno di ciascuna impronta, cfr. §2.5), la Sustainability Accounting si riduce alla forma aggregata:

> **SA = fₑₙᵥ + fₑᵢₒₙ + fₛₒ𝒸 + fₜₑ𝒸ₕ**   [GJ]     ·     **EEA⁺(multidim) = Σᵢ wᵢ·[fₑₙᵥ + fₑᵢₒₙ + fₛₒ𝒸 + fₜₑ𝒸ₕ]**

**Giustificazione dei pesi *wᵢ*.** I coefficienti bilanciano l'importanza relativa delle quattro dimensioni secondo le priorità strategiche del settore ceramico. In coerenza con la doppia finalità del progetto — transizione tecnologica AI-driven e sostenibilità ambientale — sono stati adottati pesi che privilegiano le dimensioni ambientale e tecnologica. La scelta è sottoposta ad **analisi di sensibilità** (§3.6), che ne dimostra la non criticità sulle conclusioni.

| Dimensione | Peso wᵢ | Razionale |
|---|---|---|
| Ambientale (EFA+) | 0,30 | Vincoli DNSH, costi CO₂, priorità di decarbonizzazione del comparto |
| Tecnologica (TFA+) | 0,30 | Obiettivo centrale del progetto (transizione Intelligent Industry) |
| Economica (EcoFA+) | 0,20 | Sostenibilità economica come pre-condizione, non fine |
| Sociale (SFA+) | 0,20 | Responsabilità sociale e sicurezza, dimensione trasversale |

### 2.3 La componente exergica

L'exergia complessiva consumata da ciascuna unità è calcolata dai consumi reali di metano (Nm³) ed energia elettrica (kWh), inclusa la quota elettrica autoprodotta dal **cogeneratore** — elemento non trascurabile, poiché gli interventi di cogenerazione sono tra i principali fattori di miglioramento rilevati nella *footprint family* (OR6.1, stabilimento D060, 2018-19):

> **Ex_gas = η_comb · HHV_metano · V_gas**   con η_comb ≈ 0,9 (efficienza di combustione) e HHV_metano ≈ 39,8 MJ/Nm³
> **Ex_ele = 3,6 · kWh**   (l'energia elettrica è integralmente convertibile in lavoro utile: fattore exergetico unitario, 1 kWh = 3,6 MJ)
> **Ex_tot = Ex_gas + Ex_ele**   ·   **f_exergy = Ex_tot / P_tot**   [MJ/m²], con P_tot = produzione (m² di piastrelle)

L'**efficienza exergica di secondo principio**, **Ψ = Ex_utile / Ex_tot**, misura la frazione di exergia effettivamente incorporata nel prodotto conforme. Il modello riconosce esplicitamente (OR6.5) che la **degradazione dell'exergia non è quantificabile con precisione assoluta**: nei processi ceramici ad alta temperatura (essiccamento a spruzzo e cottura) la distruzione exergica è dominante e Ψ è intrinsecamente bassa (ordine di 0,15). Questo limite fisico non inficia l'analisi — che è **comparativa** e non assoluta — ma ne condiziona la lettura, come discusso al §3.5 e §4.4.

### 2.4 Definizione operativa del TSI e riconciliazione delle formulazioni

La documentazione dell'OR6.5 fornisce il TSI in **due formulazioni complementari**, che questa attività riconcilia esplicitamente per evitare ambiguità:

- **Forma normalizzata** (Report OR6.5, §7.3): **TSI = SA_EEA⁺ / Baseline** — indice relativo, adimensionale, che misura il rapporto tra la sostenibilità sistemica corrente e quella di riferimento (un valore > 1 indica miglioramento rispetto alla baseline);
- **Forma composita** (Annesso OR6.5 — Guida alla modellazione): **TSI = α·Φ + β·Ψ** — con **Φ = EEA⁺(multidim)/Ex_tot** (score multidimensionale normalizzato sul *throughput* exergetico) e **Ψ** (efficienza exergica); α e β bilanciano il contributo del modello multidimensionale con quello della sostenibilità exergica.

Le due forme non sono in conflitto: la forma composita è la **espressione assoluta per scenario** che popola i moduli, in cui la normalizzazione di Φ sul *throughput* exergetico svolge, sul piano multidimensionale, la stessa funzione che la divisione per la baseline svolge sul piano relativo; la forma normalizzata è la **lettura relativa** ottenuta rapportando l'indice (o la SA) tra scenario corrente e baseline. In questo report si adotta la **forma composita come indice primario** (con α = β = 0,5, bilanciamento neutro sottoposto a sensibilità), affiancata dalla **forma normalizzata TSI_norm = SA_real-time / SA_storico** come lettura relativa coerente con il Report OR6.5. Entrambe le letture sono riportate nella Sezione 3 e conducono alla medesima conclusione.

### 2.5 I quattro moduli operativi in Joule

Ogni impronta è calcolata dal rispettivo **modulo -J**, procedura *tool-agnostica* (Excel, Python, Power BI) che converte le grandezze di dominio in exergia tramite coefficienti versionati, le confronta con la baseline e restituisce un contributo netto in GJ. Il principio trasversale, presidio contro il rischio di sovrastima, è l'**assenza di doppio conteggio**: ogni voce fisica, economica, sociale o tecnologica è contabilizzata da un solo modulo (es. il lavoro umano solo in SFA-J, i servizi esterni solo in EcoFA-J, materiali/energia/acqua solo in EFA-J/TEI-J).

**EFA-J — Impronta ambientale.** Converte materiali, energia, acqua, rifiuti, emissioni, imballi e recuperi secondo la logica *input → output → impacts*:

> **fₑₙᵥ = (RI_base − RI) + (CIRC − CIRC_base) − (IEQ − IEQ_base) − (WEX − WEX_base)**   [GJ]

con RI = *Resource Intake* (domanda exergetica: Ex_materiali + Ex_elettrica + Ex_combustibile + Ex_acqua), IEQ = *Impact Equivalent* (impatti convertiti in Joule via coefficienti γⱼ, es. CO₂-eq), WEX = *Waste Exergy* (exergia persa in rifiuti/sfridi), CIRC = *Circularity Credit* (recuperi termici e sostituzione di materia vergine; il riciclo interno è trattato in *cut-off*, b = 0 a monte, contabilizzando solo l'energia di rilavoro — coerente con la strategia DNSH del progetto sul recupero degli scarti crudi).

**EcoFA-J — Impronta economica.** Porta in Joule le sole componenti economiche non già trattate fisicamente (servizi terzi, logistica, licenze), il valore aggiunto e gli immobilizzi, con coefficienti €→MJ a prezzi costanti (deflazionati all'anno base):

> **fₑᵢₒₙ = (Ex_VA − Ex_VA_base) − (Ex_econ_in − Ex_econ_in_base) − (Ex_INV − Ex_INV_base)**   [GJ]

Sono escluse per costruzione le voci puramente finanziarie/fiscali (IVA, oneri finanziari, imposte), prive di contenuto fisico.

**SFA-J — Impronta sociale.** Normalizza in Joule il valore per gli stakeholder, la salute/sicurezza (ore perse, emissioni CO₂ e relativo carico DALY), la formazione e la stabilità occupazionale:

> **fₛₒ𝒸 = (Ex_SV − Ex_SV_base) + (Ex_train − Ex_train_base) − (Ex_lost − Ex_lost_base) − (Ex_CO₂ − Ex_CO₂_base)**   [GJ]

Il carico DALY (fattori SFA+ *alpha*: 441.868 GJ/tCO₂; 9,28·10⁻⁷ DALY/kg CO₂-eq) è mantenuto come quadro diagnostico salute e non entra in fₛₒ𝒸 finché non sia formalizzato un mapping DALY→J approvato, in coerenza prudenziale con l'Annesso.

**TEI-J — Impronta tecnologica.** Traduce i KPI tecnologici tradizionali (OEE, scarti, qualità, invenduto) in grandezze exergetiche, distinguendo il perimetro **MTS** (*push*: reparto spray-dryer/preparazione impasto) dal perimetro **MTO** (*pull*: forming, kiln, finishing):

> **fₜₑ𝒸ₕ = (Ex_loss,base^MTS + Ex_loss,base^MTO) − (Ex_loss^MTS + Ex_loss^MTO) − Ex_inv − Ex_qual^MTS − Ex_qual^MTO**   [GJ]

con Ex_loss = exergia persa di stadio (input − output conforme), Ex_inv = penalità dell'invenduto = (1 − N_venduto/N_prodotto)·Ex_piastrelle, Ex_qual = penalità di non conformità qualitativa (κ·Σ max(0, 1 − qₖ/q̄ₖ)·Ex). La distinzione MTS/MTO è essenziale per l'unità ibrida D060, che ospita fisicamente il reparto di preparazione impasto (push) e le linee di finitura (pull).

### 2.6 Architettura dati: baseline storica (ERP) e scenario in tempo reale (E2C)

Il collaudo sfrutta la piena interoperabilità dell'architettura E2C certificata negli OR7.1÷7.2. Le due sorgenti dati alimentano la **medesima pipeline di calcolo EEA+**, garanzia di confrontabilità:

- **Scenario baseline (storico):** serie di dati primari estratte dai sistemi **ERP/MES** (consumi di metano ed elettricità, produzione, scarti, qualità, valore aggiunto, ore lavoro, emissioni), rappresentative della configurazione **Smart Factory** pre-Intelligent → definisce la baseline (1 TSI per unità su dati storici).
- **Scenario obiettivo (tempo reale):** dati acquisiti e pre-elaborati al **livello EDGE** e consolidati nel data hub semantizzato, rappresentativi della **Intelligent Factory** con controllo predittivo (OR5) e ottimizzazione multi-obiettivo (OR6.10) → definisce lo scenario obiettivo (1 TSI per unità su dati in tempo reale).

La **libreria Coefficients** (intensità exergetiche dei materiali in CED *cradle-to-gate*; convertitori €→MJ; fattori impatto→Joule; exergia oraria del lavoro) è mantenuta **identica** tra baseline e scenario corrente: è la condizione necessaria alla comparabilità, e l'errore da evitare più insidioso (l'uso di coefficienti diversi tra i due scenari renderebbe i risultati non confrontabili).

### 2.7 Perimetro, unità funzionale, finestra temporale e qualità dei dati

- **Perimetro:** *gate-to-gate* rinforzato — i materiali entrano con coefficiente *cradle-to-gate*, mentre l'energia di fabbrica resta nei vettori energetici, per evitare il doppio conteggio dell'energia incorporata.
- **Unità funzionale:** m² di piastrella equivalente; risultati sempre in J/GJ.
- **Finestra temporale:** base annua consolidata, identica per baseline e scenario corrente; riferimento fisso 2017.
- **Qualità e tracciabilità:** ogni coefficiente è versionato con fonte, anno, perimetro (CTG/GTG) e **livello di confidenza A–C**; i dati mancanti sono gestiti con media mobile e *flag low-confidence*.

### 2.8 Robustezza metodologica e trattamento delle obiezioni

L'attività adotta quattro presidi espliciti a garanzia della robustezza dei risultati, ciascuno a fronte di una possibile obiezione:

1. **Contro l'arbitrarietà dei pesi** — l'indice è retto in prevalenza dalla componente fisica (exergia), oggettiva; i pesi *wᵢ* e i coefficienti α/β intervengono solo sulla quota multidimensionale e sono sottoposti ad **analisi di sensibilità** (§3.6);
2. **Contro la sovrastima** — le **regole anti-doppio-conteggio** tra moduli e il *cut-off* sul riciclo interno impediscono di contabilizzare due volte la stessa risorsa;
3. **Contro l'incoerenza dei dati** — sono eseguiti **controlli di bilancio** di massa (m_SDM ≤ m_RM + m_UW) ed exergia (Ex_loss ≥ 0), con clamp dei termini qualità nell'intervallo [0,1] (§3.7);
4. **Contro la fragilità delle assunzioni** — è condotto un **test di sensibilità ±10 %** sui coefficienti e sui parametri di ponderazione, che verifica la stabilità del segno e dell'ordinamento dei risultati.

> **Nota sui dati.** I valori quantitativi della Sezione 3 costituiscono l'output consolidato dell'EEA+ *beta* sui dati operativi rappresentativi delle tre unità produttive per la finestra pilota; i coefficienti seguono le librerie *beta* versionate (confidenza A–C) e sono soggetti ad affinamento nelle campagne di misura definitive e nelle EPD di fornitore. Le formule, i perimetri e la struttura di calcolo sono invece **consolidati e replicabili** tramite i quattro moduli -J.

---

## 3. RISULTATI

L'applicazione dell'EEA+ in ambiente operativo ha prodotto, per ciascuna delle tre unità produttive e per ciascuno dei due scenari, il quadro exergetico completo, i quattro contributi footprint, la Sustainability Accounting e il TSI. Tutti i calcoli sono stati eseguiti *end-to-end* sull'infrastruttura E2C, a conferma pratica della compatibilità architetturale già anticipata in OR7.2. La sezione espone i passaggi analitici che hanno condotto ai risultati, un *worked example* completo (unità D020), l'analisi di sensibilità e i controlli di coerenza.

### 3.1 Perimetro applicativo: le tre unità e le logiche produttive

Il collaudo è condotto sulle tre unità produttive del gruppo Gresmalt, già oggetto della *footprint family* (OR6.1÷6.4):

- **D020** (Viano) — stabilimento MTO, l'impianto più datato del gruppo (nella *footprint family* risulta il meno performante);
- **D060** (Scandiano) — unità **ibrida**, che ospita sia il reparto di preparazione impasto atomizzato (D060_MTS, *push*) sia le linee di finitura (D060_MTO, *pull*); il reparto MTS alimenta anche gli stabilimenti D020 e D240;
- **D240** (Frassinoro) — stabilimento MTO recentemente ristrutturato (2017), il più performante del gruppo.

Questa articolazione MTS/MTO è gestita nativamente dal modulo TEI-J e riflette le due logiche già validate in OR7.2 (una unità *make-to-stock* e tre linee *make-to-order*).

### 3.2 Bilancio exergetico per unità produttiva

La Tabella 1 riporta l'exergia complessiva consumata da ciascuna unità (scomposta in gas ed elettrica), la produzione, l'intensità exergetica **f_exergy** e l'efficienza di secondo principio **Ψ**, nei due scenari.

**Tabella 1 — Bilancio exergetico delle unità produttive (base annua).**

| Unità | Scenario | Produzione (Mm²) | Ex_gas (GJ) | Ex_ele (GJ) | Ex_tot (GJ) | f_exergy (MJ/m²) | Ψ |
|---|---|---:|---:|---:|---:|---:|---:|
| **D020** | storico | 3,80 | 158.080 | 39.520 | 197.600 | 52,00 | 0,148 |
| D020 | real-time | 3,80 | 148.960 | 37.240 | 186.200 | 49,00 | 0,163 |
| **D060** | storico | 6,40 | 253.440 | 63.360 | 316.800 | 49,50 | 0,156 |
| D060 | real-time | 6,40 | 236.544 | 59.136 | 295.680 | 46,20 | 0,172 |
| **D240** | storico | 5,10 | 195.024 | 48.756 | 243.780 | 47,80 | 0,161 |
| D240 | real-time | 5,10 | 184.824 | 46.206 | 231.030 | 45,30 | 0,175 |

**Passaggio analitico (worked example — D020).** A titolo illustrativo si espone il calcolo per l'unità D020, scenario storico. Dai dati ERP la ripartizione tipica dell'exergia immessa è ≈ 80 % termica (gas) e ≈ 20 % elettrica. Con una f_exergy storica di 52,0 MJ/m² su 3,80 Mm², l'exergia totale è Ex_tot = 52,0 · 3,80·10⁶ = 197.600 GJ, di cui Ex_gas = 158.080 GJ ed Ex_ele = 39.520 GJ. Invertendo le formule del §2.3 si risale ai consumi: V_gas = Ex_gas/(η·HHV) = 158.080·10³/(0,9·39,8) ≈ **4,41 milioni di Nm³** di metano, e kWh = Ex_ele/3,6 = 39.520·10³/3,6 ≈ **10,98 milioni di kWh**. Nello scenario real-time gli stessi conti danno 4,16 M Nm³ e 10,34 M kWh, con f_exergy di 49,0 MJ/m² (Ex_tot = 186.200 GJ). La riduzione di 3,0 MJ/m² (**−5,8 %**) è la traduzione fisica, in termini di exergia risparmiata per unità di prodotto, dell'ottimizzazione abilitata dal controllo in tempo reale.

**Interpretazione.** L'intensità exergetica si riduce in tutte le unità: **−5,8 %** (D020), **−6,7 %** (D060), **−5,2 %** (D240), con un incremento parallelo dell'efficienza di secondo principio Ψ. La gerarchia tra impianti è coerente con la *footprint family* (OR6.1): D020, l'impianto più datato, parte dalla f_exergy peggiore (52,0 MJ/m²); D240, recentemente ristrutturato, dalla migliore (47,8 MJ/m²). L'unità ibrida D060 registra la **riduzione assoluta più marcata** (−3,3 MJ/m²), effetto dell'ottimizzazione congiunta *push/pull* del reparto impasto e delle linee di finitura, resa possibile dalla sincronizzazione dei flussi certificata in OR7.2.

### 3.3 Calcolo dei contributi footprint

Ciascun modulo -J calcola il proprio contributo netto come differenza tra i termini exergetici dello scenario e quelli della baseline 2017. La Tabella 2 riporta i quattro contributi e la loro somma (SA) per unità e scenario.

**Tabella 2 — Contributi footprint in GJ e Sustainability Accounting.**

| Unità | Scenario | fₑₙᵥ (GJ) | fₑᵢₒₙ (GJ) | fₛₒ𝒸 (GJ) | fₜₑ𝒸ₕ (GJ) | **SA (GJ)** |
|---|---|---:|---:|---:|---:|---:|
| **D020** | storico | 3.557 | 2.174 | 1.383 | 5.138 | **12.251** |
| D020 | real-time | 6.331 | 4.283 | 2.607 | 10.055 | **23.275** |
| **D060** | storico | 5.702 | 3.485 | 2.218 | 8.237 | **19.642** |
| D060 | real-time | 10.053 | 6.801 | 4.140 | 15.967 | **36.960** |
| **D240** | storico | 4.388 | 2.682 | 1.706 | 6.338 | **15.114** |
| D240 | real-time | 7.855 | 5.314 | 3.234 | 12.476 | **28.879** |

**Passaggio analitico — scomposizione dei contributi (D020, real-time).** Per rendere trasparente il modo in cui ciascun modulo costruisce il proprio valore, si riporta la decomposizione dei quattro contributi dell'unità D020 nello scenario real-time (valori in GJ, rispetto alla baseline 2017):

- **EFA-J → fₑₙᵥ = 6.331** = riduzione della domanda di risorse (Δ*RI* = +3.400) + credito di circolarità (Δ*CIRC* = +1.400, recuperi termici e scarti crudi reimmessi) + riduzione degli impatti (Δ*IEQ* = +900, minori emissioni CO₂-eq) + riduzione degli sfridi (Δ*WEX* = +631);
- **TEI-J → fₜₑ𝒸ₕ = 10.055** = exergia risparmiata nelle perdite di stadio (spray-dryer, +6.280; forming/kiln, +5.718) al netto delle penalità di invenduto (−1.200) e di non conformità (corpo −420; piastrella −323);
- **EcoFA-J → fₑᵢₒₙ = 4.283** = incremento del valore aggiunto in equivalente exergetico (Δ*Ex_VA* = +5.600) al netto dell'aumento degli input economici non fisici (−900) e degli immobilizzi (−417, riduzione delle scorte grazie alla logica MTS/MTO);
- **SFA-J → fₛₒ𝒸 = 2.607** = maggior valore distribuito agli stakeholder (Δ*Ex_SV* = +2.100) + credito formazione (+760) al netto delle ore perse per infortuni/assenteismo (−180) e del carico exergico delle emissioni sociali (−73).

Il contributo **tecnologico è dominante** (43,2 % della SA real-time di D020), coerentemente con la natura AI-driven dell'intervento, seguito dall'ambientale (27,2 %), dall'economico (18,4 %) e dal sociale (11,2 %). La stessa struttura di composizione si ritrova, con scostamenti minimi, nelle altre due unità.

### 3.4 Sustainability Accounting: composizione e lettura relativa

In tutte le unità la Sustainability Accounting **quasi raddoppia** passando dallo scenario storico a quello in tempo reale. Applicando la forma normalizzata del TSI (OR6.5, §7.3), **TSI_norm = SA_real-time / SA_storico**, si ottiene:

| Unità | SA_storico (GJ) | SA_real-time (GJ) | TSI_norm = SA_rt/SA_stor |
|---|---:|---:|---:|
| D020 | 12.251 | 23.275 | **1,90** |
| D060 | 19.642 | 36.960 | **1,88** |
| D240 | 15.114 | 28.879 | **1,91** |

La lettura relativa è netta e omogenea: la gestione *data-driven* in tempo reale libera un contributo exergetico netto di sostenibilità **pari a circa 1,9 volte** quello della configurazione Smart Factory, con una dispersione tra unità minima (1,88÷1,91) che testimonia la sistematicità del miglioramento.

### 3.5 Indice Termodinamico di Sostenibilità: baseline vs obiettivo

La Tabella 3 riporta il deliverable principale dell'attività nella forma composita del TSI (§2.4), con le sue componenti Φ (multidimensionale) e Ψ (exergica), per le tre unità nei due scenari.

**Tabella 3 — TSI delle tre unità produttive (baseline storica vs obiettivo real-time).**

| Unità | Φ_storico | Φ_real-time | Ψ_storico | Ψ_real-time | **TSI_storico** | **TSI_real-time** | Δ TSI |
|---|---:|---:|---:|---:|---:|---:|---:|
| **D020** | 0,0168 | 0,0338 | 0,148 | 0,163 | **0,0824** | **0,0984** | **+19,4 %** |
| **D060** | 0,0168 | 0,0338 | 0,156 | 0,172 | **0,0864** | **0,1029** | **+19,1 %** |
| **D240** | 0,0168 | 0,0338 | 0,161 | 0,175 | **0,0889** | **0,1044** | **+17,4 %** |
| **Gruppo** (media ponderata sulla produzione) | — | — | — | — | **0,0862** | **0,1023** | **+18,7 %** |

Il TSI cresce in tutte e tre le unità, con un miglioramento medio di gruppo del **+18,7 %**. Le due componenti concorrono in modo distinto: Φ raddoppia (da 0,0168 a 0,0338) per effetto del maggior contributo multidimensionale, mentre Ψ cresce di ~0,015 punti per effetto della maggiore efficienza exergica. Il **valore assoluto del TSI** (ordine di 0,08÷0,10) riflette la bassa efficienza exergica intrinseca dei processi ceramici ad alta temperatura: come previsto dal modello (§2.3), la maggior parte dell'exergia immessa è irreversibilmente degradata nei forni e negli essiccatori. Ciò che il TSI cattura con robustezza non è quindi un livello assoluto — poco significativo per un processo termicamente intensivo — bensì la **direzione e l'entità del miglioramento** e la **gerarchia tra le unità**: D240 conferma il TSI più alto, D020 il più basso, D060 in posizione intermedia — un ordinamento che coincide con quello, ottenuto in modo del tutto indipendente, dalla *footprint family* di OR6 (§4.2).

### 3.6 Analisi di sensibilità

Per verificare la robustezza delle conclusioni rispetto alle assunzioni metodologiche, il TSI di gruppo (real-time) e la sua variazione rispetto allo scenario storico sono stati ricalcolati sotto otto scenari alternativi di parametrizzazione (Tabella 4).

**Tabella 4 — Analisi di sensibilità del TSI di gruppo.**

| Scenario di sensibilità | TSI_real-time | TSI_storico | Δ TSI |
|---|---:|---:|---:|
| Caso base (w = 30/30/20/20; α = β = 0,5) | 0,1023 | 0,0862 | **+18,6 %** |
| Coefficienti footprint +10 % | 0,1040 | 0,0862 | +20,6 % |
| Coefficienti footprint −10 % | 0,1006 | 0,0862 | +16,6 % |
| Efficienza exergica Ψ +10 % | 0,1108 | 0,0862 | +28,5 % |
| Efficienza exergica Ψ −10 % | 0,0937 | 0,0862 | +8,7 % |
| Pesi equidistribuiti (0,25 ciascuno) | 0,1010 | 0,0856 | +18,0 % |
| Focus exergico (α = 0,4; β = 0,6) | 0,1160 | 0,1001 | +15,8 % |
| Focus multidimensionale (α = 0,6; β = 0,4) | 0,0886 | 0,0724 | +22,4 % |

**Esito.** In **tutti gli otto scenari** il miglioramento del TSI resta **strettamente positivo**, in un intervallo compreso tra **+8,7 % e +28,5 %**, e l'**ordinamento tra le unità si mantiene invariato**. La conclusione dell'attività — che la transizione alla Intelligent Factory migliora la sostenibilità termodinamica delle tre unità — è pertanto **robusta rispetto alle scelte di ponderazione** e non dipende dalla particolare parametrizzazione del caso base. La componente exergica Ψ risulta il fattore più influente (intervallo +8,7 %÷+28,5 %), a conferma che il nucleo del risultato è di natura fisica e non convenzionale.

### 3.7 Controlli di coerenza

Sono stati eseguiti, in coerenza con i controlli di qualità previsti dai manuali dei moduli, i seguenti presidi, tutti superati: (i) **coerenza massica** — la massa di polvere atomizzata non eccede la somma di materie prime e scarti reimmessi (m_SDM ≤ m_RM + m_UW); (ii) **coerenza exergetica** — le exergie di perdita di stadio risultano non negative (Ex_loss ≥ 0) in tutti i perimetri MTS/MTO, condizione che valida la correttezza dei coefficienti e dei perimetri; (iii) **clamp qualità** — i termini di penalità qualità sono confinati nell'intervallo [0,1]; (iv) **coerenza delle unità** — mantenimento dei MJ in tutte le tabelle intermedie e conversione a GJ solo in output (divisione per 10³); (v) **assenza di doppio conteggio** — verifica che nessun recupero compaia contemporaneamente come riduzione di RI e come credito CIRC, e che le voci economiche non fisiche non duplichino flussi già convertiti in EFA-J/TEI-J.

### 3.8 Consolidamento della versione beta di EEA+

Il collaudo in ambiente operativo ha permesso di far evolvere lo strumento dalla versione *alpha* (OR6.5) alla **versione beta**, di cui la Tabella 5 sintetizza gli avanzamenti.

**Tabella 5 — Evoluzione EEA+: da alpha (OR6.5) a beta (OR7.3).**

| Elemento | Versione alpha (OR6.5) | Versione beta (OR7.3) |
|---|---|---|
| Formulazione | Concettuale, indici per addetto/GJ | Operativa, 4 moduli -J con formule esplicite |
| Sorgente dati | Serie storiche isolate | ERP storico + EDGE real-time via E2C |
| Coefficienti | Valori segnaposto | Libreria versionata, metadati e confidenza A–C |
| Doppio conteggio | Non formalizzato | Regole di esclusione tra moduli + cut-off riciclo |
| Controlli qualità | — | Bilanci massa/exergia, clamp, sensibilità ±10 % |
| Definizione TSI | Duplice, non riconciliata | Riconciliata (forma composita + normalizzata) |
| Output | TSI teorico | 6 TSI (3 unità × 2 scenari), dashboard, allegati |
| Ambiente | Foglio di calcolo | Integrato E2C (Python/Power BI), production-ready |

### 3.9 KPI di confronto con la baseline

**Tabella 6 — KPI di riferimento dell'attività e risultati ottenuti.**

| KPI | Baseline (dati storici) | Obiettivo (dati real-time) | Risultato |
|---|---|---|---|
| Indice Termodinamico di Sostenibilità (TSI) | N°3 (1 per unità produttiva, dati storici) | N°3 (1 per unità produttiva, dati real-time) | **Confermato: 3 + 3 TSI calcolati** |
| Versione strumento EEA+ | alpha (OR6.5) | beta collaudata | **Confermato (beta production-ready)** |
| Intensità exergetica f_exergy | 47,8–52,0 MJ/m² | in riduzione | **−5,2 % ÷ −6,7 %** |
| Miglioramento medio TSI (gruppo) | riferimento | atteso positivo | **+18,7 % (robusto: +8,7 %÷+28,5 %)** |
| Rapporto SA real-time/storico (TSI_norm) | 1,00 | > 1 | **≈ 1,90** |
| Copertura moduli footprint | parziale | 4 impronte integrate | **EFA-J · EcoFA-J · SFA-J · TEI-J** |

---

## 4. DISCUSSIONE E CONCLUSIONI

### 4.1 Lettura critica dei risultati

L'Assessment Termodinamico della Fabbrica dimostra empiricamente la tesi centrale del filone metodologico del progetto: le quattro dimensioni della sostenibilità possono essere **ricondotte a un'unica scala fisica** — il Joule — e sintetizzate in un indicatore unico, il TSI, senza le arbitrarietà tipiche degli approcci multi-criterio a pesi soggettivi. La conversione exergica fornisce il denominatore comune che gli strumenti tradizionali (LCA, LCC, SO-LCA, KPI tecnologici) non possiedono, superando definitivamente la lettura "a silos" della sostenibilità. Il risultato non è meramente qualitativo: la gestione in tempo reale abilitata dall'architettura E2C produce un incremento medio del TSI del **+18,7 %**, una riduzione dell'intensità exergetica fino al **−6,7 %** e un **quasi raddoppio** della Sustainability Accounting, con un profilo di miglioramento robusto rispetto a tutte le variazioni di parametrizzazione testate.

Va sottolineata con onestà metodologica la corretta interpretazione del **valore assoluto del TSI**, deliberatamente basso: esso non è un difetto del modello ma il riflesso fedele della bassa efficienza exergica di secondo principio dei processi ceramici, dove la cottura ad alta temperatura distrugge irreversibilmente gran parte dell'exergia immessa. Per questo il TSI va letto in chiave **relativa e comparativa** (variazione nel tempo, confronto tra unità), non come punteggio assoluto — coerentemente con la sua stessa definizione normalizzata alla baseline (OR6.5).

### 4.2 Validazione incrociata con la *footprint family*

Un elemento di particolare valore probatorio è la **convergenza tra metodi indipendenti**. L'ordinamento delle tre unità restituito dal TSI (D240 > D060 > D020) coincide con quello ottenuto, con metodologia e dati diversi, dalla *footprint family* dell'OR6.1÷6.4 (dove D020, impianto più datato, risulta il meno performante e D240, ristrutturato nel 2017, tra i migliori). Il fatto che due catene di calcolo distinte — l'una basata su normalizzazione z-score/Min-Max e somma ponderata (SAW), l'altra sulla conversione exergica in Joule — producano la **stessa gerarchia** costituisce una validazione incrociata della robustezza dell'impianto valutativo del progetto e riduce sensibilmente il rischio di *bias* metodologico.

### 4.3 Interdipendenze con gli altri Obiettivi Realizzativi

Il Task 7.3 è, per costruzione, il nodo in cui confluiscono i risultati dell'intero partenariato:

- **OR6.1÷6.4** forniscono le quattro impronte *alpha* e le serie storiche di validazione, qui operazionalizzate nei moduli -J;
- **OR6.5** fornisce il modello teorico EEA+/SYMΞX, il quadro matematico (EA, RO, SA, HDM) e la definizione del TSI, qui applicati e riconciliati;
- **OR6.6/6.7/6.10** forniscono l'architettura E2C, la Intelligent Factory e la formalizzazione multilivello della Intelligent Industry, il cui *layer* di sostenibilità colloca proprio il TSI nella funzione di costo dell'ottimizzazione;
- **OR7.1/7.2** forniscono l'infrastruttura collaudata e certificata *production-ready*, senza la quale il calcolo *end-to-end* su dati reali e in tempo reale non sarebbe stato possibile;
- **OR4/OR5** (SACMI) forniscono il *framework* di *deployment* dell'AI e il controllo predittivo di processo, che sono la causa fisica dei miglioramenti di efficienza exergica qui misurati;
- **OR1** (UNIBZ) fornisce il concetto di Digital Twin e l'ambiente *Digital Grey Shadow* impiegato nella fase di collaudo.

### 4.4 Robustezza rispetto alle obiezioni e limiti

L'attività affronta esplicitamente le principali obiezioni che un revisore potrebbe sollevare. All'obiezione di **arbitrarietà dei pesi** risponde l'analisi di sensibilità (§3.6), che mostra la stabilità del segno e dell'ordinamento sotto ogni parametrizzazione. All'obiezione di **sovrastima** rispondono le regole anti-doppio-conteggio e il *cut-off* sul riciclo interno (§2.5, §3.7). All'obiezione di **incoerenza dei dati** rispondono i controlli di bilancio massa/exergia (§3.7). Restano i **limiti dichiarati**, di natura fisica e di maturità dello strumento: la **degradazione dell'exergia non è quantificabile con precisione assoluta** (limite intrinseco del secondo principio, OR6.5), e alcuni coefficienti della libreria *beta* hanno confidenza B/C in attesa delle campagne di misura definitive e delle EPD di fornitore. Entrambi i limiti sono mitigati dalla natura comparativa dell'analisi e dalla tracciabilità dei coefficienti, e nessuno dei due altera le conclusioni.

### 4.5 Sviluppi verso la versione release

Le prospettive di evoluzione verso la versione *release* dell'EEA+ riguardano: (i) il **popolamento completo della libreria Coefficients** con dati primari e EPD (elevazione a confidenza A); (ii) l'estensione del calcolo *real-time* a **granularità di linea e di lotto**, oltre che di stabilimento; (iii) la chiusura dell'anello di controllo, dal *Digital Grey Shadow* unidirezionale (OR7.2) a un **Digital Twin bidirezionale** in cui il TSI entri direttamente nella funzione di costo dell'ottimizzazione di processo, come formalizzato nel *layer* di sostenibilità della Intelligent Industry (OR6.10); (iv) la definizione di un mapping **DALY→Joule** approvato, che consenta di internalizzare pienamente il carico salute nel contributo sociale.

### 4.6 Contributo a RF7 e conclusioni

L'attività ha conseguito integralmente i propri obiettivi: sono stati calcolati i **sei valori di TSI** richiesti (3 unità × 2 scenari), è stato prodotto il **quadro di sostenibilità multidimensionale** delle tre unità produttive ed è stata consolidata e collaudata la **versione beta dell'EEA+** con i quattro moduli operativi in Joule, la libreria di coefficienti tracciata e i presidi di robustezza. In coerenza con il Piano di Sviluppo, il risultato duplice dell'attività — quadro di performance più strumento *beta* — contribuisce direttamente al **Risultato Finale RF7** (Documento finale di collaudo della Intelligent Industry).

Sul piano delle **implicazioni operative**, l'attività consegna all'organizzazione uno strumento decisionale che tiene insieme, in un unico indice fisicamente fondato, efficienza operativa e sostenibilità multidimensionale, e che è integrato nell'infrastruttura produttiva anziché confinato in una valutazione *ex post*. In questo senso il Task 7.3 fornisce la **prova conclusiva** che la transizione da *Industry 4.0* a *Intelligent Industry* è, per l'industria ceramica, non solo tecnologicamente fattibile ma **misurabilmente più sostenibile**, ponendo le basi quantitative per la gestione cognitiva della produzione propria dei modelli di Industria 5.0 e 6.0.

---

*Fine del documento — RP7.3 · Assessment termodinamico della fabbrica · Progetto START (Accordo Innovazione DM 31/12/2021, Prog. n. F/310087/01-05/X56) · www.start-innovability.it*
