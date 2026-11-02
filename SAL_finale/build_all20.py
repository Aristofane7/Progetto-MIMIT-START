# -*- coding: utf-8 -*-
"""build_all20.py — Allegato 20 (relazione finale di progetto) START, parte Gresmalt.

Impostazione (modello: relazione finale del progetto VOLT, parte Gresmalt):
  * base = modello ufficiale All. 20 (`fonti/API-2022_ALL20_modello.docx`), compilato nei
    dati identificativi con i dati delle relazioni di SAL;
  * §3 Obiettivi e §4 Attività: OR 1-5 (altri partner) a segnaposto «Inserire»; OR 6-8
    (Gresmalt) redatti da `md/all20/`, con riassunto cumulativo di tutte le attività;
  * §5 costi, §6 effetti e §8 valutazione critica lasciati da compilare, come nel modello VOLT.

Uso:  python SAL_finale/build_all20.py
"""
from __future__ import annotations

import copy
import os
import re

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

import build_all16 as b16
from build_all16 import Builder, _rpr

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = os.path.join(HERE, "fonti", "API-2022_ALL20_modello.docx")
MD20 = os.path.join(HERE, "md", "all20")
OUT = os.path.join(HERE, "START_ALL20_Relazione_finale_Gresmalt.docx")

SOGGETTI = ["GRUPPO CERAMICHE GRESMALT S.P.A. (capofila)",
            "SACMI COOPERATIVA MECCANICI IMOLA SOCIETA' COOPERATIVA",
            "UNIVERSITÀ DEGLI STUDI DI SASSARI", "UNIVERSITÀ DELLA CALABRIA",
            "LIBERA UNIVERSITA' DI BOLZANO"]
SEDI = [
    ("GRUPPO CERAMICHE GRESMALT S.P.A.", [
        "Via Mazzalasino 39, Scandiano Fraz. Iano (RE), CAP 42019, Emilia-Romagna",
        "Via Feleghetti 26, Viano (RE), CAP 42030, Emilia-Romagna",
        "Via Regina Pacis 136, Sassuolo (MO), CAP 41049, Emilia-Romagna",
        "Via Ghiarola Nuova 162, Fiorano Modenese (MO), CAP 41042, Emilia-Romagna",
        "Via Canale 302, Casalgrande (RE), CAP 42013, Emilia-Romagna"]),
    ("SACMI COOPERATIVA MECCANICI IMOLA SOCIETA' COOPERATIVA", [
        "Via Selice Provinciale, 17/A, Imola (BO), CAP 40026, Emilia-Romagna"]),
    ("UNIVERSITÀ DEGLI STUDI DI SASSARI", [
        "Piazza Duomo, 6, Alghero (SS), CAP 07041, Sardegna",
        "DSMCF - Viale San Pietro, Sassari (SS), CAP 07100, Sardegna",
        "Via Roma 1, Sassari (SS), CAP 07100, Sardegna",
        "DSB - Viale San Pietro, Sassari (SS), CAP 07100, Sardegna"]),
    ("UNIVERSITÀ DELLA CALABRIA", ["Via Pietro Bucci 12B e cubo 41D, Rende (CS), CAP 87036, Calabria"]),
    ("LIBERA UNIVERSITA' DI BOLZANO", [
        "Piazza Università 5, Bolzano (BZ), CAP 39100, Provincia Autonoma di Bolzano",
        "Via Rosmini 7, Bolzano (BZ), CAP 39100, Provincia Autonoma di Bolzano"]),
]
SIGLA = {"Ricerca Industriale": "RI", "Sviluppo Sperimentale": "SS"}
PROP_DOC = {"1": "Libera Università di Bolzano", "2": "Università della Calabria",
            "3": "Università degli Studi di Sassari", "4": "SACMI", "5": "SACMI"}


