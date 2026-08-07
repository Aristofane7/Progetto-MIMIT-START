# -*- coding: utf-8 -*-
"""Figure 1-6 del report (SVG vettoriale + PNG). Etichette in italiano, stile sobrio, no 3D.
   Tutti i grafici basati su dati DIMOSTRATIVI."""
import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from src import core
from src.integration import compute_all
from src.sensitivity import run as sens_run

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,"output","figures")
GREEN="#0B5A3C"; TEAL="#00A98E"; GREY="#5B6770"
CMAP={"f_env":"#2E7D32","f_econ":"#00A98E","f_soc":"#7BA05B","f_tech":"#0B5A3C"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})

def _save(fig,name):
    fig.savefig(os.path.join(OUT,name+".svg"),bbox_inches="tight",transparent=True)
    fig.savefig(os.path.join(OUT,name+".png"),bbox_inches="tight",dpi=200)
    plt.close(fig)

def _box(ax,x,y,w,h,text,fc=GREEN,tc="white",fs=9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc,ec="none")); ax.text(x+w/2,y+h/2,text,ha="center",va="center",color=tc,fontsize=fs,wrap=True)
def _arrow(ax,x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=13,lw=1.4,color=GREY))

def fig1():
    fig,ax=plt.subplots(figsize=(9,1.9)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,2)
    steps=["Dati primari\n(ERP/MES + E2C)","Armonizzazione","4 moduli -J\nTEI/EFA/EcoFA/SFA","AHP\n(pesi + CR)","Sustainability\nAccounting","Layer exergico\nΦ, Ψ","TSI"]
    w=1.22; gap=0.13; x=0.15
    for i,s in enumerate(steps):
        fc=TEAL if i in (3,6) else GREEN
        _box(ax,x,0.6,w,0.8,s,fc=fc,fs=7.6)
        if i<len(steps)-1: _arrow(ax,x+w,1.0,x+w+gap,1.0)
        x+=w+gap
    ax.set_title("Figura 1 — Architettura della pipeline EEA+ beta",color=GREEN,fontsize=10,loc="left")
    _save(fig,"fig1_architettura")

def fig2():
    fig,ax=plt.subplots(figsize=(7,3.2)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0,6)
    mods=[("TEI-J","f_tech — tecnologica\n(MTS/MTO, perdite, invenduto, qualità)"),
          ("EFA-J","f_env — ambientale\n(RI, WEX, IEQ, CIRC)"),
          ("EcoFA-J","f_econ — economica\n(VA, input, immobilizzi)"),
          ("SFA-J","f_soc — sociale\n(stakeholder, lavoro, CO₂)")]
    ys=[4.6,3.4,2.2,1.0]
    for (m,d),y in zip(mods,ys):
        _box(ax,0.2,y,2.0,0.9,m,fc=GREEN,fs=10); ax.text(2.4,y+0.45,d,va="center",fontsize=8,color="#222")
        _arrow(ax,6.7,y+0.45,7.8,3.0)
    _box(ax,7.8,2.4,1.9,1.2,"Sustainability\nAccounting\n(SA_raw, SA_w)",fc=TEAL,fs=8)
    ax.set_title("Figura 2 — Schema di integrazione dei quattro moduli",color=GREEN,fontsize=10,loc="left")
    _save(fig,"fig2_moduli")

def _rows():
    rows,w,cons=compute_all(); return {(r["plant"],r["scenario"]):r for r in rows}

def fig3(R):
    plants=list(core.PLANTS); import numpy as np
    h=[R[(p,"historical")]["TSI_abs"] for p in plants]; r=[R[(p,"realtime")]["TSI_abs"] for p in plants]
    x=range(len(plants)); wd=0.38
    fig,ax=plt.subplots(figsize=(6,3.4))
    ax.bar([i-wd/2 for i in x],h,wd,label="Storico",color=GREY)
    ax.bar([i+wd/2 for i in x],r,wd,label="Real-time",color=GREEN)
    ax.set_xticks(list(x)); ax.set_xticklabels(plants); ax.set_ylabel("TSI_abs (adim.)")
    for i in x: ax.text(i, max(h[i],r[i])+0.003, f"+{(r[i]/h[i]-1)*100:.0f}%",ha="center",fontsize=8,color=GREEN)
    ax.legend(frameon=False); ax.set_title("Figura 3 — TSI_abs storico vs real-time per unità",color=GREEN,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,"fig3_tsi")

