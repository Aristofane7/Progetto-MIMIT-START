#!/usr/bin/env python3
"""
P-TSA (OR7.4) computation pipeline.
Synthetic-but-coherent data anchored to the three EPDs (7.4/8.2/20 mm) and to
RP6.x / RP7.3 series. Computes SCR/PsI/OCR -> IOAI/OPI/TQI -> P-TSI with two
normalization schemes (z-score+equal weights = primary; 1-5 scoring + AHP =
secondary), plus TII and sensitivity. Writes the three xlsx artefacts.
Structure mirrors RP7.3 (data_collection / calculation_log / weights).
"""
import math, json
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

OUT = "/home/user/Progetto-MIMIT-START"

# ----------------------------------------------------------------------------
# 0. Typologies (from EPDs in repo). mass in kg per m2 (declared unit).
# ----------------------------------------------------------------------------
TYPES = ["T1_7.4mm", "T2_8.2mm", "T3_20mm"]
mass = {"T1_7.4mm": 13.98, "T2_8.2mm": 16.05, "T3_20mm": 41.79}     # kg/m2 (EPD)
plant = {"T1_7.4mm": "D060 Scandiano", "T2_8.2mm": "D060 Scandiano",
         "T3_20mm": "D240 Frassinoro"}
# specific process energy per m2 [MJ/m2], k=3.05 MJ/kg so 8.2mm~49 MJ/m2 (~RP7.3
# D060 Ex_ref/m2). Scales with mass -> thicker = more energy (coherent).
K_EN = 3.05
e_spec = {t: round(K_EN * mass[t], 1) for t in TYPES}                # MJ/m2

# ----------------------------------------------------------------------------
# 1. RAW METRICS (synthetic, coherent) -- period t = Jul2023-Jun2024 (EPD),
#    t_1 = previous year (for TII). Each with provenance note.
#    direction: +1 higher=better, -1 lower=better (handled in scoring).
# ----------------------------------------------------------------------------
# ---- IOA metrics: SCR = AverageStock / AverageConsumption  (days of coverage)
# Sourcing raw materials, Internal-logistics finished product, Operations glazes/inks
scr_raw = {  # (AS, AC) in consistent units so SCR = days
 # input : {type: (avg_stock, avg_consumption_per_day)}
 "RawMat_sourcing":   {"T1_7.4mm": (4200, 105), "T2_8.2mm": (4600, 100), "T3_20mm": (5200, 62)},   # tons / (tons/day)
 "Finished_intlog":   {"T1_7.4mm": (95000, 3200), "T2_8.2mm": (88000, 2600), "T3_20mm": (52000, 900)}, # m2 / (m2/day)
 "Glaze_ink_ops":     {"T1_7.4mm": (48, 2.1), "T2_8.2mm": (52, 2.0), "T3_20mm": (40, 1.2)},         # tons / (tons/day)
}
# previous-year consumption slightly higher (less efficient) -> lower coverage
scr_raw_t1 = {k: {t: (v[t][0]*0.97, v[t][1]*1.03) for t in TYPES} for k, v in scr_raw.items()}

# ---- OP metrics: PI = RealOutput / RealInput
#  PI1 energy productivity [m2 first-choice per GJ], PI2 material yield [m2 sell/m2 pressed],
#  PI3 line throughput [m2/h]
ipr = {"T1_7.4mm": 0.958, "T2_8.2mm": 0.951, "T3_20mm": 0.936}   # inspection pass / first-choice rate
yield_ = {"T1_7.4mm": 0.962, "T2_8.2mm": 0.955, "T3_20mm": 0.941}
throughput = {"T1_7.4mm": 640, "T2_8.2mm": 560, "T3_20mm": 210}   # m2/h (thicker=slower)
throughput_t1 = {t: throughput[t]*0.97 for t in TYPES}
ipr_t1 = {t: ipr[t]-0.008 for t in TYPES}
yield_t1 = {t: yield_[t]-0.006 for t in TYPES}

