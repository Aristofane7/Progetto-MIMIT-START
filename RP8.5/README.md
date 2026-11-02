# RP 8.5 — Piano di Stakeholder Engagement (OR 8, attività 8.5)

Relazione parziale dell'attività 8.5 "Trasferimento tecnologico agli Stakeholders" del progetto
START, redatta sul template ufficiale (`RPX.Y Titolo_Relazione_Parziale_data.docx`) con lo stile
delle RP finali (cfr. RP 7.6).

**Fonti:** Piano di Sviluppo (Allegato 4, OR 8, attività 8.5, KPI e problema progettuale n. 5;
problema n. 6 per il legame con 8.6); Relazione tecnica SAL 1 (§3 e §4, OR 8.5, Figura 8.4.1);
GANTT di progetto (8.5: mesi 1-17, RP 8.5 conclusa nel periodo del SAL 1 (relazioni SAL 1 e SAL 2) → data 30.04.24).

**KPI:** Indicatore di rilevanza degli Stakeholder, baseline 0,0 → Matrice di rilevanza.
IR = (Influenza × Interesse) / 25, punteggi 1-5 con la rubrica di `src/engagement.py`.

> I punteggi di Influenza/Interesse e la matrice degli interessi per tema sono valutazioni
> qualitative del gruppo di gestione, codificate in `src/engagement.py` per renderle
> riproducibili: vanno confermate dal responsabile di progetto.

## Struttura

```
RP8.5/
├── src/engagement.py      registro stakeholder, rubriche, IR, quadranti, materialità → output/*.csv
├── src/build_report.py    figure + .docx sul template START (note a piè di pagina incluse)
├── docs/RP8.5_Piano_Stakeholder_Engagement.docx / .pdf
├── docs/figures/          fig_se1..4 (fig_se2 = mappatura originale del SAL 1)
└── output/                registro_stakeholder.csv, materialita_temi.csv
```

## Rigenerazione

```bash
pip install -r requirements.txt
python -m src.build_report     # dalla cartella RP8.5/
```

Il comando aggiorna anche la copia in radice `RP 8.5 Piano di Stakeholder Engagement_30-04-24.docx`.
