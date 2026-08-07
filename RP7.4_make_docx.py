#!/usr/bin/env python3
"""
Genera la relazione RP7.4 in .docx replicando la house style della RP7.3.

- Sorgente: Markdown + LaTeX (formule -> equazioni NATIVE Word/OMML via pandoc).
- Formattazione: RP7.4_reference.docx (derivato dalla RP7.3) fornisce banner di
  intestazione + logo, piè di pagina, font Times New Roman 11pt, stili dei titoli
  in teal (024C41) e stile tabella. Il reference si crea una volta dalla RP7.3 con
  build_reference() (già eseguito; il file è versionato nel repo).
- Post-processing: la prima riga di ogni tabella viene ombreggiata di verde
  (0B5A3C) con testo bianco in grassetto, come nelle tabelle della RP7.3.

Uso:  python3 RP7.4_make_docx.py
Prereq: pip install pypandoc_binary
"""
import os, re, zipfile, shutil
import pypandoc

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "RP7.4 Report di Product Technological Sustainability Assessment.md")
REF  = os.path.join(HERE, "RP7.4_reference.docx")
OUT  = os.path.join(HERE, "RP7.4 Report di Product Technological Sustainability Assessment.docx")

FROM = ("markdown+tex_math_dollars+pipe_tables+table_captions+footnotes"
        "+tex_math_single_backslash")

# 1) conversione con pandoc usando il reference-doc (banner/stili RP7.3)
pypandoc.convert_file(
    SRC, to="docx", format=FROM, outputfile=OUT,
    extra_args=[f"--reference-doc={REF}", f"--resource-path={HERE}"],
)

# 2) post-processing con python-docx (preserva i namespace, incl. OMML delle equazioni):
#    prima riga di ogni tabella -> sfondo verde 0B5A3C, testo bianco grassetto.
from docx import Document
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

d = Document(OUT)
for t in d.tables:
    if not t.rows:
        continue
    for cell in t.rows[0].cells:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = tcPr.find(qn("w:shd"))
        if shd is None:
            shd = OxmlElement("w:shd"); tcPr.append(shd)
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), "0B5A3C")
        for p in cell.paragraphs:
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
d.save(OUT)

# 3) prune: rimuove i media non referenziati (immagini-equazione della RP7.3
#    ereditate dal reference-doc e non usate), mantenendo logo header e figure.
zin = zipfile.ZipFile(OUT)
referenced = set()
for n in zin.namelist():
    if n.endswith(".rels"):
        rels = zin.read(n).decode("utf-8", "ignore")
        for tgt in re.findall(r'Target="([^"]+)"', rels):
            referenced.add(os.path.basename(tgt))
keep = []
for n in zin.namelist():
    if n.startswith("word/media/") and os.path.basename(n) not in referenced:
        continue
    keep.append(n)
data = {n: zin.read(n) for n in keep}
zin.close()
zout = zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED)
for n, b in data.items():
    zout.writestr(n, b)
zout.close()

print("Creato:", os.path.basename(OUT), "| media referenziati:", len(referenced))
