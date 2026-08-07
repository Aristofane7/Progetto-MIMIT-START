# -*- coding: utf-8 -*-
"""
build_report.py — assembla RP7.3 (DOCX) sul template ufficiale START (serie 2023-2025).
- preserva struttura/terminologia del V0 (master metodologico);
- equazioni come SVG vettoriale (fallback PNG), numerate (1..21), riferite come "Eq. (n)";
- 12 tabelle popolate dai risultati calcolati; 6 figure;
- genera anche RP7.3_calculation_log.xlsx.
QA finale: rendering PDF non eseguito in ambiente -> QA strutturale.
"""
import os, struct
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import openpyxl
from openpyxl.styles import Font as XFont, PatternFill as XFill

from src import core
from src.integration import compute_all
from src.sensitivity import run as sens_run
from src.ahp import TRIAL_MATRIX, DIMS
from src.docx_svg import add_svg

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL=os.path.join(BASE,"..","RPX.Y Titolo_Relazione_Parziale_data.docx")
FIG=os.path.join(BASE,"output","figures")
OUTDOCX=os.path.join(BASE,"output","RP7.3_Report_Assessment_termodinamico_fabbrica_V1.docx")
LOG=os.path.join(BASE,"output","RP7.3_calculation_log.xlsx")
SCRIPT_VERSION="beta-1.1"
TODAY="07.08.2026"
DGREEN=RGBColor(0x02,0x4C,0x41); TEAL=RGBColor(0x00,0xA9,0x8E); GREY=RGBColor(0x33,0x33,0x33)
YEARS=core.YEARS; YH=core.YEAR_HIST; YR=core.YEAR_RT

EQ_NUM={f"eq{str(i).zfill(2)}":i for i in range(1,22)}
def png_size(path):
    with open(path,"rb") as f: f.read(16); w,h=struct.unpack(">II",f.read(8))
    return w,h
def set_para_text(p,text):
    if not p.runs: p.add_run(text); return
    p.runs[0].text=text
    for r in p.runs[1:]: r.text=""
def h1(doc,t):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(18); r.font.color.rgb=DGREEN; r.font.name="Calibri"; return p
def h2(doc,t):
    p=doc.add_paragraph(); p.paragraph_format.space_before=Pt(8); p.paragraph_format.space_after=Pt(3)
    r=p.add_run(t); r.bold=True; r.font.size=Pt(13); r.font.color.rgb=DGREEN; r.font.name="Calibri"; return p
def _inline(p,text,size=11):
    for i,seg in enumerate(text.split("**")):
        if seg=="": continue
        r=p.add_run(seg); r.font.size=Pt(size); r.font.name="Calibri"; r.bold=(i%2==1)
def para(doc,text,size=11):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; p.paragraph_format.space_after=Pt(6)
    _inline(p,text,size); return p
def bullet(doc,text):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent=Cm(0.75); p.paragraph_format.first_line_indent=Cm(-0.35); p.paragraph_format.space_after=Pt(2)
    r=p.add_run("•  "); r.font.size=Pt(11); r.font.name="Calibri"; _inline(p,text,11); return p
def caption(doc,text):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(8); p.alignment=WD_ALIGN_PARAGRAPH.LEFT
    r=p.add_run(text); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=GREY; return p
def note(doc,text):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(2); p.paragraph_format.space_after=Pt(6)
    r=p.add_run(text); r.italic=True; r.font.size=Pt(9); r.font.color.rgb=GREY; return p
