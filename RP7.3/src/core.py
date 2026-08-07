# -*- coding: utf-8 -*-
"""
RP7.3 — EEA+ beta: core del motore di calcolo (serie annuali 2023-2025).
Convenzioni:
  - unita interne: MJ  (MJ -> GJ  =>  / 1000)
  - exergia combustibile = exergia chimica (b_fuel); efficienza di conversione in Psi (non in Ex_ref)
  - riferimento per le differenze dei moduli: anno 2022 (baseline).
Valori provvisori 2023-2025, in corso di consolidamento con le serie storiche definitive.
"""
MJ_PER_GJ = 1000.0
KEL = 3.6           # MJ/kWh
B_FUEL = 42.0       # MJ/Nm3 exergia chimica metano (~1.04*LHV)

REF_YEAR = 2022
YEARS = [2023, 2024, 2025]
# mappa scenari KPI (storico = ERP consolidato; real-time = E2C)
YEAR_HIST = 2023
YEAR_RT   = 2025

PLANTS = {
    "D020": dict(desc="Viano — MTO",               P=3_800_000),
    "D060": dict(desc="Scandiano — ibrido MTS+MTO", P=6_400_000),
    "D240": dict(desc="Frassinoro — MTO",           P=5_100_000),
}

# intensita exergetica energetica Ex_ref/m2 [MJ/m2] (in calo; D020 la piu' alta)
EXREF_INT = {
    "D020": {2022:53.0, 2023:51.5, 2024:50.0, 2025:48.5},
    "D060": {2022:50.5, 2023:49.0, 2024:47.5, 2025:46.0},
    "D240": {2022:49.0, 2023:47.5, 2024:46.2, 2025:45.0},
}
FUEL_SHARE = 0.80
PSI = {
    "D020": {2022:0.150, 2023:0.154, 2024:0.159, 2025:0.164},
    "D060": {2022:0.158, 2023:0.163, 2024:0.168, 2025:0.173},
    "D240": {2022:0.163, 2023:0.168, 2024:0.172, 2025:0.176},
}

TERM_BASE_FRAC = {   # frazione di Ex_ref@REF_YEAR
    "loss_MTS": 0.300, "loss_MTO": 0.260, "inv": 0.030, "qual_MTS": 0.010, "qual_MTO": 0.008,
    "RI": 1.200, "IEQ": 0.200, "WEX": 0.080, "CIRC": 0.060,
    "VA": 0.800, "econ_in": 0.250, "INV": 0.120,
    "SV": 0.350, "train": 0.020, "lost": 0.030, "CO2": 0.150,
}
TERM_KIND = {
    "loss_MTS":"cost","loss_MTO":"cost","inv":"cost","qual_MTS":"cost","qual_MTO":"cost",
    "RI":"cost","IEQ":"cost","WEX":"cost","CIRC":"benefit",
    "VA":"benefit","econ_in":"cost","INV":"cost",
    "SV":"benefit","train":"benefit","lost":"cost","CO2":"cost",
}
TERM_MODULE = {"loss_MTS":"TEI-J","loss_MTO":"TEI-J","inv":"TEI-J","qual_MTS":"TEI-J","qual_MTO":"TEI-J",
               "RI":"EFA-J","IEQ":"EFA-J","WEX":"EFA-J","CIRC":"EFA-J",
               "VA":"EcoFA-J","econ_in":"EcoFA-J","INV":"EcoFA-J",
               "SV":"SFA-J","train":"SFA-J","lost":"SFA-J","CO2":"SFA-J"}
# miglioramento cumulato vs REF_YEAR per anno
IMPROV = {2022:0.00, 2023:0.08, 2024:0.13, 2025:0.18}
TERM_IMPROV_MULT = {
    "loss_MTS":1.0,"loss_MTO":1.0,"inv":0.9,"qual_MTS":0.8,"qual_MTO":0.8,
    "RI":0.10,"IEQ":0.5,"WEX":1.0,"CIRC":1.5,
    "VA":0.30,"econ_in":0.5,"INV":0.7,
    "SV":0.30,"train":1.2,"lost":1.0,"CO2":0.8,
}

def exref_mj(plant, year): return EXREF_INT[plant][year]*PLANTS[plant]["P"]
def energy_split(plant, year):
    er=exref_mj(plant,year); ex_fuel=FUEL_SHARE*er; ex_el=(1-FUEL_SHARE)*er
    return dict(Ex_ref_MJ=er, Ex_fuel_MJ=ex_fuel, Ex_el_MJ=ex_el,
                V_gas_Nm3=ex_fuel/B_FUEL, kWh=ex_el/KEL,
                Ex_useful_MJ=PSI[plant][year]*er, Psi=PSI[plant][year])
def term_value(plant, year):
    er_ref=exref_mj(plant,REF_YEAR); out={}
    for t,frac in TERM_BASE_FRAC.items():
        base=frac*er_ref; f=IMPROV[year]*TERM_IMPROV_MULT[t]
        out[t]=base*(1.0-f) if TERM_KIND[t]=="cost" else base*(1.0+f)
    return out

def _gj(mj): return mj/MJ_PER_GJ
def tei_j(t,tr):  return _gj((tr["loss_MTS"]+tr["loss_MTO"])-(t["loss_MTS"]+t["loss_MTO"])-t["inv"]-t["qual_MTS"]-t["qual_MTO"])
def efa_j(t,tr):  return _gj((tr["RI"]-t["RI"])+(t["CIRC"]-tr["CIRC"])-(t["IEQ"]-tr["IEQ"])-(t["WEX"]-tr["WEX"]))
def ecofa_j(t,tr):return _gj((t["VA"]-tr["VA"])-(t["econ_in"]-tr["econ_in"])-(t["INV"]-tr["INV"]))
def sfa_j(t,tr):  return _gj((t["SV"]-tr["SV"])+(t["train"]-tr["train"])-(t["lost"]-tr["lost"])-(t["CO2"]-tr["CO2"]))
def contributions(plant, year):
    tr=term_value(plant,REF_YEAR); t=term_value(plant,year)
    return dict(f_env=efa_j(t,tr), f_econ=ecofa_j(t,tr), f_soc=sfa_j(t,tr), f_tech=tei_j(t,tr))

if __name__=="__main__":
    for p in PLANTS:
        for y in YEARS:
            c=contributions(p,y); e=energy_split(p,y); SA=sum(c.values())
            print(f"{p} {y} f_env={c['f_env']:7.0f} f_econ={c['f_econ']:7.0f} f_soc={c['f_soc']:6.0f} f_tech={c['f_tech']:7.0f} SA={SA:8.0f}GJ Psi={e['Psi']:.3f}")
