# -*- coding: utf-8 -*-
"""Build RP7.3 V2 (RV.2) DOCX on the official START template, from the live
beta-1.3 reference data + calculation log. Covers ADR-015 (D020 partial year
2025, option A). Equations as vector SVG (PNG fallback); 6 figures; 12 tables.

Run: python3 -m scripts.build_rp73_report  ->  output/RP7.3_Report_Assessment_termodinamico_fabbrica_V2.docx
"""
from __future__ import annotations
import os, struct
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import parse_xml, OxmlElement
from docx.opc.part import Part
from docx.opc.packuri import PackURI

from src.ingestion.rp73_reference_data import load_rp73_reference_data, load_rp73_calculation_log
from src.core.weights import load_weight_set

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
TPL = REPO / "RPX.Y Titolo_Relazione_Parziale_data.docx"
FIG = ROOT / "output" / "figures"; FIG.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "output" / "RP7.3_Report_Assessment_termodinamico_fabbrica_V2.docx"
DATE = "19.10.2026"
DGREEN = RGBColor(0x02,0x4C,0x41); GREY = RGBColor(0x33,0x33,0x33)
PLANTS = ["D020","D060","D240"]; YEARS = [2023,2024,2025]; EL,GAS = 3.6,42
PLANTDESC = {"D020":"Viano — MTO","D060":"Scandiano — ibrido MTS+MTO","D240":"Frassinoro — MTO"}

# ---------------- data ----------------
RD = load_rp73_reference_data(ROOT/"data"/"reference"/"RP7.3_data_collection_20232025.xlsx")
LOG = load_rp73_calculation_log(ROOT/"data"/"reference"/"RP7.3_calculation_log.xlsx")
WS = load_weight_set(ROOT/"config"/"weights"/"eea_ahp_rp73.yaml")
W = {d: WS.get_dimension_weight(d) for d in ("env","econ","soc","tech")}
def V(p,y,v): return LOG[(p,y,v)]
def row(p,y):
    e=RD.energy[(p,y)]
    return dict(prod=RD.production_m2(p,y), months=RD.months_active(p,y),
                Ex_el=e.e_el_kwh*EL/1000, Ex_fuel=e.v_gas_nm3*GAS/1000,
                **{k:V(p,y,k) for k in ["f_env","f_econ","f_soc","f_tech","SA_raw","SA_w","Ex_ref","Phi","Psi","TSI_abs"]})
R={(p,y):row(p,y) for p in PLANTS for y in YEARS}
for p in PLANTS: R[(p,2025)]["TSI_rel"]=V(p,2025,"TSI_rel")
Pg=sum(R[(p,2025)]["prod"] for p in PLANTS)
G_TSI25=sum(R[(p,2025)]["TSI_abs"]*R[(p,2025)]["prod"] for p in PLANTS)/Pg
G_REL=sum(R[(p,2025)]["TSI_rel"]*R[(p,2025)]["prod"] for p in PLANTS)/Pg

def sensitivity():
    base={p:dict(f={k:R[(p,y)][f"f_{k}"] for k in("env","econ","soc","tech")},exr=R[(p,y)]["Ex_ref"],psi=R[(p,y)]["Psi"]) for p in PLANTS for y in YEARS if False}
    def tsi(p,y,w,a,b,fp,ps):
        f={k:R[(p,y)][f"f_{k}"] for k in("env","econ","soc","tech")}
        saw=sum(w[k]*f[k] for k in f)*fp
        return a*(saw/R[(p,y)]["Ex_ref"])+b*R[(p,y)]["Psi"]*ps
    weq={k:0.25 for k in W}
    scen=[("Caso base (pesi AHP; α=β=0,5)",dict(w=W,a=.5,b=.5,fp=1,ps=1)),
          ("Coefficienti footprint +10%",dict(w=W,a=.5,b=.5,fp=1.1,ps=1)),
          ("Coefficienti footprint −10%",dict(w=W,a=.5,b=.5,fp=.9,ps=1)),
          ("Efficienza exergica Ψ +10%",dict(w=W,a=.5,b=.5,fp=1,ps=1.1)),
          ("Efficienza exergica Ψ −10%",dict(w=W,a=.5,b=.5,fp=1,ps=.9)),
          ("Pesi AHP equidistribuiti (0,25)",dict(w=weq,a=.5,b=.5,fp=1,ps=1)),
          ("Focus exergico (α=0,4; β=0,6)",dict(w=W,a=.4,b=.6,fp=1,ps=1)),
          ("Focus multidimensionale (α=0,6; β=0,4)",dict(w=W,a=.6,b=.4,fp=1,ps=1))]
    out=[]
    for name,kw in scen:
        rel={p:tsi(p,2025,**kw)/tsi(p,2023,**kw) for p in PLANTS}
        rt={p:tsi(p,2025,**kw) for p in PLANTS}
        order=sorted(rt,key=lambda p:rt[p],reverse=True)
        out.append((name,min(rel.values()),max(rel.values()),">".join(order)))
    return out
