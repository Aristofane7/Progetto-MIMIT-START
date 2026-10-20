"""Assessment dell'impatto di START — analisi input-output di Leontief (task RP 8.6).

Stampa i moltiplicatori di produzione (Tipo I / Tipo II) e l'impatto del progetto su
Emilia-Romagna, Provincia di Bolzano, Sardegna e Calabria scomposto in
diretto/indiretto/indotto (output, valore aggiunto, occupazione). Esporta
output/impatto_*.csv per il cruscotto Power BI.

Uso: dalla cartella RP8.6/  ->  python run_impatto.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd  # noqa: E402

import impatto  # noqa: E402


def main() -> None:
    print("=== Simulazione dell'impatto di START — modello input-output (RP 8.6) ===")
    print("(simulazione con valori rappresentativi; modello da applicare ex-post con dati ISTAT)\n")

    m = impatto.multipliers()
    print("Moltiplicatori di produzione per settore (Tipo I aperto / Tipo II chiuso):")
    for j, s in enumerate(impatto.SECTORS):
        print(f"  {s:42s} {m['tipo1'][j]:.2f} / {m['tipo2'][j]:.2f}")

    print("\nImpatto simulato per regione (M EUR, ULA):")
    rows = []
    for r in impatto.FINAL_DEMAND:
        i = impatto.impact(r)
        rows.append({k: v for k, v in i.items() if k != "dx_settori_totale"})
        print(f"  [{r}] moltiplicatore output {i['moltiplicatore_output']}")
        print(f"    Output:  diretto {i['output_diretto']:.1f}  indiretto {i['output_indiretto']:.1f}  "
              f"indotto {i['output_indotto']:.1f}  -> totale {i['output_totale']:.1f}")
        print(f"    Valore aggiunto: {i['va_totale']:.1f} M EUR  |  Occupazione: {i['occ_totale']:.0f} ULA")

    print("\nVerifica KPI (baseline 0 -> obiettivo 1):")
    for r in impatto.kpi_check():
        print(f"  {r['kpi']:52s} {r['baseline']} -> {r['valore']}  ({r['dettaglio']})")

    s = impatto.summary()
    print(f"\nSintesi della simulazione: output diretto {s['output_diretto_totale']} M EUR -> "
          f"attivato {s['output_attivato_totale']} M EUR (moltiplicatore medio {s['moltiplicatore_medio']}); "
          f"valore aggiunto {s['valore_aggiunto_totale']} M EUR; occupazione {s['occupazione_ula_totale']:.0f} ULA.")

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(out_dir / "impatto_regioni.csv", index=False)
    molt = pd.DataFrame({"settore": impatto.SECTORS,
                         "moltiplicatore_tipo1": m["tipo1"], "moltiplicatore_tipo2": m["tipo2"]})
    molt.to_csv(out_dir / "impatto_moltiplicatori.csv", index=False)
    pd.DataFrame(impatto.kpi_check()).to_csv(out_dir / "impatto_kpi.csv", index=False)
    print(f"\nRisultati esportati per Power BI in: {out_dir}/impatto_*.csv")


if __name__ == "__main__":
    main()
