# Istruzioni — correzioni testuali RP 7.3 RV.2

Destinatario: la sessione di lavoro dedicata all'OR 7.3 (branch
`claude/start-documentation-analysis-0tsdz8`).
Origine: rilettura della RP 7.3 RV.2 durante la rigenerazione della RP 7.8.

**Ambito: solo testo.** Numeri, log beta-1.3, dati, coefficienti e pesi restano
invariati. Nessuna tabella cambia valore. Le correzioni non toccano la regressione.

## Dove applicarle

Esistono due versioni del docx RV.2, non identiche:

- `start-iids/output/RP7.3_Report_Assessment_termodinamico_fabbrica_V2.docx`, generata
  da `start-iids/scripts/build_rp73_report.py`;
- la versione consegnata dal responsabile di progetto (presente anche nella root del
  branch `claude/sleepy-pasteur-yddrv2` come
  `RP 7.3 Report di Assessment termodinamico della fabbrica RV.2.docx`), che nel § 3.7
  contiene in più il paragrafo di commento alla Tabella 8 ("La Tabella 8 saggia la
  robustezza…").

Correggere **lo script** e rigenerare, così che script e docx restino allineati. Se il
paragrafo aggiuntivo della versione consegnata è voluto, va riportato nello script
(vedi correzione 1), altrimenti la rigenerazione lo perde.

## Correzione 1 — ordinamento in sensibilità (incoerenza sostanziale)

La Tabella 8 mostra che l'ordinamento D240 > D060 > D020 vale in **7 scenari su 8**:
nel "Focus multidimensionale (α = 0,6; β = 0,4)" l'ordinamento è D240 > D020 > D060.
D240 resta prima in tutti gli scenari. Il paragrafo di commento alla Tabella 8 lo dice
correttamente; due altri passaggi affermano invece che l'ordinamento si mantiene in
tutti gli scenari.

**1a. § 3.7, paragrafo dopo la Figura 6.** Testo attuale:

> In tutti gli scenari TSI_rel resta > 1 (intervallo complessivo 1,237–1,539) e
> l'ordinamento D240 > D060 > D020 (per TSI_abs 2025) si mantiene: il miglioramento e
> la gerarchia assoluta sono robusti.

Sostituire con:

> In tutti gli scenari TSI_rel resta > 1 (intervallo complessivo 1,237–1,539) e D240
> resta l'unità con il TSI_abs 2025 più alto; l'ordinamento D240 > D060 > D020 si
> mantiene in sette scenari su otto, con la sola inversione fra D060 e D020 nel focus
> multidimensionale. Il segno del miglioramento è robusto rispetto a tutte le ipotesi.

**1b. § 4.3 "Robustezza e correzione dell'intervallo", prima frase.** Testo attuale:

> L'analisi di sensibilità conferma TSI_rel > 1 e l'ordinamento assoluto in tutti gli
> scenari.

Sostituire con:

> L'analisi di sensibilità conferma TSI_rel > 1 in tutti gli scenari e l'ordinamento
> assoluto in sette scenari su otto (nel focus multidimensionale D020 supera D060).

L'ultima frase dello stesso paragrafo ("L'ordinamento assoluto D240 > D060 > D020 resta
invariato.") è corretta solo per il caso base: renderla esplicita, es. "Nel caso base
l'ordinamento assoluto D240 > D060 > D020 resta invariato rispetto alla RV.1."

**1c.** Cercare nel resto del documento (e in ADR-015 § 6 / ROADMAP, se lo riportano)
ogni altra formulazione "in tutti gli scenari" riferita all'ordinamento e allinearla.

## Correzione 2 — residui di markdown

Nel docx compaiono asterischi letterali, perché la funzione di paragrafo dello script
non converte il corsivo `*…*` (converte solo il grassetto `**…**`):

- § 1.2: `*consistency ratio*` → *consistency ratio* in corsivo;
- § 4.1: `*footprint family*` → *footprint family* in corsivo.

Correzione consigliata: gestire `*…*` come corsivo nella funzione che scrive i
paragrafi (oggi `_ir`/`P` in `build_rp73_report.py`), poi verificare sul docx
rigenerato che non resti alcun `*` nel testo (es. ricerca di `*` nei paragrafi e nelle
celle delle tabelle).

## Correzione 3 (consigliata) — definizione del TSI_rel di Gruppo

Il TSI_rel di Gruppo (1,3456) è la **media dei TSI_rel di unità ponderata sulla
produzione 2025**, non il rapporto fra TSI_abs di Gruppo 2025 e 2023 (0,1229 / 0,0909
= 1,352). Entrambe le letture sono legittime, ma il lettore che fa il conto trova un
numero diverso. Aggiungere alla didascalia della Tabella 10:

> TSI_rel di Gruppo: media dei TSI_rel di unità ponderata sulla produzione 2025.

La RP 7.8 adotta già questa definizione e la dichiara nella didascalia della sua
Tabella 3.

## Chiusura

1. Script corretto, docx RV.2 rigenerato; nessun `*` letterale residuo.
2. `pytest` verde (le correzioni sono testuali: nessun valore deve cambiare).
3. Confronto delle tabelle del docx rigenerato con quelle della versione consegnata:
   devono coincidere valore per valore.
4. Se cambiano il numero di versione o la data di revisione della RP 7.3, comunicarli:
   la RP 7.8 cita "RP 7.3 RV.2".
