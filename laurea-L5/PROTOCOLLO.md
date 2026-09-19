# PROTOCOLLO — Repository di studio Laurea L-5 (UniPegaso)

> File di istruzioni operative. Va letto **per intero e per primo** all'inizio di ogni sessione,
> prima di qualsiasi altra azione sul repository.
> Ultimo aggiornamento: 19/09/2026 — dopo la Lezione 1 di Filosofia Morale.

---

## 1. Scopo

Preparare gli esami della laurea L-5 con un metodo **discriminativo** (riconoscere l'opzione
corretta fra quattro) costruito sopra uno strato **concettuale** (capire l'architettura della
disciplina), senza ridurre lo studio a memorizzazione di coppie domanda–risposta.

Vincolo di fondo: lo studente ha ottime prestazioni argomentative (orale) e difficoltà sui quiz
a risposta multipla. Il metodo deve convertire il primo punto di forza nel secondo, non
combatterlo.

**Doppio obiettivo, non negoziabile:** superare la prova *e* apprendere i fondamenti.
I documenti prodotti devono restare leggibili come trattazione, non degradare a prontuario.

---

## 2. Struttura del repository

```
laurea-L5/
├── PROTOCOLLO.md                  ← questo file
├── README.md                      ← indice degli insegnamenti e stato avanzamento
│
├── filosofia-morale-mfil03/
│   ├── STATO.md                   ← dove siamo, cosa manca, prossima azione
│   ├── programma.md               ← indice ufficiale delle 41 lezioni
│   ├── dispense/                  ← SOLO testo estratto in .md, mai PDF
│   │   ├── L01.md
│   │   └── ...
│   ├── test/                      ← test di autovalutazione trascritti
│   │   ├── L01.md
│   │   └── ...
│   ├── nodi/                      ← i documenti concettuali (8 nodi, non 41 lezioni)
│   │   ├── nodo1-ontologia-persona.md
│   │   ├── nodo1-ontologia-persona.tex
│   │   └── ...
│   ├── cluster/
│   │   ├── griglia-aggettivale.md ← PRIORITARIO: il cluster più redditizio
│   │   ├── attribuzione.md
│   │   ├── formule-latine.md
│   │   ├── coppie.md
│   │   ├── gerarchie.md
│   │   ├── opere.md
│   │   ├── negazioni.md
│   │   └── lessico.md
│   ├── registro-errori.md         ← errori per ASSE, non per risposta
│   └── densita-paragrafi.md       ← quanti item per paragrafo, per lezione
│
├── storia-filosofia-moderna-mfil06/   (stessa struttura)
├── logica-ontologia-mfil02/
├── etica-relazioni-mfil03/
└── _template/                     ← scheletro vuoto per nuovi insegnamenti
```

**Regola:** nessun PDF di dispensa nel repository. Solo testo estratto in markdown.
Repository **privato**.

---

## 3. Il ciclo per lezione

Ordine obbligatorio. Il punto 1 perde ogni valore se eseguito dopo il 3 o il 5.

1. **Test a freddo** — prima di leggere la dispensa e prima di vedere la videolezione.
   Nessuna consultazione. Serve a generare il deficit che la lettura poi colma (pretesting).
2. **Correzione** — il sistema rivela risposta corretta **e paragrafo di riferimento**.
3. **Lettura mirata** — solo i paragrafi indicati dagli item sbagliati, poi scorsa in diagonale
   del resto a caccia di: nomi propri, formule latine, coppie oppositive, aggettivi qualificanti.
4. **Aggiornamento cluster** — a partire sempre dalla griglia aggettivale.
5. **Registro errori** — si annota **l'asse dell'errore**, mai la risposta corretta.
6. **Videolezione** (solo per le lezioni selezionate) — ascolto passivo, come seconda esposizione.
   Non è studio: è ripasso spaziato + copertura del rischio "domande extra".

Durata target: 30 minuti (40 per le lezioni del nucleo teorico).

---

## 4. Regole di decisione sugli item

Scoperte empiricamente, da verificare e aggiornare lezione per lezione.
**Contatore di conferme fra parentesi.**

### R1 — Ancoraggio lessicale (confermata, forte)
La risposta corretta è la formulazione che **compare letteralmente** nel paragrafo indicato,
anche quando è dottrinalmente imprecisa o quando l'argomentazione la usa in senso *critico*.
**Non ricostruire l'argomento: cercare l'occorrenza.**

