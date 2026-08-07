# -*- coding: utf-8 -*-
"""EcoFA-J — Economic Footprint Assessment in Joule. f_econ in GJ."""
from src.core import ecofa_j as _f
def f_econ(terms, terms_ref): return _f(terms, terms_ref)