# ---- TQ metrics: OCR = QualityParameter / AcceptabilityThreshold (EN14411 BIa / ISO10545)
# flexural strength [N/mm2] AT=35 ; breaking strength [N] AT depends on thickness ;
# surface quality [% first choice] AT=95 (ISO10545-2)
flex_QP = {"T1_7.4mm": 48.0, "T2_8.2mm": 50.0, "T3_20mm": 53.0}; flex_AT = 35.0
brk_QP = {"T1_7.4mm": 1400.0, "T2_8.2mm": 2050.0, "T3_20mm": 7200.0}
brk_AT = {"T1_7.4mm": 700.0, "T2_8.2mm": 1300.0, "T3_20mm": 1300.0}  # EN14411 BIa: <7.5mm->700, >=7.5mm->1300
surf_QP = {"T1_7.4mm": 97.6, "T2_8.2mm": 97.1, "T3_20mm": 96.4}; surf_AT = 95.0
flex_QP_t1 = {t: flex_QP[t]-0.6 for t in TYPES}
surf_QP_t1 = {t: surf_QP[t]-0.5 for t in TYPES}

# ----------------------------------------------------------------------------
# 2. INDICATORS
# ----------------------------------------------------------------------------
def scr(d): return {t: d[t][0]/d[t][1] for t in TYPES}
SCR = {  # days of coverage
 "SCR_RawMat": scr(scr_raw["RawMat_sourcing"]),
 "SCR_Finished": scr(scr_raw["Finished_intlog"]),
 "SCR_GlazeInk": scr(scr_raw["Glaze_ink_ops"]),
}
SCR_t1 = {"SCR_RawMat": scr(scr_raw_t1["RawMat_sourcing"]),
          "SCR_Finished": scr(scr_raw_t1["Finished_intlog"]),
          "SCR_GlazeInk": scr(scr_raw_t1["Glaze_ink_ops"])}

PI = {
 "PsI_Energy": {t: round(ipr[t] / (e_spec[t]/1000.0), 3) for t in TYPES},  # m2/GJ
 "PsI_Yield":  {t: yield_[t] for t in TYPES},
 "PsI_Through":{t: float(throughput[t]) for t in TYPES},
}
PI_t1 = {
 "PsI_Energy": {t: round(ipr_t1[t] / (e_spec[t]*1.02/1000.0), 3) for t in TYPES}, # prev yr +2% energy
 "PsI_Yield":  {t: yield_t1[t] for t in TYPES},
 "PsI_Through":{t: throughput_t1[t] for t in TYPES},
}

OCR = {
 "OCR_Flex":  {t: round(flex_QP[t]/flex_AT, 3) for t in TYPES},
 "OCR_Break": {t: round(brk_QP[t]/brk_AT[t], 3) for t in TYPES},
 "OCR_Surf":  {t: round(surf_QP[t]/surf_AT, 3) for t in TYPES},
}
OCR_t1 = {
 "OCR_Flex":  {t: round(flex_QP_t1[t]/flex_AT, 3) for t in TYPES},
 "OCR_Break": {t: round(brk_QP[t]/brk_AT[t], 3) for t in TYPES},
 "OCR_Surf":  {t: round(surf_QP_t1[t]/surf_AT, 3) for t in TYPES},
}

DIM = {"IOA": SCR, "OP": PI, "TQ": OCR}
DIM_t1 = {"IOA": SCR_t1, "OP": PI_t1, "TQ": OCR_t1}

# ----------------------------------------------------------------------------
# 3. PRIMARY: z-score across the 3 typologies, equal weights
# ----------------------------------------------------------------------------
def zscore_dim(dimdict):
    """return {indicator:{type:z}} standardized across the 3 typologies."""
    z = {}
    for ind, vals in dimdict.items():
        arr = np.array([vals[t] for t in TYPES], float)
        m, s = arr.mean(), arr.std(ddof=0)
        z[ind] = {t: (vals[t]-m)/s if s > 0 else 0.0 for t in TYPES}
    return z

def subindex_z(dimdict):
    z = zscore_dim(dimdict)
    inds = list(dimdict.keys()); w = 1.0/len(inds)          # equal weights
    return {t: sum(w*z[ind][t] for ind in inds) for t in TYPES}, z

IOAI_z, zIOA = subindex_z(SCR)
OPI_z,  zOP  = subindex_z(PI)
TQI_z,  zTQ  = subindex_z(OCR)
PTSI_z = {t: (IOAI_z[t]+OPI_z[t]+TQI_z[t])/3.0 for t in TYPES}   # equal dim weights

