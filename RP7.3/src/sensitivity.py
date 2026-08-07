# -*- coding: utf-8 -*-
"""Sensitivity analysis: robustezza di TSI_rel e dell'ordinamento a variazioni di coeff., Psi, pesi AHP, alpha/beta."""
from src import core
from src.ahp import weights_and_consistency, TRIAL_MATRIX, DIMS

def _tsi(plant, scen, w, alpha, beta, fp_scale=1.0, psi_scale=1.0):
    c=core.contributions(plant,scen)
    SA_w=(w["env"]*c["f_env"]+w["econ"]*c["f_econ"]+w["soc"]*c["f_soc"]+w["tech"]*c["f_tech"])*fp_scale
    e=core.energy_split(plant,scen); Ex_ref=e["Ex_ref_MJ"]/core.MJ_PER_GJ
    Phi=SA_w/Ex_ref; Psi=e["Psi"]*psi_scale
    return alpha*Phi+beta*Psi

def run():
    wb,lam,CI,CR=weights_and_consistency(TRIAL_MATRIX); wb=dict(zip(DIMS,wb))
    w_eq={d:0.25 for d in DIMS}
    scen=[
        ("Caso base (pesi AHP; alpha=beta=0.5)",           dict(w=wb,alpha=.5,beta=.5)),
        ("Coefficienti footprint +10%",                     dict(w=wb,alpha=.5,beta=.5,fp_scale=1.10)),
        ("Coefficienti footprint -10%",                     dict(w=wb,alpha=.5,beta=.5,fp_scale=0.90)),
        ("Efficienza exergica Psi +10%",                    dict(w=wb,alpha=.5,beta=.5,psi_scale=1.10)),
        ("Efficienza exergica Psi -10%",                    dict(w=wb,alpha=.5,beta=.5,psi_scale=0.90)),
        ("Pesi AHP equidistribuiti (0.25)",                 dict(w=w_eq,alpha=.5,beta=.5)),
        ("Focus exergico (alpha=0.4, beta=0.6)",            dict(w=wb,alpha=.4,beta=.6)),
        ("Focus multidimensionale (alpha=0.6, beta=0.4)",   dict(w=wb,alpha=.6,beta=.4)),
    ]
    out=[]
    for name,kw in scen:
        rel={}; rt={}
        for p in core.PLANTS:
            th=_tsi(p,"historical",**kw); tr=_tsi(p,"realtime",**kw)
            rel[p]=tr/th; rt[p]=tr
        order=sorted(rt,key=lambda p:rt[p],reverse=True)
        out.append(dict(scenario=name, rel=rel, order=order,
                        rel_min=min(rel.values()), rel_max=max(rel.values())))
    return out

if __name__=="__main__":
    for r in run():
        print(f"{r['scenario']:42} TSI_rel[min..max]={r['rel_min']:.3f}..{r['rel_max']:.3f} ordine={'>'.join(r['order'])}")
