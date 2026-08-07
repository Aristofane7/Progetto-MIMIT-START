"""Modello di Business guidato dall'Intelligenza Artificiale (AI-BM) — RP 7.10.

Ultima attivita dell'OR 7: definisce e propone un nuovo modello di business guidato
dalla AI (AI-BM) che colga le potenzialita della Intelligent Industry per creare e
catturare valore, superando il modello di business tradizionale (baseline).

Il KPI qualitativo della scheda e il Business Model Canvas (BMC): la baseline e il
Modello di Business tradizionale, l'obiettivo e l'AI-BM. Il modello e sviluppato in
doppia versione as-is (tradizionale) / to-be (AI-BM) e validato con un impianto di
analisi strategica composto da: catena dato -> informazione -> valore, matrice SWOT
e transition model (da logiche asset-based/episodiche a sistemi adattivi data-driven).

Riferimento teorico: Bouncken & Cesinger (2026), "Embodied Artificial Intelligence (AI)
business model dynamics: concept, framework, and the agriculture template", Review of
Managerial Science. La "Intelligent Industry" ceramica e un caso di *embodied AI*
(intelligenza incorporata negli impianti, nei sensori e nell'involucro edilizio smart)
in cui la AI passa da supporto decisionale a elemento costitutivo del valore.

Il modello sintetizza i risultati validati nei collaudi dell'OR 7 (RP 7.1-7.9).

NOTA (problema progettuale n. 10): il BM design richiede competenze specialistiche non
presenti nel Team di Progetto; l'attivita si avvale di consulenza specializzata di
esperti in BM design. I dati quantitativi non omogenei multi-fonte sono trattati come
informazione strutturata all'interno del canvas e dell'analisi strategica.
"""

from __future__ import annotations

# --- Business Model Canvas: as-is (tradizionale) -> to-be (AI-BM) -----------------
# Ogni blocco riporta la configurazione tradizionale (baseline), quella AI-BM
# (obiettivo) e la fonte / il driver AI derivante dai collaudi dell'OR 7.
BMC_BLOCKS = [
    {
        "id": 1, "blocco": "Segmenti di clientela",
        "asis": "Distributori, rivenditori e imprese edili serviti con piastrelle a catalogo.",
        "tobe": "Progettisti e clienti finali serviti con prodotti personalizzati e smart "
                "materials; segmenti guidati dai dati d'uso in opera e da servizi lifecycle.",
        "asis_key": "Distributori, rivenditori, imprese edili",
        "tobe_key": "Progettisti e clienti finali; segmenti guidati dai dati d'uso e "
                    "da servizi lifecycle",
        "driver": "Involucro sensorizzato (RP7.9); data-driven design (RP7.7)",
    },
    {
        "id": 2, "blocco": "Proposta di valore",
        "asis": "Qualita del prodotto, estetica e conformita tecnica (ISO 10545), prezzo.",
        "tobe": "Prodotto-come-servizio con performance monitorate (comfort indoor, profilo "
                "ambientale), personalizzazione agile, sostenibilita certificata data-driven, "
                "qualita predittiva.",
        "asis_key": "Qualita, estetica, conformita tecnica, prezzo",
        "tobe_key": "Prodotto-servizio; performance monitorate; personalizzazione agile; "
                    "sostenibilita certificata; qualita predittiva",
        "driver": "P-TSA (RP7.4); DDQM (RP7.5); assessment sostenibilita (OR6, RP7.3)",
    },
    {
        "id": 3, "blocco": "Canali",
        "asis": "Rete commerciale, showroom e cataloghi cartacei/statici.",
        "tobe": "Piattaforma edge-to-cloud (E2C) e servizi digitali, configuratori AI, "
                "canali attivati dai dati d'uso in opera.",
        "asis_key": "Rete commerciale, showroom, cataloghi",
        "tobe_key": "Piattaforma E2C, configuratori AI, dati d'uso",
        "driver": "Piattaforma E2C (RP7.1); Intelligent Factory (RP7.2)",
    },
    {
        "id": 4, "blocco": "Relazioni con i clienti",
        "asis": "Relazione transazionale ordine-consegna, assistenza post-vendita reattiva.",
        "tobe": "Relazioni continuative con feedback loop (embodied AI), co-design e servizi "
                "di monitoraggio ricorrenti; fiducia come asset relazionale.",
        "asis_key": "Transazionale ordine-consegna",
        "tobe_key": "Continuative, feedback loop, co-design, monitoraggio ricorrente",
        "driver": "Doppio loop di apprendimento (Bouncken & Cesinger 2026); RP7.8",
    },
    {
        "id": 5, "blocco": "Flussi di ricavi",
        "asis": "Vendita una tantum del prodotto (logica episodica, asset-based).",
        "tobe": "Ricavi ricorrenti basati sulla fiducia (lifecycle-based orchestration), "
                "servizi a valore aggiunto (sostenibilita, monitoraggio), premium per "
                "personalizzazione.",
        "asis_key": "Vendita una tantum (logica episodica)",
        "tobe_key": "Ricavi ricorrenti trust-based; servizi a valore aggiunto; premium "
                    "personalizzazione",
        "driver": "Monetizzazione ricorrente trust-based (Bouncken & Cesinger 2026)",
    },
    {
        "id": 6, "blocco": "Risorse chiave",
        "asis": "Impianti produttivi, know-how di processo, materie prime.",
        "tobe": "Dati multi-fonte, algoritmi e librerie AI, Intelligent Factory e "
                "architettura E2C, gemello digitale, competenze di data science, involucro "
                "ceramico sensorizzato.",
        "asis_key": "Impianti, know-how, materie prime",
        "tobe_key": "Dati, algoritmi AI, Intelligent Factory, E2C, gemello digitale, "
                    "competenze",
        "driver": "E2C (RP7.1); Intelligent Factory (RP7.2); Intelligent Industry (RP7.8)",
    },
    {
        "id": 7, "blocco": "Attivita chiave",
        "asis": "Produzione, controllo qualita statistico a campione, logistica.",
        "tobe": "Analisi dei dati in tempo reale, qualita predittiva (DDQM), data-driven "
                "product design, assessment di sostenibilita, orchestrazione del workflow "
                "(sensing -> decision -> actuation -> learning).",
        "asis_key": "Produzione, QC statistico, logistica",
        "tobe_key": "Analisi dati real-time, qualita predittiva, design data-driven, "
                    "orchestrazione workflow",
        "driver": "DDQM (RP7.5); data-driven design (RP7.7); assessment (RP7.3, RP7.4)",
    },
    {
        "id": 8, "blocco": "Partnership chiave",
        "asis": "Fornitori di materie prime, rete di distributori.",
        "tobe": "Ecosistema esteso: fornitori di tecnologia e componenti, software house, "
                "orchestratori di piattaforma, partner di ricerca dell'OR e clienti come "
                "co-produttori di dati (external learning loop).",
        "asis_key": "Fornitori materie prime, distributori",
        "tobe_key": "Ecosistema: tech provider, software house, orchestratori di "
                    "piattaforma, clienti co-produttori di dati",
        "driver": "Ecosistema di embodied AI (Bouncken & Cesinger 2026); partner OR1-OR5",
    },
    {
        "id": 9, "blocco": "Struttura dei costi",
        "asis": "Costi di produzione, materie prime ed energia (economie di scala).",
        "tobe": "Costi di piattaforma e IT, data governance, competenze specialistiche; "
                "spostamento verso sviluppo software/dati (economie di apprendimento e di "
                "scopo).",
        "asis_key": "Produzione, materie prime, energia (scala)",
        "tobe_key": "Piattaforma e IT, data governance, competenze (economie di "
                    "apprendimento e scopo)",
        "driver": "Consulenza BM design (problema n. 10); piattaforma E2C (RP7.1)",
    },
]

