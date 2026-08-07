# -*- coding: utf-8 -*-
"""
RP7.3 — EEA+ beta: core del motore di calcolo.
Convenzioni:
  - unita di calcolo interne: MJ  (MJ -> GJ  =>  / 1000)   [fix bug /1e9]
  - exergia combustibile = exergia chimica (b_fuel), efficienza di conversione in Psi (non in Ex_ref)
Tutti i valori numerici di default sono DIMOSTRATIVI / NON VALIDATI (confidence C).
"""
MJ_PER_GJ = 1000.0            # MJ -> GJ
KEL = 3.6                     # MJ per kWh (exergia elettrica, fattore unitario)
B_FUEL = 42.0                 # MJ/Nm3  exergia chimica specifica metano (~1.04*LHV) [DIMOSTRATIVO, conf. C]

PLANTS = {
    "D020": dict(desc="Viano — MTO",              P=3_800_000),
    "D060": dict(desc="Scandiano — ibrido MTS+MTO", P=6_400_000),
    "D240": dict(desc="Frassinoro — MTO",          P=5_100_000),
}
SCENARIOS = ["ref2017", "historical", "realtime"]   # ref2017 = riferimento per le differenze

# intensita exergetica energetica di processo Ex_ref/m2 [MJ/m2]  (ref peggiore, migliora)
EXREF_INT = {
    "D020": dict(ref2017=55.0, historical=52.0, realtime=49.0),
    "D060": dict(ref2017=53.0, historical=49.5, realtime=46.2),
    "D240": dict(ref2017=52.0, historical=47.8, realtime=45.3),
}
FUEL_SHARE = 0.80             # quota fuel dell'Ex_ref (resto elettrico)
# efficienza exergetica di II principio Psi = Ex_useful/Ex_ref
PSI = {
    "D020": dict(ref2017=0.140, historical=0.148, realtime=0.163),
    "D060": dict(ref2017=0.146, historical=0.156, realtime=0.172),
    "D240": dict(ref2017=0.150, historical=0.161, realtime=0.175),
}

# --- Termini dei 4 moduli (MJ) definiti come base@ref * fattore(scenario) ---
# "cost" = minore e' meglio ; "benefit" = maggiore e' meglio.
# base espresso come frazione g dell'Ex_ref@ref2017 (in MJ)
TERM_BASE_FRAC = {   # frazione di Ex_ref_ref2017
    # TEI-J
    "loss_MTS": 0.300, "loss_MTO": 0.260, "inv": 0.030, "qual_MTS": 0.010, "qual_MTO": 0.008,
    # EFA-J
    "RI": 1.200, "IEQ": 0.200, "WEX": 0.080, "CIRC": 0.060,
    # EcoFA-J
    "VA": 0.800, "econ_in": 0.250, "INV": 0.120,
    # SFA-J
    "SV": 0.350, "train": 0.020, "lost": 0.030, "CO2": 0.150,
}
TERM_KIND = {  # benefit -> aumenta col miglioramento ; cost -> diminuisce
    "loss_MTS":"cost","loss_MTO":"cost","inv":"cost","qual_MTS":"cost","qual_MTO":"cost",
    "RI":"cost","IEQ":"cost","WEX":"cost","CIRC":"benefit",
    "VA":"benefit","econ_in":"cost","INV":"cost",
    "SV":"benefit","train":"benefit","lost":"cost","CO2":"cost",
}
# fattori di miglioramento per scenario (0 = ref). realtime > historical
IMPROV = dict(ref2017=0.00, historical=0.10, realtime=0.20)  # scala generale
# modulatore per-termine (alcuni migliorano piu' di altri)
TERM_IMPROV_MULT = {
    "loss_MTS":1.0,"loss_MTO":1.0,"inv":0.9,"qual_MTS":0.8,"qual_MTO":0.8,
    "RI":0.10,"IEQ":0.5,"WEX":1.0,"CIRC":1.5,
    "VA":0.30,"econ_in":0.5,"INV":0.7,
    "SV":0.30,"train":1.2,"lost":1.0,"CO2":0.8,
}

def exref_mj(plant, scen):
    return EXREF_INT[plant][scen] * PLANTS[plant]["P"]

def energy_split(plant, scen):
    er = exref_mj(plant, scen)
    ex_fuel = FUEL_SHARE*er; ex_el = (1-FUEL_SHARE)*er
    V_gas = ex_fuel / B_FUEL          # Nm3
    kWh = ex_el / KEL
    return dict(Ex_ref_MJ=er, Ex_fuel_MJ=ex_fuel, Ex_el_MJ=ex_el, V_gas_Nm3=V_gas, kWh=kWh,
                Ex_useful_MJ=PSI[plant][scen]*er, Psi=PSI[plant][scen])

def term_value(plant, scen):
    """valore MJ di ciascun termine dei moduli per plant/scenario."""
    er_ref = exref_mj(plant, "ref2017")
    out = {}
    for t, frac in TERM_BASE_FRAC.items():
        base = frac * er_ref
        f = IMPROV[scen]*TERM_IMPROV_MULT[t]
        if TERM_KIND[t] == "cost":
            out[t] = base*(1.0 - f)
        else:
            out[t] = base*(1.0 + f)
    return out

# ---------------- MODULI -J (ritornano GJ) ----------------
def _gj(mj): return mj / MJ_PER_GJ

def tei_j(terms, terms_ref):
    loss_saved = (terms_ref["loss_MTS"]+terms_ref["loss_MTO"]) - (terms["loss_MTS"]+terms["loss_MTO"])
    f = loss_saved - terms["inv"] - terms["qual_MTS"] - terms["qual_MTO"]
    return _gj(f)

def efa_j(terms, terms_ref):
    f = (terms_ref["RI"]-terms["RI"]) + (terms["CIRC"]-terms_ref["CIRC"]) \
        - (terms["IEQ"]-terms_ref["IEQ"]) - (terms["WEX"]-terms_ref["WEX"])
    return _gj(f)

def ecofa_j(terms, terms_ref):
    f = (terms["VA"]-terms_ref["VA"]) - (terms["econ_in"]-terms_ref["econ_in"]) - (terms["INV"]-terms_ref["INV"])
    return _gj(f)

def sfa_j(terms, terms_ref):
    f = (terms["SV"]-terms_ref["SV"]) + (terms["train"]-terms_ref["train"]) \
        - (terms["lost"]-terms_ref["lost"]) - (terms["CO2"]-terms_ref["CO2"])
    return _gj(f)

def contributions(plant, scen):
    tr = term_value(plant, "ref2017"); t = term_value(plant, scen)
    return dict(f_env=efa_j(t,tr), f_econ=ecofa_j(t,tr), f_soc=sfa_j(t,tr), f_tech=tei_j(t,tr))

if __name__ == "__main__":
    for p in PLANTS:
        for s in ["historical","realtime"]:
            c = contributions(p,s); e = energy_split(p,s)
            SA = sum(c.values())
            print(f"{p} {s:10} f_env={c['f_env']:7.0f} f_econ={c['f_econ']:7.0f} f_soc={c['f_soc']:7.0f} f_tech={c['f_tech']:7.0f} SA_raw={SA:8.0f} GJ | Ex_ref={_gj(e['Ex_ref_MJ']):8.0f}GJ Psi={e['Psi']:.3f}")