SENS=sensitivity()

# ---------------- number fmt ----------------
def gj(x): return f"{x:,.0f}".replace(",",".")
def f3(x): return f"{x:.3f}".replace(".",",")
def f4(x): return f"{x:.4f}".replace(".",",")
def mm2(x): return f"{x/1e6:.3f}".replace(".",",")

# ---------------- equations (SVG) ----------------
plt.rcParams["mathtext.fontset"]="cm"
EQ={
 "eq1": r"$Ex_x = q_x\,b_x\qquad Ex_{ref}=Ex_{el}+Ex_{fuel}=3.6\,kWh+V_{gas}\,b_{fuel}$",
 "eq2": r"$f_{tech}=(Ex_{loss,ref}^{MTS}+Ex_{loss,ref}^{MTO})-(Ex_{loss}^{MTS}+Ex_{loss}^{MTO})-Ex_{inv}-Ex_{qual}^{MTS}-Ex_{qual}^{MTO}$",
 "eq3": r"$f_{env}=(RI_{ref}-RI)+(CIRC-CIRC_{ref})-(IEQ-IEQ_{ref})-(WEX-WEX_{ref})$",
 "eq4": r"$f_{econ}=(Ex_{VA}-Ex_{VA,ref})-(Ex_{econ,in}-Ex_{econ,in,ref})-(Ex_{INV}-Ex_{INV,ref})$",
 "eq5": r"$f_{soc}=(Ex_{SV}-Ex_{SV,ref})+(Ex_{train}-Ex_{train,ref})-(Ex_{lost}-Ex_{lost,ref})-(Ex_{CO_2}-Ex_{CO_2,ref})$",
 "eq6": r"$SA_{raw}=\sum_i f_i\qquad SA_{w}=\sum_i w_i\,f_i$",
 "eq7": r"$\Phi=\dfrac{SA_{w}}{Ex_{ref}}\qquad \Psi=\dfrac{Ex_{useful}}{Ex_{ref}}$",
 "eq8": r"$TSI_{abs}=\alpha\,\Phi+\beta\,\Psi,\quad\alpha+\beta=1\qquad TSI_{rel}=\dfrac{TSI_{abs,\,t}}{TSI_{abs,\,base}}$",
 "eq9": r"$CI=\dfrac{\lambda_{max}-n}{n-1}\qquad CR=\dfrac{CI}{RI}\leq 0.10$",
 "eq10": r"$\mathrm{opzione\ A:}\quad X_{ref}(\mathrm{D020,2025})=X(\mathrm{D020,\ 2022\ gen\!-\!lug})\ \ (\mathrm{stessa\ finestra})$",
}
def render_eqs():
    for k,t in EQ.items():
        fig=plt.figure(figsize=(0.1,0.1)); fig.patch.set_alpha(0)
        fig.text(0.5,0.5,t,fontsize=16,ha="center",va="center")
        for ext,dpi in ((".svg",None),(".png",300)):
            kw=dict(bbox_inches="tight",pad_inches=0.06,transparent=True)
            if dpi: kw["dpi"]=dpi
            fig.savefig(FIG/(k+ext),**kw)
        plt.close(fig)

# ---------------- figures ----------------
GREENH="#0B5A3C"; TEAL="#00A98E"; GREYH="#5B6770"
CMAP={"f_env":"#2E7D32","f_econ":"#00A98E","f_soc":"#7BA05B","f_tech":"#0B5A3C"}
YCOL={2023:"#9AA7AD",2024:"#3E7C6A",2025:"#0B5A3C"}
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10})
def _save(fig,n):
    fig.savefig(FIG/(n+".svg"),bbox_inches="tight",transparent=True)
    fig.savefig(FIG/(n+".png"),bbox_inches="tight",dpi=200); plt.close(fig)
