# Istruzioni — aggiornamento RP 7.3 per la cessazione di D020 (luglio 2025)

Destinatario: la sessione di lavoro dedicata all'OR 7.3.
Origine: collaudo RP 7.8 (branch `claude/sleepy-pasteur-yddrv2`, file
`RP 7.8 Report di collaudo della Intelligent Industry.docx`).

## 1. Il fatto da recepire

L'unità **D020 (Viano)** ha prodotto nel 2025 solo per una parte dell'anno e ha
**cessato le attività nel luglio 2025** per la riconversione a polo logistico
(confermato anche dalla RP 7.5, § 1.2). Dal 2026 il perimetro produttivo è D060 + D240.

## 2. L'incoerenza nei dati attuali

I file di input della RP 7.3 trattano il 2025 di D020 come un anno pieno:

| File / foglio | Valore attuale D020 2025 | Problema |
|---|---|---|
| `RP7.3_data_collection_20232025.xlsx` › `Unita` | `produzione_m2 = 3.800.000` | Un solo valore per unità, identico per tutti gli anni: non esiste una produzione per anno |
| › `Energia` | gas 3.510.476 Nm³, el. 10.238.889 kWh | Prosegue il trend di anno pieno (−2,9 %/anno) |
| › `Moduli_TEI/EFA/EcoFA/SFA` | termini 2025 in trend di anno pieno | Idem |
| `RP7.3_calculation_log.xlsx` | R021–R031 (D020 2025), Ψ = 0,164 | Calcolati su anno pieno |

Il file esiste in **due copie identiche** (stesso md5): nella root del repo e in
`start-iids/data/reference/`. Vanno aggiornate entrambe allo stesso modo.

## 3. Dati da raccogliere (reali, non stimati)

Per D020, periodo **gennaio – data di cessazione luglio 2025** (indicare il giorno esatto):

1. produzione (m²) del periodo;
2. gas naturale (Nm³) ed energia elettrica (kWh, inclusa autoproduzione) del periodo;
3. termini dei quattro moduli in MJ (TEI: loss_MTS, loss_MTO, inv, qual_MTS, qual_MTO;
   EFA: RI, IEQ, WEX, CIRC; EcoFA: VA, econ_in, INV; SFA: SV, train, lost, CO2);
4. Ψ (o Ex_useful) per il periodo;
5. **gli stessi termini per il 2022 sul medesimo periodo gennaio–luglio** (vedi § 4).

Non ricavare questi valori riproporzionando quelli di anno pieno: sarebbe un dato
costruito, non misurato. Se un dato non è disponibile, va dichiarato come tale.

## 4. Decisione metodologica da prendere PRIMA del ricalcolo

I contributi dei moduli sono **differenze rispetto al 2022 (anno pieno)**, ad es.
`f_env = (RI_ref − RI) + (CIRC − CIRC_ref) − (IEQ − IEQ_ref) − (WEX − WEX_ref)`.
Se si inseriscono i valori di sette mesi del 2025 contro un riferimento di dodici
mesi del 2022, la differenza diventa artificialmente enorme: D020 risulterebbe in
fortissimo "miglioramento" solo perché ha prodotto meno mesi.

Opzioni (scegliere con il responsabile e registrare la scelta in un ADR):

- **A (raccomandata)** — riferimento omologo: per D020 2025 il termine `_ref` è il
  2022 sullo stesso periodo gennaio–luglio. Richiede i dati del § 3.5.
- **B** — normalizzazione per m²: termini 2025 e riferimento 2022 espressi per m²
  prodotto, poi riportati alla produzione del periodo. Va dichiarata come scelta
  metodologica, perché cambia la definizione del modulo.
- **C** — esclusione: D020 2025 non calcolato; per D020 la serie si ferma al 2024 e
  TSI_rel diventa 2024/2023 (oggi 1,176). È la più semplice, ma riduce i "6 TSI
  calcolati" del KPI.

Con qualsiasi opzione, TSI_abs, Φ e Ψ restano confrontabili perché sono rapporti.
Ex_ref, SA_raw, SA_w e i contributi f_i di D020 2025 **non** sono confrontabili con
gli anni pieni.

## 5. Interventi sul codice `start-iids` (regole già in vigore nel repo)

