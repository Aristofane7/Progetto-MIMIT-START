# RP7.3 — Assessment termodinamico della fabbrica (EEA+ beta)

Pipeline riproducibile per il calcolo dell'**Indice Termodinamico di Sostenibilità (TSI)**
delle unità produttive D020, D060, D240 (scenari *storico* e *real-time*), secondo il
master metodologico **V0** e il modello **EEA+ beta**.

> ⚠️ **STATO: VERSIONE DI LAVORO V1.0 — VALORI DIMOSTRATIVI / NON VALIDATI (confidenza C).**
> Non sono stati forniti dati primari ERP/MES né export E2C. I numeri presenti servono a
> esercitare e verificare la pipeline; **vanno sostituiti con dati verificati** prima di
> qualsiasi uso decisionale o del collaudo formale della beta.

## Struttura
```
RP7.3/
├── input/                      dati dimostrativi (CSV) + cartelle per dati reali
│   ├── energy_exergy.csv        vettori energetici ed exergia per unità/scenario
│   ├── module_terms.csv         termini dei 4 moduli (MJ) per unità/scenario
│   ├── data_historical/         (vuoto) → export ERP/MES storici
│   └── data_realtime/           (vuoto) → export E2C real-time
├── coefficients/
│   ├── coefficients_master.xlsx libreria coefficienti (code, valore, unità, fonte, anno, boundary, metodo, confidenza, versione)
│   └── ahp_weights.xlsx         matrice AHP di prova + pesi + λmax/CI/CR
├── src/                        motore di calcolo (vedi sotto)
└── output/
    ├── figures/                equazioni SVG (eq01..eq21) + figure (fig1..fig6), con PNG di fallback
    ├── tables/                 (riservato a esportazioni tabellari)
    ├── RP7.3_calculation_log.xlsx   registro di tracciabilità dei risultati
    └── RP7.3_Report_Assessment_termodinamico_fabbrica_V1.docx   report finale
```

## Moduli `src/`
| File | Ruolo |
|---|---|
| `core.py` | costanti, parametrizzazione dimostrativa, formule dei 4 moduli, exergia |
| `ingest.py` / `validation.py` | lettura input CSV / controlli di coerenza |
| `tei_j.py` `efa_j.py` `ecofa_j.py` `sfa_j.py` | i quattro moduli -J (wrapper sulle formule di `core`) |
| `ahp.py` | pesi da matrice di confronto (media geometrica) + CI/CR |
| `integration.py` | SA_raw, SA_w, Φ, Ψ, TSI_abs, TSI_rel |
| `sensitivity.py` | analisi di sensibilità (coeff. ±10%, Ψ, pesi, α/β) |
| `equations.py` | rende le equazioni in SVG vettoriale (+PNG) |
| `figures.py` | figure 1–6 (SVG+PNG) |
| `docx_svg.py` | inserimento di immagini SVG in DOCX (fallback PNG, meccanismo Word 2016+) |
| `build_report.py` | assembla il DOCX V1 sul template START + calculation_log |
| `run_all.py` | orchestratore end-to-end |

## Convenzioni di calcolo (fix rispetto alle bozze)
- unità native → **MJ** (layer di calcolo) → **GJ** con **/1.000** (1 GJ = 1.000 MJ = 10⁹ J). *Non* si divide per 10⁹ valori già in MJ.
- exergia del combustibile = **exergia chimica** (`b_fuel`); l'efficienza di conversione è in **Ψ**, non in `Ex_ref`.
- `Ex_ref = Ex_el + Ex_fuel`; `Ψ = Ex_useful/Ex_ref`; `Φ = SA_w/Ex_ref`; `TSI_abs = αΦ + βΨ` (α+β=1); `TSI_rel = TSI_abs,rt/TSI_abs,stor`.
- pesi dimensionali **da AHP** (CR ≤ 0,10), non assunti a priori.

## Esecuzione
```bash
# dalla cartella RP7.3/ (dipendenze: numpy, pandas, openpyxl, matplotlib, python-docx)
python3 -m src.run_all
```
Rigenera input dimostrativi, coefficienti, AHP, equazioni, figure, `calculation_log.xlsx` e il DOCX V1.

## Come integrare i dati reali
1. Popolare `input/data_historical/` e `input/data_realtime/` (o `energy_exergy.csv` e `module_terms.csv`) con i dati primari per D020/D060/D240.
2. Valorizzare `coefficients/coefficients_master.xlsx` con coefficienti primari/EPD (elevare la confidenza da C ad A/B).
3. Sostituire la matrice `ahp_weights.xlsx` con i giudizi del panel (verificare CR ≤ 0,10).
4. Confermare la baseline (matrice di disponibilità) o selezionare il primo anno comune valido.
5. Rieseguire `python3 -m src.run_all`: la struttura di calcolo resta invariata, cambiano solo i valori.

## QA / PDF
Il rendering PDF non è disponibile nell'ambiente di build (LibreOffice non operativo): la QA è
**strutturale** (equazioni SVG, tabelle, loghi, header/footer verificati). Il PDF di controllo va
generato aprendo il DOCX in Microsoft Word.

## Dipendenze
`numpy`, `pandas`, `openpyxl`, `matplotlib`, `python-docx`.
