# -*- coding: utf-8 -*-
"""Validation: controlli di coerenza (unita, segni, bilanci, completezza)."""
import pandas as pd
def check(energy, terms):
    issues=[]
    if energy.isnull().any().any(): issues.append("Valori mancanti in energy_exergy.csv")
    if terms.isnull().any().any(): issues.append("Valori mancanti in module_terms.csv")
    neg = terms[terms["value_MJ"]<0]
    if len(neg): issues.append(f"{len(neg)} termini negativi (fisicamente non ammessi)")
    # coerenza: Ex_useful <= Ex_ref
    bad = energy[energy["Ex_useful_MJ"]>energy["Ex_ref_MJ"]]
    if len(bad): issues.append("Ex_useful > Ex_ref in alcune righe")
    return issues
