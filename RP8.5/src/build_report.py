# -*- coding: utf-8 -*-
"""build_report.py — genera figure e documento .docx della RP 8.5 sul template ufficiale START.

Apre `RPX.Y Titolo_Relazione_Parziale_data.docx` (testata con loghi, piè di pagina,
impostazione di pagina), compila la copertina, elimina il corpo di esempio da
"1.INTRODUZIONE" in poi e ricostruisce il contenuto con lo stile delle relazioni
finali (cfr. RP 7.6): titoli verde START, corpo Calibri 11 giustificato con
interlinea 1,5 e rientro di prima riga, tabelle con intestazione verde scuro,
riferimenti bibliografici in nota a piè di pagina.

I valori (IR, quadranti, materialità) sono importati da `engagement.py`, così
tabelle, figure, CSV e testo restano coerenti.

Uso (dalla cartella RP8.5/):  python -m src.build_report
"""
from __future__ import annotations

import os
import re
import shutil
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

from docx import Document  # noqa: E402
from docx.enum.table import WD_TABLE_ALIGNMENT  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Mm, Pt, RGBColor  # noqa: E402
from lxml import etree  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engagement as eng  # noqa: E402

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # .../RP8.5
ROOT = os.path.dirname(BASE)
TPL = os.path.join(ROOT, "RPX.Y Titolo_Relazione_Parziale_data.docx")
FIG = os.path.join(BASE, "docs", "figures")
OUTDOCX = os.path.join(BASE, "docs", "RP8.5_Piano_Stakeholder_Engagement.docx")
ROOTDOCX = os.path.join(ROOT, "RP 8.5 Piano di Stakeholder Engagement_30-04-24.docx")

DATA_REV = "30.04.24"
VERSIONE = "RV.1"

DGREEN_HEX = "024C41"
TEAL_HEX = "00A98E"
DGREEN = RGBColor(0x02, 0x4C, 0x41)
GREY = RGBColor(0x40, 0x40, 0x40)
C_DG = "#024C41"
C_TE = "#00A98E"
C_LG = "#E6F2EF"

# ======================================================================================
# Riferimenti bibliografici (note a piè di pagina)
# ======================================================================================
REFS = {
    "freeman": "Freeman, R. E. (1984). Strategic Management: A Stakeholder Approach. Boston: Pitman.",
    "stilgoe": "Stilgoe, J., Owen, R., & Macnaghten, P. (2013). Developing a framework for responsible "
               "innovation. Research Policy, 42(9), 1568-1580.",
    "aa1000": "AccountAbility (2015). AA1000 Stakeholder Engagement Standard (AA1000SES). London: "
              "AccountAbility.",
    "reed": "Reed, M. S., Graves, A., Dandy, N., Posthumus, H., Hubacek, K., Morris, J., Prell, C., "
            "Quinn, C. H., & Stringer, L. C. (2009). Who's in and why? A typology of stakeholder analysis "
            "methods for natural resource management. Journal of Environmental Management, 90(5), "
            "1933-1949.",
    "mitchell": "Mitchell, R. K., Agle, B. R., & Wood, D. J. (1997). Toward a theory of stakeholder "
                "identification and salience: Defining the principle of who and what really counts. "
                "Academy of Management Review, 22(4), 853-886.",
    "mendelow": "Mendelow, A. (1991). Stakeholder mapping. Proceedings of the 2nd International "
                "Conference on Information Systems, Cambridge, MA.",
    "gri": "Global Reporting Initiative (2021). GRI 3: Material Topics 2021. Amsterdam: GRI.",
    "bellantuono": "Bellantuono, N., Pontrandolfo, P., & Scozzi, B. (2016). Capturing the stakeholders' "
                   "view in sustainability reporting: A novel approach. Sustainability, 8(4), 379.",
    "vacchi": "Vacchi, M., Siligardi, C., Demaria, F., Cedillo-González, E. I., González-Sánchez, R., & "
              "Settembre-Blundo, D. (2021). Technological sustainability or sustainable technology? A "
              "multidimensional vision of sustainability in manufacturing. Sustainability, 13(17), 9942.",
}


