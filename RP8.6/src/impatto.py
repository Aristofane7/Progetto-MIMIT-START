"""Assessment dell'impatto di START — SIMULAZIONE input-output di Leontief — RP 8.6.

Attivita 8.6 dell'OR 8, svolta in collaborazione con le Universita del partenariato
(Libera Universita di Bolzano, Universita della Calabria, Universita di Sassari). In
assenza dei dati macroeconomici regionali (problema progettuale n. 6), l'attivita assume
la forma di una SIMULAZIONE dell'impatto potenziale e, soprattutto, della predisposizione
e validazione del MODELLO ANALITICO (input-output di Leontief) da applicare ex-post — nei
mesi e negli anni successivi alla chiusura del progetto — quando saranno disponibili i
consuntivi degli investimenti e le tavole input-output regionali ISTAT. Il modello stima
l'impatto diretto, indiretto e indotto dei risultati del progetto sui territori dove
operano le attivita industriali e di ricerca (Emilia-Romagna, Provincia di Bolzano,
Sardegna, Calabria), sul modello econometrico di Wassily Leontief. La simulazione con
valori rappresentativi ne dimostra l'operativita e l'ordine di grandezza degli effetti
attesi; e' pronta a essere ri-eseguita con i dati ufficiali (logica di "analisi degli
scostamenti" dell'OR 8).

Metodo. Data la matrice dei coefficienti tecnici A (acquisti intersettoriali per unita
di produzione), la matrice inversa di Leontief L = (I - A)^-1 traduce una variazione
della domanda finale df in variazione della produzione totale dx = L @ df, catturando
gli effetti a cascata lungo la filiera. Si calcolano:
  - moltiplicatori di produzione di Tipo I (somma per colonna di L, modello aperto);
  - moltiplicatori di Tipo II (modello chiuso rispetto ai consumi delle famiglie, che
    aggiunge l'effetto indotto dal reddito);
  - impatto su valore aggiunto (contributo al PIL) e occupazione (ULA) tramite i
    rispettivi coefficienti settoriali.
L'impatto e scomposto in diretto (df), indiretto (filiera) e indotto (consumi).

NOTA sui dati (problema progettuale n. 6). Le tavole input-output regionali e i dati
macroeconomici su scala regionale non sono direttamente disponibili al Team di progetto:
in accordo con il Piano di Stakeholder Engagement (RP 8.5) le autorita territoriali
saranno coinvolte per accedere alle informazioni necessarie (ISTAT, tavole SUT/IO
regionali). I coefficienti qui usati sono RAPPRESENTATIVI, calibrati sull'ordine di
grandezza della filiera ceramica, e vanno consolidati con le tavole ufficiali.

La struttura del modello (settori, matrice A, coefficienti di valore aggiunto e
occupazione) e' quella della filiera ceramica: coincide con quella impiegata per il
progetto gemello VOLT (RP 9.6), perche' i due progetti insistono sulla stessa industria
e sullo stesso distretto produttivo. Cio' che cambia e' la RIPARTIZIONE REGIONALE dello
shock di domanda finale (FINAL_DEMAND), differenziata sui quattro territori di START
secondo il ruolo dei rispettivi soggetti attuatori.
"""

from __future__ import annotations

import numpy as np

# --- Settori del modello (filiera ceramica e indotto territoriale) ----------------
SECTORS = [
    "Estrazione minerali non metalliferi",   # argille, feldspati, sabbie
    "Fabbricazione prodotti ceramici",       # piastrelle (core del distretto)
    "Chimica (smalti, additivi, chemicals)",
    "Trasporti e logistica",
    "Energia (gas, elettricita)",
    "Servizi (ICT, R&S, professionali)",     # AI, digital twin, progettazione
]
N = len(SECTORS)

# Matrice dei coefficienti tecnici A[i, j] = input dal settore i per 1 EUR di output j.
# Rappresentativa della struttura di costo della filiera ceramica (le colonne, cioe
# la somma dei consumi intermedi per settore, restano < 1: il resto e valore aggiunto).
A = np.array([
    # min    cer    chim   trasp  ener   serv    <- verso settore j
    [0.02,  0.11,  0.04,  0.01,  0.00,  0.00],   # da Estrazione minerali
    [0.00,  0.06,  0.01,  0.00,  0.00,  0.00],   # da Ceramica
    [0.01,  0.09,  0.05,  0.00,  0.00,  0.01],   # da Chimica
    [0.06,  0.08,  0.05,  0.07,  0.02,  0.03],   # da Trasporti e logistica
    [0.10,  0.14,  0.09,  0.04,  0.06,  0.02],   # da Energia
    [0.05,  0.10,  0.08,  0.06,  0.05,  0.12],   # da Servizi
])

