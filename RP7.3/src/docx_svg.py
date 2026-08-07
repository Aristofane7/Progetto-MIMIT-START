# -*- coding: utf-8 -*-
"""Helper: inserisce un'immagine SVG (vettoriale) in un DOCX con fallback PNG,
   secondo il meccanismo Word 2016+ (a:blip -> asvg:svgBlip). Editabile/zoomabile senza perdita."""
from docx.oxml import parse_xml
from docx.oxml.ns import qn
from docx.opc.part import Part
from docx.opc.packuri import PackURI
from docx.shared import Mm
import os

SVG_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
_counter = {"n": 0}

def add_svg(paragraph, doc, svg_path, png_path, width_mm):
    """Aggiunge l'immagine al paragrafo: PNG come fallback + SVG vettoriale."""
    run = paragraph.add_run()
    run.add_picture(png_path, width=Mm(width_mm))          # crea blip PNG
    # crea part SVG e relazione dal document part
    _counter["n"] += 1
    partname = PackURI(f"/word/media/svg{_counter['n']}.svg")
    with open(svg_path, "rb") as f:
        svg_bytes = f.read()
    svg_part = Part(partname, "image/svg+xml", svg_bytes, doc.part.package)
    rId = doc.part.relate_to(svg_part, SVG_REL)
    # inietta svgBlip nel blip appena creato
    blips = run._element.findall(".//" + qn("a:blip"))
    blip = blips[-1]
    ext_xml = (
        '<a:extLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        '<a:ext uri="{96DAC541-7F89-4952-8B84-B3F5B99F14F2}">'
        '<asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'r:embed="%s"/></a:ext></a:extLst>' % rId
    )
    blip.append(parse_xml(ext_xml))
    return run
