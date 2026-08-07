# -*- coding: utf-8 -*-
"""TEI-J — Technological-Exergy Integration. f_tech in GJ (vs baseline di riferimento)."""
from src.core import tei_j as _f
def f_tech(terms, terms_ref): return _f(terms, terms_ref)