1. **Non modificare in-place** il registro `RP7.3_calculation_log.xlsx` (beta-1.1):
   è il riferimento della regressione `tests/regression/test_rp73_calculation_log.py`.
   Archiviarlo come fixture versionata (es. `RP7.3_calculation_log_beta-1.1.xlsx`) e
   produrre un nuovo registro `beta-1.2`; la regressione deve verificare il nuovo,
   mantenendo un test sul vecchio per tracciabilità.
2. Il foglio `Unita` va portato a **produzione per anno** (`plant, year, produzione_m2`)
   e aggiornato `src/ingestion/rp73_reference_data.py` di conseguenza.
3. Aggiungere un campo di **periodo di esercizio** per unità/anno (es. `months_active`
   o date inizio/fine) e un controllo di qualità che blocchi il confronto di
   grandezze estensive fra periodi di durata diversa.
4. I set `COEFF_RP73_PROVISIONAL_2026` e `EEA_AHP_RP73_1` sono `APPROVED` (ADR-013) e
   **non cambiano**: qui cambiano i dati, non i coefficienti. Se il consolidamento
   toccasse anche i coefficienti, serve un nuovo `coefficient_set_id`, mai una
   modifica di quello approvato.
5. Nuovo ADR (es. `ADR-015-d020-partial-year-2025.md`) con: fatto, opzione scelta
   (§ 4), fonte dei dati del periodo, effetto sui valori.
6. Aggiornare `start-iids/data/reference/README.md`, il README e `docs/ROADMAP.md`
   (oggi citano "66 punti reali" / "93 valori"), poi `pytest` tutto verde.
7. La media di Gruppo è oggi ponderata con `produzione_m2` costante: con la
   produzione per anno, D020 2025 peserà per la produzione effettiva del periodo.

## 6. Interventi sul testo della RP 7.3

Nuova versione **RV.2** (data di revisione da decidere), stesse sezioni:

- § 1.3 *Perimetro*: D020 in esercizio fino a luglio 2025, poi riconvertita; opzione
  metodologica adottata.
- Tabella 1 *Disponibilità dati*: D020 2025 = gennaio–luglio.
- Tabella 4 *Bilancio exergetico*: produzione per anno; valori D020 2025 del periodo,
  con nota di non confrontabilità.
- Tabelle 5–6 *Contributi e SA*: idem.
- Tabella 7 *TSI*: nuovi valori D020 2025 e TSI_rel; la nota "2025 = tempo reale (E2C)"
  per D020 vale per il solo periodo di attività.
- Tabella 8 *Sensibilità* e Tabella 10 *α/β di Gruppo*: ricalcolate.
- Tabella 12 *KPI*: rivedere "6 TSI calcolati (2023 e 2025)" secondo l'opzione scelta.
- § 4.3 *Lettura dei risultati*: verificare che l'ordinamento D240 > D060 > D020 e
  l'intervallo TSI_rel 1,32–1,36 siano ancora veri dopo il ricalcolo; correggere il
  testo, non i numeri.
- Figure 3–6: rigenerate.

## 7. Ricadute su altri documenti — da segnalare a valle

- **RP 7.8** (collaudo Intelligent Industry) usa i valori RP 7.3 attuali: Tabelle 2,
  3, 4, Figura 1, Tabella 8 (KPI), TSI di Gruppo 0,0909 → 0,1219, TSI_rel 1,341,
  "93 valori su 93". Dopo l'aggiornamento della RP 7.3 va rigenerata.
  Oggi la RP 7.8 già dichiara la cessazione di D020 e marca "n.c." la variazione di
  Ex_ref di D020.
- **RP 7.4** non è toccata (T1, T2 su D060; T3 su D240).
- **RP 8.6** (impatto): verificare se usa grandezze EEA+ di D020 2025.

## 8. Criterio di chiusura

- Dati D020 2025 del periodo reale inseriti in entrambe le copie del file di raccolta;
- ADR della scelta metodologica registrato;
- `python3 -m src.run_all` rigenera il nuovo registro e `pytest` è verde;
- RP 7.3 RV.2 coerente con il nuovo registro, valore per valore;
- comunicazione dei nuovi valori per la rigenerazione della RP 7.8.