class All20(Builder):
    def __init__(self):            # noqa: D401 - sostituisce l'init della base SAL 2
        self.doc = Document(MODEL)
        d = self.doc
        self.t_sino = {}
        for t in d.tables:
            first = t.rows[0].cells[0].text.strip()
            if len(t.columns) == 3:
                self.t_sino[first[:30]] = copy.deepcopy(t._tbl)
            elif len(t.rows) > 1 and "ATTIVITA' DI RICERCA" in t.rows[1].cells[0].text:
                self.t_costi = copy.deepcopy(t._tbl)
        P = d.paragraphs
        for p, name in zip(P[13:18], SOGGETTI):
            self._set_text(p, name)
        self._multiline(P[21], ["Data sottoscrizione Accordo per l'innovazione: 14/12/2022",
                                "Amministrazione sottoscrittrice: Ministero delle Imprese e del Made in Italy",
                                "Denominazione progetto: START - SusTainable dAta-dRiven manufacTuring"])
        self._set_text(P[22], "Decreto n. 0001020 del 30/03/2023, con il quale sono state concesse le "
                              "agevolazioni a valere sulle risorse rese disponibili con decreto del Ministro "
                              "delle Imprese e del Made in Italy 31 dicembre 2021.")
        self._set_text(P[23], "Data di inizio 01/05/2023 e fine 31/10/2026 del progetto")
        self._multiline(P[24], ["Responsabile del progetto: Davide Settembre Blundo",
                                "Sedi di svolgimento del progetto:"])
        anchor = P[25]
        for ente, vie in SEDI:
            q = anchor.insert_paragraph_before(style="Normal")
            _rpr(q.add_run(ente), size=10, bold=True)
            for v in vie:
                q = anchor.insert_paragraph_before(style="Normal")
                q.paragraph_format.left_indent = Pt(14)
                _rpr(q.add_run(v), size=10)
        # prototipo dei titoli di sezione numerati e svuotamento del corpo da «3. OBIETTIVI»
        sec = next(p for p in d.paragraphs if p.text.startswith("3.\tOBIETTIVI"))
        self.sec_proto = copy.deepcopy(sec._p)
        body = d.element.body
        kill = False
        for el in list(body.iterchildren()):
            if el is sec._p:
                kill = True
            if kill and el.tag != qn("w:sectPr"):
                body.remove(el)
        self.sect = body.find(qn("w:sectPr"))

    def _multiline(self, p, lines):
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        self._set_text(p, lines[0])
        r0 = p.runs[0]
        for ln in lines[1:]:
            r = p.add_run()
            r._r.append(copy.deepcopy(r0._r.find(qn("w:rPr")))) if r0._r.find(qn("w:rPr")) is not None else None
            r.add_break()
            r.add_text(ln)

    def section(self, text):
        el = copy.deepcopy(self.sec_proto)
        ts = list(el.iter(qn("w:t")))
        ts[0].text = text
        for t in ts[1:]:
            t.text = ""
        self._append(el)
        sp = self.p("Body Text")
        sp.paragraph_format.space_after = Pt(0)

    def or_line(self, n, title, tipo, prop):
        par = self.p("Normal")
        par.paragraph_format.space_before = Pt(12)
        par.paragraph_format.keep_with_next = True
        _rpr(par.add_run(f"OR {n} – {title} – {SIGLA[tipo]} - {prop}"), size=11, bold=True)

    def insert(self, txt="Inserire"):
        self.para(txt, italic=True)

    def blocks20(self, name):
        out, key = {}, None
        for ln in open(os.path.join(MD20, name), encoding="utf-8").read().splitlines():
            if ln.startswith("@@"):
                key = ln[2:].strip()
                out[key] = []
            elif key is not None:
                out[key].append(ln)
        return {k: "\n".join(v).strip() for k, v in out.items()}

    def build(self):
        g = self.blocks20("generale.md")
        gres = {n: (t, tipo) for n, t, tipo, _ in b16.GRESMALT_OR}

        # ---------------------------------------------------------------- 3. OBIETTIVI
        self.section("3.\tOBIETTIVI")
        self.instr("(Descrivere e commentare gli obiettivi raggiunti)")
        for n, title, tipo, prop, _ in b16.ALTRI_OR:
            self.or_line(n, title, tipo, prop)
            self.insert()
        for n in ("6", "7", "8"):
            self.or_line(n, gres[n][0], gres[n][1], "Gruppo Ceramiche Gresmalt")
            self.text_block(g[f"OB{n}"])
        for key, instr in (("L’obiettivo finale del progetto è inva",
                            "(In caso di risposta negativa illustrare le variazioni introdotte, le motivazioni ed "
                            "i possibili sviluppi)"),
                           ("L’obiettivo finale del progetto è stat",
                            "(In caso di risposta negativa illustrare le motivazioni dell’insuccesso)"),
                           ("Le caratteristiche e prestazioni raggi",
                            "(Confrontare le caratteristiche e le prestazioni del prodotto/processo/servizio "
                            "sviluppato con quelle indicate nel piano di sviluppo approvato)")):
            tbl = next(v for k, v in self.t_sino.items() if k.startswith(key[:30]))
            self.clone(tbl)
            self.instr(instr)
            self.insert("…")

        # ---------------------------------------------------------------- 4. ATTIVITÀ
        self.section("4.\tATTIVITÀ")
        self.instr("Ricapitolare sinteticamente le attività svolte durante l’esecuzione del programma e "
                   "raffrontarle con quelle previste nel piano di sviluppo approvato, separatamente per le "
                   "diverse tipologie di attività di Sviluppo e Ricerca. In caso di progetti congiunti, "
                   "specificare le attività svolte da ciascun partecipante.")
        for n, title, tipo, prop, _ in b16.ALTRI_OR:
            self.or_line(n, title, tipo, prop)
            self.insert()
        files = {"6": ["or6a.md", "or6b.md"], "7": ["or7.md"], "8": ["or8.md"]}
        for n in ("6", "7", "8"):
            self.or_line(n, gres[n][0], gres[n][1], "Gruppo Ceramiche Gresmalt")
            self.text_block(g[f"AT{n}"])
            for f in files[n]:
                self.markdown(os.path.join(MD20, f))

        # ---------------------------------------------------------------- 5. COSTI
        self.section("5.\tRIEPILOGO DEI COSTI")
        self.instr("(In caso di progetti congiunti, compilare una tabella per ciascun proponente e una tabella "
                   "riepilogativa per progetto)")
        for nome in ("TABELLA RIEPILOGATIVA DI PROGETTO", "GRUPPO CERAMICHE GRESMALT S.P.A.",
                     "SACMI COOPERATIVA MECCANICI IMOLA SOCIETA' COOPERATIVA",
                     "UNIVERSITÀ DEGLI STUDI DI SASSARI", "UNIVERSITÀ DELLA CALABRIA",
                     "LIBERA UNIVERSITA' DI BOLZANO"):
            self.text_block(f"**{nome}**")
            self.clone(self.t_costi)
            self.instr("(Commentare gli scostamenti, motivando quelli per le voci di costo con variazioni "
                       "superiore al 10% rispetto al valore del piano di sviluppo approvato)")
            self.insert("Da commentare dopo l'inserimento dei valori.")

        # ---------------------------------------------------------------- 6. EFFETTI
        self.section("6.\tEFFETTI DEL PROGETTO")
        self.instr("Descrivere i principali effetti del progetto, illustrando dettagliatamente:")
        for b in ("le potenzialità di sviluppo industriale dei risultati del progetto;",
                  "gli investimenti che si prevede di effettuare per l’industrializzazione;",
                  "le ricadute economiche attese, anche con riferimento alla possibilità di penetrare in nuovi "
                  "mercati;", "gli effetti sull’occupazione;",
                  "gli eventuali miglioramenti ambientali, ivi comprese le condizioni di lavoro, e i risparmi "
                  "energetici."):
            self.bullet(b)
        self.insert("….")
        self.instr("Illustrare le eventuali ricadute in altri ambiti o settori dei risultati del progetto.")
        self.insert("….")

        # ---------------------------------------------------------------- 7. DOCUMENTAZIONE
        self.section("7.\tDOCUMENTAZIONE")
        self.instr("(Elencare i documenti aziendali - registri, quaderni di laboratorio, schede di impianto, "
                   "disegni, relazioni ecc. – che contengono i dettagli tecnici sulla realizzazione del "
                   "programma e che saranno tenuti a disposizione presso la sede di svolgimento del programma)")
        for n in ("1", "2", "3", "4", "5"):
            self.text_block(f"**OR {n} – {PROP_DOC[n]}**")
            self.insert()
        for n in ("6", "7", "8"):
            self.text_block(f"**OR {n} – Gruppo Ceramiche Gresmalt**")
            self.text_block(g[f"DOC{n}"])

        # ---------------------------------------------------------------- 8. VALUTAZIONE
        self.section("8.\tVALUTAZIONE CRITICA DEI RISULTATI DEL PROGETTO")
        self.insert("….")

        for t, bold in (("Casalgrande (RE), __/__/____", False), ("Il responsabile del progetto", False),
                        ("Davide Settembre Blundo", True), ("", False),
                        ("Il Legale Rappresentante della Capofila GRUPPO CERAMICHE GRESMALT S.P.A.", False),
                        ("Filippo Salvarani", True), ("(firma digitale)", False)):
            par = self.p("Normal")
            par.paragraph_format.space_before = Pt(6)
            if t:
                _rpr(par.add_run(t), bold=bold)
        self.doc.save(OUT)
        print("Generato:", OUT)


if __name__ == "__main__":
    os.chdir(HERE)
    All20().build()
