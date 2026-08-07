# -*- coding: utf-8 -*-
"""Integration layer (serie annuali): SA_raw, SA_w (pesi AHP), Phi, Psi, TSI_abs; TSI_rel = TSI(2025)/TSI(2023)."""
from src import core
from src.ahp import weights_and_consistency, TRIAL_MATRIX, DIMS
ALPHA_DEFAULT, BETA_DEFAULT = 0.5, 0.5

def ahp_weights():
    w,lam,CI,CR=weights_and_consistency(TRIAL_MATRIX); return dict(zip(DIMS,w)),lam,CI,CR

def row(plant, year, w, alpha=ALPHA_DEFAULT, beta=BETA_DEFAULT):
    c=core.contributions(plant,year); e=core.energy_split(plant,year)
    Ex_ref=e["Ex_ref_MJ"]/core.MJ_PER_GJ
    SA_raw=c["f_env"]+c["f_econ"]+c["f_soc"]+c["f_tech"]
    SA_w=w["env"]*c["f_env"]+w["econ"]*c["f_econ"]+w["soc"]*c["f_soc"]+w["tech"]*c["f_tech"]
    Phi=SA_w/Ex_ref; Psi=e["Psi"]; TSI=alpha*Phi+beta*Psi
    return dict(plant=plant, year=year, **c, SA_raw=SA_raw, SA_w=SA_w, Ex_ref_GJ=Ex_ref,
                Ex_useful_GJ=e["Ex_useful_MJ"]/core.MJ_PER_GJ, Phi=Phi, Psi=Psi, TSI_abs=TSI)

def compute_all(alpha=ALPHA_DEFAULT, beta=BETA_DEFAULT):
    w,lam,CI,CR=weights_and_consistency(TRIAL_MATRIX); w=dict(zip(DIMS,w))
    rows=[row(p,y,w,alpha,beta) for p in core.PLANTS for y in core.YEARS]
    tsi={(r["plant"],r["year"]):r["TSI_abs"] for r in rows}
    for r in rows:
        if r["year"]==core.YEAR_RT:
            r["TSI_rel"]=tsi[(r["plant"],core.YEAR_RT)]/tsi[(r["plant"],core.YEAR_HIST)]
    return rows, w, (lam,CI,CR)

if __name__=="__main__":
    rows,w,(lam,CI,CR)=compute_all()
    print("AHP:",{k:round(v,4) for k,v in w.items()},"CR=%.4f"%CR)
    for r in rows:
        rel=("  TSI_rel(25/23)=%.3f"%r["TSI_rel"]) if "TSI_rel" in r else ""
        print(f"{r['plant']} {r['year']} SA_raw={r['SA_raw']:8.0f} SA_w={r['SA_w']:8.0f} Phi={r['Phi']:.4f} Psi={r['Psi']:.3f} TSI={r['TSI_abs']:.4f}{rel}")