# ----------------------------------------------------------------------------
# 4. SECONDARY: 1-5 scoring + AHP
# ----------------------------------------------------------------------------
# thresholds (4 boundaries) -> score 1..5, all "higher = better"
TH = {
 "SCR_RawMat": [20,30,40,55], "SCR_Finished": [12,18,25,35], "SCR_GlazeInk": [12,18,25,32],
 "PsI_Energy": [8.0,12.0,16.0,20.0], "PsI_Yield": [0.93,0.945,0.955,0.965],
 "PsI_Through": [200,350,500,620],
 "OCR_Flex": [1.15,1.30,1.40,1.50], "OCR_Break": [1.2,1.6,2.2,3.5], "OCR_Surf": [1.005,1.015,1.025,1.03],
}
def score15(ind, x):
    th = TH[ind]
    if x < th[0]: return 1
    if x < th[1]: return 2
    if x < th[2]: return 3
    if x < th[3]: return 4
    return 5

def ahp_weights(M):
    M = np.array(M, float); n = M.shape[0]
    gm = np.prod(M, axis=1)**(1.0/n); w = gm/gm.sum()
    lam = (M @ w / w).mean()
    CI = (lam-n)/(n-1); RI = {2:0,3:0.58,4:0.90}[n]; CR = CI/RI if RI else 0
    return w, lam, CI, CR

# within-dimension AHP (3 indicators each)
AHP_IOA = [[1,1,2],[1,1,2],[0.5,0.5,1]]      # raw & finished coverage > glaze
AHP_OP  = [[1,2,2],[0.5,1,1],[0.5,1,1]]      # energy productivity most important
AHP_TQ  = [[1,1,3],[1,1,3],[1/3,1/3,1]]      # flex & break > surface
# across dimensions: TQ (conformity/norm) >= OP > IOA
AHP_DIM = [[1,0.5,1/3],[2,1,0.5],[3,2,1]]    # order IOA,OP,TQ

wIOA,_,_,crIOA = ahp_weights(AHP_IOA)
wOP,_,_,crOP  = ahp_weights(AHP_OP)
wTQ,_,_,crTQ  = ahp_weights(AHP_TQ)
wDIM,lamD,ciD,crD = ahp_weights(AHP_DIM)

def sdim_score(dimdict, wvec):
    inds = list(dimdict.keys())
    S = {}
    for t in TYPES:
        S[t] = sum(wvec[i]*score15(inds[i], dimdict[inds[i]][t]) for i in range(len(inds)))
    return S

def ptsi_score(dims):
    S_IOA = sdim_score(dims["IOA"], wIOA)
    S_OP  = sdim_score(dims["OP"],  wOP)
    S_TQ  = sdim_score(dims["TQ"],  wTQ)
    P = {t: wDIM[0]*S_IOA[t]+wDIM[1]*S_OP[t]+wDIM[2]*S_TQ[t] for t in TYPES}
    return S_IOA, S_OP, S_TQ, P

S_IOA, S_OP, S_TQ, PTSI_5 = ptsi_score(DIM)
S_IOA1,S_OP1,S_TQ1,PTSI_5_t1 = ptsi_score(DIM_t1)
TII = {t: round((PTSI_5[t]/PTSI_5_t1[t]-1)*100, 2) for t in TYPES}

# equal-weight variant of scoring (for sensitivity)
def ptsi_score_equal(dims):
    def sd(d):
        inds=list(d.keys()); w=1.0/len(inds)
        return {t: sum(w*score15(i,d[i][t]) for i in inds) for t in TYPES}
    a,b,c = sd(dims["IOA"]),sd(dims["OP"]),sd(dims["TQ"])
    return {t:(a[t]+b[t]+c[t])/3 for t in TYPES}
PTSI_5_eq = ptsi_score_equal(DIM)

# ----------------------------------------------------------------------------
# 5. RANKINGS + summary
# ----------------------------------------------------------------------------
def rank(d, rev=True):
    return [k for k,_ in sorted(d.items(), key=lambda kv: kv[1], reverse=rev)]

