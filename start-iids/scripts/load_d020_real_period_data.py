"""Load the REAL measured D020 partial-year period data into the RP7.3 model (ADR-015).

Reads the filled `data/reference/RP7.3_D020_partial_year_data_collection.xlsx`
(project owner delivered 2026-10-19, ERP/MES/HSE, cessation 2025-07-31) and writes
the real values into:
  - `Unita` (D020/2025 period production),
  - `Energia` + `Moduli_*` (D020/2025 period),
  - `Riferimento` (D020/2022 Jan–July homologous baseline, option A),
  - `Periodo` (D020/2025 window, 7 months),
then recomputes the calculation log, bumping it to **beta-1.3**. Replaces the
provisional seasonal-profile values that were in beta-1.2. Writes both mirror
copies (repo root + data/reference). Idempotent given the same input file.

D020 (Viano) is an MTO-only plant: `loss_MTS` and `qual_MTS` are legitimately 0
(no spray-dryer / MTS stage); the real data reflect this.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import openpyxl

from src.engines.ecofa.formulas import compute_f_econ
from src.engines.efa.formulas import compute_f_env
from src.engines.sfa.formulas import compute_f_soc
from src.engines.tei.formulas import compute_f_tech

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
DATA = ROOT / "data" / "reference"
COLLECTION = DATA / "RP7.3_D020_partial_year_data_collection.xlsx"
WB_COPIES = [DATA / "RP7.3_data_collection_20232025.xlsx", REPO_ROOT / "RP7.3_data_collection_20232025.xlsx"]
LOG_COPIES = [DATA / "RP7.3_calculation_log.xlsx", REPO_ROOT / "RP7.3_calculation_log.xlsx"]

NEW_VERSION = "beta-1.3"
TODAY = "2026-10-19"
PERIOD_2025 = ("2025-01-01", "2025-07-31")
PERIOD_2022H = ("2022-01-01", "2022-07-31")
MONTHS_ACTIVE = 7
W = {"env": 0.3661, "econ": 0.1451, "soc": 0.0955, "tech": 0.3934}
EL_EX, GAS_EX = 3.6, 42

TEI_KEYS = ["loss_MTS_MJ", "loss_MTO_MJ", "inv_MJ", "qual_MTS_MJ", "qual_MTO_MJ"]
EFA_KEYS = ["RI_MJ", "IEQ_MJ", "WEX_MJ", "CIRC_MJ"]
ECO_KEYS = ["VA_MJ", "econ_in_MJ", "INV_MJ"]
SFA_KEYS = ["SV_MJ", "train_MJ", "lost_MJ", "CO2_MJ"]
MODULE_OF = {k: "TEI-J" for k in TEI_KEYS} | {k: "EFA-J" for k in EFA_KEYS} \
    | {k: "EcoFA-J" for k in ECO_KEYS} | {k: "SFA-J" for k in SFA_KEYS}


def read_collection() -> tuple[dict, dict]:
    wb = openpyxl.load_workbook(COLLECTION, data_only=True)

    def sheet(name: str) -> dict:
        rows = list(wb[name].iter_rows(values_only=True))
        hi = next(i for i, r in enumerate(rows) if r and r[0] == "campo")
        iv = rows[hi].index("VALORE")
        return {r[0]: r[iv] for r in rows[hi + 1:] if r and r[0]}

    return sheet("03_D020_2025_periodo"), sheet("04_D020_2022_omologo")


def update_workbook(cur: dict, base: dict) -> None:
    wb = openpyxl.load_workbook(WB_COPIES[0])

    def set_cells(sheet: str, year: int, mapping: dict) -> None:
        ws = wb[sheet]
        hdr = [c.value for c in ws[1]]
        for row in ws.iter_rows(min_row=2):
            if row[0].value == "D020" and row[1].value == year:
                for term, val in mapping.items():
                    row[hdr.index(term)].value = val

    set_cells("Unita", 2025, {"produzione_m2": cur["produzione_m2"]})
    set_cells("Energia", 2025, {"V_gas_Nm3": cur["V_gas_Nm3"], "E_el_kWh": cur["E_el_kWh"]})
    set_cells("Moduli_TEI", 2025, {k: cur[k] for k in TEI_KEYS})
    set_cells("Moduli_EFA", 2025, {k: cur[k] for k in EFA_KEYS})
    set_cells("Moduli_EcoFA", 2025, {k: cur[k] for k in ECO_KEYS})
    set_cells("Moduli_SFA", 2025, {k: cur[k] for k in SFA_KEYS})

    # Riferimento: real homologous 2022 Jan-July terms (rebuild D020/2025 rows)
    rif = wb["Riferimento"]
    keep = [r for r in rif.iter_rows(min_row=2, values_only=True)
            if not (r[0] == "D020" and r[1] == 2025)]
    rif.delete_rows(2, rif.max_row)
    for r in keep:
        rif.append(r)
    for term in TEI_KEYS + EFA_KEYS + ECO_KEYS + SFA_KEYS:
        rif.append(["D020", 2025, "D020", 2022, PERIOD_2022H[0], PERIOD_2022H[1],
                    MODULE_OF[term], term, base[term]])

    wb.save(WB_COPIES[0])
    for dst in WB_COPIES[1:]:
        shutil.copyfile(WB_COPIES[0], dst)
    print(f"workbook updated with REAL D020 period data -> {len(WB_COPIES)} copies")


def compute_d020_2025(cur: dict, base: dict) -> dict:
    f_env = compute_f_env(cur["RI_MJ"], base["RI_MJ"], cur["CIRC_MJ"], base["CIRC_MJ"],
                          cur["IEQ_MJ"], base["IEQ_MJ"], cur["WEX_MJ"], base["WEX_MJ"]) / 1000
    f_econ = compute_f_econ(cur["VA_MJ"], base["VA_MJ"], cur["econ_in_MJ"], base["econ_in_MJ"],
                            cur["INV_MJ"], base["INV_MJ"]) / 1000
    f_soc = compute_f_soc(cur["SV_MJ"], base["SV_MJ"], cur["train_MJ"], base["train_MJ"],
                          cur["lost_MJ"], base["lost_MJ"], cur["CO2_MJ"], base["CO2_MJ"]) / 1000
    f_tech = compute_f_tech(ex_loss_base_mts_mj=base["loss_MTS_MJ"], ex_loss_base_mto_mj=base["loss_MTO_MJ"],
                            ex_loss_mts_mj=cur["loss_MTS_MJ"], ex_loss_mto_mj=cur["loss_MTO_MJ"],
                            ex_inv_mj=cur["inv_MJ"], ex_qual_mts_mj=cur["qual_MTS_MJ"],
                            ex_qual_mto_mj=cur["qual_MTO_MJ"]) / 1000
    sa_raw = f_env + f_econ + f_soc + f_tech
    sa_w = W["env"] * f_env + W["econ"] * f_econ + W["soc"] * f_soc + W["tech"] * f_tech
    ex_ref = (cur["E_el_kWh"] * EL_EX + cur["V_gas_Nm3"] * GAS_EX) / 1000
    phi = sa_w / ex_ref
    psi = cur["Psi"]
    tsi_abs = 0.5 * phi + 0.5 * psi
    return {"f_env": f_env, "f_econ": f_econ, "f_soc": f_soc, "f_tech": f_tech,
            "SA_raw": sa_raw, "SA_w": sa_w, "Ex_ref": ex_ref, "Phi": phi,
            "Psi": psi, "TSI_abs": tsi_abs}


def update_log(out: dict) -> None:
    wb = openpyxl.load_workbook(LOG_COPIES[0])
    ws = wb["calculation_log"]
    hdr = [c.value for c in ws[1]]
    i_var, i_out, i_date, i_ver = (hdr.index("variable"), hdr.index("output"),
                                   hdr.index("date"), hdr.index("script_version"))
    tsi_abs_2023 = next(r[i_out].value for r in ws.iter_rows(min_row=2)
                        if r[2].value == "D020" and r[3].value == 2023 and r[i_var].value == "TSI_abs")
    for row in ws.iter_rows(min_row=2):
        row[i_ver].value = NEW_VERSION
        if row[2].value == "D020" and row[3].value == 2025:
            row[i_date].value = TODAY
            var = row[i_var].value
            if var in out:
                row[i_out].value = round(out[var], 4)
            elif var == "TSI_rel":
                row[i_out].value = round(out["TSI_abs"] / tsi_abs_2023, 4)
    wb.save(LOG_COPIES[0])
    for dst in LOG_COPIES[1:]:
        shutil.copyfile(LOG_COPIES[0], dst)
    print(f"calculation log {NEW_VERSION} written -> {len(LOG_COPIES)} copies")


def main() -> None:
    cur, base = read_collection()
    update_workbook(cur, base)
    out = compute_d020_2025(cur, base)
    print("D020/2025 (REAL):", {k: round(v, 4) for k, v in out.items()})
    update_log(out)


if __name__ == "__main__":
    main()
