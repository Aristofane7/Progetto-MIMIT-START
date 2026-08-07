# -*- coding: utf-8 -*-
"""EFA-J — Environmental Footprint Assessment in Joule. f_env in GJ."""
from src.core import efa_j as _f
def f_env(terms, terms_ref): return _f(terms, terms_ref)
