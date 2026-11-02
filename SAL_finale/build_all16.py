# -*- coding: utf-8 -*-
"""build_all16.py — Allegato 16 (relazione tecnica di SAL finale) del progetto START, parte Gresmalt.

Impostazione (modello: relazione di SAL finale del progetto VOLT):
  * base = relazione ufficiale del SAL 2 (`fonti/START_ALL16_SAL2.docx`): se ne conservano
    intestazione, dati identificativi, sedi e stili; tutto il corpo da «3. DESCRIZIONE…»
    in poi viene ricostruito;
  * OR 1-5 (altri partner): solo titoli e segnaposto «Inserire…», come nel modello VOLT;
  * OR 6-8 (Gresmalt): introduzione di OR, una riga per le attività concluse nei SAL
    precedenti, sezione estesa per le attività svolte nel periodo (testi in `md/`,
    figure in `figures/`);
  * tabelle ore/uomo e costi e GANTT lasciati da compilare.

Uso:  python SAL_finale/build_all16.py
"""
from __future__ import annotations

import copy
import os
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_DOCX = os.path.join(HERE, "fonti", "START_ALL16_SAL2.docx")
MODEL_DOCX = os.path.join(HERE, "fonti", "API-2022_ALL16_modello.docx")
MD = os.path.join(HERE, "md")
FIG = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "START_ALL16_SAL_finale_Gresmalt.docx")

PERIODO = "SAL FINALE\tdal 01/11/2025 al 31/10/2026"
HDR_FILL = "0F4761"
MAX_IMG_CM = 16.0

# ------------------------------------------------------------------------- struttura OR
ALTRI_OR = [
    ("1", "Concetto globale di Digital Twin per la transizione da Industry 4.0 a Intelligent Industry "
          "basata sull'Intelligenza Artificiale", "Ricerca Industriale", "Libera Università di Bolzano",
     ["Analisi dei requisiti generici e specifici",
      "Definizione del concetto globale di un DT intelligente",
      "Definizione e ontologia di un data hub integrato",
      "Implementazione prototipale, adattamento continuo e concetto di cybersecurity del Data Hub integrato",
      "Linee guida per la progettazione di sistemi di IA affidabili ed eticamente sostenibili",
      "Sviluppo di un sistema di assistenza basati sull'IA",
      "Esplorazione del potenziale di sistemi di produzione biointelligenti"]),
    ("2", "Modelli per la previsione e la classificazione della qualità di materiali ceramici basati su "
          "approcci di feature extraction e machine learning", "Ricerca Industriale",
     "Università della Calabria",
     ["Modelli per la predizione della qualità del prodotto basati su dati in ingresso e di processo a "
      "partire da materie prime nazionali",
      "Modelli per la predizione della qualità del prodotto basati su dati in ingresso e di processo a "
      "partire da materie prime di importazione e da mix di materie prime",
      "Metodi di controllo qualità di processo e detezione difetti tramite tecniche NDT e ML",
      "Modellazione del sistema combinato prodotto ceramico-fondi di posa",
      "Analisi di sensitività dei modelli di footprint assessment"]),
    ("3", "Dalla fabbrica all'utente: l'Intelligenza Artificiale a supporto dell'Architectural Design 4.0+ "
          "per il confort ambientale", "Ricerca Industriale", "Università degli Studi di Sassari",
     ["Involucri edilizi ceramici performanti, prototipazione e monitoraggio",
      "Analisi, studio ed implementazione dei parametri ambientali di confort indoor",
      "Analisi ed elaborazione dei dati ambientali per un sistema di controllo predittivo per involucri "
      "ventilati",
      "Multiperformance ed ottimizzazione del prodotto ceramico da involucro e da interno"]),
    ("4", "Studio per l'integrazione dell'Intelligenza Artificiale per la gestione della Intelligent Industry",
     "Ricerca Industriale", "SACMI",
     ["Individuazione dei casi d'uso adeguati all'applicazione di strumenti AI nel settore Ceramico",
      "Analisi degli algoritmi AI più indicati rispetto ai casi d'uso individuati",
      "Definizione e mappatura delle variabili fondamentali da considerare per l'alimentazione degli "
      "algoritmi",
      "Definizione e progettazione di una infrastruttura IoT edge-cloud hybrid di riferimento"]),
    ("5", "Applicazione di strumenti di AI per aumentare la sostenibilità del processo ceramico",
     "Sviluppo Sperimentale", "SACMI",
     ["Mappatura del processo produttivo all'interno dell'impianto pilota",
      "Mappatura dei dati da raccogliere nell'impianto pilota",
      "Implementazione su impianto pilota dell'infrastruttura di raccolta ed elaborazione dati",
      "Attribuzione dei dati ai processi di lavorazioni del prodotto all'interno dell'impianto pilota",
      "Sviluppo e test su dati batch/offline dello stack algoritmico per il controllo predittivo obiettivo",
      "Sviluppo e test su dati online dello stack algoritmico per il controllo predittivo obiettivo"]),
]