# --- Catena dato -> informazione -> valore (motore dell'AI-BM) --------------------
# Risponde allo scopo della scheda: trasformare i dati in informazioni e le
# informazioni in valore, sfruttando la Intelligent Industry.
DATA_VALUE_CHAIN = [
    {
        "stadio": "Dato",
        "contenuto": "Dati storici multi-fonte delle linee di produzione, dati dei sensori "
                     "dell'involucro edilizio (indoor/outdoor), dati di processo e prodotto.",
        "fonte": "E2C (RP7.1), Intelligent Factory (RP7.2), involucro smart (RP7.9)",
    },
    {
        "stadio": "Informazione",
        "contenuto": "Algoritmi AI (affidabilita > 75%) che producono qualita predittiva, "
                     "indicatori di sostenibilita (footprint OR6) e P-TSA di prodotto.",
        "fonte": "DDQM (RP7.5), P-TSA (RP7.4), assessment termodinamico (RP7.3)",
    },
    {
        "stadio": "Valore",
        "contenuto": "Proposte di valore dell'AI-BM: personalizzazione agile, sostenibilita "
                     "certificata, prodotto-servizio con performance monitorate, ricavi "
                     "ricorrenti basati sulla fiducia.",
        "fonte": "AI-BM (RP7.10), sintesi OR7 (RP7.8)",
    },
]

# --- Transition model: da asset-based/episodico a adattivo/data-driven ------------
# Dimensioni del passaggio (Bouncken & Cesinger 2026, transition model).
TRANSITION = [
    {"dimensione": "Logica del valore", "da": "Asset-based (prodotto)",
     "a": "Data-driven (sistema adattivo)"},
    {"dimensione": "Temporalita", "da": "Episodica (vendita una tantum)",
     "a": "Continua (ottimizzazione del workflow)"},
    {"dimensione": "Ruolo della AI", "da": "Supporto decisionale",
     "a": "Elemento costitutivo del valore"},
    {"dimensione": "Orchestrazione", "da": "Centrata sul prodotto",
     "a": "Lifecycle ed ecosistema"},
    {"dimensione": "Monetizzazione", "da": "Transazionale",
     "a": "Ricorrente basata sulla fiducia"},
    {"dimensione": "Apprendimento", "da": "Assente / manuale",
     "a": "Doppio loop (interno + ecosistema)"},
]

