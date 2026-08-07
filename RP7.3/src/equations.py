# -*- coding: utf-8 -*-
"""Rende le equazioni del V0 come SVG vettoriale (+ PNG fallback) via matplotlib mathtext.
   Nessun LaTeX visibile, nessuna rasterizzazione del testo (SVG = vettoriale)."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["mathtext.fontset"]="cm"

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"output","figures")

# insieme finito e numerato delle equazioni (mathtext)
EQUATIONS = {
 "eq01": r"$Ex_x = q_x\, b_x$",
 "eq02": r"$b_{mix} = \sum_j w_j\, b_j$",
 "eq03": r"$Ex_{loss}^{MTS} = (Ex_{RM}+Ex_{UW}+Ex_{E,SD}) - Ex_{SDM}$",
 "eq04": r"$IP^{MTS}=\dfrac{Ex_{SDM}}{T_{prod}}\qquad EF^{MTS}=\dfrac{Ex_{SDU}}{Ex_{SDM}}$",
 "eq05": r"$Ex_{qual}^{MTS}=\sum_k \kappa_k \max\!\left(0,\,1-\dfrac{q_k}{\bar q_k}\right)Ex_{SDM}$",
 "eq06": r"$Ex_{loss}^{MTO}=(Ex_{SDU}+Ex_{E,form}+Ex_{E,kiln}+Ex_{E,fin})-Ex_T$",
 "eq07": r"$Ex_{inv}=\left(1-\dfrac{N_T^{sold}}{N_T^{man}}\right)Ex_T$",
 "eq08": r"$f_{tech}=(Ex_{loss,base}^{MTS}+Ex_{loss,base}^{MTO})-(Ex_{loss}^{MTS}+Ex_{loss}^{MTO})-Ex_{inv}-Ex_{qual}^{MTS}-Ex_{qual}^{MTO}$",
 "eq09": r"$RI=Ex_{mat}+Ex_{el}+Ex_{fuel}+Ex_{H_2O}$",
 "eq10": r"$WEX=\sum_k R_k\, b_{w,k}\qquad IEQ=\sum_j Em_j\,\gamma_j\qquad CIRC=Ex_{rec,mat}+Ex_{rec,th}$",
 "eq11": r"$f_{env}=(RI_{base}-RI)+(CIRC-CIRC_{base})-(IEQ-IEQ_{base})-(WEX-WEX_{base})$",
 "eq12": r"$Ex_{econ,in}=\sum_c C_c\,\gamma_c\qquad Ex_{VA}=VA\,\gamma_{VA}\qquad Ex_{INV}=INV\,\gamma_{INV}$",
 "eq13": r"$f_{econ}=(Ex_{VA}-Ex_{VA,base})-(Ex_{econ,in}-Ex_{econ,in,base})-(Ex_{INV}-Ex_{INV,base})$",
 "eq14": r"$Ex_{SV}=\sum_{stk} V_{stk}\,\gamma_{\euro}\quad Ex_{lost}=H_{lost}\,b_{L,h}\quad Ex_{train}=\rho_{train}H_{train}b_{L,h}\quad Ex_{CO_2}=Em_{CO_2}\gamma_{CO_2}$",
 "eq15": r"$f_{soc}=(Ex_{SV}-Ex_{SV,base})+(Ex_{train}-Ex_{train,base})-(Ex_{lost}-Ex_{lost,base})-(Ex_{CO_2}-Ex_{CO_2,base})$",
 "eq16": r"$SA_{raw}=\sum_i f_i\qquad SA_{w}=\sum_i w_i\, f_i$",
 "eq17": r"$\Phi=\dfrac{SA_{w}}{Ex_{ref}}\qquad \Psi=\dfrac{Ex_{useful}}{Ex_{ref}}$",
 "eq18": r"$Ex_{el}=3.6\,E_{el,kWh}\qquad Ex_{fuel}=V_{fuel}\,b_{fuel}$",
 "eq19": r"$TSI_{abs}=\alpha\,\Phi+\beta\,\Psi,\qquad \alpha+\beta=1$",
 "eq20": r"$TSI_{rel}=\dfrac{TSI_{abs,\,current}}{TSI_{abs,\,base}}$",
 "eq21": r"$CI=\dfrac{\lambda_{max}-n}{n-1}\qquad CR=\dfrac{CI}{RI}\qquad CR\leq 0.10$",
}
# rimuovo \euro (non in mathtext cm): uso testo
EQUATIONS["eq14"]=EQUATIONS["eq14"].replace(r"\gamma_{\euro}", r"\gamma_{eur}")

def render(name, tex, fontsize=17):
    fig=plt.figure(figsize=(0.1,0.1)); fig.patch.set_alpha(0)
    t=fig.text(0.5,0.5,tex,fontsize=fontsize,ha="center",va="center")
    svg=os.path.join(OUT,name+".svg"); png=os.path.join(OUT,name+".png")
    for path,dpi in [(svg,None),(png,300)]:
        kw=dict(bbox_inches="tight",pad_inches=0.06,transparent=True)
        if dpi: kw["dpi"]=dpi
        fig.savefig(path,**kw)
    plt.close(fig); return svg,png

def render_all():
    n=0
    for k,v in EQUATIONS.items():
        render(k,v); n+=1
    return n

if __name__=="__main__":
    print("equazioni renderizzate:", render_all())