# Coefficienti di valore aggiunto (quota di VA sull'output per settore).
VA_COEFF = np.array([0.55, 0.35, 0.45, 0.50, 0.40, 0.65])
# Quota del valore aggiunto distribuita come reddito da lavoro (per chiusura Tipo II).
WAGE_SHARE = np.array([0.45, 0.55, 0.45, 0.55, 0.30, 0.60])
# Propensione media al consumo delle famiglie sul reddito.
CONSUMO_PROPENSIONE = 0.80
# Ripartizione dei consumi delle famiglie sui settori del modello (quota che ricade
# sui settori qui rappresentati; il resto e importato/altri settori).
CONSUMO_MIX = np.array([0.00, 0.05, 0.03, 0.10, 0.12, 0.30])
# Coefficienti di occupazione: ULA (unita di lavoro) per milione di EUR di output.
EMP_COEFF = np.array([4.5, 5.0, 3.8, 6.0, 1.5, 7.0])

# --- Shock di domanda finale attivato dal progetto START (M EUR/anno a regime) -----
# Rappresentativo: investimenti + produzione addizionale abilitata dalla transizione
# Smart Factory -> Intelligent Factory -> Intelligent Industry guidata dall'AI (KET di
# START), dalle 4 impronte/EEA+, dall'architettura Edge-to-Cloud e dal data-driven
# product design. Differenziato per regione secondo il ruolo del soggetto attuatore e
# la localizzazione delle attivita industriali e di ricerca:
#   Emilia-Romagna: cuore del distretto ceramico (Gresmalt capofila e SACMI) ->
#     shock concentrato su ceramica, estrazione, chimica, logistica ed energia.
#   Provincia di Bolzano: Libera Universita di Bolzano (OR1, concetto globale di Digital
#     Twin, AI etica/biointelligente, ontologie) -> ricerca, ICT/R&S, servizi.
#   Sardegna: Universita di Sassari (OR3, Architectural Design 4.0+, involucro edilizio
#     ceramico ventilato con IoT) -> servizi/progettazione, applicazione del prodotto
#     ceramico, logistica.
#   Calabria: Universita della Calabria (OR2, modelli ML/ANN e diagnostica non
#     distruttiva della qualita) -> ricerca, ICT/R&S, strumentazione (servizi/chimica).
FINAL_DEMAND = {
    "Emilia-Romagna":       np.array([6.0, 22.0, 5.0, 4.0, 1.5, 3.5]),
    "Provincia di Bolzano": np.array([0.3,  1.0, 1.0, 1.0, 0.7, 5.0]),
    "Sardegna":             np.array([0.4,  2.5, 0.8, 1.2, 0.6, 3.5]),
    "Calabria":             np.array([0.3,  1.2, 0.9, 0.9, 0.6, 4.1]),
}


def leontief_inverse(a: np.ndarray) -> np.ndarray:
    """Matrice inversa di Leontief L = (I - A)^-1."""
    return np.linalg.inv(np.eye(a.shape[0]) - a)


def _closed_matrix() -> np.ndarray:
    """Estende A con una riga/colonna 'famiglie' per il modello di Tipo II.

    Colonna famiglie = consumi per unita di reddito; riga famiglie = reddito da lavoro
    generato per unita di output settoriale.
    """
    ac = np.zeros((N + 1, N + 1))
    ac[:N, :N] = A
    # colonna consumi delle famiglie (domanda di consumo per unita di reddito)
    ac[:N, N] = CONSUMO_PROPENSIONE * CONSUMO_MIX
    # riga reddito da lavoro (VA * quota salari) per unita di output
    ac[N, :N] = VA_COEFF * WAGE_SHARE
    return ac


def multipliers() -> dict:
    """Moltiplicatori di produzione di Tipo I (aperto) e Tipo II (chiuso)."""
    L = leontief_inverse(A)
    type1 = L.sum(axis=0)                      # somma per colonna
    Lc = leontief_inverse(_closed_matrix())
    type2 = Lc[:N, :N].sum(axis=0)             # esclude la riga famiglie dal conteggio
    return {"L": L, "Lc": Lc, "tipo1": type1, "tipo2": type2}


