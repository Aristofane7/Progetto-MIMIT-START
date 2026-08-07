#!/usr/bin/env python3
"""
Genera la relazione RP7.4 in .docx a partire dal sorgente Markdown+LaTeX
usando pandoc e il TEMPLATE di progetto come reference-doc.

Le formule in LaTeX ($...$ e $$...$$) sono convertite da pandoc in equazioni
NATIVE di Word (OMML), editabili con l'editor matematico di Word. Le tabelle
Markdown diventano tabelle Word; le figure PNG sono incorporate.

Uso:
    python3 RP7.4_make_docx.py
Prerequisito:
    pip install pypandoc_binary   (fornisce il binario pandoc)
"""
import os, pypandoc

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "RP7.4 Report di Product Technological Sustainability Assessment.md")
REF  = os.path.join(HERE, "RPX.Y Titolo_Relazione_Parziale_data.docx")   # template fornito
OUT  = os.path.join(HERE, "RP7.4 Report di Product Technological Sustainability Assessment.docx")

FROM = ("markdown+tex_math_dollars+pipe_tables+table_captions+footnotes"
        "+tex_math_single_backslash")

pypandoc.convert_file(
    SRC, to="docx", format=FROM, outputfile=OUT,
    extra_args=[f"--reference-doc={REF}", f"--resource-path={HERE}"],
)
print("Creato:", os.path.basename(OUT))