> Caso L01/1 — «L'*actus essendi* è unità di forma e materia» è dottrinalmente falso
> (l'atto d'essere si aggiunge all'essenza), ma il §1 contiene quella sequenza di parole.
>
> Caso L01/6 — «La personalità è relazione diretta con l'assoluto»: nel §2 l'Assoluto compare
> *dentro la critica a Hegel*. L'item lo assume in positivo. Chi ricostruisce la polemica
> esclude la risposta giusta.

### R2 — Opzione semplice (2 conferme su 2)
Quando fra le quattro opzioni ce n'è una lunga e onnicomprensiva (tipo «A, B e C insieme»),
è **esca**. La corretta è l'opzione semplice.
→ Da riverificare. Se regge su 5 lezioni, promuovere a regola di decisione sotto pressione.

### R3 — Premessa inaffidabile (1 conferma)
Negli item «Per [autore] X è…» l'attribuzione nella domanda può essere **errata** e non va usata
come indizio. Rispondere sul contenuto.

> Caso L01/7 — «Per Tommaso è sostanza dotata di razionalità»: la definizione è di **Boezio**,
> e la dispensa lo dice esplicitamente.

### R4 — Struttura aggettivale (dominante in L01)
La maggioranza degli item ha forma: **«X è: [sostantivo fisso] + aggettivo variabile»**, e i
quattro distrattori si ottengono ruotando l'aggettivo dentro un lessico chiuso.
→ Da qui la priorità assoluta della griglia aggettivale sui cluster di attribuzione.

### Avvertenza permanente
La competenza filosofica dello studente è, su questo formato, **un fattore di rischio**:
porta a scartare l'opzione testualmente presente in favore di quella dottrinalmente esatta.
Vale anche per l'assistente: nella sessione del 19/09 l'item L01/6 è stato sbagliato **tre volte**
per ricostruzione dottrinale. Applicare R1 prima di ogni ragionamento.

---

## 5. La griglia aggettivale (cumulativa — priorità 1)

Formato: `nozione → aggettivo corretto (aggettivi-esca osservati) [lezione]`

| Nozione | Aggettivo corretto | Esche osservate | Lez. |
|---|---|---|---|
| Sussistenza (Maritain) | **ontologico** | spirituale, culturale, etico | L01 |
| Personalità | **spirituale** | materiale, individuale, sociale | L01 |
| Individualità | **materiale** | sociale, gnoseologica, spirituale | L01 |
| Persona (def. Boezio) | **razionale** | materialità, spiritualità, forme accidentali | L01 |
| Vita richiesta dalla persona | **politica** | individuale, culturale, socio-culturale | L01 |
| Movimento (La persona e il bene comune) | **metafisico, doppio** | sociale, semplice | L01 |

**Lessico aggettivale chiuso del corso:** materiale, spirituale, individuale, sociale, razionale,
ontologico, etico, culturale, gnoseologico, metafisico, politico.

---

## 6. Densità per paragrafo

Registrare per ogni lezione quanti item provengono da ciascun paragrafo.
Serve a prevedere dove il docente pescherà le **domande extra** della prova finale:
nei paragrafi già densi negli autovalutativi, non in quelli deserti.

| Lezione | §1 | §2 | §3 | §4 | Nota |
|---|---|---|---|---|---|
| L01 | 2 | 5 | 3 | — | paragrafo centrale il più battuto |

---

## 7. Formato dei file

### 7.1 `test/Lxx.md` — trascrizione del test

```markdown
# Lezione xx — [titolo]

## Item 1
**Domanda:** ...
- A) ...
- B) ...
- C) ...
- D) ...
**Corretta:** B
**Paragrafo:** 2 — [titolo del paragrafo come mostrato dal sistema]
**Risposta data a freddo:** D
**Asse dell'errore:** aggettivale / attribuzione / gerarchia / polarità / negazione / quantificatore / —
```

Vincoli di trascrizione: **verbatim**, refusi inclusi. Gli errori tipografici della dispensa e dei
test non vanno corretti silenziosamente: si trascrivono e si annotano. Un refuso può essere esso
stesso l'ancoraggio lessicale di R1.

### 7.2 `nodi/nodoN-*.md` — il documento concettuale

Un nodo = un blocco di lezioni, **non** una lezione. Struttura fissa a quattro livelli:

1. **L'idea in una frase** (riquadro)
2. **La spiegazione argomentata** — prosa discorsiva in movimenti numerati, ricostruzione
   logica dell'argomento, non riassunto sequenziale della dispensa
3. **Dove la dottrina tradisce** — i punti in cui la ricostruzione corretta porta fuori strada
4. **Il test del blocco** — tabella item / risposta / paragrafo + densità
5. **Lo schema** — catene, scale, griglie, gancio narrativo mnemonico
6. **Righe per i cluster** — già formattate per il copia-incolla nei file di `cluster/`
7. **Autotest** — punti da ricostruire a voce alta

Target: 10–20 pagine per nodo. **Non** 62 come il ripasso di Storia della Filosofia Moderna:
quel formato era tarato su un orale, qui è sovradimensionato.

### 7.3 `STATO.md`

Tre sezioni sole: *Fatto* / *Prossima azione* / *Questioni aperte*.
Va aggiornato alla fine di ogni sessione. È la prima cosa da leggere dopo il PROTOCOLLO.

---

## 8. Stile dei documenti prodotti

Serie consolidata, da mantenere identica per coerenza visiva:

- LaTeX, `pdflatex`, `mathpazo` (Palatino)
- colore accento `blu` = `rgb 0.12,0.23,0.37`; accento secondario `oro` = `rgb 0.54,0.43,0.11`
- ambienti `tcolorbox`: `ideabox` (idea centrale), `schemabox` (schemi), `orobox` (avvertenze)
- `longtable` + `booktabs` per le tabelle, `fancyhdr` per i running header
- `babel` con opzione `english` — il pacchetto italiano non è disponibile nell'ambiente
- indice navigabile, frontespizio con riquadro di struttura

Lingua di lavoro: **italiano**.

---

## 9. Divisione del lavoro

**Delegabile** (lavoro meccanico, verificabile *guardando*):
- trascrizione degli screenshot dei test in markdown
- estrazione del testo delle dispense da PDF a markdown pulito
- impaginazione e conversioni

**Non delegabile** (giudizio interpretativo, verificabile solo *capendo*):
- scrittura dei nodi
- individuazione dell'asse di un errore
- formulazione e revisione delle regole di decisione

Criterio: *delegare ciò che si verifica guardando, non ciò che si verifica capendo.*

---

## 10. Filosofia Morale — piano operativo

**Esame: 28/10/2026.** Inizio effettivo 26/09. 41 lezioni, 8 nodi.

| Nodo | Lezioni | Tema |
|---|---|---|
| 1 | 1 | L'ontologia della persona ✅ |
| 2 | 2–7 | Passioni, virtù, amore di dilezione |
| 3 | 8–12 | L'educazione personalista |
| 4 | 13–16 | Democrazia, pluralismo, intracultura |
| 5 | 17–21 | Diritti, doveri, giustizia (Rawls, Nagel) |
| 6 | 22–26 | Ambiente, misericordia, pace |
| 7 | 27–32 | Tecnica e bellezza (Galimberti, Severino, Vattimo) |
| 8 | 33–41 | Teoria, deontologia, etica professionale (Kohlberg) |

**Tesi architettonica del corso:** le lezioni 8–41 non sono 34 argomenti nuovi, ma l'antropologia
del nodo 1 proiettata su ambiti diversi. Studiato bene il nodo 1–2, gran parte del resto si
**deriva** invece di memorizzarsi. Scrivere i nodi facendo emergere questa derivazione.

**Videolezioni** — obbligo di fruizione ≥70%, player senza velocità aumentata.
Criterio di conteggio non documentato (pare sommare video + obiettivi + test).
→ **Azione diagnostica prioritaria:** eseguire una lezione completa e una senza video,
misurare i due delta percentuali, annotare qui il risultato.
Da vedere in ogni caso: 1–8, 13–21, 27, 28, 32–41.
Sacrificabili se il conteggio lo consente: 9–12, 22–26, 29–31 (la 30 e la 31 hanno titolo
quasi identico: probabile sovrapposizione).

**I test di autovalutazione si eseguono tutti e 41**, senza eccezione, anche per le lezioni di
cui si salta il video: contribuiscono al conteggio, alimentano il panel della prova finale e sono
l'unica fonte di allenamento discriminativo disponibile.

**Ultimi 5 giorni (22–27/10):** nessuna rilettura di dispense. Solo: rifare tutti i test,
ripassare i cluster, analizzare il registro errori per asse dominante.

---

## 11. Checklist di inizio sessione

1. Leggere `PROTOCOLLO.md` (questo file) — per intero.
2. Leggere `<insegnamento>/STATO.md`.
3. Leggere `cluster/griglia-aggettivale.md` e `registro-errori.md`.
4. Solo allora aprire dispense e test della sessione.
5. A fine sessione: aggiornare cluster, registro, densità, `STATO.md` — e committare.