# --- Quattro tensioni sistemiche dell'embodied AI-BM ------------------------------
TENSIONS = [
    "Apertura vs controllo (i dati d'uso viaggiano oltre l'impresa)",
    "Scala vs adattamento locale (standard di piattaforma vs specificita di prodotto)",
    "Ambizione di automazione vs vincoli di affidabilita",
    "Monetizzazione vs fiducia (servizi ricorrenti sostenibili nel tempo)",
]

# --- Analisi SWOT dell'AI-BM ------------------------------------------------------
SWOT = {
    "Forze": [
        "Intelligent Factory e piattaforma E2C operative (RP7.1, RP7.2)",
        "Qualita predittiva via Data-Driven Quality Management (RP7.5)",
        "Sostenibilita certificata e data-driven (OR6, P-TSA RP7.4)",
        "Capacita di personalizzazione agile e smart materials sensorizzati (RP7.7, RP7.9)",
    ],
    "Debolezze": [
        "Competenze di BM design e data science non presenti nel team (problema n. 10)",
        "Dati quantitativi non omogenei da fonti diverse",
        "Cambiamento organizzativo e culturale richiesto ai reparti",
        "Costi di piattaforma e di data governance da ammortizzare",
    ],
    "Opportunita": [
        "Domanda di mercato per prodotti green e personalizzati",
        "Servitizzazione e ricavi ricorrenti (prodotto-come-servizio)",
        "Coerenza con gli Accordi per l'Innovazione (MIMIT) e requisiti ESG/CBAM",
        "Replicabilita del modello al distretto ceramico",
    ],
    "Minacce": [
        "Maturita digitale non uniforme di clienti e canali",
        "Rischi di cybersecurity sui dati d'uso e di processo",
        "Dipendenza da fornitori tecnologici e orchestratori di piattaforma",
        "Volatilita dei costi di energia e materie prime; evoluzione normativa",
    ],
}


def kpi_check() -> list[dict]:
    """KPI qualitativo della scheda: il Business Model Canvas (AI-BM) prodotto.

    Baseline 0 = Modello di Business tradizionale; obiettivo 1 = AI-BM.
    L'esito e riconosciuto quando tutti i 9 blocchi del canvas sono riconfigurati
    dalla versione tradizionale (as-is) a quella AI-BM (to-be).
    """
    blocchi_riconfigurati = sum(1 for b in BMC_BLOCKS if b["tobe"])
    return [
        {
            "kpi": "Business Model Canvas (AI-BM)",
            "baseline": "Modello di Business tradizionale",
            "obiettivo": "AI-BM",
            "blocchi_riconfigurati": blocchi_riconfigurati,
            "blocchi_totali": len(BMC_BLOCKS),
            "prodotto": int(blocchi_riconfigurati == len(BMC_BLOCKS)),
        }
    ]


def bmc_rows() -> list[dict]:
    """Righe del Business Model Canvas per l'export tabellare."""
    return [
        {"id": b["id"], "blocco": b["blocco"], "as_is_tradizionale": b["asis"],
         "to_be_ai_bm": b["tobe"], "driver_ai_or7": b["driver"]}
        for b in BMC_BLOCKS
    ]


if __name__ == "__main__":
    print("RP 7.10 — Modello di Business guidato dall'Intelligenza Artificiale (AI-BM)\n")
    print("Business Model Canvas (as-is tradizionale -> to-be AI-BM):")
    for b in BMC_BLOCKS:
        print(f"  [{b['id']}] {b['blocco']}")
        print(f"      as-is:  {b['asis']}")
        print(f"      to-be:  {b['tobe']}")
    r = kpi_check()[0]
    print(f"\nVerifica KPI: {r['kpi']} — baseline '{r['baseline']}' -> obiettivo "
          f"'{r['obiettivo']}' (blocchi riconfigurati {r['blocchi_riconfigurati']}/"
          f"{r['blocchi_totali']}, prodotto: {'SI' if r['prodotto'] else 'no'})")
    print("\nCatena dato -> informazione -> valore:")
    for s in DATA_VALUE_CHAIN:
        print(f"  {s['stadio']}: {s['contenuto']}  [{s['fonte']}]")
    print("\nSWOT:")
    for k, v in SWOT.items():
        print(f"  {k}: {len(v)} voci")
    print("\nTensioni sistemiche:")
    for t in TENSIONS:
        print(f"  - {t}")