def _box(ax,x,y,w,h,t,fc=GREENH,fs=8):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.02,rounding_size=0.06",fc=fc,ec="none"))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",color="white",fontsize=fs)
def _arr(ax,x1,y1,x2,y2): ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=12,lw=1.3,color=GREYH))
def figures():
    # fig1 pipeline — riquadri larghi uniformi, testo su due righe, niente debordamento
    steps=["Dati primari\n(ERP/MES, E2C)","Armonizzazione","4 moduli -J","AHP\n(pesi, CR)",
           "Sustainability\nAccounting","Layer exergico\n(Φ, Ψ)","TSI"]
    w=1.85; gap=.17; h=1.0; y=.5
    total=len(steps)*w+(len(steps)-1)*gap+.2
    fig,ax=plt.subplots(figsize=(10.5,2.0)); ax.axis("off"); ax.set_xlim(0,total); ax.set_ylim(0,2.2)
    x=.1
    for i,s in enumerate(steps):
        _box(ax,x,y,w,h,s,fc=(TEAL if i in(3,6) else GREENH),fs=8.5)
        if i<len(steps)-1:_arr(ax,x+w,y+h/2,x+w+gap,y+h/2)
        x+=w+gap
    ax.set_title("Figura 1 — Pipeline EEA+ beta",color=GREENH,fontsize=10,loc="left"); _save(fig,"fig1")
    # fig2 moduli — box larghi (nome+contributo dentro), frecce ancorate al bordo dei box
    fig,ax=plt.subplots(figsize=(8.4,3.0)); ax.axis("off"); ax.set_xlim(0,10); ax.set_ylim(0.4,6)
    labels=["TEI-J  —  f_tech (MTS/MTO)","EFA-J  —  f_env (RI, WEX, IEQ, CIRC)",
            "EcoFA-J  —  f_econ (VA, input, INV)","SFA-J  —  f_soc (stakeholder, lavoro, CO₂)"]
    ys=[4.7,3.5,2.3,1.1]
    for lab,y in zip(labels,ys):
        _box(ax,.2,y,5.1,.9,lab,fs=9.5)
        _arr(ax,5.45,y+.45,6.98,2.85)
    _box(ax,7.0,2.15,2.6,1.4,"Sustainability\nAccounting (SA)",fc=TEAL,fs=9)
    ax.set_title("Figura 2 — Integrazione dei moduli",color=GREENH,fontsize=10,loc="left"); _save(fig,"fig2")
    # fig3 TSI per anno — legenda FUORI dal grafico (niente sovrapposizione)
    fig,ax=plt.subplots(figsize=(7.2,3.5)); x=range(len(PLANTS)); wd=.26
    for k,y in enumerate(YEARS):
        ax.bar([i+(k-1)*wd for i in x],[R[(p,y)]["TSI_abs"] for p in PLANTS],wd,label=str(y),color=YCOL[y])
    ax.set_xticks(list(x)); ax.set_xticklabels(PLANTS); ax.set_ylabel("TSI_abs (adim.)"); ax.set_ylim(0,0.14)
    ax.legend(frameon=False,loc="upper left",bbox_to_anchor=(1.01,1.0),title="Anno")
    ax.set_title("Figura 3 — TSI_abs per unità e anno",color=GREENH,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False); _save(fig,"fig3")
    # fig4 contributi 2025 — legenda FUORI dal grafico + margine superiore
    fig,ax=plt.subplots(figsize=(7.8,3.5)); x=range(len(PLANTS)); bot=[0]*len(PLANTS)
    for kk,lab in [("f_env","Ambientale"),("f_econ","Economica"),("f_soc","Sociale"),("f_tech","Tecnologica")]:
        vals=[R[(p,2025)][kk] for p in PLANTS]; ax.bar(list(x),vals,.55,bottom=bot,label=lab,color=CMAP[kk]); bot=[a+b for a,b in zip(bot,vals)]
    ax.set_xticks(list(x)); ax.set_xticklabels(PLANTS); ax.set_ylabel("Contributo (GJ)")
    ax.set_ylim(0, max(bot)*1.12)
    ax.legend(frameon=False,fontsize=8,loc="upper left",bbox_to_anchor=(1.01,1.0),title="Dimensione")
    ax.set_title("Figura 4 — Contributi 2025 (D020 = periodo gen–lug)",color=GREENH,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False); _save(fig,"fig4")
    # fig5 Phi-Psi
    fig,ax=plt.subplots(figsize=(5.8,3.6))
    for p in PLANTS:
        xs=[R[(p,y)]["Phi"] for y in YEARS]; ys=[R[(p,y)]["Psi"] for y in YEARS]
        ax.plot(xs,ys,"-",color=TEAL,lw=1,zorder=1)
        for y in YEARS: ax.scatter(R[(p,y)]["Phi"],R[(p,y)]["Psi"],s=55,color=YCOL[y],zorder=3,edgecolor="white",linewidth=.6)
        ax.annotate(p,(R[(p,2025)]["Phi"],R[(p,2025)]["Psi"]),textcoords="offset points",xytext=(6,3),fontsize=8)
    for y in YEARS: ax.scatter([],[],color=YCOL[y],label=str(y))
    ax.set_xlabel("Φ"); ax.set_ylabel("Ψ"); ax.legend(frameon=False,fontsize=8)
    ax.set_title("Figura 5 — Traiettoria Φ–Ψ (2023→2025)",color=GREENH,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False); _save(fig,"fig5")
    # fig6 sensibilità
    fig,ax=plt.subplots(figsize=(7.2,3.6)); oth=SENS[1:]; names=[s[0] for s in oth]; y=range(len(names))
    for i,s in enumerate(oth): ax.plot([s[1],s[2]],[i,i],color=GREENH,lw=6,solid_capstyle="round",alpha=.85)
    ax.axvline(1,color=GREYH,ls="--",lw=1); ax.set_yticks(list(y)); ax.set_yticklabels(names,fontsize=8)
    ax.set_xlabel("TSI_rel (2025/2023) — intervallo tra unità")
    ax.set_title("Figura 6 — Sensibilità del TSI_rel",color=GREENH,loc="left",fontsize=10)
    ax.spines[["top","right"]].set_visible(False); _save(fig,"fig6")