summary = {
 "e_spec_MJ_m2": e_spec, "SCR": SCR, "PI": PI, "OCR": OCR,
 "IOAI_z": IOAI_z, "OPI_z": OPI_z, "TQI_z": TQI_z, "PTSI_z": PTSI_z,
 "S_IOA": S_IOA, "S_OP": S_OP, "S_TQ": S_TQ, "PTSI_5": PTSI_5,
 "PTSI_5_t1": PTSI_5_t1, "TII": TII, "PTSI_5_eq": PTSI_5_eq,
 "AHP": {"wIOA": list(np.round(wIOA,4)), "wOP": list(np.round(wOP,4)),
         "wTQ": list(np.round(wTQ,4)), "wDIM": list(np.round(wDIM,4)),
         "CR": {"IOA":round(crIOA,4),"OP":round(crOP,4),"TQ":round(crTQ,4),"DIM":round(crD,4)}},
 "rank_z": rank(PTSI_z), "rank_5": rank(PTSI_5),
}
print(json.dumps({k:(v if not isinstance(v,dict) else {kk:(round(vv,4) if isinstance(vv,float) else vv) for kk,vv in v.items()}) for k,v in summary.items()}, indent=1, default=str))

# save summary for the report step
with open("/tmp/claude-0/-home-user-Progetto-MIMIT-START/a500ca18-79ff-5559-beb7-7cbae02fde97/scratchpad/ptsa_results.json","w") as f:
    json.dump(summary, f, indent=1, default=lambda o: float(o) if isinstance(o,(np.floating,)) else o)

# ============================================================================
# 6. WRITE XLSX ARTEFACTS
# ============================================================================
HFILL = PatternFill("solid", fgColor="4F6228"); HFONT = Font(color="FFFFFF", bold=True)
def style_header(ws, row=1):
    for c in ws[row]:
        c.fill = HFILL; c.font = HFONT; c.alignment = Alignment(horizontal="center")

def autosize(ws):
    for col in ws.columns:
        w = max((len(str(c.value)) for c in col if c.value is not None), default=8)
        ws.column_dimensions[col[0].column_letter].width = min(max(w+2, 10), 48)

# ---- (a) data_collection ----
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Istruzioni"
notes = [
 "RP7.4 - Scheda di raccolta dati (P-TSA, 3 tipologie di prodotto)",
 "Tipologie definite dagli EPD in repository: 7.4 mm e 8.2 mm (Scandiano/D060), 20 mm (Frassinoro/D240).",
 "Periodo t = lug2023-giu2024 (coerente EPD); t-1 = anno precedente (per il TII).",
 "Serie provvisorie, in corso di consolidamento (ancoraggio: EPD - massa/m2, parametri ISO 10545 - e serie RP6.x/RP7.3).",
 "Struttura di calcolo invariata al consolidamento: sostituire i valori e rieseguire ptsa_build.py.",
 "Convenzione: SCR=Stock medio/Consumo medio [giorni]; PsI=Output reale/Input reale; OCR=Parametro qualita/Soglia normativa (EN14411 BIa / ISO 10545).",
]
for i,n in enumerate(notes,1): ws.cell(i,1,n)
ws.column_dimensions["A"].width = 120

ws = wb.create_sheet("Tipologie")
ws.append(["tipologia","EPD","spessore_mm","massa_kg_m2","stabilimento","gruppo","energia_processo_MJ_m2"])
for t in TYPES:
    sp = {"T1_7.4mm":7.4,"T2_8.2mm":8.2,"T3_20mm":20.0}[t]
    ws.append([t, t.split("_")[1], sp, mass[t], plant[t], "BIa (assorb.<=0.5%)", e_spec[t]])
style_header(ws); autosize(ws)

ws = wb.create_sheet("IOA_SCR_input")
ws.append(["indicatore","attivita_valuechain","input","tipologia","stock_medio","consumo_medio_giorno","unita","SCR_giorni","periodo"])
labels = {"SCR_RawMat":("Sourcing (cradle-to-gate)","materie prime impasto","RawMat_sourcing","t/(t/gg)"),
          "SCR_Finished":("Internal Logistics (gate-to-gate)","prodotto finito","Finished_intlog","m2/(m2/gg)"),
          "SCR_GlazeInk":("Operations (gate-to-gate)","smalti/engobbi/inchiostri","Glaze_ink_ops","t/(t/gg)")}
