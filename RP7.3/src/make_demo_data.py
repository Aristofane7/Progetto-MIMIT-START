# -*- coding: utf-8 -*-
"""Genera input (CSV) e librerie controllate (coefficients_master.xlsx, ahp_weights.xlsx).
   Serie provvisorie 2023-2025 (+ riferimento 2022), in corso di consolidamento."""
import os, csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from src import core
from src.ahp import weights_and_consistency, TRIAL_MATRIX, DIMS
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INP=os.path.join(BASE,"input"); COE=os.path.join(BASE,"coefficients")
HDR_FILL=PatternFill("solid",fgColor="0B5A3C"); HDR_FONT=Font(color="FFFFFF",bold=True)
ALLYEARS=[core.REF_YEAR]+core.YEARS
def _hdr(ws,row=1):
    for c in ws[row]: c.fill=HDR_FILL; c.font=HDR_FONT; c.alignment=Alignment(horizontal="center",vertical="center")
def write_inputs():
    with open(os.path.join(INP,"energy_exergy.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["plant","year","production_m2","V_gas_Nm3","E_el_kWh","Ex_fuel_MJ","Ex_el_MJ","Ex_ref_MJ","Ex_useful_MJ"])
        for p in core.PLANTS:
            for y in ALLYEARS:
                e=core.energy_split(p,y)
                w.writerow([p,y,core.PLANTS[p]["P"],round(e["V_gas_Nm3"],1),round(e["kWh"],1),round(e["Ex_fuel_MJ"],1),round(e["Ex_el_MJ"],1),round(e["Ex_ref_MJ"],1),round(e["Ex_useful_MJ"],1)])
    with open(os.path.join(INP,"module_terms.csv"),"w",newline="") as f:
        w=csv.writer(f); w.writerow(["plant","year","module","term","value_MJ","kind"])
        for p in core.PLANTS:
            for y in ALLYEARS:
                for t,v in core.term_value(p,y).items():
                    w.writerow([p,y,core.TERM_MODULE[t],t,round(v,1),core.TERM_KIND[t]])
def write_coefficients():
    wb=openpyxl.Workbook(); ws=wb.active; ws.title="Coefficients"
    ws.append(["code","description","value","unit","source","year","boundary","method","confidence","version"])
    rows=[
        ["EL_EX","Exergia elettrica (fattore unitario)",core.KEL,"MJ/kWh","fisica (1 kWh=3.6 MJ)",2025,"—","fisico","A","1.0"],
        ["GAS_EX","Exergia chimica gas naturale",core.B_FUEL,"MJ/Nm3","exergia chimica (~1.04·LHV)","2025","CTG","termodinamico","B","1.0"],
        ["MAT_CLAY","Argilla (CED cradle-to-gate)",1.5,"MJ/kg","EPD fornitore","2024","CTG","LCA","B","1.0"],
        ["MAT_FELD","Feldspato",2.1,"MJ/kg","DB LCA (ecoinvent)","2024","CTG","LCA","B","1.0"],
        ["IMP_CO2","CO2-eq -> Joule",441868.0,"MJ/tCO2e","modello SYMΞX","2024","—","modello","B","1.0"],
        ["ECO_VA","Valore aggiunto EUR->MJ",3.2,"MJ/EUR","intensita' energetica settoriale","2024","—","top-down","B","1.0"],
        ["ECO_IN","Input economici EUR->MJ",4.5,"MJ/EUR","dati fornitori","2024","—","bottom-up","B","1.0"],
        ["LAB_H","Exergia oraria del lavoro",3.5,"MJ/h","modello EEA+ (metab.+cogn.)","2024","—","modello","B","1.0"],
    ]
    for r in rows: ws.append(r)
    _hdr(ws)
    for col,wd in zip("ABCDEFGHIJ",[10,34,12,10,28,8,10,14,11,9]): ws.column_dimensions[col].width=wd
    n=wb.create_sheet("NOTE"); n["A1"]="Libreria coefficienti — versione provvisoria, soggetta a consolidamento con EPD/dati primari."
    n["A1"].font=Font(bold=True)
    wb.save(os.path.join(COE,"coefficients_master.xlsx"))
def write_ahp():
    w,lam,CI,CR=weights_and_consistency(TRIAL_MATRIX)
    wb=openpyxl.Workbook(); ws=wb.active; ws.title="Pairwise_Matrix"; ws.append([""]+DIMS)
    for i,d in enumerate(DIMS): ws.append([d]+[round(x,4) for x in TRIAL_MATRIX[i]])
    _hdr(ws)
    for c in ws["A"]: c.font=Font(bold=True)
    ws2=wb.create_sheet("Weights_Consistency"); ws2.append(["dimension","weight_AHP"])
    for d,val in zip(DIMS,w): ws2.append([d,round(float(val),4)])
    ws2.append(["SUM",round(float(sum(w)),4)]); ws2.append([]); ws2.append(["lambda_max",round(lam,4)])
    ws2.append(["CI",round(CI,4)]); ws2.append(["RI(n=4)",0.90]); ws2.append(["CR",round(CR,4)])
    ws2.append(["esito","CONSISTENTE (CR<=0.10)" if CR<=0.10 else "REVISIONE"]); _hdr(ws2)
    n=wb.create_sheet("NOTE"); n["A1"]="Matrice di confronto a coppie del panel — provvisoria, da confermare."; n["A1"].font=Font(bold=True)
    for col in "ABCDE": ws.column_dimensions[col].width=14; ws2.column_dimensions[col].width=16
    wb.save(os.path.join(COE,"ahp_weights.xlsx"))
if __name__=="__main__":
    write_inputs(); write_coefficients(); write_ahp(); print("Input + coefficienti + AHP (serie 2023-2025) generati.")
