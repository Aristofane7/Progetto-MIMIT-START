# Allegato 16 — Relazione tecnica di SAL finale (01/11/2025–31/10/2026), parte Gresmalt

Impostazione e lunghezza modellate sulla relazione di SAL finale del progetto VOLT
(`Progetto_MIMIT-VOLT/reports/relazioni_SAL3/VOLT_SAL_FINALE_ALL16_Gresmalt_OR7-OR9.docx`).

- Base: relazione ufficiale SAL 2 (`fonti/START_ALL16_SAL2.docx`): intestazione, dati identificativi,
  sedi e stili; periodo aggiornato a «SAL FINALE dal 01/11/2025 al 31/10/2026».
- OR 1–5 (altri partner), tabelle ore/uomo, tabelle costi, GANTT: segnaposto da compilare.
- OR 6–8 (Gresmalt): introduzione di OR; attività chiuse nei SAL precedenti in una riga
  (6.1–6.4, 8.1–8.5 → SAL 1; 6.5–6.10, 7.1–7.2 → SAL 2); sezione estesa per 7.3–7.10 e 8.6.
- Fanno fede le date delle relazioni di SAL (non il GANTT): 7.3–7.10 risultavano «non ancora avviate»
  al SAL 2, 8.6 al 63%.
- Fonti per attività: RP 7.3 RV.2; RP 7.4; RP 7.5, 7.6, 7.8, 7.9 (versioni PDF aggiornate);
  RP 7.7 + annessi; RP 7.10 (`Attivita_7.10/`); RP 8.6 V1.0 (31.10.2026).

```
md/            testi delle sezioni (una per attività + intro_or.md + sezioni_finali.md)
figures/       figure (estratte dalle RP o rielaborate dai loro dati, come indicato in didascalia)
build_all16.py genera START_ALL16_SAL_finale_Gresmalt.docx (+ PDF di anteprima)
```

Rigenerazione: `python SAL_finale/build_all16.py`

# Allegato 20 — Relazione finale di progetto, parte Gresmalt

Modello: `Progetto_MIMIT-VOLT/reports/relazioni_SAL3/VOLT_ALL20_Relazione_finale_Gresmalt_OR7-OR9.docx`.
Base: modello ufficiale All. 20 (`fonti/API-2022_ALL20_modello.docx`) compilato con i dati delle
relazioni di SAL. §3 Obiettivi e §4 Attività (riassunto cumulativo di tutte le 26 attività
Gresmalt, 6.1–8.6) da `md/all20/`; OR 1–5, §5 costi, §6 effetti e §8 valutazione critica a
segnaposto, come nel modello VOLT. Rigenerazione: `python SAL_finale/build_all20.py`.