for ind,(act,inp,key,un) in labels.items():
    for t in TYPES:
        s,c = scr_raw[key][t]; ws.append([ind,act,inp,t,s,c,un,round(SCR[ind][t],2),"t"])
    for t in TYPES:
        s,c = scr_raw_t1[key][t]; ws.append([ind,act,inp,t,round(s,1),round(c,2),un,round(SCR_t1[ind][t],2),"t-1"])
style_header(ws); autosize(ws)

ws = wb.create_sheet("OP_PsI_input")
ws.append(["indicatore","attivita_valuechain","tipologia","output_reale","input_reale","unita","PsI","periodo"])
for t in TYPES:
    ws.append(["PsI_Energy","Operations",t,round(ipr[t],3),round(e_spec[t]/1000,4),"m2 / GJ",PI["PsI_Energy"][t],"t"])
for t in TYPES:
    ws.append(["PsI_Yield","Operations",t,round(yield_[t],3),1.0,"m2 sell / m2 pressato",PI["PsI_Yield"][t],"t"])
for t in TYPES:
    ws.append(["PsI_Through","Operations/Outbound",t,throughput[t],1.0,"m2 / h",PI["PsI_Through"][t],"t"])
for t in TYPES:
    ws.append(["PsI_Energy","Operations",t,round(ipr_t1[t],3),round(e_spec[t]*1.02/1000,4),"m2 / GJ",PI_t1["PsI_Energy"][t],"t-1"])
for t in TYPES:
    ws.append(["PsI_Yield","Operations",t,round(yield_t1[t],3),1.0,"m2 sell / m2 pressato",PI_t1["PsI_Yield"][t],"t-1"])
for t in TYPES:
    ws.append(["PsI_Through","Operations/Outbound",t,round(throughput_t1[t],1),1.0,"m2 / h",PI_t1["PsI_Through"][t],"t-1"])
style_header(ws); autosize(ws)

ws = wb.create_sheet("TQ_OCR_input")
ws.append(["indicatore","norma","parametro_qualita_QP","soglia_AT","tipologia","QP","AT","OCR","periodo"])
for t in TYPES: ws.append(["OCR_Flex","ISO 10545-4 / EN14411","resistenza a flessione [N/mm2]","min 35",t,flex_QP[t],flex_AT,OCR["OCR_Flex"][t],"t"])
for t in TYPES: ws.append(["OCR_Break","ISO 10545-4 / EN14411","sforzo di rottura [N]","min 700(<7.5mm)/1300",t,brk_QP[t],brk_AT[t],OCR["OCR_Break"][t],"t"])
for t in TYPES: ws.append(["OCR_Surf","ISO 10545-2","qualita superficiale [% prima scelta]","min 95",t,surf_QP[t],surf_AT,OCR["OCR_Surf"][t],"t"])
for t in TYPES: ws.append(["OCR_Flex","ISO 10545-4 / EN14411","resistenza a flessione [N/mm2]","min 35",t,round(flex_QP_t1[t],1),flex_AT,OCR_t1["OCR_Flex"][t],"t-1"])
for t in TYPES: ws.append(["OCR_Surf","ISO 10545-2","qualita superficiale [% prima scelta]","min 95",t,round(surf_QP_t1[t],1),surf_AT,OCR_t1["OCR_Surf"][t],"t-1"])
style_header(ws); autosize(ws)
wb.save(f"{OUT}/RP7.4_data_collection.xlsx")

# ---- (b) weights ----
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "AHP_within_dim"
def dump_ahp(ws, name, M, w, cr, inds):
    ws.append([name]); ws.append([""]+inds)
    for i,r in enumerate(M): ws.append([inds[i]]+list(r))
    ws.append(["peso_AHP"]+list(np.round(w,4)))
    ws.append(["CR", round(cr,4), "OK (<=0.10)" if cr<=0.10 else "RIVEDERE"]); ws.append([])
