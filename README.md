# START — Modello di business guidato dall'Intelligenza Artificiale (AI-BM)

Materiali e codice a supporto dell'attività **7.10** del progetto **START** (*SusTainable
dAta-dRiven manufacTuring*) — OR 7, *Validazione in ambiente operativo della Intelligent
Industry*, capofila **Gresmalt S.p.A.**

L'attività 7.10 è la conclusione dell'OR 7: definisce e propone un **modello di business
guidato dall'AI (AI-BM)** che valorizza la transizione verso la *Intelligent Industry*.
Il KPI qualitativo è il **Business Model Canvas** (baseline: Modello di Business
tradizionale → obiettivo: AI-BM). L'impostazione replica quella del *Circular Business
Plan* del progetto VOLT (RP 8.8): relazione + codice riproducibile + figure + export
tabellare per Power BI.

## Struttura del repository

```
Progetto-MIMIT-START/
├── README.md
├── requirements.txt
├── run_collaudo_aibm.py        # runner: BMC, KPI, catena del valore, SWOT, transition + export CSV
├── src/
│   └── aibm.py                 # modello codificato dell'AI-BM (BMC as-is/to-be, SWOT, transition)
├── scripts/
│   └── gen_figures_aibm.py     # genera le figure della relazione
├── docs/
│   ├── RP7.10_AI_Business_Model.md    # relazione (template ufficiale a 4 sezioni)
│   ├── RP7.10_AI_Business_Model.docx  # versione Word
│   └── figures/                       # figure fig_aibm*.png
└── output/                     # collaudo_aibm_*.csv (per Power BI)
```

I documenti di riferimento del progetto (RP 6.x, RP 7.x, EPD, manuali EEA+, paper) sono i
PDF presenti nella radice del repository.

## Riproducibilità

```bash
pip install -r requirements.txt
python run_collaudo_aibm.py         # stampa gli esiti ed esporta output/collaudo_aibm_*.csv
python scripts/gen_figures_aibm.py  # rigenera docs/figures/fig_aibm*.png
```

## Impianto metodologico

- **Business Model Canvas (KPI):** i 9 blocchi in doppia versione *as-is* (tradizionale)
  e *to-be* (AI-BM).
- **Catena dato → informazione → valore:** il "motore" dell'AI-BM, alimentato dai
  collaudi dell'OR 7 (RP 7.1–7.9).
- **Analisi strategica:** SWOT dell'AI-BM e *transition model* (da logiche
  asset-based/episodiche a sistemi adattivi data-driven), con le quattro tensioni
  sistemiche dell'*embodied AI* (Bouncken & Cesinger, 2026).

Il *BM design* si avvale di consulenza specialistica (problema progettuale n. 10).
Le voci del modello sono rappresentative e vanno consolidate con i dati aziendali.
