# -*- coding: utf-8 -*-
"""engagement.py — modello dati e calcoli della RP 8.5 (Piano di Stakeholder Engagement).

Contiene, in forma esplicita e verificabile:
  * il registro degli stakeholder (mappatura della Relazione tecnica SAL 1, Fig. 8.4.1,
    estesa ai livelli "interni" e "mercato" richiesti dalla scheda di attività 8.5);
  * i punteggi di Influenza e Interesse (scala 1-5) attribuiti con la rubrica di
    `RUBRICA_INFLUENZA` / `RUBRICA_INTERESSE`;
  * l'Indicatore di Rilevanza degli Stakeholder  IR = (I x Int) / 25  in [0, 1]
    (baseline di scheda 0.0) e il quadrante della matrice di rilevanza;
  * l'analisi di materialita' dei temi (problema progettuale n. 5): rilevanza per gli
    stakeholder (media pesata con IR degli interessi di gruppo) e rilevanza per il
    progetto (rubrica 1-5 ancorata al Piano di Sviluppo).

Nessun dato riservato: i punteggi sono valutazioni qualitative del gruppo di gestione
del progetto, codificate qui per renderle riproducibili e rivedibili.

Uso:  python -m src.engagement   (dalla cartella RP8.5/)  -> esporta output/*.csv
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "output")

# --------------------------------------------------------------------------------------
# Rubriche di valutazione (Tabella 2 della relazione)
# --------------------------------------------------------------------------------------
RUBRICA_INFLUENZA = {
    5: "Potere decisionale o di controllo sul progetto (concessione, verifica, governance)",
    4: "Controllo di risorse, dati o politiche necessari al progetto",
    3: "Capacità di orientare adozione, autorizzazione o diffusione dei risultati",
    2: "Influenza locale o indiretta",
    1: "Influenza marginale",
}
RUBRICA_INTERESSE = {
    5: "Destinatario diretto degli effetti o dei risultati del progetto",
    4: "Beneficiario del trasferimento e della replicabilità nel proprio settore",
    3: "Interesse istituzionale o di policy sui temi del progetto",
    2: "Interesse informativo",
    1: "Interesse marginale",
}

# Gruppi di stakeholder (livelli della scheda 8.5: interni -> associazioni -> territori
# -> clienti/utenti finali, piu' le istituzioni dell'Accordo per l'Innovazione).
GRUPPI = {
    "G1": "Istituzioni nazionali dell'Accordo",
    "G2": "Regioni e Provincia autonoma",
    "G3": "Comuni sedi operative Gresmalt",
    "G4": "Comuni sedi dei partner",
    "G5": "Associazioni di categoria",
    "G6": "Ordini professionali",
    "G7": "Stakeholder interni ai partner",
    "G8": "Clienti e utenti finali",
}


@dataclass(frozen=True)
class Stakeholder:
    sid: str
    nome: str
    gruppo: str
    livello: str          # Interno / Associativo / Territoriale / Istituzionale / Mercato
    ambito: str           # territorio o perimetro di riferimento
    influenza: int        # 1..5
    interesse: int        # 1..5
    motivazione: str      # sintesi della valutazione
    fonte_sal1: bool      # presente nella mappatura SAL 1 (Fig. 8.4.1)

    @property
    def ir(self) -> float:
        return round(self.influenza * self.interesse / 25.0, 2)

    @property
    def quadrante(self) -> str:
        hi_i, hi_t = self.influenza >= 4, self.interesse >= 4
        if hi_i and hi_t:
            return "Gestire attivamente"
        if hi_i:
            return "Mantenere soddisfatti"
        if hi_t:
            return "Mantenere informati"
        return "Monitorare"


S = Stakeholder
REGISTRO: list[Stakeholder] = [
    # --- Istituzionali nazionali ---------------------------------------------------
    S("S01", "Ministero delle Imprese e del Made in Italy (MIMIT)", "G1", "Istituzionale", "Nazionale",
      5, 4, "Amministrazione concedente; verifica SAL e risultato intermedio; interesse di policy "
            "sulla transizione digitale e sulla replicabilità.", True),
    S("S02", "Fondo per la Crescita Sostenibile (FCS)", "G1", "Istituzionale", "Nazionale",
      4, 2, "Fonte delle risorse dell'Accordo; interesse limitato alla corretta destinazione dei fondi.",
      True),
    # --- Regioni / Provincia autonoma ----------------------------------------------
    S("S03", "Regione Emilia-Romagna", "G2", "Territoriale", "Emilia-Romagna",
      4, 5, "Politiche industriali e statistiche regionali (dati I-O per 8.6); territorio del "
            "distretto ceramico e delle sedi Gresmalt e SACMI.", True),
    S("S04", "Provincia Autonoma di Bolzano", "G2", "Territoriale", "Alto Adige",
      4, 3, "Statistiche provinciali per l'analisi I-O (8.6); sede della Libera Università di Bolzano.",
      True),
    S("S05", "Regione Sardegna", "G2", "Territoriale", "Sardegna",
      4, 3, "Statistiche regionali per l'analisi I-O (8.6); sede dell'Università di Sassari.", True),
    S("S06", "Regione Calabria", "G2", "Territoriale", "Calabria",
      4, 3, "Statistiche regionali per l'analisi I-O (8.6); sede dell'Università della Calabria.", True),
    # --- Comuni sedi operative Gresmalt --------------------------------------------
    S("S07", "Comune di Sassuolo (MO)", "G3", "Territoriale", "Emilia-Romagna",
      3, 5, "Sede direzionale e unità produttiva; effetti occupazionali e ambientali diretti.", True),
    S("S08", "Comune di Fiorano Modenese (MO)", "G3", "Territoriale", "Emilia-Romagna",
      3, 5, "Unità produttiva e logistica; effetti occupazionali e ambientali diretti.", True),
    S("S09", "Comune di Scandiano (RE)", "G3", "Territoriale", "Emilia-Romagna",
      3, 5, "Unità produttiva (Iano); effetti occupazionali e ambientali diretti.", True),
    S("S10", "Comune di Viano (RE)", "G3", "Territoriale", "Emilia-Romagna",
      3, 5, "Unità produttiva; effetti occupazionali e ambientali diretti.", True),
    S("S11", "Comune di Casalgrande (RE)", "G3", "Territoriale", "Emilia-Romagna",
      3, 5, "Unità produttiva; effetti occupazionali e ambientali diretti.", True),
    # --- Comuni sedi dei partner ---------------------------------------------------
    S("S12", "Comune di Imola (BO)", "G4", "Territoriale", "Emilia-Romagna",
      2, 4, "Sede SACMI; ricadute sulla filiera dei costruttori di macchine per ceramica.", True),
    S("S13", "Comune di Bolzano", "G4", "Territoriale", "Alto Adige",
      2, 3, "Sede della Libera Università di Bolzano.", True),
    S("S14", "Comune di Brunico-Bruneck (BZ)", "G4", "Territoriale", "Alto Adige",
      2, 3, "Sede di attività della Libera Università di Bolzano.", True),
    S("S15", "Comune di Alghero (SS)", "G4", "Territoriale", "Sardegna",
      2, 3, "Sede di attività dell'Università di Sassari (Architectural Design 4.0+).", True),
    S("S16", "Comune di Sassari", "G4", "Territoriale", "Sardegna",
      2, 3, "Sede dell'Università di Sassari.", True),
    S("S17", "Comune di Rende (CS)", "G4", "Territoriale", "Calabria",
      2, 3, "Sede dell'Università della Calabria.", True),
    # --- Associazioni di categoria -------------------------------------------------
    S("S18", "Confindustria Ceramica", "G5", "Associativo", "Nazionale (distretto ceramico)",
      4, 4, "Rappresentanza del settore e dati statistici di comparto; principale canale di "
            "replicabilità dei risultati verso i produttori ceramici.", True),
    S("S19", "Acimac", "G5", "Associativo", "Nazionale",
      3, 4, "Costruttori di macchine e attrezzature per ceramica; canale di trasferimento verso "
            "la filiera tecnologica.", True),
    # --- Ordini professionali ------------------------------------------------------
    S("S20", "Ordine degli Architetti P.P.C.", "G6", "Associativo", "Sardegna",
      3, 4, "Progettisti: adozione dell'involucro a matrice ceramica e dell'Architectural Design 4.0+.",
      True),
    S("S21", "Ordine degli Ingegneri", "G6", "Associativo", "Sardegna",
      3, 4, "Progettisti e tecnici: adozione delle soluzioni costruttive e di monitoraggio.", True),
    # --- Stakeholder interni ai partner (scheda 8.5: "partendo dagli stakeholder interni") --
    S("S22", "Gresmalt — Direzione e team di progetto (CdG)", "G7", "Interno", "Partenariato",
      5, 5, "Capofila: governance del progetto, decisioni di investimento, attuazione OR 6-8.", False),
    S("S23", "SACMI — Team di progetto", "G7", "Interno", "Partenariato",
      4, 5, "Partner industriale: OR 4-5 e interfaccia tecnologica con gli impianti.", False),
    S("S24", "Università partner — Gruppi di ricerca (UNIBZ, UNICAL, UNISS)", "G7", "Interno",
      "Partenariato", 4, 4, "Responsabili scientifici degli OR 1-3; produzione di conoscenza e "
                            "pubblicazioni.", False),
    S("S25", "Personale degli stabilimenti Gresmalt", "G7", "Interno", "Emilia-Romagna",
      3, 5, "Utenti finali dei sistemi collaudati in OR 7; effetti su competenze e condizioni di "
            "lavoro.", False),
    # --- Clienti e utenti finali (scheda 8.5: "fino ai clienti/utenti finali") ---------
    S("S26", "Clienti B2B (distributori, rivenditori, grandi progetti)", "G8", "Mercato",
      "Italia ed estero", 3, 4, "Domanda di prodotti sostenibili e personalizzati; destinatari delle "
                                "nuove collezioni.", False),
    S("S27", "Utenti finali e occupanti degli edifici", "G8", "Mercato", "Italia ed estero",
      1, 3, "Beneficiari del comfort indoor e della qualità del prodotto posato.", False),
]

# --------------------------------------------------------------------------------------
# Analisi di materialita' (problema progettuale n. 5)
# --------------------------------------------------------------------------------------
# Rilevanza per il progetto (1-5) -- rubrica ancorata al Piano di Sviluppo:
#   5 = parte dell'obiettivo finale (§5) e misurata da KPI di piu' OR
#   4 = misurata da KPI di almeno un OR o risultato intermedio
#   3 = finalita' dichiarata (§4) o attivita' senza KPI quantitativo
#   2 = tema trasversale abilitante;  1 = marginale
TEMI = [
    # (codice, tema, rilevanza progetto, riferimenti al Piano)
    ("T01", "Efficienza energetica ed emissioni", 5, "Finalità §4; OR 5; KPI EEA+ (6.5, 7.3)"),
    ("T02", "Uso efficiente di materie prime e risorse naturali", 4, "Finalità §4; KPI EFA+ (6.2); OR 2"),
    ("T03", "Occupazione, competenze e condizioni di lavoro", 4, "KPI SFA+ (6.3); occupazione (8.6)"),
    ("T04", "Etica e trasparenza dell'Intelligenza Artificiale", 4, "Linee guida etiche OR 1 (risultato intermedio)"),
    ("T05", "Sicurezza dei dati e cybersecurity", 3, "Finalità §4; architettura E2C (6.6)"),
    ("T06", "Competitività e trasformazione digitale", 5, "Obiettivo finale §5; OR 1, 4, 6, 7"),
    ("T07", "Qualità e sostenibilità del prodotto", 5, "KPI P-TSI (7.4), qualità (7.5); OR 2"),
    ("T08", "Design e personalizzazione del prodotto", 4, "Finalità §4; KPI 6.9, 7.7"),
    ("T09", "Comfort abitativo e prestazioni dell'involucro", 4, "Obiettivo specifico 7 (§5); OR 3"),
    ("T10", "Ricadute economiche sui territori", 4, "Contributo innovativo OR 8; KPI 8.6"),
    ("T11", "Trasferimento tecnologico e replicabilità", 3, "Attività 8.4 e 8.5"),
    ("T12", "Nuovi modelli di business guidati dall'IA", 4, "KPI AI-BM (7.10)"),
]

# Interesse di ciascun gruppo per ciascun tema: 0 = nessuno, 1 = moderato, 2 = elevato.
INTERESSI = {
    #      T01 T02 T03 T04 T05 T06 T07 T08 T09 T10 T11 T12
    "G1": [1,  1,  1,  1,  1,  2,  0,  0,  0,  2,  2,  1],
    "G2": [2,  1,  2,  0,  0,  2,  0,  0,  0,  2,  1,  0],
    "G3": [2,  2,  2,  0,  0,  1,  0,  0,  0,  2,  1,  0],
    "G4": [0,  0,  1,  0,  0,  0,  0,  0,  1,  1,  1,  0],
    "G5": [2,  1,  1,  0,  1,  2,  2,  1,  0,  1,  2,  2],
    "G6": [1,  1,  0,  0,  0,  0,  2,  2,  2,  0,  1,  0],
    "G7": [1,  1,  2,  2,  2,  2,  1,  1,  0,  0,  1,  1],
    "G8": [1,  1,  0,  0,  0,  0,  2,  2,  2,  0,  0,  0],
}


def peso_gruppi() -> dict[str, float]:
    """Peso di ciascun gruppo = IR medio dei suoi membri."""
    out = {}
    for g in GRUPPI:
        vals = [s.ir for s in REGISTRO if s.gruppo == g]
        out[g] = sum(vals) / len(vals)
    return out


def materialita() -> list[dict]:
    w = peso_gruppi()
    tot = sum(w.values())
    rows = []
    for j, (cod, tema, ril_prog, rif) in enumerate(TEMI):
        x = sum(w[g] * INTERESSI[g][j] for g in GRUPPI) / (2.0 * tot)
        x5 = 1 + 4 * x   # riportata su scala 1-5 per confronto con l'asse progetto
        prior = "Prioritario" if (x5 >= 3.0 and ril_prog >= 4) else (
            "Rilevante" if (x5 >= 3.0 or ril_prog >= 4) else "Da monitorare")
        rows.append({"codice": cod, "tema": tema, "ril_stakeholder": round(x5, 2),
                     "ril_progetto": ril_prog, "classe": prior, "riferimenti": rif})
    return rows


def sintesi() -> dict:
    n = len(REGISTRO)
    quad = {}
    for s in REGISTRO:
        quad[s.quadrante] = quad.get(s.quadrante, 0) + 1
    return {
        "n_stakeholder": n,
        "n_sal1": sum(1 for s in REGISTRO if s.fonte_sal1),
        "ir_medio": round(sum(s.ir for s in REGISTRO) / n, 2),
        "quadranti": quad,
        "n_temi": len(TEMI),
        "n_prioritari": sum(1 for r in materialita() if r["classe"] == "Prioritario"),
    }


def export_csv() -> None:
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "registro_stakeholder.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(["id", "stakeholder", "gruppo", "livello", "ambito", "influenza", "interesse",
                     "IR", "quadrante", "mappatura_SAL1", "motivazione"])
        for s in REGISTRO:
            wr.writerow([s.sid, s.nome, GRUPPI[s.gruppo], s.livello, s.ambito, s.influenza,
                         s.interesse, f"{s.ir:.2f}".replace(".", ","), s.quadrante,
                         "si" if s.fonte_sal1 else "no", s.motivazione])
    with open(os.path.join(OUT, "materialita_temi.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f, delimiter=";")
        wr.writerow(["codice", "tema", "rilevanza_stakeholder_1_5", "rilevanza_progetto_1_5",
                     "classe", "riferimenti_piano"])
        for r in materialita():
            wr.writerow([r["codice"], r["tema"], f"{r['ril_stakeholder']:.2f}".replace(".", ","),
                         r["ril_progetto"], r["classe"], r["riferimenti"]])


if __name__ == "__main__":
    export_csv()
    print(sintesi())
    for r in materialita():
        print(r)