dump_ahp(ws,"IOA (SCR)",AHP_IOA,wIOA,crIOA,["SCR_RawMat","SCR_Finished","SCR_GlazeInk"])
dump_ahp(ws,"OP (PsI)",AHP_OP,wOP,crOP,["PsI_Energy","PsI_Yield","PsI_Through"])
dump_ahp(ws,"TQ (OCR)",AHP_TQ,wTQ,crTQ,["OCR_Flex","OCR_Break","OCR_Surf"])
autosize(ws)
ws = wb.create_sheet("AHP_between_dim")
ws.append(["","IOA","OP","TQ"])
for i,r in enumerate(AHP_DIM): ws.append([["IOA","OP","TQ"][i]]+list(r))
ws.append(["peso_AHP"]+list(np.round(wDIM,4)))
ws.append(["lambda_max",round(lamD,4)]); ws.append(["CI",round(ciD,4)]); ws.append(["RI(n=3)",0.58]); ws.append(["CR",round(crD,4),"OK (<=0.10)" if crD<=0.10 else "RIVEDERE"])
autosize(ws)
ws = wb.create_sheet("Soglie_scoring_1_5")
ws.append(["indicatore","classe1_<","classe2_<","classe3_<","classe4_<","classe5_>=","direzione"])
for ind,th in TH.items(): ws.append([ind,th[0],th[1],th[2],th[3],th[3],"higher=better"])
style_header(ws); autosize(ws)
ws = wb.create_sheet("NOTE")
ws.append(["Pesi/soglie provvisori, da confermare in workshop produzione/qualita/manutenzione (come OR6.8 / paper O-TSA)."])
wb.save(f"{OUT}/RP7.4_weights.xlsx")

# ---- (c) calculation_log ----
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "calculation_log"
ws.append(["result_id","report_table","tipologia","periodo","variabile","formula","input_source","output","unita","note","versione"])
rid = 0
def add(tbl,t,per,var,formula,src,out,unit):
    global rid; rid += 1
    ws.append([f"P{rid:03d}",tbl,t,per,var,formula,src,round(out,4) if isinstance(out,float) else out,unit,"provvisorio - in corso di consolidamento",'beta-1.0'])
for ind in SCR:
    for t in TYPES: add("T2",t,"t",ind,"AS/AC","IOA_SCR_input",SCR[ind][t],"giorni")
for ind in PI:
    for t in TYPES: add("T3",t,"t",ind,"ROU/RIN","OP_PsI_input",PI[ind][t],"varie")
for ind in OCR:
    for t in TYPES: add("T4",t,"t",ind,"QP/AT","TQ_OCR_input",OCR[ind][t],"adim")
for t in TYPES: add("T5",t,"t","IOAI_z","mean(w*z(SCR))","zscore",IOAI_z[t],"adim")
for t in TYPES: add("T5",t,"t","OPI_z","mean(w*z(PsI))","zscore",OPI_z[t],"adim")
for t in TYPES: add("T5",t,"t","TQI_z","mean(w*z(OCR))","zscore",TQI_z[t],"adim")
for t in TYPES: add("T6",t,"t","P-TSI_z","mean(IOAI,OPI,TQI)","T5",PTSI_z[t],"adim (z, primario)")
for t in TYPES: add("T7",t,"t","S_IOA","sum(w_AHP*score15)","weights",S_IOA[t],"[1-5]")
for t in TYPES: add("T7",t,"t","S_OP","sum(w_AHP*score15)","weights",S_OP[t],"[1-5]")
for t in TYPES: add("T7",t,"t","S_TQ","sum(w_AHP*score15)","weights",S_TQ[t],"[1-5]")
for t in TYPES: add("T8",t,"t","P-TSI_5","sum(wDIM*S_dim)","T7",PTSI_5[t],"[1-5] (secondario)")
for t in TYPES: add("T8",t,"t-1","P-TSI_5","sum(wDIM*S_dim)","T7",PTSI_5_t1[t],"[1-5]")
for t in TYPES: add("T9",t,"t-1,t","TII","(P-TSI_5_t/P-TSI_5_t1-1)*100","T8",TII[t],"%")
style_header(ws); autosize(ws)
ws = wb.create_sheet("NOTE")
ws.append(["Serie 2023-2024 sintetiche provvisorie, ancorate a EPD e serie RP6.x/RP7.3, in corso di consolidamento."])
ws.append(["A fine progetto: assessment rieseguito con dati reali, struttura di calcolo invariata."])
wb.save(f"{OUT}/RP7.4_calculation_log.xlsx")

print("\nWROTE: RP7.4_data_collection.xlsx / RP7.4_weights.xlsx / RP7.4_calculation_log.xlsx")
print("AHP CR:", summary["AHP"]["CR"])
print("rank_z:", summary["rank_z"], " rank_5:", summary["rank_5"])