# ======================================================================================
# Figure
# ======================================================================================
def fig_metodo(path):
    fig, ax = plt.subplots(figsize=(11, 3.6), dpi=200)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 3.6)
    ax.axis("off")
    fasi = [
        ("1", "Identificazione", "livelli della scheda 8.5:\ninterni → associazioni →\nterritori → clienti"),
        ("2", "Mappatura", "registro degli\nstakeholder\n(istituzionali,\nassociativi, interni)"),
        ("3", "Rilevanza", "Influenza × Interesse\nIR ∈ [0,1]\nmatrice di rilevanza"),
        ("4", "Materialità", "temi del Piano ×\ninteressi dei gruppi\n(problema n. 5)"),
        ("5", "Piano operativo", "livelli, canali,\nfrequenze, responsabili\ne monitoraggio"),
    ]
    w, gap, x0 = 1.85, 0.32, 0.25
    for i, (n, t, d) in enumerate(fasi):
        x = x0 + i * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 1.05), w, 1.95, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=C_LG, ec=C_DG, lw=1.4))
        ax.add_patch(FancyBboxPatch((x, 2.45), w, 0.55, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=C_DG, ec=C_DG, lw=1.4))
        ax.text(x + w / 2, 2.72, f"{n}. {t}", ha="center", va="center", color="white", fontsize=10.5,
                weight="bold")
        ax.text(x + w / 2, 1.72, d, ha="center", va="center", color="#1a1a1a", fontsize=8.6)
        if i < len(fasi) - 1:
            ax.annotate("", xy=(x + w + gap - 0.03, 1.95), xytext=(x + w + 0.03, 1.95),
                        arrowprops=dict(arrowstyle="-|>", color=C_TE, lw=2))
    ax.annotate("", xy=(x0 + 0.4, 0.98), xytext=(x0 + 4 * (w + gap) + w - 0.4, 0.98),
                arrowprops=dict(arrowstyle="-|>", color=C_TE, lw=1.4, ls="--",
                                connectionstyle="arc3,rad=0.18"))
    ax.text(5.5, 0.3, "Revisione periodica (monitoraggio → aggiornamento della mappatura e della matrice)",
            ha="center", va="center", fontsize=8.6, color=C_DG, style="italic")
    ax.text(5.5, 3.38, "Principi AA1000SES: inclusività · materialità · rispondenza · impatto",
            ha="center", va="center", fontsize=10, color=C_DG, weight="bold")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_matrice_rilevanza(path):
    fig, ax = plt.subplots(figsize=(9.5, 7.2), dpi=200)
    # quadranti (soglia: punteggio >= 4)
    ax.add_patch(Rectangle((3.5, 3.5), 2, 2, fc="#CDE7E1", ec="none", zorder=0))
    ax.add_patch(Rectangle((0.5, 3.5), 3, 2, fc="#EEF5F3", ec="none", zorder=0))
    ax.add_patch(Rectangle((3.5, 0.5), 2, 3, fc="#EEF5F3", ec="none", zorder=0))
    ax.add_patch(Rectangle((0.5, 0.5), 3, 3, fc="#FAFAFA", ec="none", zorder=0))
    kw = dict(fontsize=10, color=C_DG, weight="bold", alpha=0.85)
    ax.text(5.45, 5.42, "GESTIRE ATTIVAMENTE", ha="right", va="top", **kw)
    ax.text(0.55, 5.42, "MANTENERE SODDISFATTI", ha="left", va="top", **kw)
    ax.text(5.45, 0.58, "MANTENERE INFORMATI", ha="right", va="bottom", **kw)
    ax.text(0.55, 0.58, "MONITORARE", ha="left", va="bottom", **kw)
    celle = {}
    for s in eng.REGISTRO:
        celle.setdefault((s.interesse, s.influenza), []).append(s)
    for (x, y), lst in celle.items():
        n = len(lst)
        ir = lst[0].ir
        ax.scatter([x], [y], s=380 + 260 * n, color=C_TE if ir >= 0.64 else C_DG,
                   alpha=0.85, edgecolor="white", lw=1.5, zorder=3)
        ax.text(x, y, str(n), ha="center", va="center", color="white", fontsize=10, weight="bold",
                zorder=4)
        ids = [s.sid for s in lst]
        righe = [", ".join(ids[i:i + 3]) for i in range(0, len(ids), 3)]
        ax.text(x, y - 0.3, "\n".join(righe), ha="center", va="top", fontsize=7.6, color="#222",
                zorder=4)
        ax.text(x + 0.2, y + 0.2, f"IR {ir:.2f}".replace(".", ","), ha="left", va="bottom",
                fontsize=7.4, color=C_DG, zorder=4)
    ax.axhline(3.5, color=C_DG, lw=1, ls="--")
    ax.axvline(3.5, color=C_DG, lw=1, ls="--")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Interesse (1-5)", fontsize=10.5)
    ax.set_ylabel("Influenza (1-5)", fontsize=10.5)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def fig_materialita(path):
    rows = eng.materialita()
    fig, ax = plt.subplots(figsize=(9.5, 6.6), dpi=200)
    ax.add_patch(Rectangle((3.0, 3.5), 2.0, 2.0, fc="#CDE7E1", ec="none", zorder=0))
    ax.text(4.95, 5.42, "TEMI PRIORITARI", ha="right", va="top", fontsize=10, color=C_DG, weight="bold")
    col = {"Prioritario": C_TE, "Rilevante": C_DG, "Da monitorare": "#9E9E9E"}
    for r in rows:
        x, y = r["ril_stakeholder"], r["ril_progetto"]
        ax.scatter([x], [y], s=150, color=col[r["classe"]], edgecolor="white", lw=1.2, zorder=3)
        k = int(r["codice"][1:])
        dy = 0.12 if k % 2 else -0.2
        dx = -0.09 if r["codice"] == "T10" else (0.06 if r["codice"] == "T02" else 0.0)
        ax.text(x + dx, y + dy, r["codice"], ha="center", fontsize=9, color="#222", weight="bold", zorder=4)
    ax.axvline(3.0, color=C_DG, lw=1, ls="--")
    ax.axhline(3.5, color=C_DG, lw=1, ls="--")
    ax.set_xlim(1.5, 5.0)
    ax.set_ylim(2.5, 5.5)
    ax.set_xlabel("Rilevanza per gli stakeholder (1-5, media pesata con IR)", fontsize=10)
    ax.set_ylabel("Rilevanza per il progetto (1-5, Piano di Sviluppo)", fontsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    from matplotlib.lines import Line2D
    h = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=9, label=k)
         for k, c in col.items()]
    ax.legend(handles=h, loc="lower right", fontsize=8.5, frameon=False)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def build_figures():
    os.makedirs(FIG, exist_ok=True)
    fig_metodo(os.path.join(FIG, "fig_se1_metodo.png"))
    fig_matrice_rilevanza(os.path.join(FIG, "fig_se3_matrice_rilevanza.png"))
    fig_materialita(os.path.join(FIG, "fig_se4_materialita.png"))
    # fig_se2_mappatura_SAL1.png: mappatura originale (Relazione tecnica SAL 1, Fig. 8.4.1),
    # versionata nel repository.


# ======================================================================================
# Helper docx (stile RP finali)
# ======================================================================================
class Notes:
    """Gestione delle note a piè di pagina sul part footnotes.xml del template."""

    W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    def __init__(self, doc):
        self.part = None
        for rel in doc.part.rels.values():
            if rel.reltype.endswith("/footnotes"):
                self.part = rel.target_part
        self.root = etree.fromstring(self.part.blob)
        ids = [int(e.get(qn("w:id"))) for e in self.root.findall(qn("w:footnote"))]
        self.next = max([0] + ids) + 1
        self.used = {}

    def _w(self, tag):
        return etree.SubElement if False else None

    def add(self, text) -> int:
        fid = self.next
        self.next += 1
        W = "{%s}" % self.W
        fn = etree.SubElement(self.root, W + "footnote")
        fn.set(W + "id", str(fid))
        p = etree.SubElement(fn, W + "p")
        ppr = etree.SubElement(p, W + "pPr")
        jc = etree.SubElement(ppr, W + "jc")
        jc.set(W + "val", "both")
        r1 = etree.SubElement(p, W + "r")
        rpr = etree.SubElement(r1, W + "rPr")
        self._font(rpr, 16)
        va = etree.SubElement(rpr, W + "vertAlign")
        va.set(W + "val", "superscript")
        etree.SubElement(r1, W + "footnoteRef")
        r2 = etree.SubElement(p, W + "r")
        rpr2 = etree.SubElement(r2, W + "rPr")
        self._font(rpr2, 16)
        t = etree.SubElement(r2, W + "t")
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = " " + text
        return fid

    def _font(self, rpr, size):
        W = "{%s}" % self.W
        rf = etree.SubElement(rpr, W + "rFonts")
        for a in ("ascii", "hAnsi", "cs"):
            rf.set(W + a, "Calibri")
        sz = etree.SubElement(rpr, W + "sz")
        sz.set(W + "val", str(size))

    def ref(self, key) -> int:
        if key not in self.used:
            self.used[key] = self.add(REFS[key])
        return self.used[key]

    def save(self):
        self.part._blob = etree.tostring(self.root, xml_declaration=True, encoding="UTF-8",
                                         standalone=True)


