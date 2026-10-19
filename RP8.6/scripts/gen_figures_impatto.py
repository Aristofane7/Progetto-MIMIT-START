"""Genera le figure della relazione RP 8.6 (Assessment dell'impatto — input-output).

Produce in docs/figures/:
  fig_imp1_metodo.png         - schema del modello di Leontief (domanda -> output)
  fig_imp2_moltiplicatori.png - moltiplicatori di produzione per settore (Tipo I / II)
  fig_imp3_regioni.png        - impatto sull'output per regione (diretto/indiretto/indotto)
  fig_imp4_impatto.png        - valore aggiunto e occupazione attivati per regione
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import impatto as im

GREEN = "#2E5A34"
GREEN_L = "#7DAF87"
NAVY = "#1F3864"
GREY = "#5A5A5A"
LIGHT = "#EDF2EE"
AMBER = "#E0A100"
RED = "#B23A2E"
BLUEG = "#6B7FB3"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "figure.dpi": 150, "savefig.dpi": 150, "savefig.bbox": "tight"})

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)


def _wrap(t, w):
    return "\n".join(textwrap.wrap(t, w))


# --- Fig 1: schema del modello di Leontief ----------------------------------------
def fig1_metodo():
    fig, ax = plt.subplots(figsize=(13, 5.4))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    ax.text(7, 6.6, "Modello input-output di Leontief: dalla domanda finale all'impatto totale",
            ha="center", color=NAVY, fontsize=13, fontweight="bold")

    def box(x, y, w, h, title, sub, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=fc, edgecolor="white", lw=1.6))
        ax.text(x + w / 2, y + h - 0.42, title, ha="center", va="top", color="white",
                fontsize=10.5, fontweight="bold")
        ax.text(x + w / 2, y + h - 1.05, sub, ha="center", va="top", color="white", fontsize=8.4)

    def arrow(x0, x1, y, label=""):
        ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=18,
                                     color=GREY, lw=2.4))
        if label:
            ax.text((x0 + x1) / 2, y + 0.35, label, ha="center", color=GREY, fontsize=8.5,
                    style="italic")

    box(0.4, 2.7, 3.0, 2.2, "Domanda finale df", "shock del progetto START\n(investimenti +\nproduzione abilitata)", NAVY)
    box(5.0, 2.7, 3.4, 2.2, "Inversa di Leontief", "L = (I - A)^-1\n(coefficienti tecnici A\ndella filiera)", GREEN)
    box(10.0, 2.7, 3.4, 2.2, "Output attivato dx", "dx = L x df\n(diretto + indiretto\n+ indotto)", AMBER)
    arrow(3.5, 4.9, 3.8)
    arrow(8.5, 9.9, 3.8)

    ax.text(7, 1.35, "Impatto = Output  ->  Valore aggiunto (contributo al PIL)  ->  Occupazione (ULA)",
            ha="center", color=NAVY, fontsize=10.5, fontweight="bold")
    ax.text(7, 0.6, "Modello da eseguire in simulazione ora e applicare ex-post con i dati regionali ISTAT",
            ha="center", color=GREY, fontsize=9, style="italic")
    fig.savefig(FIG / "fig_imp1_metodo.png")
    plt.close(fig)


# --- Fig 2: moltiplicatori per settore --------------------------------------------
def fig2_moltiplicatori():
    m = im.multipliers()
    labels = [_wrap(s, 16) for s in im.SECTORS]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(11, 6))
    h = 0.38
    ax.barh(y + h / 2, m["tipo1"], height=h, color=GREEN, edgecolor="white", label="Tipo I (aperto)")
    ax.barh(y - h / 2, m["tipo2"], height=h, color=AMBER, edgecolor="white", label="Tipo II (chiuso)")
    for i in range(len(labels)):
        ax.text(m["tipo1"][i] + 0.02, y[i] + h / 2, f"{m['tipo1'][i]:.2f}", va="center", fontsize=8.5, color=GREEN)
        ax.text(m["tipo2"][i] + 0.02, y[i] - h / 2, f"{m['tipo2'][i]:.2f}", va="center", fontsize=8.5, color="#9a7000")
    ax.axvline(1.0, color=GREY, lw=1, ls="--")
    ax.text(1.0, len(labels) - 0.3, " soglia 1.0", color=GREY, fontsize=8, va="top")
    ax.set_yticks(y, labels, fontsize=9)
    ax.set_xlabel("Moltiplicatore di produzione (EUR di output totale per 1 EUR di domanda finale)")
    ax.set_title("Moltiplicatori di produzione per settore (modello di Leontief)",
                 fontsize=12.5, fontweight="bold", color=NAVY)
    ax.legend(loc="lower right", frameon=False, fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig_imp2_moltiplicatori.png")
    plt.close(fig)


# --- Fig 3: impatto sull'output per regione ---------------------------------------
def fig3_regioni():
    regs = list(im.FINAL_DEMAND)
    imps = [im.impact(r) for r in regs]
    x = np.arange(len(regs))
    dir_ = [i["output_diretto"] for i in imps]
    ind = [i["output_indiretto"] for i in imps]
    indu = [i["output_indotto"] for i in imps]
    fig, ax = plt.subplots(figsize=(10.5, 6.2))
    w = 0.5
    b1 = ax.bar(x, dir_, w, color=NAVY, edgecolor="white", label="Diretto (domanda finale)")
    b2 = ax.bar(x, ind, w, bottom=dir_, color=GREEN, edgecolor="white", label="Indiretto (filiera)")
    b3 = ax.bar(x, indu, w, bottom=np.array(dir_) + np.array(ind), color=AMBER, edgecolor="white",
                label="Indotto (consumi)")
    for i, imp in enumerate(imps):
        tot = imp["output_totale"]
        ax.text(i, tot + 1.2, f"{tot:.1f} M EUR\n(x{imp['moltiplicatore_output']})", ha="center",
                va="bottom", fontsize=9.5, fontweight="bold", color=NAVY)
    for bars, vals in [(b1, dir_), (b2, ind), (b3, indu)]:
        for rect, v in zip(bars, vals):
            if rect.get_height() > 1.5:
                ax.text(rect.get_x() + rect.get_width() / 2, rect.get_y() + rect.get_height() / 2,
                        f"{v:.1f}", ha="center", va="center", color="white", fontsize=8.5, fontweight="bold")
    ax.set_xticks(x, [_wrap(r, 12) for r in regs], fontsize=10)
    ax.set_ylabel("Output attivato (M EUR / anno)")
    ax.set_ylim(0, max(i["output_totale"] for i in imps) * 1.22)
    ax.set_title("Simulazione dell'impatto sull'output per regione\n(scomposizione diretto / indiretto / indotto — valori rappresentativi)",
                 fontsize=12.5, fontweight="bold", color=NAVY)
    ax.legend(loc="upper right", frameon=False, fontsize=9.5)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "fig_imp3_regioni.png")
    plt.close(fig)


# --- Fig 4: valore aggiunto e occupazione -----------------------------------------
def fig4_impatto():
    regs = list(im.FINAL_DEMAND)
    imps = [im.impact(r) for r in regs]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.6))

    x = np.arange(len(regs))
    xlabels = [_wrap(r, 12) for r in regs]
    # valore aggiunto
    va_d = [i["va_diretto"] for i in imps]
    va_i = [i["va_indiretto"] for i in imps]
    va_u = [i["va_indotto"] for i in imps]
    ax1.bar(x, va_d, 0.5, color=NAVY, edgecolor="white", label="Diretto")
    ax1.bar(x, va_i, 0.5, bottom=va_d, color=GREEN, edgecolor="white", label="Indiretto")
    ax1.bar(x, va_u, 0.5, bottom=np.array(va_d) + np.array(va_i), color=AMBER, edgecolor="white", label="Indotto")
    for i, imp in enumerate(imps):
        ax1.text(i, imp["va_totale"] + 0.6, f"{imp['va_totale']:.1f}", ha="center", fontsize=9.5,
                 fontweight="bold", color=NAVY)
    ax1.set_xticks(x, xlabels, fontsize=9)
    ax1.set_ylabel("Valore aggiunto attivato (M EUR / anno)")
    ax1.set_title("Contributo al valore aggiunto (PIL)", fontsize=11.5, fontweight="bold", color=NAVY)
    ax1.set_ylim(0, max(i["va_totale"] for i in imps) * 1.25)
    ax1.legend(loc="upper right", frameon=False, fontsize=9)
    ax1.spines[["top", "right"]].set_visible(False)

    # occupazione
    oc_d = [i["occ_diretta"] for i in imps]
    oc_i = [i["occ_indiretta"] for i in imps]
    oc_u = [i["occ_indotta"] for i in imps]
    ax2.bar(x, oc_d, 0.5, color=NAVY, edgecolor="white", label="Diretta")
    ax2.bar(x, oc_i, 0.5, bottom=oc_d, color=GREEN, edgecolor="white", label="Indiretta")
    ax2.bar(x, oc_u, 0.5, bottom=np.array(oc_d) + np.array(oc_i), color=AMBER, edgecolor="white", label="Indotta")
    for i, imp in enumerate(imps):
        ax2.text(i, imp["occ_totale"] + 6, f"{imp['occ_totale']:.0f}", ha="center", fontsize=9.5,
                 fontweight="bold", color=NAVY)
    ax2.set_xticks(x, xlabels, fontsize=9)
    ax2.set_ylabel("Occupazione attivata (ULA)")
    ax2.set_title("Occupazione attivata", fontsize=11.5, fontweight="bold", color=NAVY)
    ax2.set_ylim(0, max(i["occ_totale"] for i in imps) * 1.25)
    ax2.legend(loc="upper right", frameon=False, fontsize=9)
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Simulazione dell'impatto socio-economico del progetto START (valori rappresentativi)",
                 fontsize=12.5, fontweight="bold", color=NAVY, y=1.02)
    fig.tight_layout()
    fig.savefig(FIG / "fig_imp4_impatto.png")
    plt.close(fig)


if __name__ == "__main__":
    fig1_metodo()
    fig2_moltiplicatori()
    fig3_regioni()
    fig4_impatto()
    print("Figure RP 8.6 generate in", FIG)
    for f in sorted(FIG.glob("fig_imp*.png")):
        print(" -", f.name)