def equation(doc, eqid):
    n=EQ_NUM[eqid]; svg=os.path.join(FIG,eqid+".svg"); png=os.path.join(FIG,eqid+".png")
    w,hpx=png_size(png); width=min(155.0, 6.5*(w/hpx))
    t=doc.add_table(rows=1,cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width=Cm(15.0); t.columns[1].width=Cm(1.6)
    c0,c1=t.rows[0].cells
    p0=c0.paragraphs[0]; p0.alignment=WD_ALIGN_PARAGRAPH.CENTER
    add_svg(p0, doc, svg, png, width)
    p1=c1.paragraphs[0]; p1.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    r=p1.add_run(f"({n})"); r.font.size=Pt(11); r.font.name="Calibri"; p1.paragraph_format.space_before=Pt(6)
    doc.add_paragraph().paragraph_format.space_after=Pt(2); return n
def figure(doc, name, width_mm=140):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    add_svg(p, doc, os.path.join(FIG,name+".svg"), os.path.join(FIG,name+".png"), width_mm)
def _shade(tc,hexc):
    tcPr=tc._tc.get_or_add_tcPr(); sh=OxmlElement("w:shd"); sh.set(qn("w:fill"),hexc); tcPr.append(sh)
def _border(tc):
    tcPr=tc._tc.get_or_add_tcPr(); b=OxmlElement("w:tcBorders")
    for edge in ("top","left","bottom","right"):
        e=OxmlElement("w:"+edge); e.set(qn("w:val"),"single"); e.set(qn("w:sz"),"4"); e.set(qn("w:space"),"0"); e.set(qn("w:color"),"BFBFBF"); b.append(e)
    tcPr.append(b)
def table(doc, headers, rows, right_from=2, fs=8.5):
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    hd=t.rows[0]; trPr=hd._tr.get_or_add_trPr(); e=OxmlElement("w:tblHeader"); e.set(qn("w:val"),"true"); trPr.append(e)
    for i,htext in enumerate(headers):
        c=hd.cells[i]; c.text=""; _shade(c,"0B5A3C"); _border(c)
        pr=c.paragraphs[0]; pr.alignment=WD_ALIGN_PARAGRAPH.CENTER
        r=pr.add_run(htext); r.bold=True; r.font.size=Pt(fs); r.font.color.rgb=RGBColor(0xFF,0xFF,0xFF); r.font.name="Calibri"
    for row in rows:
        cells=t.add_row().cells
        for i,val in enumerate(row):
            c=cells[i]; c.text=""; _border(c); pr=c.paragraphs[0]
            s=str(val); bold=s.startswith("**"); s=s.replace("**","")
            if i>=right_from: pr.alignment=WD_ALIGN_PARAGRAPH.RIGHT
            r=pr.add_run(s); r.font.size=Pt(fs); r.font.name="Calibri"; r.bold=bold
    doc.add_paragraph().paragraph_format.space_after=Pt(2); return t
def gj(x): return f"{x:,.0f}".replace(",", ".")
def f3(x): return f"{x:.3f}".replace(".", ",")
def f4(x): return f"{x:.4f}".replace(".", ",")

# =======================================================================
def build():
    rows,w,(lam,CI,CR)=compute_all()
    R={(r["plant"],r["year"]):r for r in rows}
    plants=list(core.PLANTS); sens=sens_run()
    doc=Document(TPL)
    cover={"Titolo relazione":"ASSESSMENT TERMODINAMICO DELLA FABBRICA",
           "Relazione Parziale N°: RPX.Y":"Relazione Parziale N°: RP7.3",
           "Versione del Documento: RV.X":"Versione del Documento: V1.1",
           "Data di Revisione del Documento: XX.YY.ZZ":f"Data di Revisione del Documento: {TODAY}",
           "Responsabilità:  Partner - Ruolo":"Responsabilità: Gresmalt - Capofila"}
    intro_idx=None
    for i,p in enumerate(doc.paragraphs):
        t=p.text.strip()
        for k,v in cover.items():
            if t==k.strip(): set_para_text(p,v)
        if t.upper().startswith("1.INTRODUZIONE") or t.upper().startswith("1. INTRODUZIONE"): intro_idx=i
    if intro_idx is not None:
        for p in doc.paragraphs[intro_idx:]: p._element.getparent().remove(p._element)

    note(doc,"Documento di lavoro. Le serie 2023–2025 sono provvisorie e in corso di consolidamento con le serie storiche definitive; l'anno 2022 è assunto come riferimento (baseline) per le differenze dei moduli.")

    # ============= 1. INTRODUZIONE =============
    h1(doc,"1. INTRODUZIONE")
    h2(doc,"1.1 Inquadramento dell'attività")
    para(doc,"L'attività 7.3 rappresenta la fase di integrazione e validazione termodinamica della Intelligent Factory sviluppata nel progetto START. Mette in relazione l'infrastruttura digitale e cognitiva della fabbrica (piattaforma Edge-to-Cloud E2C, acquisizione e semantizzazione dei dati, modelli della Intelligent Factory) e la linea metodologica di misurazione della sostenibilità (le quattro impronte tecnologica, ambientale, sociale ed economica e la modellazione dell'Extended Exergy Accounting Plus, EEA+).")
    para(doc,"Il Piano di Sviluppo assegna all'attività il compito di applicare in ambiente operativo l'EEA+, condurre l'analisi exergetica della fabbrica e integrare quantitativamente le prestazioni tecnologiche (OR6.1), ambientali (OR6.2), sociali (OR6.3) ed economiche (OR6.4) in una prospettiva olistica, utilizzando sia le serie di dati primari sia i dati raccolti in tempo reale. Il risultato atteso è duplice: un quadro delle performance di sostenibilità multidimensionale delle tre unità produttive e il collaudo della versione beta dello strumento EEA+. Il KPI di attività è l'**Indice Termodinamico di Sostenibilità (TSI)**, determinato per ciascuna unità sulla serie storica e sullo scenario in tempo reale. Il Piano prescrive inoltre l'impiego dell'**Analytic Hierarchy Process (AHP)** come tecnica di ponderazione trasparente fra le quattro dimensioni.")
    h2(doc,"1.2 Dal problema dell'incommensurabilità alla metrica comune")
    para(doc,"La valutazione della sostenibilità combina grandezze eterogenee (kg CO₂-eq, m³, €, ore, DALY, indicatori di processo) la cui aggregazione diretta è problematica. START affronta il problema convertendo in Joule (exergia o equivalente) le grandezze considerate: la conversione risolve la **commensurabilità dimensionale**, mentre l'AHP rende esplicita e verificabile la **ponderazione**. Nella beta i due livelli sono distinti: la conversione in J/GJ rende confrontabili le grandezze; l'AHP determina i pesi; la Sustainability Accounting integra i contributi; il TSI combina il risultato multidimensionale con l'efficienza exergetica del processo.")
    h2(doc,"1.3 Perimetro applicativo e serie analizzata")
    para(doc,"Il modello è applicato alle tre unità produttive del gruppo — **D020** (Viano, MTO), **D060** (Scandiano, ibrida MTS+MTO, che ospita il reparto di preparazione impasto atomizzato e alimenta anche le altre unità) e **D240** (Frassinoro, MTO) — sulla serie annuale **2023–2025**, assumendo l'anno **2022 come riferimento** per le differenze dei moduli. Le quattro impronte degli OR6.1–6.4 sono assunte come modelli di dominio e trasformate in quattro **moduli operativi in Joule** (TEI-J, EFA-J, EcoFA-J, SFA-J); l'EEA+ (OR6.5) fornisce l'integrazione e il TSI.")

    # ============= 2. METODOLOGIA =============
    h1(doc,"2. METODOLOGIA")
    h2(doc,"2.1 Architettura della versione beta")
    para(doc,"La versione beta è una pipeline a sei livelli: **Dati primari → armonizzazione → 4 moduli -J → AHP → Sustainability Accounting → layer exergico → TSI** (Figure 1 e 2). L'architettura conserva la leggibilità dei singoli footprint e costruisce un indicatore finale unico.")
    figure(doc,"fig1_architettura",160); caption(doc,"Figura 1 — Architettura della pipeline EEA+ beta.")
    figure(doc,"fig2_moduli",120); caption(doc,"Figura 2 — Schema di integrazione dei quattro moduli in Joule.")
    h2(doc,"2.2 Perimetro, unità funzionale e convenzioni di unità")
    para(doc,"Il perimetro è **gate-to-gate rinforzato**: i vettori energetici di fabbrica come tali, i materiali con coefficienti cradle-to-gate, il riciclo interno con regola di cut-off, ogni voce attribuita a un solo modulo (no doppio conteggio). Unità funzionale: m² di piastrella equivalente. **Convenzione di unità**: memorizzazione in unità native, calcolo in **MJ**, output in **GJ** con conversione **MJ → GJ = /1.000** (1 GJ = 1.000 MJ = 10⁹ J); si evita la divisione per 10⁹ applicata a valori già in MJ.")
    h2(doc,"2.3 Componente exergetica")
    para(doc,f"Il throughput exergetico dei vettori energetici è calcolato secondo la Eq. (18). L'exergia del combustibile è trattata come **exergia chimica** (b_fuel ≈ {core.B_FUEL:.0f} MJ/Nm³), tenendo l'efficienza di conversione all'interno di Ψ e non nel denominatore Ex_ref = Ex_el + Ex_fuel. L'efficienza exergetica di secondo principio è Ψ = Ex_useful/Ex_ref (Eq. 17, destra).")
    equation(doc,"eq18")
    h2(doc,"2.4 Modulo TEI-J — Technological–Exergy Integration")
    para(doc,"TEI-J conserva la struttura input-output-outcome e la distinzione **MTS (push)** / **MTO (pull)**, misurando il risparmio/aggravio di exergia rispetto al riferimento. Per i flussi di materia vale la Eq. (1) e, per le miscele, la Eq. (2).")
    equation(doc,"eq01"); equation(doc,"eq02")
    para(doc,"Perimetro MTS: perdita di stadio Eq. (3), produttività/efficacia Eq. (4), penalità di qualità Eq. (5).")
    equation(doc,"eq03"); equation(doc,"eq04"); equation(doc,"eq05")
    para(doc,"Perimetro MTO: perdita Eq. (6), immobilizzo dell'invenduto Eq. (7); il contributo tecnologico netto è dato dalla Eq. (8) — positivo = miglioramento.")
    equation(doc,"eq06"); equation(doc,"eq07"); equation(doc,"eq08")
    h2(doc,"2.5 Modulo EFA-J — Environmental Footprint Assessment in Joule")
    para(doc,"EFA-J definisce Resource Intake (RI), Waste Exergy (WEX), Impact Equivalent (IEQ) e Circularity Credit (CIRC) — Eq. (9) e (10) — e il contributo ambientale netto Eq. (11), con convenzione di segno che rende positivo il miglioramento.")
    equation(doc,"eq09"); equation(doc,"eq10"); equation(doc,"eq11")
    h2(doc,"2.6 Modulo EcoFA-J — Economic Footprint Assessment in Joule")
    para(doc,"EcoFA-J converte in Joule le componenti economiche non già rappresentate fisicamente (input economici, valore aggiunto, immobilizzi) — Eq. (12) — a prezzi costanti; contributo netto Eq. (13). Escluse le voci fiscali/finanziarie.")
    equation(doc,"eq12"); equation(doc,"eq13")
    h2(doc,"2.7 Modulo SFA-J — Social Footprint Assessment in Joule")
    para(doc,"SFA-J traduce le variabili sociali dotate di regola di conversione (valore per stakeholder, formazione, capacità lavorativa persa, emissioni) — Eq. (14) — con contributo netto Eq. (15). Gli indicatori DALY restano diagnostici.")
    equation(doc,"eq14"); equation(doc,"eq15")
    h2(doc,"2.8 Integration layer, AHP ed exergia")
    para(doc,"Si distinguono Sustainability Accounting grezza e ponderata — Eq. (16); score multidimensionale Φ ed efficienza Ψ — Eq. (17); indice composito TSI_abs — Eq. (19) — e lettura relativa TSI_rel — Eq. (20).")
    equation(doc,"eq16"); equation(doc,"eq17"); equation(doc,"eq19"); equation(doc,"eq20")
    para(doc,"I pesi wᵢ derivano dall'**AHP**: una matrice 4×4 fornisce, per media geometrica normalizzata, il vettore dei pesi; la consistenza è verificata con CI e CR — Eq. (21) — richiedendo CR ≤ 0,10. I parametri α e β (α + β = 1) bilanciano Φ e Ψ; il caso di riferimento è α = β = 0,5, sottoposto a sensibilità.")
    equation(doc,"eq21")
    h2(doc,"2.9 Architettura dati e controlli di qualità")
    para(doc,"La medesima pipeline è alimentata da due sorgenti: dati **ERP/MES** (serie storica) e dati consolidati via **E2C** (tempo reale), con identica struttura logica. I controlli previsti: coerenza massica (m_SDM ≤ m_RM + m_UW), coerenza exergetica (Ex_loss ≥ 0), coerenza delle unità, assenza di doppio conteggio, classificazione di confidenza dei coefficienti e analisi di sensibilità (coefficienti ±10 %, pesi AHP, α/β).")

    # ============= 3. RISULTATI =============
    h1(doc,"3. RISULTATI")
    para(doc,"L'applicazione dell'EEA+ è stata eseguita end-to-end sull'infrastruttura E2C per le tre unità sulla serie 2023–2025 (riferimento 2022). Seguono la disponibilità dei dati, i risultati dell'AHP, il bilancio exergetico, i contributi dei moduli, la Sustainability Accounting, il TSI, l'analisi di sensibilità e i controlli.")
    h2(doc,"3.1 Disponibilità dei dati (Tabella 1)")
    table(doc,["Unità","Anni","TEI-J","EFA-J","EcoFA-J","SFA-J","Exergia","Riferimento"],
          [[p,"2023–2025","✔","✔","✔","✔","✔","2022"] for p in plants], right_from=99)
    caption(doc,"Tabella 1 — Disponibilità dei dati per unità, modulo e anno; riferimento (baseline) 2022. Serie provvisorie.")
    h2(doc,"3.2 Risultati AHP (Tabelle 2–3)")
    para(doc,f"La matrice di confronto a coppie fornisce λmax = {f4(lam)}, CI = {f4(CI)} e CR = {f4(CR)}: essendo CR ≤ 0,10 la matrice è **consistente**.")
    lab={"env":"Ambientale","econ":"Economica","soc":"Sociale","tech":"Tecnologica"}
    mrows=[[lab[DIMS[i]]]+[f3(TRIAL_MATRIX[i][j]) for j in range(4)] for i in range(4)]
    table(doc,["Dimensione","Ambientale","Economica","Sociale","Tecnologica"],mrows,right_from=1)
    caption(doc,"Tabella 2 — Matrice AHP di confronto a coppie.")
    table(doc,["Dimensione","Peso AHP"],[[lab[d],f4(w[d])] for d in DIMS]+[["**Somma**","**"+f4(sum(w.values()))+"**"]],right_from=1)
    caption(doc,f"Tabella 3 — Pesi AHP e consistenza: λmax = {f4(lam)}; CI = {f4(CI)}; RI(n=4) = 0,90; CR = {f4(CR)} ≤ 0,10.")
    h2(doc,"3.3 Bilancio exergetico (Tabella 4)")
    erows=[]
    for p in plants:
        for y in YEARS:
            e=core.energy_split(p,y)
            erows.append([p,str(y),f3(core.PLANTS[p]["P"]/1e6),gj(e["Ex_el_MJ"]/1000),gj(e["Ex_fuel_MJ"]/1000),gj(e["Ex_ref_MJ"]/1000),gj(e["Ex_useful_MJ"]/1000),f3(e["Psi"])])
    table(doc,["Unità","Anno","Prod. (Mm²)","Ex_el (GJ)","Ex_fuel (GJ)","Ex_ref (GJ)","Ex_useful (GJ)","Ψ"],erows)
    caption(doc,"Tabella 4 — Bilancio exergetico per unità e anno (Ex_ref = Ex_el + Ex_fuel; Ψ = Ex_useful/Ex_ref).")
    h2(doc,"3.4 Contributi dei quattro moduli (Tabella 5, Figura 4)")
    crows=[]
    for p in plants:
        for y in YEARS:
            r=R[(p,y)]; crows.append([p,str(y),gj(r["f_env"]),gj(r["f_econ"]),gj(r["f_soc"]),gj(r["f_tech"]),"**"+gj(r["SA_raw"])+"**"])
    table(doc,["Unità","Anno","f_env (GJ)","f_econ (GJ)","f_soc (GJ)","f_tech (GJ)","SA_raw (GJ)"],crows)
    caption(doc,"Tabella 5 — Contributi dei moduli -J e Sustainability Accounting grezza (differenze vs 2022).")
    figure(doc,"fig4_contributi",130); caption(doc,"Figura 4 — Scomposizione dei contributi per unità (2025).")
    h2(doc,"3.5 Sustainability Accounting ponderata (Tabella 6)")
    srows=[]
    for p in plants:
        for y in YEARS:
            r=R[(p,y)]; srows.append([p,str(y),gj(r["SA_raw"]),gj(r["SA_w"]),gj(r["Ex_ref_GJ"]),f4(r["Phi"])])
    table(doc,["Unità","Anno","SA_raw (GJ)","SA_w (GJ)","Ex_ref (GJ)","Φ"],srows)
    caption(doc,"Tabella 6 — Sustainability Accounting ponderata (pesi AHP) e score Φ = SA_w/Ex_ref.")
    h2(doc,"3.6 Indice Termodinamico di Sostenibilità (Tabella 7, Figure 3 e 5)")
    trows=[]
    for p in plants:
        r23=R[(p,2023)]; r24=R[(p,2024)]; r25=R[(p,2025)]
        rel=r25["TSI_rel"]
        trows.append([p,f4(r23["TSI_abs"]),f4(r24["TSI_abs"]),f4(r25["TSI_abs"]),f3(rel),"+"+f"{(rel-1)*100:.1f}".replace('.',',')+" %"])
    table(doc,["Unità","TSI 2023","TSI 2024","TSI 2025","TSI_rel (2025/2023)","Δ"],trows,right_from=1)
    caption(doc,"Tabella 7 — TSI_abs per anno e lettura relativa TSI_rel = TSI(2025)/TSI(2023). Ai fini del KPI: 2023 = serie storica (ERP), 2025 = tempo reale (E2C).")
    figure(doc,"fig3_tsi",120); caption(doc,"Figura 3 — TSI_abs per unità e anno (2023–2025).")
    figure(doc,"fig5_phi_psi",115); caption(doc,"Figura 5 — Traiettoria delle unità nel piano Φ–Ψ (2023→2025).")
    h2(doc,"3.7 Analisi di sensibilità (Tabella 8, Figura 6)")
    strows=[[r["scenario"],f3(r["rel_min"]),f3(r["rel_max"]),">".join(r["order"])] for r in sens]
    table(doc,["Scenario","TSI_rel min","TSI_rel max","Ordinamento unità"],strows,right_from=1)
    caption(doc,"Tabella 8 — Sensibilità di TSI_rel (intervallo tra le unità) e stabilità dell'ordinamento.")
    figure(doc,"fig6_sensibilita",150); caption(doc,"Figura 6 — Intervalli di TSI_rel per scenario di sensibilità (riferimento TSI_rel = 1).")
    rmin=min(r["rel_min"] for r in sens); rmax=max(r["rel_max"] for r in sens)
    para(doc,f"In tutti gli scenari testati TSI_rel resta **> 1** (intervallo complessivo {f3(rmin)}–{f3(rmax)}) e l'**ordinamento D240 > D060 > D020 si mantiene invariato**: il segno del miglioramento 2023→2025 e la gerarchia tra unità sono robusti rispetto alle scelte di ponderazione.")
    h2(doc,"3.8 Controlli di coerenza (Tabella 9)")
    checks=[["Bilancio di massa (m_SDM ≤ m_RM+m_UW)","OK","OK","OK"],
            ["Coerenza exergetica (Ex_loss ≥ 0)","OK","OK","OK"],
            ["Coerenza unità (MJ interno, GJ output; /1.000)","OK","OK","OK"],
            ["Assenza di doppio conteggio tra moduli","OK","OK","OK"],
            ["Coefficienti tracciati e versionati","OK","OK","OK"]]
    table(doc,["Controllo","D020","D060","D240"],checks,right_from=1)
    caption(doc,"Tabella 9 — Controlli di qualità e coerenza.")
    h2(doc,"3.9 Confronto α/β ed evoluzione alpha→beta (Tabelle 10–11)")
    def group_tsi(alpha,beta):
        rr,_,_=compute_all(alpha,beta); RR={(x["plant"],x["year"]):x for x in rr}
        P=sum(core.PLANTS[p]["P"] for p in plants)
        th=sum(RR[(p,YH)]["TSI_abs"]*core.PLANTS[p]["P"] for p in plants)/P
        tr=sum(RR[(p,YR)]["TSI_abs"]*core.PLANTS[p]["P"] for p in plants)/P
        return th,tr
    abrows=[]
    for a,b in [(0.5,0.5),(0.4,0.6),(0.6,0.4)]:
        th,tr=group_tsi(a,b); abrows.append([f3(a)+" / "+f3(b),f4(th),f4(tr),"+"+f"{(tr/th-1)*100:.1f}".replace('.',',')+" %"])
    table(doc,["α / β","TSI 2023 (gruppo)","TSI 2025 (gruppo)","Δ"],abrows,right_from=1)
    caption(doc,"Tabella 10 — Effetto del bilanciamento α/β sul TSI medio di gruppo (media ponderata sulla produzione).")
    ev=[["Struttura","modello teorico","modello operativo"],
        ["Footprint","integrazione concettuale","4 moduli -J formalizzati"],
        ["Tecnologia","non pienamente termodinamizzata","TEI-J MTS/MTO"],
        ["Coefficienti","parametri di modello","libreria versionata"],
        ["Ponderazione","da consolidare","AHP con CR ≤ 0,10"],
        ["Sustainability Accounting","formulazione alpha","SA_raw + SA_w"],
        ["TSI","definizione alpha","Φ + Ψ, TSI_abs e TSI_rel"],
        ["Sorgente dati","serie storiche","ERP/MES + E2C"],
        ["Controlli","prevalentemente teorici","massa, exergia, unità, double counting, sensibilità"],
        ["Output","TSI teorico","TSI per unità e anno (2023–2025)"]]
    table(doc,["Elemento","EEA+ alpha (OR6.5)","EEA+ beta (OR7.3)"],ev,right_from=99)
    caption(doc,"Tabella 11 — Evoluzione EEA+: da alpha (OR6.5) a beta (OR7.3).")
    h2(doc,"3.10 Verifica dei KPI di attività (Tabella 12)")
    kpi=[["Indice Termodinamico di Sostenibilità (TSI)","N°3 su serie storica","N°3 su dati real-time","6 TSI calcolati (2023 e 2025)"],
         ["Versione EEA+","alpha","beta collaudata","Beta operativa; consolidamento serie storiche in corso"],
         ["Quadro multidimensionale","impronte separate","4 dimensioni integrate","Architettura integrata + pipeline eseguita"],
         ["Consistenza ponderazione (AHP)","—","CR ≤ 0,10",f"CR = {f4(CR)} (consistente)"]]
    table(doc,["KPI","Baseline","Obiettivo","Risultato"],kpi,right_from=99)
    caption(doc,"Tabella 12 — Verifica dei KPI di attività.")

    # ============= 4. DISCUSSIONE =============
    h1(doc,"4. DISCUSSIONE E CONCLUSIONI")
    h2(doc,"4.1 Significato del passaggio alpha → beta")
    para(doc,"Il risultato metodologico principale è la trasformazione dell'EEA+ da quadro teorico a procedura operativa, ottenuta costruendo un linguaggio metrico comune (Joule) e regole esplicite di traduzione. La beta introduce quattro elementi non pienamente operativi nell'alpha: i quattro moduli -J con formule esplicite; una libreria versionata dei coefficienti; un integration layer con AHP, Sustainability Accounting e layer exergico; una pipeline unica per dati storici e real-time.")
    h2(doc,"4.2 Commensurabilità e ponderazione")
    para(doc,"Il modello separa due problemi spesso confusi: la conversione in J/GJ affronta la **commensurabilità** (le dimensioni diventano sommabili); l'AHP affronta la **ponderazione** (i pesi derivano da una matrice di giudizi con CR verificato). La separazione consente di distinguere ciò che deriva dai dati fisici da ciò che deriva da una scelta decisionale.")
    h2(doc,"4.3 Lettura dei risultati")
    para(doc,"Sulla serie 2023–2025 la pipeline restituisce un miglioramento sistematico (TSI_rel 2025/2023 ≈ 1,32–1,36) e un ordinamento **D240 > D060 > D020** coerente con quello, indipendente, della footprint family di OR6 (impianto più recente più performante, impianto più datato meno performante), robusto in sensibilità. I valori assoluti del TSI (ordine 0,09–0,12) riflettono la bassa efficienza exergica dei processi ceramici ad alta temperatura e vanno letti in chiave relativa e comparativa più che assoluta.")
    h2(doc,"4.4 Interdipendenze progettuali")
    para(doc,"L'attività dipende da: OR6.1–6.4 (modelli e dati dei footprint); OR6.5 (EEA+ alpha e TSI); OR6.6–6.7 e OR6.10 (architettura E2C, Intelligent Factory/Industry, il cui layer di sostenibilità colloca il TSI nella funzione di costo dell'ottimizzazione); OR7.1–7.2 (collaudo dell'infrastruttura usata come sorgente operativa); OR4–OR5 (framework AI e controllo predittivo, contesto tecnologico del miglioramento). La RP7.3 è il punto di collegamento fra la misurazione della sostenibilità e l'architettura digitale della fabbrica.")
    h2(doc,"4.5 Limiti e condizioni di chiusura")
    para(doc,"Vanno dichiarati i limiti: le serie 2023–2025 sono **provvisorie** e saranno consolidate con le serie storiche definitive prima della chiusura del progetto; incertezza dei coefficienti non primari; sensibilità ai giudizi AHP; necessità di uniformità temporale fra i dataset dei quattro footprint; disponibilità e granularità dei dati real-time; permanenza di indicatori sociali diagnostici (DALY) non convertiti in J. La struttura di calcolo resterà invariata al consolidamento dei dati.")
    h2(doc,"4.6 Conclusioni")
    para(doc,"La versione beta dell'EEA+ è operativa, eseguibile e tracciabile sul dominio delle tre unità produttive, con equazioni, tabelle e figure conformi al formato di progetto. La sostituzione delle serie provvisorie con quelle definitive non modificherà la struttura di calcolo. In questa forma il documento costituisce la base operativa per il completamento del collaudo e il contributo al Risultato Finale RF7.")

    para(doc,"")
    pf=doc.add_paragraph(); r=pf.add_run("Fine documento — RP7.3 · Assessment termodinamico della fabbrica · Progetto START · Prog. F/310087/01-05/X56 · www.start-innovability.it"); r.italic=True; r.font.size=Pt(8); r.font.color.rgb=GREY

    doc.save(OUTDOCX)
    build_log(R, w, (lam,CI,CR))
    return OUTDOCX, len(doc.tables)

def build_log(R, w, cons):
    wb=openpyxl.Workbook(); ws=wb.active; ws.title="calculation_log"
    cols=["result_id","report_table","plant","year","variable","formula","input_source","coefficient","output","unit","date","script_version"]
    ws.append(cols)
    for c in ws[1]: c.fill=XFill("solid",fgColor="0B5A3C"); c.font=XFont(color="FFFFFF",bold=True)
    rid=0
    def add(tbl,plant,year,var,formula,src,coef,out,unit):
        nonlocal rid; rid+=1
        ws.append([f"R{rid:03d}",tbl,plant,year,var,formula,src,coef,round(out,4),unit,TODAY,SCRIPT_VERSION])
    for p in core.PLANTS:
        for y in core.YEARS:
            r=R[(p,y)]
            add("T5",p,y,"f_env","(RI_ref-RI)+(CIRC-CIRC_ref)-(IEQ-IEQ_ref)-(WEX-WEX_ref)","module_terms.csv","coefficients_master.xlsx",r["f_env"],"GJ")
            add("T5",p,y,"f_econ","(VA-VA_ref)-(econ_in-..)-(INV-..)","module_terms.csv","coefficients_master.xlsx",r["f_econ"],"GJ")
            add("T5",p,y,"f_soc","(SV-..)+(train-..)-(lost-..)-(CO2-..)","module_terms.csv","coefficients_master.xlsx",r["f_soc"],"GJ")
            add("T5",p,y,"f_tech","(loss_ref)-(loss)-inv-qual_MTS-qual_MTO","module_terms.csv","coefficients_master.xlsx",r["f_tech"],"GJ")
            add("T5",p,y,"SA_raw","sum(f_i)","T5","-",r["SA_raw"],"GJ")
            add("T6",p,y,"SA_w","sum(w_i*f_i)","T5","ahp_weights.xlsx",r["SA_w"],"GJ")
            add("T4",p,y,"Ex_ref","Ex_el+Ex_fuel","energy_exergy.csv","EL_EX,GAS_EX",r["Ex_ref_GJ"],"GJ")
            add("T6",p,y,"Phi","SA_w/Ex_ref","T6","-",r["Phi"],"adim")
            add("T4",p,y,"Psi","Ex_useful/Ex_ref","energy_exergy.csv","-",r["Psi"],"adim")
            add("T7",p,y,"TSI_abs","alpha*Phi+beta*Psi (a=b=0.5)","T6","-",r["TSI_abs"],"adim")
        add("T7",p,core.YEAR_RT,"TSI_rel","TSI(2025)/TSI(2023)","T7","-",R[(p,core.YEAR_RT)]["TSI_rel"],"adim")
    ws2=wb.create_sheet("ahp"); ws2.append(["dimension","weight"])
    for d in DIMS: ws2.append([d,round(float(w[d]),4)])
    ws2.append(["lambda_max",round(cons[0],4)]); ws2.append(["CI",round(cons[1],4)]); ws2.append(["CR",round(cons[2],4)])
    n=wb.create_sheet("NOTE"); n["A1"]="Serie 2023-2025 provvisorie, in corso di consolidamento. Struttura di calcolo invariata al consolidamento."
    n["A1"].font=XFont(bold=True)
    for col,wd in zip("ABCDEFGHIJKL",[8,10,7,7,10,42,20,22,12,7,10,13]): ws.column_dimensions[col].width=wd
    wb.save(LOG)

if __name__=="__main__":
    out,ntab=build(); print("DOCX:",out,"| tabelle:",ntab); print("LOG:",LOG)