NOTES: Notes | None = None


def _run(p, text, size=11, bold=False, italic=False, color=None):
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(size)
    r.bold = bold
    r.italic = italic
    if color is not None:
        r.font.color.rgb = color
    return r


def _fnref(p, key):
    fid = NOTES.ref(key)
    r = p.add_run()
    rpr = r._r.get_or_add_rPr()
    va = OxmlElement("w:vertAlign")
    va.set(qn("w:val"), "superscript")
    rpr.append(va)
    fr = OxmlElement("w:footnoteReference")
    fr.set(qn("w:id"), str(fid))
    r._r.append(fr)


TOKEN = re.compile(r"(\*\*|\{fn:\w+\}|\*)")


def _inline(p, text, size=11, italic_all=False):
    bold = False
    ital = False
    for tok in TOKEN.split(text):
        if tok == "**":
            bold = not bold
        elif tok == "*":
            ital = not ital
        elif tok.startswith("{fn:"):
            _fnref(p, tok[4:-1])
        elif tok:
            _run(p, tok, size=size, bold=bold, italic=ital or italic_all)


def _spacing(p, after=6, before=0, line=1.5):
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pf.line_spacing = line


def h1(doc, t, new_page=False):
    p = doc.add_paragraph()
    p.paragraph_format.page_break_before = new_page
    _spacing(p, after=6, before=12, line=1.5)
    p.paragraph_format.keep_with_next = True
    _run(p, t, size=18, bold=True, color=DGREEN)


def h2(doc, t):
    p = doc.add_paragraph()
    _spacing(p, after=4, before=8, line=1.5)
    p.paragraph_format.keep_with_next = True
    _run(p, t, size=13, bold=True, color=DGREEN)


def para(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _spacing(p)
    p.paragraph_format.first_line_indent = Cm(0.5)
    _inline(p, text)
    return p


def formula(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=8, before=4)
    _inline(p, text, italic_all=True)


def bullet(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    _spacing(p, after=3)
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    _run(p, "•\t")
    p.paragraph_format.tab_stops.add_tab_stop(Cm(1.0))
    _inline(p, text)


def cap_table(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=2, before=6, line=1.0)
    p.paragraph_format.keep_with_next = True
    _run(p, text, size=9.5, italic=True)


def cap_figure(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=10, before=2, line=1.0)
    _run(p, text, size=9.5, italic=True)


def figure(doc, name, width_mm=165):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, after=0, before=6, line=1.0)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(FIG, name), width=Mm(width_mm))


def _shade(cell, hexc):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), hexc)
    tcPr.append(sh)


def _borders(cell, bottom="BFBFBF"):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "right"):
        e = OxmlElement("w:" + edge)
        e.set(qn("w:val"), "nil")
        b.append(e)
    e = OxmlElement("w:bottom")
    e.set(qn("w:val"), "single")
    e.set(qn("w:sz"), "4")
    e.set(qn("w:color"), bottom)
    b.append(e)
    tcPr.append(b)


def table(doc, headers, rows, widths_cm, fs=9, center_cols=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    hdr = t.rows[0]
    trPr = hdr._tr.get_or_add_trPr()
    e = OxmlElement("w:tblHeader")
    e.set(qn("w:val"), "true")
    trPr.append(e)
    for i, h in enumerate(headers):
        c = hdr.cells[i]
        _shade(c, DGREEN_HEX)
        _borders(c, bottom=DGREEN_HEX)
        pr = c.paragraphs[0]
        pr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _spacing(pr, after=1, before=1, line=1.0)
        _run(pr, h, size=fs, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            c = cells[i]
            _borders(c)
            pr = c.paragraphs[0]
            _spacing(pr, after=1, before=1, line=1.0)
            pr.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            _inline(pr, str(val), size=fs)
    for row in t.rows:
        # impedisce lo spezzamento di riga tra pagine
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit")
        cs.set(qn("w:val"), "true")
        trPr.append(cs)
        for i, w in enumerate(widths_cm):
            row.cells[i].width = Cm(w)
    tbl = t._tbl
    grid = tbl.tblGrid
    for gc in list(grid):
        grid.remove(gc)
    for w in widths_cm:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(w * 567)))
        grid.append(gc)
    tblPr = tbl.tblPr
    tw = OxmlElement("w:tblW")
    tw.set(qn("w:w"), str(int(sum(widths_cm) * 567)))
    tw.set(qn("w:type"), "dxa")
    for old in tblPr.findall(qn("w:tblW")):
        tblPr.remove(old)
    tblPr.append(tw)
    lay = OxmlElement("w:tblLayout")
    lay.set(qn("w:type"), "fixed")
    tblPr.append(lay)
    sp = doc.add_paragraph()
    _spacing(sp, after=4, line=1.0)
    return t


def set_para_text(p, text):
    if not p.runs:
        p.add_run(text)
        return
    p.runs[0].text = text
    for r in p.runs[1:]:
        r.text = ""


def n2(x):
    return f"{x:.2f}".replace(".", ",")


