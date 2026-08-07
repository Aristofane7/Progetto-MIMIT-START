"""Genera il documento finale RP 7.10 in .docx con la formattazione delle relazioni
finali del progetto START (es. RP 7.4).

Metodo:
  1. si usa come reference-doc di pandoc l'asset `docs/assets/rp_format_reference.docx`
     (derivato dalla RP 7.4 svuotandone il corpo): esso porta con sé gli stili
     (Normal in Arial Narrow 11; titoli in Times New Roman grassetto verde scuro),
     l'impostazione di pagina (A4, margini) e — soprattutto — l'intestazione con il
     logo di progetto e il piè di pagina (banner www.start-innovability.it + numero
     di pagina). pandoc sostituisce solo il corpo, mantenendo testata e piè di pagina;
  2. pandoc converte il corpo della relazione (dalla sezione "## 1" in poi), mappando
     '## ' -> Heading 2 (sezioni) e '### ' -> Heading 3 (sottosezioni);
  3. si antepone il blocco di testata (titolo + 4 righe di metadati) e si rifiniscono
     didascalie (10 pt centrate) e immagini (centrate), come nelle RP finali.

Uso: python scripts/build_docx.py
Requisiti: pandoc nel PATH, python-docx.

Nota: `docs/assets/rp_format_reference.docx` contiene solo la formattazione e la
grafica di progetto (testata/piè di pagina), non testo di altre relazioni.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
MD = DOCS / "RP7.10_AI_Business_Model.md"
REF = DOCS / "assets" / "rp_format_reference.docx"
OUT = DOCS / "RP7.10_AI_Business_Model.docx"

BODY_FONT = "Arial Narrow"     # font del corpo/titolo di testata
META_FONT = "Calibri"         # font dei metadati di testata

# Blocco di testata (come nelle RP finali): titolo + 4 righe di metadati.
TITLE = "Sviluppo di un modello di business basato sull'Intelligenza Artificiale (AI-BM)"
META_LINES = [
    "Relazione Parziale N°: RP7.10",
    "Versione del Documento: RV.1",
    "Data di Revisione del Documento: 07.08.2026",
    "Responsabilità: Gresmalt — Capofila",
]


def body_markdown() -> Path:
    """Estrae il corpo della relazione dalla sezione '## 1' in poi (testata esclusa)."""
    text = MD.read_text(encoding="utf-8")
    body = DOCS / ".body_rp710.md"
    body.write_text(text[text.index("## 1"):], encoding="utf-8")
    return body


def run_pandoc(body: Path) -> None:
    # '-implicit_figures': le immagini non generano didascalia automatica dal testo
    # alternativo (si usa la sola riga di didascalia descrittiva della relazione).
    subprocess.run(
        ["pandoc", body.name, "--reference-doc", "assets/rp_format_reference.docx",
         "-f", "markdown-implicit_figures", "-o", OUT.name],
        check=True, cwd=str(DOCS),
    )


def _center_para(p, text, *, font, size, bold=True, space_after=4):
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(space_after)
    r = p.add_run(text)
    r.font.name = font
    r.font.bold = bold
    r.font.size = Pt(size)


def finalize() -> None:
    """Antepone la testata e rifinisce didascalie e immagini."""
    d = Document(str(OUT))
    body_first = d.paragraphs[0]._element

    made = []
    p = d.add_paragraph(); _center_para(p, TITLE, font=BODY_FONT, size=28, space_after=10)
    made.append(p)
    for line in META_LINES:
        p = d.add_paragraph(); _center_para(p, line, font=META_FONT, size=18, space_after=3)
        made.append(p)

    # Riga separatrice sotto la testata (w:pBdr prima di w:spacing, come da OOXML).
    sep = d.add_paragraph()
    pPr = sep._element.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr"); bottom = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "6"), ("w:space", "1"), ("w:color", "024C41")):
        bottom.set(qn(k), v)
    pbdr.append(bottom); pPr.append(pbdr)
    sep.paragraph_format.space_after = Pt(10)
    made.append(sep)

    for p in made:
        body_first.addprevious(p._element)

    _style_captions_and_images(d)
    d.save(str(OUT))


def _style_captions_and_images(d) -> None:
    """Centra le immagini e porta le didascalie (Figura/Tabella) a 10 pt, come RP 7.4."""
    for p in d.paragraphs:
        if p._element.findall(".//" + qn("w:drawing")):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            continue
        t = p.text.strip()
        if t.startswith("Figura ") or t.startswith("Tabella "):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.size = Pt(10)


def main() -> None:
    body = body_markdown()
    run_pandoc(body)
    finalize()
    body.unlink(missing_ok=True)
    print("Documento finale generato:", OUT)


if __name__ == "__main__":
    main()
