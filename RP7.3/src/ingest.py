# -*- coding: utf-8 -*-
"""Ingest: legge gli input CSV dimostrativi (energia + termini moduli) in DataFrame."""
import os, pandas as pd
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load_energy():
    return pd.read_csv(os.path.join(BASE,"input","energy_exergy.csv"))
def load_terms():
    return pd.read_csv(os.path.join(BASE,"input","module_terms.csv"))
if __name__=="__main__":
    print(load_energy().head()); print(load_terms().head())
