# -*- coding: utf-8 -*-
"""Sensitivity: robustezza di TSI_rel(2025/2023) e dell'ordinamento (per anno 2025) a variazioni parametriche."""
from src import core
from src.ahp import weights_and_consistency, TRIAL_MATRIX, DIMS
def _tsi(plant,year,w,alpha,beta,fp=1.0,ps=1.0):
    c=core.contributions(plant,year)
    SA_w=(w["env"]*c["f_env"]+w["econ"]*c["f_econ"]+w["soc"]*c["f_soc"]+w["tech"]*c["f_tech"])*fp
    e=core.energy_split(plant,year); Ex_ref=e["Ex_ref_MJ"]/core.MJ_PER_GJ
    return alpha*(SA_w/Ex_ref)+beta*e["Psi"]*ps
def run():
    wb,lam,CI,CR=weights_and_consistency(TRIAL_MATRIX); wb=dict(zip(DIMS,wb)); w_eq={d:.25 for d in DIMS}
    scen=[("Caso base (pesi AHP; alpha=beta=0.5)",dict(w=wb,alpha=.5,beta=.5)),
          ("Coefficienti footprint +10%",dict(w=wb,alpha=.5,beta=.5,fp=1.10)),
          ("Coefficienti footprint -10%",dict(w=wb,alpha=.5,beta=.5,fp=0.90)),
          ("Efficienza exergica Psi +10%",dict(w=wb,alpha=.5,beta=.5,ps=1.10)),
          ("Efficienza exergica Psi -10%",dict(w=wb,alpha=.5,beta=.5,ps=0.90)),
          ("Pesi AHP equidistribuiti (0.25)",dict(w=w_eq,alpha=.5,beta=.5)),
          ("Focus exergico (alpha=0.4, beta=0.6)",dict(w=wb,alpha=.4,beta=.6)),
          ("Focus multidimensionale (alpha=0.6, beta=0.4)",dict(w=wb,alpha=.6,beta=.4))]
    out=[]
    for name,kw in scen:
        rel={p:_tsi(p,core.YEAR_RT,**kw)/_tsi(p,core.YEAR_HIST,**kw) for p in core.PLANTS}
        rt={p:_tsi(p,core.YEAR_RT,**kw) for p in core.PLANTS}
        order=sorted(rt,key=lambda p:rt[p],reverse=True)
        out.append(dict(scenario=name,rel=rel,order=order,rel_min=min(rel.values()),rel_max=max(rel.values())))
    return out
if __name__=="__main__":
    for r in run(): print(f"{r['scenario']:42} rel[{r['rel_min']:.3f}..{r['rel_max']:.3f}] {'>'.join(r['order'])}")