def fig4(R):
    plants=list(core.PLANTS); import numpy as np
    keys=["f_env","f_econ","f_soc","f_tech"]; labels={"f_env":"Ambientale","f_econ":"Economica","f_soc":"Sociale","f_tech":"Tecnologica"}
    fig,ax=plt.subplots(figsize=(6.6,3.4)); x=range(len(plants)); bottom=[0]*len(plants)
    for k in keys:
        vals=[R[(p,"realtime")][k] for p in plants]
        ax.bar(list(x),vals,0.55,bottom=bottom,label=labels[k],color=CMAP[k])
        bottom=[b+v for b,v in zip(bottom,vals)]
    ax.set_xticks(list(x)); ax.set_xticklabels(plants); ax.set_ylabel("Contributo (GJ)")
    ax.legend(frameon=False,ncol=2,fontsize=8); ax.set_title("Figura 4 — Scomposizione dei contributi (real-time)",color=GREEN,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,"fig4_contributi")

def fig5(R):
    plants=list(core.PLANTS)
    fig,ax=plt.subplots(figsize=(5.6,3.6))
    for p in plants:
        for scen,mk,col in [("historical","o",GREY),("realtime","s",GREEN)]:
            r=R[(p,scen)]; ax.scatter(r["Phi"],r["Psi"],marker=mk,s=70,color=col,zorder=3)
            ax.annotate(f"{p}",(r["Phi"],r["Psi"]),textcoords="offset points",xytext=(6,4),fontsize=8)
        ax.annotate("",xy=(R[(p,"realtime")]["Phi"],R[(p,"realtime")]["Psi"]),
                    xytext=(R[(p,"historical")]["Phi"],R[(p,"historical")]["Psi"]),
                    arrowprops=dict(arrowstyle="->",color=TEAL,lw=1.2))
    ax.set_xlabel("Φ — componente multidimensionale"); ax.set_ylabel("Ψ — efficienza exergica")
    ax.scatter([],[],marker="o",color=GREY,label="Storico"); ax.scatter([],[],marker="s",color=GREEN,label="Real-time")
    ax.legend(frameon=False,fontsize=8); ax.set_title("Figura 5 — Posizionamento Φ–Ψ",color=GREEN,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,"fig5_phi_psi")

def fig6():
    s=sens_run(); base=[r for r in s if r["scenario"].startswith("Caso base")][0]
    others=[r for r in s if not r["scenario"].startswith("Caso base")]
    names=[r["scenario"] for r in others]
    mins=[r["rel_min"] for r in others]; maxs=[r["rel_max"] for r in others]
    import numpy as np
    fig,ax=plt.subplots(figsize=(7.2,3.6)); y=range(len(names))
    for i,(mn,mx) in enumerate(zip(mins,maxs)):
        ax.plot([mn,mx],[i,i],color=GREEN,lw=6,solid_capstyle="round",alpha=0.85)
    ax.axvline(1.0,color=GREY,ls="--",lw=1); ax.set_yticks(list(y)); ax.set_yticklabels(names,fontsize=8)
    ax.set_xlabel("TSI_rel (real-time / storico)  —  intervallo tra unità")
    ax.set_title("Figura 6 — Sensibilità del TSI_rel",color=GREEN,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False)
    _save(fig,"fig6_sensibilita")

def make_all():
    fig1(); fig2(); R=_rows(); fig3(R); fig4(R); fig5(R); fig6()
    return 6

if __name__=="__main__":
    print("figure generate:",make_all())
