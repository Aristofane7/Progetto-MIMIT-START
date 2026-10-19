# RP 8.6 — Assessment dell'impatto di START (analisi input‑output di Leontief)

Pacchetto riproducibile dell'attività **8.6 dell'OR 8** del progetto START: **simulazione**
dell'impatto socio‑economico del progetto sui quattro territori della scheda (**Emilia‑Romagna,
Provincia di Bolzano, Sardegna, Calabria**) e **predisposizione del modello analitico** input‑output
da applicare **ex‑post** con i dati ISTAT.

> **STATO: simulazione con valori rappresentativi.** In assenza dei dati macroeconomici regionali
> (problema progettuale n. 6), i coefficienti e lo shock di domanda finale sono **rappresentativi**,
> calibrati sull'ordine di grandezza della filiera ceramica; **nessun dato riservato**. Il deliverable
> è lo *strumento* (modello + protocollo), non la misura consuntiva. La struttura di calcolo resta
> invariata al consolidamento con le tavole I‑O regionali ISTAT (accesso via RP 8.5).

## Struttura

```
RP8.6/
├── README.md
├── requirements.txt
├── run_impatto.py                       runner end‑to‑end → output/impatto_*.csv
├── src/
│   ├── impatto.py                       modello di Leontief (matrice A, inversa L, moltiplicatori I/II)
│   └── build_report.py                  assembla il .docx sul template ufficiale START
├── scripts/
│   └── gen_figures_impatto.py           genera le 4 figure della relazione
├── docs/
│   ├── RP8.6_Assessment_Impatto.md      relazione (sorgente Markdown, per lettura/diff)
│   ├── RP8.6_Assessment_Impatto.docx    relazione ufficiale (template START: loghi, header, stili)
│   ├── RP8.5-8.6_Contesto_Preliminare.md  nota di inquadramento (perimetro, baseline, metodo)
│   └── figures/                         fig_imp1..4 (PNG)
└── output/
    ├── impatto_regioni.csv              impatto per regione (diretto/indiretto/indotto)
    ├── impatto_moltiplicatori.csv       moltiplicatori Tipo I/II per settore
    └── impatto_kpi.csv                  verifica del KPI di scheda
```

## Esecuzione

```bash
pip install -r requirements.txt          # numpy, pandas, matplotlib
python run_impatto.py                    # calcolo + export CSV
python scripts/gen_figures_impatto.py    # rigenera le figure
python src/build_report.py               # assembla il .docx ufficiale sul template START
```

Il `.docx` è generato da `src/build_report.py`, che apre il template ufficiale
`RPX.Y Titolo_Relazione_Parziale_data.docx` (loghi, intestazioni, piè di pagina e stili),
compila i segnaposto di copertina e ricostruisce il contenuto (testo, tabelle, figure)
importando i numeri dal motore `impatto.py` — così documento, CSV e figure restano coerenti.
Dipendenza: `python-docx`. Il template dev'essere presente nella radice del repository.

## Sintesi dei risultati (simulazione)

| Regione | Domanda diretta (M€) | Output totale (M€) | Molt. | Valore aggiunto (M€) | Occupazione (ULA) |
|---|:--:|:--:|:--:|:--:|:--:|
| Emilia‑Romagna | 42,0 | 75,1 | 1,79 | 35,1 | 365 |
| Provincia di Bolzano | 9,0 | 14,3 | 1,58 | 7,8 | 80 |
| Sardegna | 9,0 | 14,9 | 1,66 | 7,7 | 80 |
| Calabria | 8,0 | 12,8 | 1,60 | 6,9 | 71 |
| **Totale** | **68,0** | **117,1** | **1,72** | **57,6** | **596** |

Moltiplicatore di produzione più alto: **ceramica** (1,75 Tipo I / 2,03 Tipo II), coerente con la
posizione di core della filiera.

## Come integrare i dati reali (applicazione ex‑post)

1. Acquisire, via coinvolgimento delle autorità territoriali (RP 8.5), le **tavole I‑O regionali
   ISTAT** (SUT/IO) e i **consuntivi degli investimenti** del progetto.
2. In `src/impatto.py` sostituire la matrice `A`, i coefficienti `VA_COEFF`/`EMP_COEFF` e il
   dizionario `FINAL_DEMAND` con i valori ufficiali (la struttura del modello resta invariata).
3. Ri‑eseguire `python run_impatto.py` per ottenere la **stima consuntiva** e i moltiplicatori reali.
4. Confrontare simulato vs consuntivo (**analisi degli scostamenti**, OR 8) e alimentare il RF 8.

## Nota metodologica

La struttura del modello (settori, matrice `A`, coefficienti di VA e occupazione) è quella della
filiera ceramica e coincide con quella del progetto gemello **VOLT (RP 9.6)**; ciò che è stato
ricalibrato per START è la **ripartizione regionale dello shock** di domanda finale sui quattro
territori della scheda.

## Dipendenze

`numpy`, `pandas`, `matplotlib` (figure), `python-docx` (generazione del `.docx` sul template).