def impact(region: str) -> dict:
    """Impatto del progetto su una regione: output, valore aggiunto, occupazione.

    Scompone in diretto (domanda finale), indiretto (filiera, Tipo I) e indotto
    (consumi delle famiglie, differenza Tipo II - Tipo I).
    """
    df = FINAL_DEMAND[region]
    m = multipliers()
    L, Lc = m["L"], m["Lc"]

    # produzione attivata
    dx_direct = df.copy()
    dx_type1 = L @ df                                   # diretto + indiretto
    dx_indirect = dx_type1 - dx_direct
    # modello chiuso: propaga anche i consumi indotti
    dfc = np.concatenate([df, [0.0]])
    dxc = Lc @ dfc
    dx_type2 = dxc[:N]
    dx_induced = dx_type2 - dx_type1

    def va(vec):
        return float((VA_COEFF * vec).sum())

    def emp(vec):
        return float((EMP_COEFF * vec).sum())          # ULA (output in M EUR)

    return {
        "regione": region,
        "output_diretto": float(dx_direct.sum()),
        "output_indiretto": float(dx_indirect.sum()),
        "output_indotto": float(dx_induced.sum()),
        "output_totale": float(dx_type2.sum()),
        "va_diretto": va(dx_direct),
        "va_indiretto": va(dx_indirect),
        "va_indotto": va(dx_induced),
        "va_totale": va(dx_type2),
        "occ_diretta": emp(dx_direct),
        "occ_indiretta": emp(dx_indirect),
        "occ_indotta": emp(dx_induced),
        "occ_totale": emp(dx_type2),
        "moltiplicatore_output": round(float(dx_type2.sum() / dx_direct.sum()), 2),
        "dx_settori_totale": dx_type2,
    }


def kpi_check() -> list[dict]:
    """KPI di scheda: matrice / analisi input-output effettuata (baseline assente).

    Il KPI e' soddisfatto costruendo ed ESEGUENDO IN SIMULAZIONE il modello (lo strumento
    e' il deliverable), pronto per l'applicazione ex-post con i dati regionali ufficiali.
    """
    regs = list(FINAL_DEMAND)
    return [
        {"kpi": "Matrice / modello input-output (Leontief) impostato", "baseline": 0, "obiettivo": 1, "valore": 1,
         "dettaglio": f"modello a {N} settori, inversa di Leontief e moltiplicatori Tipo I/II"},
        {"kpi": "Analisi input-output eseguita in simulazione", "baseline": 0, "obiettivo": 1, "valore": 1,
         "dettaglio": f"simulazione applicata a {len(regs)} regioni ({', '.join(regs)})"},
        {"kpi": "Protocollo di applicazione ex-post", "baseline": 0, "obiettivo": 1, "valore": 1,
         "dettaglio": "dati ISTAT + consuntivi via RP 8.5; confronto previsione/consuntivo (scostamenti)"},
    ]


def summary() -> dict:
    imps = {r: impact(r) for r in FINAL_DEMAND}
    tot_out = sum(i["output_totale"] for i in imps.values())
    tot_va = sum(i["va_totale"] for i in imps.values())
    tot_emp = sum(i["occ_totale"] for i in imps.values())
    tot_dir = sum(i["output_diretto"] for i in imps.values())
    return {
        "settori": N, "regioni": list(FINAL_DEMAND),
        "output_diretto_totale": round(tot_dir, 1),
        "output_attivato_totale": round(tot_out, 1),
        "valore_aggiunto_totale": round(tot_va, 1),
        "occupazione_ula_totale": round(tot_emp, 0),
        "moltiplicatore_medio": round(tot_out / tot_dir, 2),
    }


if __name__ == "__main__":
    print("RP 8.6 — Simulazione dell'impatto di START (modello input-output di Leontief)\n")
    m = multipliers()
    print("Moltiplicatori di produzione per settore (Tipo I / Tipo II):")
    for j, s in enumerate(SECTORS):
        print(f"  {s:42s} {m['tipo1'][j]:.2f} / {m['tipo2'][j]:.2f}")
    print()
    for r in FINAL_DEMAND:
        i = impact(r)
        print(f"[{r}] moltiplicatore output {i['moltiplicatore_output']}")
        print(f"  Output (M EUR):   diretto {i['output_diretto']:.1f}  indiretto {i['output_indiretto']:.1f}  "
              f"indotto {i['output_indotto']:.1f}  -> totale {i['output_totale']:.1f}")
        print(f"  Valore aggiunto:  totale {i['va_totale']:.1f} M EUR")
        print(f"  Occupazione:      totale {i['occ_totale']:.0f} ULA\n")
    print("Sintesi:", summary())
