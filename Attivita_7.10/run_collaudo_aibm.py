"""Modello di Business guidato dall'Intelligenza Artificiale — AI-BM (task RP 7.10).

Stampa il Business Model Canvas (as-is tradizionale -> to-be AI-BM), la verifica del
KPI qualitativo (BMC), la catena dato -> informazione -> valore, l'analisi SWOT e il
transition model. Esporta output/collaudo_aibm_*.csv per Power BI.

Uso: python run_collaudo_aibm.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd  # noqa: E402

import aibm  # noqa: E402


def main() -> None:
    print("=== AI-BM: Modello di Business guidato dall'IA (RP 7.10) ===\n")

    print("Business Model Canvas (as-is tradizionale -> to-be AI-BM):")
    for b in aibm.BMC_BLOCKS:
        print(f"  [{b['id']}] {b['blocco']}")
        print(f"      as-is: {b['asis']}")
        print(f"      to-be: {b['tobe']}")

    r = aibm.kpi_check()[0]
    print(f"\nVerifica KPI (qualitativo): {r['kpi']}")
    print(f"  baseline: {r['baseline']}  ->  obiettivo: {r['obiettivo']}")
    print(f"  blocchi riconfigurati: {r['blocchi_riconfigurati']}/{r['blocchi_totali']}  "
          f"(canvas prodotto: {'SI' if r['prodotto'] else 'no'})")

    print("\nCatena dato -> informazione -> valore:")
    for s in aibm.DATA_VALUE_CHAIN:
        print(f"  {s['stadio']:12s}: {s['contenuto']}")
        print(f"  {'':12s}  fonte: {s['fonte']}")

    print("\nTransition model (da asset-based/episodico a adattivo/data-driven):")
    for d in aibm.TRANSITION:
        print(f"  {d['dimensione']:18s}: {d['da']}  ->  {d['a']}")

    print("\nAnalisi SWOT dell'AI-BM:")
    for k, items in aibm.SWOT.items():
        print(f"  {k}:")
        for it in items:
            print(f"    - {it}")

    print("\nTensioni sistemiche dell'embodied AI-BM:")
    for t in aibm.TENSIONS:
        print(f"  - {t}")

    f = aibm.financials()
    print("\nQuantificazione economica (valori rappresentativi, k EUR):")
    print(f"  Investimento: {f['investimento']:.0f}  |  Beneficio netto annuo: "
          f"{f['beneficio_netto_annuo']:.0f}")
    print(f"  Livello progetto -> ROI: {f['roi_pct']:.1f}%  |  Payback: "
          f"{f['payback_anni']:.2f} anni")
    print(f"  Contesto di gruppo -> ROA ~{f['roa_gruppo_pct']:.0f}%  |  contributo "
          f"marginale AI-BM: +{f['contributo_roa_pp']:.2f} pp  (beneficio = "
          f"{f['quota_ebitda_pct']:.1f}% dell'EBITDA)")

    print("\nEsito: AI-BM definito e proposto (Business Model Canvas prodotto; "
          "analisi strategica via SWOT e transition model; validazione economica via "
          "ROI/payback; baseline BM tradizionale -> obiettivo AI-BM).")

    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    pd.DataFrame(aibm.kpi_check()).to_csv(out_dir / "collaudo_aibm_kpi.csv", index=False)
    pd.DataFrame(aibm.bmc_rows()).to_csv(out_dir / "collaudo_aibm_bmc.csv", index=False)
    pd.DataFrame(aibm.DATA_VALUE_CHAIN).to_csv(out_dir / "collaudo_aibm_datavalue.csv", index=False)
    pd.DataFrame(aibm.TRANSITION).to_csv(out_dir / "collaudo_aibm_transition.csv", index=False)
    swot_rows = [{"quadrante": k, "voce": it} for k, items in aibm.SWOT.items() for it in items]
    pd.DataFrame(swot_rows).to_csv(out_dir / "collaudo_aibm_swot.csv", index=False)
    pd.DataFrame([f]).to_csv(out_dir / "collaudo_aibm_finanza.csv", index=False)
    print(f"\nRisultati esportati per Power BI in: {out_dir}/collaudo_aibm_*.csv")


if __name__ == "__main__":
    main()