SAL1 = "L'attività è stata completata nel periodo del SAL 1."
SAL2 = "L'attività è stata completata nel periodo del SAL 2."
GRESMALT_OR = [
    ("6", "Modellazione di soluzioni tecnologiche per la transizione verso la Intelligent Industry",
     "Ricerca Industriale", [
         ("6.1", "Modellazione dell'impronta tecnologica per la Intelligent Industry", SAL1),
         ("6.2", "Modellazione dell'impronta ambientale per la Intelligent Industry", SAL1),
         ("6.3", "Modellazione dell'impronta sociale per la Intelligent Industry", SAL1),
         ("6.4", "Modellazione dell'impronta economica per la Intelligent Industry", SAL1),
         ("6.5", "Modellazione termodinamica della sostenibilità per la Intelligent Industry", SAL2),
         ("6.6", "Studio e progettazione di un'architettura edge-to-cloud (E2C) per la Intelligent "
                 "Industry", SAL2),
         ("6.7", "Studio e progettazione della Intelligent Factory per la Intelligent Industry", SAL2),
         ("6.8", "Data-driven product analysis", SAL2),
         ("6.9", "Data-driven product design", SAL2),
         ("6.10", "Modellizzazione della Intelligent Industry", SAL2),
     ]),
    ("7", "Validazione in ambiente operativo della Intelligent Industry", "Sviluppo Sperimentale", [
        ("7.1", "User acceptance testing (UAT) della piattaforma edge-to-cloud (E2C)", SAL2),
        ("7.2", "Performance testing della Intelligent Factory", SAL2),
        ("7.3", None, "md"), ("7.4", None, "md"), ("7.5", None, "md"), ("7.6", None, "md"),
        ("7.7", None, "md"), ("7.8", None, "md"), ("7.9", None, "md"), ("7.10", None, "md"),
    ]),
    ("8", "Misurazione e valutazione dei risultati di progetto e analisi degli scostamenti",
     "Sviluppo Sperimentale", [
         ("8.1", "Creazione del Comitato di Gestione (CdG)", SAL1),
         ("8.2", "Costruzione Intranet di Progetto", SAL1),
         ("8.3", "Implementazione e monitoraggio delle attività", SAL1),
         ("8.4", "Diffusione dei risultati", SAL1),
         ("8.5", "Coinvolgimento degli Stakeholders", SAL1 + " Il Piano di Stakeholder Engagement è "
                 "documentato nella relazione RP 8.5."),
         ("8.6", None, "md"),
     ]),
]


# ------------------------------------------------------------------------- helper di formattazione
def _rpr(run, size=11, bold=None, italic=False, color=None):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color


INLINE = re.compile(r"(\*\*)")


def _inline(p, text, size=11, italic=False, bold_all=False):
    bold = False
    for tok in INLINE.split(text):
        if tok == "**":
            bold = not bold
            continue
        if tok:
            _rpr(p.add_run(tok), size=size, bold=bold or bold_all, italic=italic)