# ======================================================================================
# Documento
# ======================================================================================
def build():
    global NOTES
    build_figures()
    eng.export_csv()
    sint = eng.sintesi()
    mat = eng.materialita()
    reg = eng.REGISTRO
    q = sint["quadranti"]

    doc = Document(TPL)
    NOTES = Notes(doc)
    cover = {
        "Titolo relazione": "PIANO DI STAKEHOLDER ENGAGEMENT",
        "Relazione Parziale N°: RPX.Y": "Relazione Parziale N°: RP 8.5",
        "Versione del Documento: RV.X": f"Versione del Documento: {VERSIONE}",
        "Data di Revisione del Documento: XX.YY.ZZ": f"Data di Revisione del Documento: {DATA_REV}",
        "Responsabilità:  Partner - Ruolo": "Responsabilità: Gresmalt - Capofila",
    }
    intro_idx = None
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        for k, v in cover.items():
            if t == k.strip():
                set_para_text(p, v)
        if t.upper().replace(" ", "").startswith("1.INTRODUZIONE"):
            intro_idx = i
    resp_idx = max(i for i, p in enumerate(doc.paragraphs) if p.text.startswith("Responsabilit"))
    for p in doc.paragraphs[resp_idx + 1:]:
        p._element.getparent().remove(p._element)

    # ================================================================= 1. INTRODUZIONE
    h1(doc, "1.INTRODUZIONE", new_page=True)
    para(doc, "Un progetto di ricerca e sviluppo a carattere industriale produce effetti che vanno oltre "
              "il perimetro delle imprese e degli enti che lo realizzano: modifica processi produttivi, "
              "competenze e condizioni di lavoro, genera conoscenza trasferibile ad altre imprese del "
              "settore e ricade sui territori in cui le attività si svolgono. La teoria degli "
              "stakeholder riconosce che il successo di un'iniziativa dipende dalla capacità di "
              "identificare e integrare le aspettative di tutti i soggetti che possono influenzarla o "
              "esserne influenzati{fn:freeman}; il paradigma della ricerca e innovazione responsabile "
              "aggiunge che l'inclusione dei portatori d'interesse lungo l'intero ciclo di sviluppo è "
              "condizione per orientare l'innovazione verso risultati socialmente desiderabili e "
              "accettati{fn:stilgoe}.")
    para(doc, "Nel progetto START questa prospettiva è affidata all'OR 8 \"Misurazione e valutazione dei "
              "risultati di progetto e analisi degli scostamenti\", che ha lo scopo di creare un sistema "
              "di gestione e coordinamento adeguato al carattere plurisettoriale e multidisciplinare del "
              "partenariato e di diffondere i risultati ai principali portatori d'interesse. Mentre le "
              "attività 8.1-8.4 hanno dotato il progetto degli strumenti di governo e comunicazione "
              "(Regolamento del Comitato di Gestione, intranet SharePoint, modello di monitoraggio in "
              "MS Excel e sito web), l'attività 8.5 \"Trasferimento tecnologico agli Stakeholders\" "
              "ha il compito di garantire il principio di inclusività degli stakeholder istituzionali "
              "già nella fase di collaudo del sistema e di prototipazione dei nuovi prodotti, "
              "predisponendo e implementando un piano per il loro coinvolgimento nella valutazione "
              "delle attività e dei risultati raggiunti, così da favorirne la replicabilità nei settori "
              "di appartenenza delle imprese partner. Il Piano di Sviluppo indica anche il percorso da "
              "seguire: partire dagli stakeholder interni a ogni partner per arrivare alle associazioni "
              "confindustriali, ai territori (comuni e regioni) e infine ai clienti e agli utenti "
              "finali.")
    para(doc, "La baseline dell'attività è rappresentata dall'assenza di una mappatura strutturata "
              "dei portatori d'interesse del progetto, cui corrisponde un valore pari a 0,0 "
              "dell'Indicatore di rilevanza degli Stakeholder; l'obiettivo è la Matrice di rilevanza "
              "degli Stakeholder, risultato del task \"Mappatura degli Stakeholder\" e base del Piano "
              "di Stakeholder Engagement. Il Piano di Sviluppo individua inoltre un rischio specifico "
              "(problema progettuale n. 5): il processo di engagement potrebbe essere ostacolato se la "
              "rappresentatività e l'inclusività dei portatori d'interesse non fossero adeguatamente "
              "garantite dalla mappatura; la soluzione prevista è l'applicazione della tecnica della "
              "Materiality Assessment (analisi della rilevanza), per stabilire quali stakeholder e quali "
              "temi debbano essere considerati prioritari. L'attività ha infine un ruolo abilitante per "
              "l'attività 8.6 \"Assessment dell'impatto di START\": l'analisi input-output dell'impatto "
              "territoriale richiede dati macroeconomici regionali non direttamente disponibili al "
              "gruppo di progetto (problema progettuale n. 6), che il Piano prevede di ottenere "
              "proprio attraverso il coinvolgimento delle autorità territoriali previsto dal Piano di "
              "Stakeholder Engagement.")
    para(doc, "La presente relazione chiude l'attività al termine del primo periodo di rendicontazione "
              "(30/04/2024). Suo scopo è: (i) consolidare la mappatura secondo i livelli indicati dal Piano di "
              "Sviluppo; (ii) misurare l'Indicatore di rilevanza per ciascuno stakeholder e costruire "
              "la Matrice di rilevanza; (iii) completare l'analisi di materialità dei temi; (iv) "
              "definire il Piano operativo di Stakeholder Engagement e il relativo sistema di "
              "monitoraggio, quale contributo al Risultato Finale RF 8 \"Piano di Coordinamento "
              "Progetto Start\".")

    # ================================================================= 2. METODOLOGIA
    h1(doc, "2. METODOLOGIA")
    para(doc, "Il riferimento metodologico è lo standard AA1000 Stakeholder Engagement Standard "
              "(AA1000SES){fn:aa1000}, che fonda il coinvolgimento dei portatori d'interesse su quattro "
              "principi: inclusività (partecipazione di chi è influenzato dalle attività), materialità "
              "(identificazione dei temi rilevanti), rispondenza (risposta trasparente alle aspettative) "
              "e impatto (monitoraggio degli effetti delle azioni). Coerentemente, il processo adottato "
              "si articola in cinque fasi successive, rappresentate in Figura 1, con un ciclo di "
              "revisione periodica che riporta gli esiti del monitoraggio nella mappatura e nella "
              "matrice.")
    figure(doc, "fig_se1_metodo.png", 170)
    cap_figure(doc, "Figura 1: Processo di stakeholder engagement adottato nell'attività 8.5.")

    h2(doc, "2.1 Identificazione e mappatura")
    para(doc, "L'identificazione ha seguito un approccio top-down per categorie{fn:reed}, organizzato "
              "secondo i livelli concentrici indicati dalla scheda di attività: stakeholder interni ai "
              "partner, associazioni di categoria e ordini professionali, territori (comuni e regioni "
              "che ospitano le sedi operative del progetto), clienti e utenti finali, a cui si "
              "aggiungono le istituzioni nazionali dell'Accordo per l'Innovazione. Il punto di partenza "
              "è la mappatura istituzionale degli stakeholder, costruita "
              "a partire dalle sedi di svolgimento del progetto dei cinque soggetti beneficiari e dalla "
              "rappresentanza di settore. Gli stakeholder sono stati quindi raggruppati in otto gruppi "
              "omogenei per ruolo, che costituiscono l'unità di analisi della materialità e del piano "
              "operativo.")

    h2(doc, "2.2 Indicatore di rilevanza e Matrice di rilevanza degli Stakeholder")
    para(doc, "La rilevanza di ciascuno stakeholder è stata valutata lungo due dimensioni, secondo la "
              "logica della griglia potere-interesse{fn:mendelow} e della teoria della salienza degli "
              "stakeholder{fn:mitchell}: l'Influenza, ossia la capacità di condizionare lo svolgimento "
              "e i risultati del progetto, e l'Interesse, ossia la misura in cui lo stakeholder è "
              "esposto agli effetti del progetto o ne può trarre beneficio. Entrambe sono espresse su "
              "una scala ordinale da 1 a 5, con i criteri riportati in Tabella 1, così che ogni "
              "punteggio sia riconducibile a un ruolo documentato e possa essere riesaminato.")
    cap_table(doc, "Tabella 1: Criteri di attribuzione dei punteggi di Influenza e Interesse.")
    table(doc, ["Punteggio", "Influenza (I)", "Interesse (Int)"],
          [[str(k), eng.RUBRICA_INFLUENZA[k], eng.RUBRICA_INTERESSE[k]] for k in (5, 4, 3, 2, 1)],
          [2.2, 8.4, 8.4], center_cols=(0,))
    para(doc, "L'Indicatore di rilevanza degli Stakeholder (IR), previsto dal Piano di Sviluppo come "
              "KPI dell'attività, è definito come prodotto normalizzato delle due dimensioni:")
    formula(doc, "IR = (I × Int) / 25,   con IR ∈ [0,04 ; 1,00]")
    para(doc, "Il valore 0,0 della baseline corrisponde all'assenza di valutazione, mentre il valore "
              "massimo identifica uno stakeholder con potere decisionale sul progetto e direttamente "
              "esposto ai suoi effetti. Posizionando ciascuno stakeholder nel piano Interesse-Influenza "
              "si ottiene la Matrice di rilevanza, suddivisa in quattro quadranti (soglia: punteggio "
              "pari o superiore a 4) a cui corrispondono strategie di coinvolgimento differenziate: "
              "gestire attivamente (influenza e interesse elevati), mantenere soddisfatti (influenza "
              "elevata), mantenere informati (interesse elevato) e monitorare. Gli stakeholder con "
              "IR pari o superiore a 0,64 sono considerati stakeholder chiave.")

    h2(doc, "2.3 Analisi di materialità")
    para(doc, "In risposta al problema progettuale n. 5, l'analisi di materialità è stata condotta "
              "secondo l'impostazione dei Material Topics della Global Reporting Initiative{fn:gri}, "
              "adattata al contesto di un progetto di ricerca e sviluppo come proposto in letteratura "
              "per combinare il punto di vista degli stakeholder con quello dell'organizzazione"
              "{fn:bellantuono}. I temi candidati sono stati derivati dalle Finalità (paragrafo 4) e "
              "dall'Obiettivo finale (paragrafo 5) del Piano di Sviluppo e dai KPI degli Obiettivi "
              "Realizzativi, ottenendo un elenco di "
              f"{sint['n_temi']} temi. Per ciascun tema sono state stimate due grandezze:")
    bullet(doc, "**Rilevanza per gli stakeholder**: per ciascun gruppo g è stato valutato l'interesse per "
                "il tema t (a = 0 nessuno, 1 moderato, 2 elevato); il valore è la media degli interessi "
                "ponderata con l'IR medio del gruppo (w), riportata sulla scala 1-5: "
                "R = 1 + 4 · Σ(w · a) / (2 · Σw).")
    bullet(doc, "**Rilevanza per il progetto**: punteggio da 1 a 5 ancorato al Piano di Sviluppo (5 = tema "
                "compreso nell'Obiettivo finale e misurato da KPI di più OR; 4 = tema misurato da KPI di "
                "almeno un OR o da un risultato intermedio; 3 = finalità dichiarata senza KPI "
                "quantitativo; 2 = tema trasversale abilitante; 1 = tema marginale).")
    para(doc, "Sono considerati prioritari i temi con rilevanza per gli stakeholder pari o superiore a "
              "3,0 e rilevanza per il progetto pari o superiore a 4; rilevanti i temi che superano una "
              "sola delle due soglie; da monitorare i restanti.")

    h2(doc, "2.4 Livelli di coinvolgimento e canali")
    para(doc, "Per la definizione del piano operativo sono stati adottati i livelli di coinvolgimento "
              "dello standard AA1000SES, in ordine crescente di intensità: informare, consultare, "
              "coinvolgere e collaborare. A ciascun gruppo è stato associato il livello coerente con il "
              "quadrante di appartenenza nella Matrice di rilevanza e con i temi materiali che lo "
              "riguardano. I canali privilegiati sono gli strumenti già realizzati nelle attività 8.1-8.4 "
              "(Comitato di Gestione, intranet SharePoint e Microsoft Teams, sito web di progetto in "
              "lingua italiana e inglese, affiancato dalla pagina LinkedIn prevista dal Piano), "
              "integrati da incontri tecnici, seminari ed eventi di settore.")

    # ================================================================= 3. RISULTATI
    h1(doc, "3.RISULTATI")
    h2(doc, "3.1 Mappatura degli stakeholder")
    para(doc, "La mappatura istituzionale (Figura 2) individua "
              f"{sint['n_sal1']} stakeholder istituzionali e associativi: il Ministero delle Imprese e "
              "del Made in Italy e il Fondo per la Crescita Sostenibile; le quattro amministrazioni "
              "regionali e provinciali dei territori del partenariato (Emilia-Romagna, Provincia "
              "Autonoma di Bolzano, Sardegna, Calabria); undici comuni sede delle unità operative di "
              "Gresmalt, SACMI e delle tre università; le due associazioni di categoria del comparto "
              "ceramico (Confindustria Ceramica e Acimac) e gli ordini professionali di architetti e "
              "ingegneri, destinatari dei risultati sull'involucro edilizio a matrice ceramica.")
    figure(doc, "fig_se2_mappatura_SAL1.png", 165)
    cap_figure(doc, "Figura 2: Mappatura degli stakeholder istituzionali e associativi.")
    para(doc, "In coerenza con il percorso indicato dalla scheda di attività, la mappatura è stata "
              "completata con il livello interno (direzione e team di progetto di Gresmalt, team di "
              "SACMI, gruppi di ricerca delle università partner, personale degli stabilimenti "
              "Gresmalt coinvolto nei collaudi in ambiente operativo) e con il livello di mercato "
              "(clienti B2B e utenti finali). Il registro risultante comprende "
              f"{sint['n_stakeholder']} stakeholder ripartiti in otto gruppi (Tabella 2).")
    rows2 = []
    for g, nome in eng.GRUPPI.items():
        membri = [s for s in reg if s.gruppo == g]
        livello = membri[0].livello
        rows2.append([g, nome, livello, str(len(membri)), "; ".join(s.nome.split(" — ")[0]
                                                                      if s.gruppo != "G7" else s.nome
                                                                      for s in membri)])
    cap_table(doc, "Tabella 2: Registro degli stakeholder per gruppo e livello.")
    table(doc, ["Gruppo", "Denominazione", "Livello", "N.", "Stakeholder"], rows2,
          [1.4, 3.8, 2.3, 0.9, 10.6], fs=8.5, center_cols=(0, 3))

    h2(doc, "3.2 Indicatore e Matrice di rilevanza degli Stakeholder")
    para(doc, "L'applicazione dei criteri di Tabella 1 ha consentito di calcolare l'Indicatore di "
              f"rilevanza per tutti i {sint['n_stakeholder']} stakeholder del registro (Tabella 3), con "
              f"un valore medio di {n2(sint['ir_medio'])} rispetto alla baseline di 0,0.")
    rows3 = [[s.sid, s.nome, str(s.influenza), str(s.interesse), n2(s.ir), s.quadrante]
             for s in sorted(reg, key=lambda z: (-z.ir, z.sid))]
    cap_table(doc, "Tabella 3: Indicatore di rilevanza (IR) e quadrante della Matrice di rilevanza per "
                   "ciascuno stakeholder.")
    table(doc, ["ID", "Stakeholder", "I", "Int", "IR", "Quadrante"], rows3,
          [1.1, 9.8, 0.9, 0.9, 1.2, 5.1], fs=8.5, center_cols=(0, 2, 3, 4))
    chiave = [s for s in reg if s.ir >= 0.64]
    para(doc, "La Matrice di rilevanza (Figura 3) evidenzia "
              f"{q.get('Gestire attivamente', 0)} stakeholder da gestire attivamente, "
              f"{q.get('Mantenere soddisfatti', 0)} da mantenere soddisfatti, "
              f"{q.get('Mantenere informati', 0)} da mantenere informati e "
              f"{q.get('Monitorare', 0)} da monitorare. Gli stakeholder chiave (IR ≥ 0,64) sono "
              f"{len(chiave)}: i team di progetto dei partner, il Ministero delle Imprese e del Made in "
              "Italy, la Regione Emilia-Romagna, che ospita il distretto ceramico e le sedi dei partner "
              "industriali, e Confindustria Ceramica, che rappresenta il principale canale di "
              "replicabilità dei risultati verso le altre imprese del settore.")
    figure(doc, "fig_se3_matrice_rilevanza.png", 150)
    cap_figure(doc, "Figura 3: Matrice di rilevanza degli Stakeholder (la dimensione delle bolle è "
                    "proporzionale al numero di stakeholder; i codici rimandano alla Tabella 3).")
    para(doc, "La lettura della matrice restituisce tre indicazioni operative. In primo luogo, le "
              "amministrazioni regionali e provinciali hanno un'influenza elevata che deriva non solo "
              "dalle politiche industriali, ma anche dal controllo dei dati statistici territoriali "
              "necessari all'analisi input-output dell'attività 8.6: la Regione Emilia-Romagna, "
              "direttamente esposta agli effetti del progetto, va gestita attivamente, mentre le altre "
              "tre amministrazioni vanno mantenute soddisfatte attraverso un coinvolgimento mirato "
              "alla condivisione dei dati. In secondo luogo, i comuni che ospitano gli stabilimenti "
              "Gresmalt presentano l'interesse più elevato tra gli stakeholder territoriali, perché "
              "destinatari diretti degli effetti occupazionali e ambientali degli interventi di "
              "adeguamento degli impianti; per essi la strategia è di informazione e consultazione "
              "continua. Infine, il personale degli stabilimenti, pur con influenza intermedia, è "
              "direttamente coinvolto nei collaudi dell'OR 7 e rappresenta un interlocutore essenziale "
              "per l'accettazione delle soluzioni di intelligenza artificiale.")

    h2(doc, "3.3 Analisi di materialità")
    para(doc, "La Tabella 4 riporta, per ciascuno dei temi, la rilevanza per gli stakeholder e per il "
              "progetto e la conseguente classificazione; la Figura 4 ne rappresenta la matrice di "
              "materialità.")
    rows4 = [[r["codice"], r["tema"], n2(r["ril_stakeholder"]), str(r["ril_progetto"]), r["classe"],
              r["riferimenti"]] for r in sorted(mat, key=lambda z: (-z["ril_progetto"] - z["ril_stakeholder"]))]
    cap_table(doc, "Tabella 4: Analisi di materialità dei temi del progetto.")
    table(doc, ["Cod.", "Tema", "Ril. stakeholder", "Ril. progetto", "Classe", "Riferimento nel Piano"],
          rows4, [1.1, 5.6, 2.0, 1.8, 2.4, 6.1], fs=8.5, center_cols=(0, 2, 3))
    figure(doc, "fig_se4_materialita.png", 150)
    cap_figure(doc, "Figura 4: Matrice di materialità dei temi del progetto START (codici dei temi in Tabella 4).")
    prior = [r for r in mat if r["classe"] == "Prioritario"]
    para(doc, f"Risultano prioritari {len(prior)} temi: "
              + "; ".join(r["tema"].lower() for r in prior) + ". "
              "Si tratta dei temi su cui convergono sia gli obiettivi misurabili del progetto "
              "(indicatori EEA+, EFA+ e SFA+ dell'OR 6, transizione verso la Intelligent Industry, "
              "analisi di impatto dell'attività 8.6), sia gli interessi degli stakeholder territoriali "
              "e associativi. Qualità e design del prodotto e comfort dell'involucro edilizio sono "
              "temi centrali per il progetto ma interessano un insieme più ristretto di stakeholder "
              "(clienti, progettisti e associazioni di settore): richiedono quindi un coinvolgimento "
              "mirato più che diffuso. L'etica dell'intelligenza artificiale e la sicurezza dei dati, "
              "infine, sono avvertite soprattutto all'interno del partenariato e vanno presidiate "
              "attraverso le linee guida etiche dell'OR 1 e l'architettura Edge-to-Cloud, "
              "rendendone conto agli stakeholder esterni in sede di diffusione dei risultati.")

    h2(doc, "3.4 Piano operativo di Stakeholder Engagement")
    para(doc, "Sulla base della Matrice di rilevanza e dell'analisi di materialità è stato definito il "
              "Piano operativo di Stakeholder Engagement (Tabella 5), che assegna a ciascun gruppo un "
              "livello di coinvolgimento, gli obiettivi, i temi materiali di riferimento, i canali, la "
              "frequenza e il responsabile dell'attuazione. Il Piano si applica dalla conclusione "
              "dell'attività fino al termine del progetto, accompagnando in particolare la fase di "
              "collaudo del sistema e di prototipazione dei nuovi prodotti dell'OR 7, come richiesto "
              "dalla scheda di attività.")
    rows5 = [
        ["G1 Istituzioni nazionali", "Collaborare / Informare",
         "Rendere conto dell'avanzamento e dei risultati; condividere gli elementi di replicabilità "
         "(T06, T10, T11)",
         "Relazioni di SAL e relazione finale; verifica intermedia; incontri con il Soggetto Gestore",
         "Alle scadenze di rendicontazione", "Responsabile di progetto"],
        ["G2 Regioni e Provincia autonoma", "Coinvolgere / Consultare",
         "Condividere i risultati sui territori; acquisire i dati statistici regionali per l'analisi "
         "input-output (T10, T03, T01)",
         "Incontri tecnici con gli assessorati e gli uffici statistici; richieste formali di dati",
         "Semestrale; all'avvio dell'attività 8.6", "Responsabile di progetto con le Università"],
        ["G3 Comuni sedi Gresmalt", "Consultare / Informare",
         "Informare sugli interventi di adeguamento degli impianti e sui loro effetti; raccogliere "
         "osservazioni (T01, T02, T03, T10)",
         "Incontri con le amministrazioni; comunicazioni dedicate; sito web e LinkedIn",
         "Annuale e in occasione di interventi rilevanti", "Gresmalt (Direzione)"],
        ["G4 Comuni sedi partner", "Informare",
         "Diffondere i risultati delle attività svolte sul territorio (T10, T11)",
         "Sito web, pagina LinkedIn, iniziative delle Università",
         "Semestrale", "Responsabili scientifici di OR"],
        ["G5 Associazioni di categoria", "Collaborare / Coinvolgere",
         "Validare la replicabilità dei risultati nel settore; diffondere buone pratiche (T06, T01, "
         "T07, T11, T12)",
         "Tavoli tecnici; workshop; eventi di settore; contributi a iniziative associative",
         "Almeno annuale", "Gresmalt e SACMI"],
        ["G6 Ordini professionali", "Coinvolgere",
         "Trasferire ai progettisti i risultati sull'involucro edilizio e sul prodotto (T09, T07, T08)",
         "Seminari tecnici, anche validi per la formazione professionale continua",
         "Nella fase di sperimentazione dell'OR 3", "Università di Sassari con Gresmalt"],
        ["G7 Stakeholder interni", "Collaborare",
         "Coordinare le attività; coinvolgere il personale nei collaudi; presidiare etica dell'IA e "
         "sicurezza dei dati (T03, T04, T05, T06)",
         "Comitato di Gestione; SharePoint e Teams; formazione e sessioni di collaudo con gli utenti",
         "Periodica, secondo il Regolamento di gestione", "Comitato di Gestione"],
        ["G8 Clienti e utenti finali", "Consultare / Informare",
         "Raccogliere riscontri sulle nuove collezioni e sulla sostenibilità del prodotto (T07, T08, T09)",
         "Presentazioni delle collezioni; questionari di gradimento; sito web e LinkedIn",
         "In fase di prototipazione e test preindustriale", "Gresmalt (area commerciale)"],
    ]
    cap_table(doc, "Tabella 5: Piano operativo di Stakeholder Engagement.")
    table(doc, ["Gruppo", "Livello", "Obiettivi e temi", "Canali e strumenti", "Frequenza", "Responsabile"],
          rows5, [2.6, 2.3, 4.8, 4.4, 2.5, 2.4], fs=8)

    h2(doc, "3.5 Monitoraggio dell'efficacia")
    para(doc, "In attuazione del principio di impatto dello standard AA1000SES, il Piano è accompagnato "
              "da un insieme di indicatori di monitoraggio (Tabella 6), integrati nel modello di "
              "monitoraggio del progetto realizzato nell'attività 8.3. Gli esiti del monitoraggio "
              "alimentano la revisione annuale della mappatura, della Matrice di rilevanza e della "
              "matrice di materialità.")
    rows6 = [
        ["Copertura degli stakeholder chiave", "Quota degli stakeholder del quadrante \"gestire "
         "attivamente\" con almeno un'iniziativa di coinvolgimento nel semestre", "100 %",
         "Modello di monitoraggio (8.3)"],
        ["Iniziative di coinvolgimento", "Numero di iniziative realizzate per gruppo di stakeholder",
         "≥ 1 all'anno per gruppo", "Registro delle iniziative"],
        ["Accesso ai dati territoriali", "Territori per i quali sono stati acquisiti i dati "
         "statistici necessari all'analisi input-output", "4 su 4", "Attività 8.6"],
        ["Riscontri raccolti", "Questionari e osservazioni raccolti presso stakeholder esterni e "
         "relativo esito", "Almeno un ciclo all'anno", "Questionari; verbali"],
        ["Diffusione digitale", "Aggiornamenti del sito web (IT/EN) e pubblicazioni sulla pagina "
         "LinkedIn", "Almeno trimestrale", "Sito web; LinkedIn"],
        ["Aggiornamento della matrice", "Revisione dei punteggi di Influenza e Interesse alla luce "
         "dei riscontri", "Annuale", "Comitato di Gestione"],
    ]
    cap_table(doc, "Tabella 6: Indicatori di monitoraggio del Piano di Stakeholder Engagement.")
    table(doc, ["Indicatore", "Definizione", "Obiettivo", "Fonte"], rows6, [4.0, 8.6, 3.2, 3.2], fs=8.5)

    h2(doc, "3.6 Verifica del KPI")
    cap_table(doc, "Tabella 7: Verifica del KPI dell'attività 8.5 rispetto al Piano di Sviluppo.")
    table(doc, ["Relazione task", "Risultato task", "KPI", "Baseline", "Obiettivo", "Risultato"],
          [["Piano di Stakeholder Engagement", "Mappatura degli Stakeholder",
            "Indicatore di rilevanza degli Stakeholder", "0,0", "Matrice di rilevanza degli Stakeholder",
            f"IR calcolato per {sint['n_stakeholder']} stakeholder (media {n2(sint['ir_medio'])}); "
            "Matrice di rilevanza e Piano operativo definiti"]],
          [3.2, 3.0, 3.2, 1.6, 3.4, 4.6], fs=8.5, center_cols=(3,))

    # ================================================================= 4. DISCUSSIONE
    h1(doc, "4.DISCUSSIONE E CONCLUSIONI")
    para(doc, "L'attività 8.5 ha portato il progetto da una baseline priva di una mappatura strutturata "
              "dei portatori d'interesse a un Piano di Stakeholder Engagement fondato su una Matrice di "
              "rilevanza misurata per ciascuno stakeholder e su un'analisi di materialità dei temi. Il "
              "KPI previsto dal Piano di Sviluppo può pertanto considerarsi raggiunto. L'adozione "
              "dell'analisi di materialità risponde inoltre al problema progettuale n. 5: la "
              "rappresentatività della mappatura è stata verificata estendendola, secondo il percorso "
              "indicato dalla scheda, dagli stakeholder istituzionali ai livelli interno e di mercato, "
              "e la priorità di stakeholder e temi è stata stabilita con criteri espliciti e "
              "riesaminabili.")
    para(doc, "I risultati presentano forti interdipendenze con le altre attività del progetto:")
    bullet(doc, "con le attività 8.1-8.4, di cui il Piano utilizza gli strumenti (Comitato di Gestione, "
                "intranet, modello di monitoraggio, sito web) come canali di coinvolgimento e di "
                "rendicontazione;")
    bullet(doc, "con l'attività 8.6, per la quale il coinvolgimento delle amministrazioni regionali e "
                "provinciali costituisce il presupposto per accedere ai dati macroeconomici necessari "
                "all'analisi input-output (problema progettuale n. 6);")
    bullet(doc, "con l'OR 6, poiché i temi prioritari di efficienza energetica, uso delle risorse e "
                "occupazione corrispondono alle dimensioni misurate dagli strumenti EEA+, EFA+ e SFA+, "
                "che diventano così anche strumenti di rendicontazione verso gli stakeholder"
                "{fn:vacchi};")
    bullet(doc, "con l'OR 7, poiché il coinvolgimento del personale degli stabilimenti e dei clienti "
                "accompagna i collaudi in ambiente operativo e la prototipazione delle nuove "
                "collezioni;")
    bullet(doc, "con gli OR 1 e 3, rispettivamente per il presidio dei temi etici dell'intelligenza "
                "artificiale e per il trasferimento ai progettisti dei risultati sull'involucro "
                "edilizio a matrice ceramica.")
    para(doc, "In questo quadro, l'attività contribuisce direttamente al Risultato Finale RF 8 \"Piano "
              "di Coordinamento Progetto Start\", di cui il Piano di Stakeholder Engagement costituisce "
              "la componente rivolta all'esterno del partenariato, e prepara la finalità che il Piano di "
              "Sviluppo indica come contributo innovativo dell'OR 8: la valutazione dell'impatto del "
              "progetto sulla società e sui territori di riferimento. Rispetto alle Finalità del "
              "progetto (paragrafo 4 del Piano di Sviluppo), il coinvolgimento strutturato degli "
              "stakeholder è la condizione perché la transizione dell'industria ceramica dalla Smart "
              "Factory alla Intelligent Industry non resti confinata nelle imprese partner, ma "
              "diventi un modello replicabile per il distretto e per la filiera, coerente con la "
              "domanda di prodotti più sostenibili e con la competitività del settore.")
    para(doc, "Le implicazioni operative riguardano tre aspetti. In primo luogo, i punteggi di "
              "Influenza e Interesse sono valutazioni qualitative del gruppo di gestione del progetto: "
              "il primo ciclo di consultazione previsto dal Piano dovrà verificarli presso gli "
              "stakeholder stessi, aggiornando la matrice. In secondo luogo, il coinvolgimento delle "
              "amministrazioni regionali e provinciali va avviato con anticipo rispetto all'analisi di "
              "impatto dell'attività 8.6, per assicurare la disponibilità dei dati statistici. Infine, "
              "la mappatura e la matrice di materialità sono strumenti dinamici: la loro revisione "
              "annuale, alimentata dagli indicatori di monitoraggio, consentirà di adeguare il Piano "
              "all'evoluzione del progetto e delle aspettative dei portatori d'interesse.")

    NOTES.save()
    os.makedirs(os.path.dirname(OUTDOCX), exist_ok=True)
    doc.save(OUTDOCX)
    shutil.copyfile(OUTDOCX, ROOTDOCX)
    print("DOCX generato:", OUTDOCX)
    print("Copia in radice:", ROOTDOCX)


if __name__ == "__main__":
    build()
