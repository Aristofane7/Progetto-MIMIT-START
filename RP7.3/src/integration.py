# -*- coding: utf-8 -*-
"""Integration layer: SA_raw, SA_w (pesi AHP), Phi, Psi, TSI_abs, TSI_rel."""
from src import core
from src.ahp import weights_and_consistency, TRIAL_MATRIX, DIMS
ALPHA_DEFAULT, BETA_DEFAULT = 0.5, 0.5

def ahp_weights():
    w,lam,CI,CR = weights_and_consistency(TRIAL_MATRIX)
    return dict(zip(DIMS, w)), lam, CI, CR

def scenario_row(plant, scen, w, alpha=ALPHA_DEFAULT, beta=BETA_DEFAULT):
    c = core.contributions(plant, scen)                 # GJ
    e = core.energy_split(plant, scen)
    Ex_ref_GJ = e["Ex_ref_MJ"]/core.MJ_PER_GJ
    SA_raw = c["f_env"]+c["f_econ"]+c["f_soc"]+c["f_tech"]
    SA_w = w["env"]*c["f_env"]+w["econ"]*c["f_econ"]+w["soc"]*c["f_soc"]+w["tech"]*c["f_tech"]
    Phi = SA_w/Ex_ref_GJ
    Psi = e["Psi"]
    TSI_abs = alpha*Phi + beta*Psi
    return dict(plant=plant, scenario=scen, **c, SA_raw=SA_raw, SA_w=SA_w,
                Ex_ref_GJ=Ex_ref_GJ, Ex_useful_GJ=e["Ex_useful_MJ"]/core.MJ_PER_GJ,
                Phi=Phi, Psi=Psi, TSI_abs=TSI_abs)

def compute_all(alpha=ALPHA_DEFAULT, beta=BETA_DEFAULT):
    w,lam,CI,CR = weights_and_consistency(TRIAL_MATRIX); w=dict(zip(DIMS,w))
    rows=[]; tsi={}
    for p in core.PLANTS:
        for s in ["historical","realtime"]:
            r=scenario_row(p,s,w,alpha,beta); rows.append(r); tsi[(p,s)]=r["TSI_abs"]
    for p in core.PLANTS:
        for r in rows:
            if r["plant"]==p and r["scenario"]=="realtime":
                r["TSI_rel"]=tsi[(p,"realtime")]/tsi[(p,"historical")]
    return rows, w, (lam,CI,CR)

if __name__=="__main__":
    rows,w,(lam,CI,CR)=compute_all()
    print("AHP w:",{k:round(v,4) for k,v in w.items()},"CR=%.4f"%CR)
    for r in rows:
        rel = ("  TSI_rel=%.3f"%r["TSI_rel"]) if "TSI_rel" in r else ""
        print(f"{r['plant']} {r['scenario']:10} SA_raw={r['SA_raw']:8.0f} SA_w={r['SA_w']:8.0f} Phi={r['Phi']:.4f} Psi={r['Psi']:.3f} TSI_abs={r['TSI_abs']:.4f}{rel}")