class Builder:
    def __init__(self):
        self.doc = Document(BASE_DOCX)
        model = Document(MODEL_DOCX)
        b = self.doc
        # tabelle-modello da riutilizzare (copiate prima di svuotare il corpo)
        self.t_ore = copy.deepcopy(next(t for t in b.tables
                                        if t.rows[0].cells[0].text.strip() == "Personale Impiegato")._tbl)
        self.t_sintesi = copy.deepcopy(next(t for t in b.tables
                                            if t.rows[0].cells[0].text.strip() == "OR"
                                            and len(t.columns) == 6)._tbl)
        self.t_sino = {}
        for t in model.tables:
            first = t.rows[0].cells[0].text.strip()
            if len(t.columns) == 3 and t.rows[0].cells[1].text.strip() == "SI":
                self.t_sino[first[:25]] = copy.deepcopy(t._tbl)
            if "ATTIVITA' DI RICERCA" in t.rows[1].cells[0].text if len(t.rows) > 1 else False:
                self.t_costi = copy.deepcopy(t._tbl)
        # svuota il corpo dopo la riga del periodo di SAL
        body = b.element.body
        idx = None
        for i, p in enumerate(b.paragraphs):
            if p.text.strip().startswith("SAL 2"):
                idx = i
                self._set_text(p, PERIODO)
                break
        anchor = b.paragraphs[idx]._p
        kill = False
        for el in list(body.iterchildren()):
            if el is anchor:
                kill = True
                continue
            if kill and el.tag != qn("w:sectPr"):
                body.remove(el)
        self._drop_orphans()
        self.sect = body.find(qn("w:sectPr"))

    # --- infrastruttura
    def _set_text(self, p, text):
        runs = p.runs
        runs[0].text = text
        for r in runs[1:]:
            r.text = ""

    def _drop_orphans(self):
        xml = self.doc.element.xml
        used = set(re.findall(r'r:(?:embed|id|link)="(rId\d+)"', xml))
        for rid, rel in list(self.doc.part.rels.items()):
            if rel.reltype.endswith(("/image", "/hyperlink", "/chart", "/oleObject")) and rid not in used:
                self.doc.part.drop_rel(rid)

    def _append(self, el):
        self.sect.addprevious(el)
        return el

    def p(self, style="Body Text"):
        par = self.doc.add_paragraph(style=style)
        # add_paragraph appende in coda al body, prima di sectPr: ok
        return par

    # --- blocchi
    def section(self, text):
        par = self.p("Normal")
        pf = par.paragraph_format
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pPr = par._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), "D9D9D9")
        pPr.append(shd)
        _rpr(par.add_run(text), size=10, bold=True)

    def instr(self, text):
        par = self.p("Body Text")
        par.paragraph_format.space_before = Pt(4)
        _rpr(par.add_run(text), size=10, italic=True)

    def or_head(self, n, title, tipo, prop):
        par = self.p("Body Text")
        par.paragraph_format.space_before = Pt(14)
        par.paragraph_format.keep_with_next = True
        _rpr(par.add_run(f"OR {n}. {title}"), size=14, bold=True)
        for k, v in (("Tipologia: ", tipo), ("Soggetto Proponente: ", prop)):
            q = self.p("Body Text")
            q.paragraph_format.space_before = Pt(2)
            _rpr(q.add_run(k), bold=True)
            _rpr(q.add_run(v), bold=False)

    def act_head(self, code, title):
        par = self.p("Body Text")
        pf = par.paragraph_format
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pf.keep_with_next = True
        _rpr(par.add_run(f"OR {code}: {title}"), size=12, bold=True)

    def sub(self, text):
        par = self.p("Body Text")
        pf = par.paragraph_format
        pf.space_before = Pt(8)
        pf.space_after = Pt(2)
        pf.keep_with_next = True
        _rpr(par.add_run(text), size=11, bold=True, italic=True)

    def para(self, text, italic=False):
        par = self.p("Body Text")
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = par.paragraph_format
        pf.space_before = Pt(6)
        pf.line_spacing = 1.1
        _inline(par, text, italic=italic)
        return par

    def bullet(self, text):
        par = self.p("Body Text")
        par.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf = par.paragraph_format
        pf.left_indent = Cm(0.9)
        pf.first_line_indent = Cm(-0.45)
        pf.space_before = Pt(2)
        _rpr(par.add_run("•  "))
        _inline(par, text)

    def formula(self, text):
        par = self.p("Body Text")
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(6)
        par.paragraph_format.space_after = Pt(6)
        _rpr(par.add_run(text), italic=True)

    def caption(self, text):
        par = self.p("Body Text")
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(3)
        par.paragraph_format.space_after = Pt(8)
        _rpr(par.add_run(text), size=9, italic=True)

    def figure(self, path, cap):
        from PIL import Image
        with Image.open(path) as im:
            w, h = im.size
        width = MAX_IMG_CM
        if h / w > 1.1:            # immagini verticali: limita l'altezza
            width = min(MAX_IMG_CM, 17.0 * w / h)
        par = self.p("Body Text")
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_before = Pt(6)
        par.paragraph_format.keep_with_next = True
        par.add_run().add_picture(path, width=Cm(width))
        self.caption(cap)

    def table(self, rows, cap):
        hdr, data = rows[0], rows[1:]
        t = self.doc.add_table(rows=1, cols=len(hdr))
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, h in enumerate(hdr):
            c = t.rows[0].cells[i]
            tcPr = c._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), HDR_FILL)
            tcPr.append(shd)
            par = c.paragraphs[0]
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _inline(par, h, size=9, bold_all=True)
            for r in par.runs:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        trPr = t.rows[0]._tr.get_or_add_trPr()
        th = OxmlElement("w:tblHeader")
        th.set(qn("w:val"), "true")
        trPr.append(th)
        for row in data:
            cells = t.add_row().cells
            for i in range(len(hdr)):
                val = row[i] if i < len(row) else ""
                par = cells[i].paragraphs[0]
                _inline(par, val, size=9)
        for row in t.rows:
            cs = OxmlElement("w:cantSplit")
            cs.set(qn("w:val"), "true")
            row._tr.get_or_add_trPr().append(cs)
        self.caption(cap)

    def clone(self, tbl):
        el = copy.deepcopy(tbl)
        self._append(el)
        sp = self.p("Body Text")
        sp.paragraph_format.space_after = Pt(2)
        return el

    def ore_uomo(self):
        lab = self.p("Body Text")
        lab.paragraph_format.space_before = Pt(10)
        lab.paragraph_format.keep_with_next = True
        _rpr(lab.add_run("Risorse umane impiegate nell'OR"), bold=True)
        el = self.clone(self.t_ore)
        # svuota i valori numerici (colonne Numero / Ore uomo)
        for tr in el.findall(qn("w:tr"))[1:]:
            for tc in tr.findall(qn("w:tc"))[1:]:
                for t in tc.iter(qn("w:t")):
                    t.text = ""

    # --- markdown delle attività
    def markdown(self, path):
        lines = open(path, encoding="utf-8").read().splitlines()
        i = 0
        buf_table = []
        while i < len(lines):
            ln = lines[i].rstrip()
            if ln.startswith("## "):
                m = re.match(r"## OR ([\d.]+):\s*(.*)", ln)
                self.act_head(m.group(1), m.group(2).strip())
            elif ln.startswith("### "):
                self.sub(ln[4:].strip())
            elif ln.startswith("!["):
                m = re.match(r"!\[(.*)\]\((.*)\)", ln)
                cap, src = m.group(1), m.group(2)
                src = os.path.join(FIG, os.path.basename(src))
                self.figure(src, cap)
            elif ln.startswith("|"):
                buf_table = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r":?-{2,}:?", c) for c in row):
                        buf_table.append(row)
                    i += 1
                cap = ""
                if i < len(lines) and lines[i].strip().startswith("Tabella"):
                    cap = lines[i].strip()
                    i += 1
                self.table(buf_table, cap)
                continue
            elif ln.startswith("$$"):
                self.formula(ln.strip("$ ").strip())
            elif ln.startswith("- "):
                self.bullet(ln[2:].strip())
            elif ln.strip():
                # paragrafo: unisce righe consecutive non vuote
                parts = [ln.strip()]
                while (i + 1 < len(lines) and lines[i + 1].strip()
                       and not re.match(r"(#|!\[|\||\$\$|- )", lines[i + 1])):
                    i += 1
                    parts.append(lines[i].strip())
                self.para(" ".join(parts))
            i += 1

    def blocks(self, name):
        """Legge un file a blocchi `@@CHIAVE` → testo."""
        out, key = {}, None
        for ln in open(os.path.join(MD, name), encoding="utf-8").read().splitlines():
            if ln.startswith("@@"):
                key = ln[2:].strip()
                out[key] = []
            elif key is not None:
                out[key].append(ln)
        return {k: "\n".join(v).strip() for k, v in out.items()}

    def text_block(self, text):
        for chunk in re.split(r"\n\s*\n", text):
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk.startswith("- "):
                for b in chunk.splitlines():
                    self.bullet(b[2:].strip())
            elif chunk.startswith("### "):
                self.sub(chunk[4:])
            elif chunk.startswith("**") and chunk.endswith("**") and "\n" not in chunk:
                par = self.p("Normal")
                par.paragraph_format.space_before = Pt(10)
                _rpr(par.add_run(chunk.strip("*")), bold=True)
            else:
                self.para(" ".join(chunk.splitlines()))

    # --------------------------------------------------------------------- documento
    def build(self):
        intro = self.blocks("intro_or.md")
        fin = self.blocks("sezioni_finali.md")

        self.section("3. DESCRIZIONE DELLE ATTIVITA' DEL PROGETTO SVOLTE")
        self.instr("(Descrivere le attività svolte nel periodo in esame per ciascun obiettivo realizzativo e "
                   "raffrontarle al piano di sviluppo approvato; indicare le risorse tecniche umane impiegate "
                   "in relazione a ciascun obiettivo realizzativo)")
        for n, title, tipo, prop, acts in ALTRI_OR:
            self.or_head(n, title, tipo, prop)
            self.para("Inserire breve descrizione dell'OR. MAX 250 parole.", italic=True)
            for k, a in enumerate(acts, 1):
                self.act_head(f"{n}.{k}", a)
                self.para("Inserire descrizione attività. MAX 1500 parole.", italic=True)
            self.ore_uomo()
        for n, title, tipo, acts in GRESMALT_OR:
            self.or_head(n, title, tipo, "Gresmalt")
            self.para(intro[f"OR{n}"])
            for code, a, how in acts:
                if how == "md":
                    self.markdown(os.path.join(MD, f"{code}.md"))
                else:
                    self.act_head(code, a)
                    self.para(how)
            self.ore_uomo()

        self.instr("(Compilare la seguente tabella di sintesi)")
        el = self.clone(self.t_sintesi)
        for tr in el.findall(qn("w:tr"))[1:]:
            tcs = tr.findall(qn("w:tc"))
            orn = "".join(t.text or "" for t in tcs[0].iter(qn("w:t"))).strip()
            for tc in tcs[4:]:
                ts = list(tc.iter(qn("w:t")))
                for t in ts:
                    t.text = ""
                if orn in ("6", "7", "8") and tc is tcs[4] and ts:
                    ts[0].text = "100%"
        self.clone(self.t_sino["Le attività sono sostanzi"])
        self.instr("(In caso di risposta negativa illustrare gli scostamenti)")

        self.section("4. OBIETTIVI PARZIALI DEL PROGETTO CHE SONO STATI RAGGIUNTI")
        self.instr("(Illustrare gli obiettivi parziali che sono stati conseguiti nel periodo del SAL e "
                   "confrontarli con il piano di sviluppo approvato)")
        for partner in ("LIBERA UNIVERSITÀ DI BOLZANO", "UNIVERSITÀ DELLA CALABRIA",
                        "UNIVERSITÀ DEGLI STUDI DI SASSARI", "SACMI"):
            self.text_block(f"**{partner}**")
            self.para("Inserire. MAX 1000 parole.", italic=True)
        self.text_block("**GRUPPO CERAMICHE GRESMALT S.P.A.**")
        self.text_block(fin["OBIETTIVI"])
        self.clone(self.t_sino["L’obiettivo finale del pr"])
        self.instr("(In caso di risposta negativa illustrare le variazioni introdotte, le relative motivazioni "
                   "ed i possibili sviluppi)")

        self.section("5. DOCUMENTAZIONE")
        self.instr("(Elencare i documenti aziendali - registri, quaderni di laboratorio, schede di impianto, "
                   "disegni, relazioni ecc. - che contengono i dettagli tecnici sulla realizzazione del "
                   "progetto e che saranno tenuti a disposizione presso la sede di svolgimento del progetto. "
                   "In caso di progetti congiunti elencare separatamente tali documenti per ciascuno dei "
                   "soggetti beneficiari)")
        for partner in ("LIBERA UNIVERSITÀ DI BOLZANO", "UNIVERSITÀ DELLA CALABRIA",
                        "UNIVERSITÀ DEGLI STUDI DI SASSARI", "SACMI"):
            self.text_block(f"**{partner}**")
            self.para("Inserire", italic=True)
        self.text_block("**GRUPPO CERAMICHE GRESMALT S.P.A.**")
        self.text_block(fin["DOCUMENTAZIONE"])

        self.section("6. CONFRONTO CON I DATI DEL PIANO DI SVILUPPO APPROVATO")
        self.clone(self.t_sino["Sono state eliminate atti"])
        self.instr("(Riportare il diagramma temporale aggiornato del progetto, sovrapposto a quello del piano "
                   "di sviluppo approvato; commentare i ritardi, le soppressioni o le interruzioni di "
                   "attività, nonché l'inserimento di nuove attività)")
        self.para("INSERIRE GANTT", italic=True)

        self.section("7. TABELLA ANDAMENTO DEI COSTI")
        self.instr("(In caso di progetti congiunti, compilare una tabella per ciascun proponente che ha "
                   "rendicontato costi nel SAL in argomento e una tabella riepilogativa per progetto)")
        for nome in ("TABELLA RIEPILOGATIVA PROGETTO START – SAL FINALE", "GRUPPO CERAMICHE GRESMALT S.P.A.",
                     "SACMI COOPERATIVA MECCANICI IMOLA SOCIETA' COOPERATIVA",
                     "UNIVERSITÀ DEGLI STUDI DI SASSARI", "UNIVERSITÀ DELLA CALABRIA",
                     "LIBERA UNIVERSITA' DI BOLZANO"):
            self.text_block(f"**{nome}**")
            self.clone(self.t_costi)
            self.instr("(Commentare eventuali variazioni e scostamenti di costo rispetto al piano di sviluppo "
                       "approvato)")
            self.para("….", italic=True)

        self.section("8. VALUTAZIONE CRITICA")
        self.text_block("**Evoluzioni rispetto al piano di sviluppo approvato**")
        self.clone(self.t_sino["Sono emerse o si intraved"])
        self.instr("(In caso di almeno una risposta affermativa specificare le cause e i prevedibili effetti "
                   "sulla realizzazione del progetto; in ogni caso esprimere, motivandolo, il parere "
                   "sull'opportunità di continuare il progetto)")
        self.text_block(fin["VALUTAZIONE"])

        for t, b in (("Casalgrande (RE), __/__/____", False), ("Il responsabile del progetto", False),
                     ("Davide Settembre Blundo", True), ("", False),
                     ("Il Legale Rappresentante della Capofila GRUPPO CERAMICHE GRESMALT S.P.A.", False),
                     ("Filippo Salvarani", True), ("(firma digitale)", False)):
            par = self.p("Normal")
            par.paragraph_format.space_before = Pt(6)
            if t:
                _rpr(par.add_run(t), bold=b)

        self.doc.save(OUT)
        print("Generato:", OUT)


if __name__ == "__main__":
    Builder().build()