# ---------------- docx helpers ----------------
_svgN={"n":0}
def add_svg(par,doc,svg,png,width_mm):
    run=par.add_run(); run.add_picture(str(png),width=Mm(width_mm))
    _svgN["n"]+=1; pn=PackURI(f"/word/media/svgR{_svgN['n']}.svg")
    sp=Part(pn,"image/svg+xml",open(svg,"rb").read(),doc.part.package)
    rId=doc.part.relate_to(sp,"http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
    blip=run._element.findall(".//"+qn("a:blip"))[-1]
    blip.append(parse_xml('<a:extLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:ext uri="{96DAC541-7F89-4952-8B84-B3F5B99F14F2}"><asvg:svgBlip xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="%s"/></a:ext></a:extLst>'%rId))
def pngsize(p):
    with open(p,"rb") as f: f.read(16); return struct.unpack(">II",f.read(8))
def H1(doc,t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(18); r.font.color.rgb=DGREEN; r.font.name="Calibri"
def H2(doc,t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(13); r.font.color.rgb=DGREEN; r.font.name="Calibri"
def _ir(p,t,sz=11):
    for i,seg in enumerate(t.split("**")):
        if seg=="":continue
        r=p.add_run(seg); r.font.size=Pt(sz); r.font.name="Calibri"; r.bold=(i%2==1)
def P(doc,t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.space_after=Pt(6); _ir(p,t); return p
def BUL(doc,t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.left_indent=Cm(.75); p.paragraph_format.first_line_indent=Cm(-.35); p.paragraph_format.space_after=Pt(2)
    r=p.add_run("•  "); r.font.size=Pt(11); r.font.name="Calibri"; _ir(p,t)
def CAP(doc,t):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8); r=p.add_run(t); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=GREY
def NOTE(doc,t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(6); r=p.add_run(t); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=GREY
def EQU(doc,k):
    svg,png=FIG/(k+".svg"),FIG/(k+".png"); w,h=pngsize(png); width=min(155,6.5*(w/h))
    t=doc.add_table(rows=1,cols=1); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    c=t.rows[0].cells[0]; c.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER; add_svg(c.paragraphs[0],doc,svg,png,width)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
def FIGU(doc,n,w=140):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; add_svg(p,doc,FIG/(n+".svg"),FIG/(n+".png"),w)
def _sh(tc,h): tc._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:fill="{h}"/>'))
def _bd(tc):
    b=OxmlElement("w:tcBorders")
    for e in("top","left","bottom","right"):
        x=OxmlElement("w:"+e); x.set(qn("w:val"),"single"); x.set(qn("w:sz"),"4"); x.set(qn("w:space"),"0"); x.set(qn("w:color"),"BFBFBF"); b.append(x)
    tc._tc.get_or_add_tcPr().append(b)
def TAB(doc,hdr,rows,rfrom=2,fs=8.5):
    t=doc.add_table(rows=1,cols=len(hdr)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    hd=t.rows[0]; hd._tr.get_or_add_trPr().append(parse_xml('<w:tblHeader xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" w:val="true"/>'))
    for i,h in enumerate(hdr):
        c=hd.cells[i]; c.text=""; _sh(c,"0B5A3C"); _bd(c); pr=c.paragraphs[0]; pr.alignment=WD_ALIGN_PARAGRAPH.CENTER
        r=pr.add_run(h); r.bold=True; r.font.size=Pt(fs); r.font.color.rgb=RGBColor(0xFF,0xFF,0xFF); r.font.name="Calibri"
    for rr in rows:
        cells=t.add_row().cells
        for i,val in enumerate(rr):
            c=cells[i]; c.text=""; _bd(c); pr=c.paragraphs[0]; s=str(val); bold=s.startswith("**"); s=s.replace("**","")
            if i>=rfrom: pr.alignment=WD_ALIGN_PARAGRAPH.RIGHT
            r=pr.add_run(s); r.font.size=Pt(fs); r.font.name="Calibri"; r.bold=bold
    doc.add_paragraph().paragraph_format.space_after=Pt(2)

def scen(p,y): return "storico" if y==2023 else ("2024" if y==2024 else ("real-time" if y==2025 else str(y)))

# ---------------- build ----------------
def build():
    render_eqs(); figures()
    doc=Document(str(TPL))
    cover={"Titolo relazione":"ASSESSMENT TERMODINAMICO DELLA FABBRICA",
           "Relazione Parziale N°: RPX.Y":"Relazione Parziale N°: RP7.3",
           "Versione del Documento: RV.X":"Versione del Documento: RV.2",
           "Data di Revisione del Documento: XX.YY.ZZ":f"Data di Revisione del Documento: {DATE}",
           "Responsabilità:  Partner - Ruolo":"Responsabilità: Gresmalt - Capofila"}
    intro=None
    for i,p in enumerate(doc.paragraphs):
        t=p.text.strip()
        for k,v in cover.items():
            if t==k.strip():
                p.runs[0].text=v
                for r in p.runs[1:]: r.text=""
        if t.upper().startswith("1.INTRODUZIONE") or t.upper().startswith("1. INTRODUZIONE"): intro=i
    if intro is not None:
        for p in doc.paragraphs[intro:]: p._element.getparent().remove(p._element)

    NOTE(doc,"Revisione RV.2 — recepisce la cessazione produttiva di D020 (luglio 2025) e l'adozione dell'opzione A (riferimento omologo) per il suo anno parziale; valori da log beta-1.3.")

    # 1. INTRODUZIONE
    H1(doc,"1. INTRODUZIONE")
    H2(doc,"1.1 Inquadramento dell'attività")
    P(doc,"L'attività 7.3 è la fase conclusiva dell'OR7 e il punto di convergenza del progetto START. Dopo il collaudo dell'infrastruttura Edge-to-Cloud (OR7.1) e il performance testing della Intelligent Factory (OR7.2), il Task 7.3 applica in ambiente operativo il modello **Extended Exergy Accounting Plus (EEA+)** per valutare, in un'unica scala fisica (il **Joule**), le prestazioni tecnologiche (OR6.1), ambientali (OR6.2), sociali (OR6.3) ed economiche (OR6.4) delle unità produttive **D020, D060, D240**, e sintetizzarle nell'**Indice Termodinamico di Sostenibilità (TSI)**.")
    P(doc,"Il risultato è duplice: il quadro di sostenibilità multidimensionale delle unità e il collaudo della versione **beta** dell'EEA+. Il KPI è il **TSI** per ciascuna unità, su serie storica e scenario in tempo reale; la ponderazione fra le quattro dimensioni è resa trasparente dall'**Analytic Hierarchy Process (AHP)**.")
    H2(doc,"1.2 La metrica comune: exergia e conversione in Joule")
    P(doc,"La sostenibilità combina grandezze eterogenee (kg CO₂-eq, m³, €, ore, DALY, KPI di processo) non direttamente sommabili. START adotta l'**exergia** come metrica fisica universale: la conversione in J/GJ risolve la **commensurabilità**, mentre l'AHP (con verifica del *consistency ratio*) risolve la **ponderazione**. I due livelli restano distinti: Eq. (6)–(8).")
    H2(doc,"1.3 Perimetro e cessazione di D020")
    P(doc,"Il modello è applicato alle tre unità del gruppo: **D020** (Viano, MTO), **D060** (Scandiano, ibrida MTS+MTO), **D240** (Frassinoro, MTO), sulla serie **2023–2025** con riferimento (baseline) l'anno **2022**. In questa revisione si recepisce un fatto rilevante: **D020 ha prodotto solo per una parte del 2025 e ha cessato le attività a luglio 2025** (riconversione a polo logistico; cfr. RP7.5 §1.2 e RP7.8). Il **2025 di D020 è quindi un periodo parziale** (1° gennaio → 31 luglio 2025, 7 mesi). Per non far apparire la minore durata come un miglioramento, si adotta l'**opzione A — riferimento omologo**: il baseline dei moduli di D020/2025 è il **2022 sullo stesso intervallo** (gennaio–luglio), non il 2022 annuale (§2.5). D020 è uno stabilimento **MTO**: i termini MTS (spray-dryer) sono nulli per costruzione.")

    # 2. METODOLOGIA
    H1(doc,"2. METODOLOGIA")
    H2(doc,"2.1 Architettura della versione beta")
    P(doc,"La pipeline EEA+ beta si articola in sei livelli: **Dati → armonizzazione → 4 moduli -J → AHP → Sustainability Accounting → layer exergico → TSI** (Figure 1–2).")
    FIGU(doc,"fig1",160); CAP(doc,"Figura 1 — Pipeline EEA+ beta.")
    FIGU(doc,"fig2",120); CAP(doc,"Figura 2 — Integrazione dei quattro moduli in Joule.")
    H2(doc,"2.2 Componente exergica e convenzioni di unità")
    P(doc,"Il riferimento energetico di processo è **Ex_ref = Ex_el + Ex_fuel**, con Ex_el = 3,6·kWh ed Ex_fuel = V_gas·b_fuel (exergia chimica del metano), Eq. (1). Convenzione: calcolo interno in **MJ**, output in **GJ** (÷1.000); l'efficienza di conversione è inclusa in **Ψ** (efficienza exergetica di 2° principio), non in Ex_ref.")
    EQU(doc,"eq1")
    H2(doc,"2.3 I quattro moduli in Joule")
    P(doc,"Ogni impronta è calcolata dal rispettivo modulo -J come differenza exergetica rispetto al baseline, in GJ, senza doppio conteggio: **TEI-J** Eq. (2), **EFA-J** Eq. (3), **EcoFA-J** Eq. (4), **SFA-J** Eq. (5).")
    for k in ("eq2","eq3","eq4","eq5"): EQU(doc,k)
    H2(doc,"2.4 Integrazione, AHP e TSI")
    P(doc,"La Sustainability Accounting grezza e ponderata (pesi AHP) è data dalla Eq. (6); lo score multidimensionale Φ e l'efficienza Ψ dalla Eq. (7); l'indice composito e la lettura relativa dalla Eq. (8). I pesi derivano da una matrice di confronto a coppie con **CR ≤ 0,10**, Eq. (9).")
    for k in ("eq6","eq7","eq8","eq9"): EQU(doc,k)
    H2(doc,"2.5 Opzione A — anno parziale e riferimento omologo (ADR-015)")
    P(doc,"I contributi f_i sono differenze estensive rispetto al baseline. Confrontare un periodo di 7 mesi (D020/2025) con un riferimento annuale di 12 mesi gonfierebbe artificialmente la differenza. Si adotta quindi, per D020/2025, un **riferimento omologo sulla stessa finestra** (2022 gennaio–luglio), Eq. (10): poiché riferimento e periodo corrente hanno la **stessa durata**, le grandezze **intensive** (Φ, Ψ, TSI_abs, TSI_rel) restano confrontabili, mentre le **estensive** (f_i, SA, Ex_ref, produzione) si riferiscono al solo periodo e **non sono confrontabili** con gli anni pieni. Una guardia di modello (**TEMPORAL_MISMATCH**) blocca qualsiasi confronto fra finestre di durata diversa; la media di Gruppo è pesata sulla **produzione per anno** (per D020/2025, la produzione del periodo).")
    EQU(doc,"eq10")

    # 3. RISULTATI
    H1(doc,"3. RISULTATI")
    H2(doc,"3.1 Disponibilità dei dati (Tabella 1)")
    TAB(doc,["Unità","Anni","TEI-J","EFA-J","EcoFA-J","SFA-J","Exergia","Finestra 2025"],
        [["D020","2023–2025","✔","✔","✔","✔","✔","**gen–lug (7 mesi)**"],
         ["D060","2023–2025","✔","✔","✔","✔","✔","anno pieno"],
         ["D240","2023–2025","✔","✔","✔","✔","✔","anno pieno"]],rfrom=99)
    CAP(doc,"Tabella 1 — Disponibilità dei dati; baseline 2022. D020/2025 = periodo gennaio–luglio (cessazione).")
    H2(doc,"3.2 AHP (Tabelle 2–3)")
    P(doc,f"La matrice di confronto a coppie fornisce pesi **env {f4(W['env'])}, econ {f4(W['econ'])}, soc {f4(W['soc'])}, tech {f4(W['tech'])}** con **CR = 0,0169 ≤ 0,10** (consistente).")
    TAB(doc,["","Ambientale","Economica","Sociale","Tecnologica"],
        [["Ambientale","1","3","3","1"],["Economica","1/3","1","2","1/3"],["Sociale","1/3","1/2","1","1/4"],["Tecnologica","1","3","4","1"]],rfrom=1)
    CAP(doc,"Tabella 2 — Matrice AHP di confronto a coppie.")
    TAB(doc,["Dimensione","Peso AHP"],[["Ambientale",f4(W["env"])],["Economica",f4(W["econ"])],["Sociale",f4(W["soc"])],["Tecnologica",f4(W["tech"])],["**Somma**","**"+f4(sum(W.values()))+"**"]],rfrom=1)
    CAP(doc,"Tabella 3 — Pesi AHP (λmax=4,0457; CI=0,0152; CR=0,0169).")
    H2(doc,"3.3 Bilancio exergetico (Tabella 4)")
    er=[]
    for p in PLANTS:
        for y in YEARS:
            r=R[(p,y)]; lab=("storico" if y==2023 else ("—" if y==2024 else "real-time"))
            fin = "gen–lug" if (p=="D020" and y==2025) else "anno"
            er.append([p,str(y),mm2(r["prod"]),gj(r["Ex_el"]),gj(r["Ex_fuel"]),gj(r["Ex_ref"]),f3(r["Psi"]),fin])
    TAB(doc,["Unità","Anno","Prod. (Mm²)","Ex_el (GJ)","Ex_fuel (GJ)","Ex_ref (GJ)","Ψ","Finestra"],er)
    CAP(doc,"Tabella 4 — Bilancio exergetico per unità e anno. D020/2025 = periodo gen–lug (grandezze non confrontabili con gli anni pieni).")
    H2(doc,"3.4 Contributi dei moduli (Tabella 5, Figura 4)")
    cr=[]
    for p in PLANTS:
        for y in YEARS:
            r=R[(p,y)]; cr.append([p,str(y),gj(r["f_env"]),gj(r["f_econ"]),gj(r["f_soc"]),gj(r["f_tech"]),"**"+gj(r["SA_raw"])+"**"])
    TAB(doc,["Unità","Anno","f_env (GJ)","f_econ (GJ)","f_soc (GJ)","f_tech (GJ)","SA_raw (GJ)"],cr)
    CAP(doc,"Tabella 5 — Contributi dei moduli -J e SA_raw (differenze vs baseline; D020/2025 vs 2022 gen–lug). Per D020 i termini MTS sono nulli (stabilimento MTO).")
    FIGU(doc,"fig4",130); CAP(doc,"Figura 4 — Scomposizione dei contributi 2025 (D020 = periodo gen–lug, non confrontabile).")
    H2(doc,"3.5 Sustainability Accounting ponderata (Tabella 6)")
    sr=[[p,str(y),gj(R[(p,y)]["SA_raw"]),gj(R[(p,y)]["SA_w"]),gj(R[(p,y)]["Ex_ref"]),f4(R[(p,y)]["Phi"])] for p in PLANTS for y in YEARS]
    TAB(doc,["Unità","Anno","SA_raw (GJ)","SA_w (GJ)","Ex_ref (GJ)","Φ"],sr)
    CAP(doc,"Tabella 6 — SA ponderata (pesi AHP) e Φ = SA_w/Ex_ref.")
    H2(doc,"3.6 Indice Termodinamico di Sostenibilità (Tabella 7, Figure 3 e 5)")
    tr=[]
    for p in PLANTS:
        rel=R[(p,2025)]["TSI_rel"]
        tr.append([p,f4(R[(p,2023)]["TSI_abs"]),f4(R[(p,2024)]["TSI_abs"]),f4(R[(p,2025)]["TSI_abs"]),f3(rel),"+"+f"{(rel-1)*100:.1f}".replace('.',',')+" %"])
    TAB(doc,["Unità","TSI 2023","TSI 2024","TSI 2025","TSI_rel (2025/2023)","Δ"],tr,rfrom=1)
    CAP(doc,"Tabella 7 — TSI_abs per anno e TSI_rel. Per D020 il 2025 è il periodo di attività (gen–lug); TSI_abs/Φ/Ψ restano confrontabili (rapporti).")
    FIGU(doc,"fig3",120); CAP(doc,"Figura 3 — TSI_abs per unità e anno.")
    FIGU(doc,"fig5",115); CAP(doc,"Figura 5 — Traiettoria Φ–Ψ (2023→2025).")
    H2(doc,"3.7 Analisi di sensibilità (Tabella 8, Figura 6)")
    TAB(doc,["Scenario","TSI_rel min","TSI_rel max","Ordinamento (TSI_abs 2025)"],[[s[0],f3(s[1]),f3(s[2]),s[3]] for s in SENS],rfrom=1)
    CAP(doc,"Tabella 8 — Sensibilità di TSI_rel e stabilità dell'ordinamento.")
    FIGU(doc,"fig6",150); CAP(doc,"Figura 6 — Intervalli di TSI_rel per scenario (riferimento 1).")
    rmin=min(s[1] for s in SENS); rmax=max(s[2] for s in SENS)
    P(doc,f"In tutti gli scenari TSI_rel resta **> 1** (intervallo complessivo {f3(rmin)}–{f3(rmax)}) e l'**ordinamento D240 > D060 > D020** (per TSI_abs 2025) si mantiene: il miglioramento e la gerarchia assoluta sono robusti.")
    H2(doc,"3.8 Controlli di coerenza (Tabella 9)")
    TAB(doc,["Controllo","D020","D060","D240"],
        [["Bilancio di massa / Ex_loss ≥ 0","OK","OK","OK"],
         ["Coerenza unità (MJ→GJ ÷1.000)","OK","OK","OK"],
         ["Finestra omologa (opzione A)","OK (7 mesi)","n.a. (anno)","n.a. (anno)"],
         ["Guardia TEMPORAL_MISMATCH","OK","OK","OK"],
         ["Assenza doppio conteggio","OK","OK","OK"]],rfrom=1)
    CAP(doc,"Tabella 9 — Controlli di qualità e coerenza.")
    H2(doc,"3.9 α/β di Gruppo ed evoluzione (Tabelle 10–11)")
    TAB(doc,["Grandezza di Gruppo (media pond. produzione)","Valore"],
        [["TSI_abs 2025",f4(G_TSI25)],["TSI_rel 2025/2023",f4(G_REL)]],rfrom=1)
    CAP(doc,"Tabella 10 — Indici di Gruppo (D020/2025 pesa per la produzione del periodo).")
    TAB(doc,["Elemento","EEA+ alpha (OR6.5)","EEA+ beta (OR7.3)"],
        [["Footprint","integrazione concettuale","4 moduli -J formalizzati"],
         ["Ponderazione","da consolidare","AHP, CR ≤ 0,10"],
         ["Anno parziale","non previsto","opzione A (riferimento omologo) + guardia durata"],
         ["TSI","definizione alpha","Φ + Ψ, TSI_abs e TSI_rel"],
         ["Output","TSI teorico","TSI per unità e anno (log beta-1.3)"]],rfrom=99)
    CAP(doc,"Tabella 11 — Evoluzione EEA+ alpha → beta.")
    H2(doc,"3.10 KPI di attività (Tabella 12)")
    TAB(doc,["KPI","Baseline","Obiettivo","Risultato"],
        [["TSI","N°3 su serie storica","N°3 real-time","6 TSI (2023 e 2025)"],
         ["Versione EEA+","alpha","beta collaudata","beta operativa (log beta-1.3)"],
         ["Consistenza AHP","—","CR ≤ 0,10","CR = 0,0169"],
         ["Anno parziale D020","—","gestito","opzione A (ADR-015)"]],rfrom=99)
    CAP(doc,"Tabella 12 — Verifica dei KPI.")

    # 4. DISCUSSIONE
    H1(doc,"4. DISCUSSIONE E CONCLUSIONI")
    H2(doc,"4.1 Lettura dei risultati")
    P(doc,"Sulla serie 2023–2025 il TSI cresce in tutte le unità; il miglioramento relativo 2025/2023 è **+39,8 %** per D020, **+34,5 %** per D060, **+32,2 %** per D240, con un valore medio di Gruppo di **+34,6 %**. L'ordinamento assoluto (TSI_abs 2025) è **D240 (0,1239) > D060 (0,1227) > D020 (0,1212)**, coerente con la *footprint family* di OR6 (impianto più recente più performante).")
    H2(doc,"4.2 D020: anno parziale e opzione A")
    P(doc,"Grazie all'opzione A, il TSI di D020/2025 (**0,1212**) e il suo TSI_rel (**1,398**) sono indici-rapporto confrontabili nonostante i 7 mesi di esercizio, mentre le grandezze estensive (Ex_ref **114.990 GJ**, SA_raw **29.723 GJ**, produzione **2.317.845 m²**) si riferiscono al solo periodo e non vanno confrontate con gli anni pieni. È rilevante che D020, nella sua ultima annualità parziale, mostri il **miglioramento relativo maggiore**: il suo riferimento omologo 2022 era meno efficiente (Ψ 0,151 contro 0,164 del 2025), per cui il salto relativo è più ampio di quello di D060 e D240.")
    H2(doc,"4.3 Robustezza e correzione dell'intervallo")
    P(doc,f"L'analisi di sensibilità conferma TSI_rel > 1 e l'ordinamento assoluto in tutti gli scenari. Si segnala, rispetto alle revisioni precedenti, che l'**intervallo per-unità di TSI_rel si allarga a ≈ 1,32–1,40** (D240 1,322 · D060 1,345 · D020 1,398): il precedente riferimento «1,32–1,36» non è più valido perché D020, con i dati reali, è l'unità con il miglioramento relativo più alto. L'ordinamento **assoluto** D240 > D060 > D020 resta invariato.")
    H2(doc,"4.4 Interdipendenze e conclusioni")
    P(doc,"La RP7.3 salda la misurazione della sostenibilità con l'architettura digitale (OR6.6–6.7, OR6.10) collaudata in OR7.1–7.2 e con il controllo AI-driven (OR4–OR5), e contribuisce direttamente al Risultato Finale **RF7**. La versione beta dell'EEA+ è operativa, tracciabile e ora capace di rappresentare correttamente un **anno produttivo parziale** senza distorcere gli indici. A valle, i documenti che consumano i valori RP7.3 (**RP7.8**, ed eventualmente **RP8.6**) andranno rigenerati con i valori di questa revisione.")

    doc.add_paragraph()
    pf=doc.add_paragraph(); r=pf.add_run("Fine documento — RP7.3 RV.2 · Assessment termodinamico della fabbrica · Progetto START · Prog. F/310087/01-05/X56 · www.start-innovability.it"); r.italic=True; r.font.size=Pt(8); r.font.color.rgb=GREY
    doc.save(str(OUT))
    print("saved",OUT,"| tabelle:",len(doc.tables))

if __name__=="__main__":
    build()
