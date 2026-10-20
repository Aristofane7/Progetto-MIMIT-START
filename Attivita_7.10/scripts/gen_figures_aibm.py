"""Genera le figure della relazione RP 7.10 (AI-BM).

Produce in docs/figures/:
  fig_aibm1_metodo.png      - metodo: dati OR7 -> catena dato/valore -> BMC + analisi strategica
  fig_aibm2_bmc.png         - Business Model Canvas (as-is tradizionale -> to-be AI-BM) = KPI
  fig_aibm3_swot.png        - matrice SWOT 2x2 dell'AI-BM
  fig_aibm4_transition.png  - transition model + catena dato->valore + tensioni sistemiche
  fig_aibm5_finanza.png     - validazione economica (ROI/payback livello progetto; ROA di gruppo)
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch  # noqa: E402

import aibm  # noqa: E402

GREEN = "#2E5A34"
GREEN_L = "#7DAF87"
NAVY = "#1F3864"
GREY = "#5A5A5A"
LIGHT = "#EDF2EE"
LIGHT2 = "#E7ECF4"
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


def _box(ax, x, y, w, h, title, body, fc, ec, tc="white", fs_t=10, fs_b=8.5, body_w=34):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                                linewidth=1.6, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h - 0.18, title, ha="center", va="top", color=tc,
            fontsize=fs_t, fontweight="bold", linespacing=1.1)
    if body:
        n_title = title.count("\n") + 1
        body_y = y + h - 0.30 - 0.30 * n_title
        ax.text(x + w / 2, body_y, _wrap(body, body_w), ha="center", va="top",
                color=tc, fontsize=fs_b, linespacing=1.15)


def _arrow(ax, p0, p1, color=GREY, lw=2.0):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=16,
                                 linewidth=lw, color=color, shrinkA=2, shrinkB=2))


# ---------------------------------------------------------------- fig 1: metodo
def fig_metodo():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 12); ax.set_ylim(0, 5); ax.axis("off")

    _box(ax, 0.2, 1.6, 2.6, 1.9,
         "Collaudi OR 7", "E2C (7.1), Intelligent Factory (7.2), assessment (7.3-7.4), "
         "DDQM (7.5), design (7.7), Intelligent Industry (7.8), involucro smart (7.9)",
         LIGHT, GREEN, tc=GREEN, fs_b=8, body_w=26)
    _box(ax, 3.2, 1.6, 2.6, 1.9,
         "Dato -> Informazione\n-> Valore", "La Intelligent Industry trasforma i dati "
         "multi-fonte in informazioni (AI) e in valore.", LIGHT, NAVY, tc=NAVY, body_w=26)
    _box(ax, 6.2, 1.6, 2.6, 1.9,
         "Business Model\nCanvas (KPI)", "9 blocchi riconfigurati as-is (tradizionale) "
         "-> to-be (AI-BM).", GREEN, GREEN, tc="white", body_w=26)
    _box(ax, 9.2, 1.6, 2.6, 1.9,
         "Analisi strategica", "SWOT + transition model (asset-based/episodico -> "
         "adattivo/data-driven) + tensioni.", NAVY, NAVY, tc="white", body_w=26)

    for x0, x1 in [(2.8, 3.2), (5.8, 6.2), (8.8, 9.2)]:
        _arrow(ax, (x0, 2.55), (x1, 2.55), color=GREY)

    ax.text(6.0, 4.5, "Metodo dell'attivita 7.10: dall'evidenza dei collaudi all'AI-BM validato",
            ha="center", va="center", fontsize=12, fontweight="bold", color=GREEN)
    ax.text(6.0, 0.5, "Baseline: Modello di Business tradizionale  ->  Obiettivo: AI-BM   "
            "(problema n. 10: consulenza specialistica di BM design)",
            ha="center", va="center", fontsize=8.5, color=GREY, style="italic")
    fig.savefig(FIG / "fig_aibm1_metodo.png"); plt.close(fig)


# ---------------------------------------------------------------- fig 2: BMC
def fig_bmc():
    # Layout canonico Osterwalder: 9 blocchi. Nel canvas si riportano le versioni
    # sintetiche (asis_key / tobe_key); il testo esteso e nella relazione e nei CSV.
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    short = {
        "Partnership chiave": "Partner chiave",
        "Attivita chiave": "Attivita chiave",
        "Proposta di valore": "Proposta di valore",
        "Relazioni con i clienti": "Relazioni con i clienti",
        "Segmenti di clientela": "Segmenti di clientela",
        "Risorse chiave": "Risorse chiave",
        "Canali": "Canali",
        "Flussi di ricavi": "Flussi di ricavi",
        "Struttura dei costi": "Struttura dei costi",
    }
    B = {b["blocco"]: b for b in aibm.BMC_BLOCKS}

    def cell(x, y, w, h, name):
        b = B[name]
        cw = max(16, int(w * 12.0))          # larghezza di wrap in caratteri
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.02",
                                    linewidth=1.3, edgecolor=NAVY, facecolor="white"))
        ax.text(x + 0.09, y + h - 0.12, short[name], ha="left", va="top",
                fontsize=9, fontweight="bold", color=NAVY)
        # sezione tradizionale (as-is)
        ax.text(x + 0.09, y + h - 0.48, "tradizionale", ha="left", va="top",
                fontsize=6.6, color=GREY, style="italic")
        ax.text(x + 0.09, y + h - 0.66, _wrap(b["asis_key"], cw), ha="left", va="top",
                fontsize=6.8, color=GREY, linespacing=1.15)
        # sezione AI-BM (to-be), evidenziata
        hb = h * 0.5
        ax.add_patch(FancyBboxPatch((x + 0.05, y + 0.05), w - 0.1, hb,
                                    boxstyle="round,pad=0.006,rounding_size=0.02",
                                    linewidth=0, facecolor=LIGHT))
        ax.text(x + 0.09, y + hb - 0.03, "AI-BM", ha="left", va="top",
                fontsize=6.8, color=GREEN, fontweight="bold")
        ax.text(x + 0.09, y + hb - 0.21, _wrap(b["tobe_key"], cw), ha="left", va="top",
                fontsize=6.8, color=GREEN, linespacing=1.15)

    # top row: colonne alte h=4.6 (y 2.9..7.5); celle impilate h=2.25
    cell(0.2, 2.9, 1.92, 4.6, "Partnership chiave")
    cell(2.16, 5.25, 1.92, 2.25, "Attivita chiave")
    cell(2.16, 2.9, 1.92, 2.25, "Risorse chiave")
    cell(4.12, 2.9, 1.92, 4.6, "Proposta di valore")
    cell(6.08, 5.25, 1.92, 2.25, "Relazioni con i clienti")
    cell(6.08, 2.9, 1.92, 2.25, "Canali")
    cell(8.04, 2.9, 1.76, 4.6, "Segmenti di clientela")
    # bottom row
    cell(0.2, 0.65, 4.86, 2.15, "Struttura dei costi")
    cell(5.1, 0.65, 4.7, 2.15, "Flussi di ricavi")

    ax.text(5.0, 9.5, "Business Model Canvas: da Modello tradizionale (grigio) ad AI-BM (verde)",
            ha="center", va="center", fontsize=13, fontweight="bold", color=GREEN)
    ax.text(5.0, 8.9, "KPI qualitativo — baseline: Modello di Business tradizionale  ->  "
            "obiettivo: AI-BM  (9/9 blocchi riconfigurati)",
            ha="center", va="center", fontsize=10, color=NAVY)
    fig.savefig(FIG / "fig_aibm2_bmc.png"); plt.close(fig)


# ---------------------------------------------------------------- fig 3: SWOT
def fig_swot():
    fig, ax = plt.subplots(figsize=(11, 6.4))
    ax.set_xlim(0, 10); ax.set_ylim(0, 7); ax.axis("off")
    quad = [("Forze", 0.2, 3.7, GREEN, "white"),
            ("Debolezze", 5.1, 3.7, RED, "white"),
            ("Opportunita", 0.2, 0.3, GREEN_L, "black"),
            ("Minacce", 5.1, 0.3, AMBER, "black")]
    for name, x, y, fc, tc in quad:
        ax.add_patch(FancyBboxPatch((x, y), 4.7, 3.2, boxstyle="round,pad=0.02,rounding_size=0.05",
                                    linewidth=1.6, edgecolor=fc, facecolor=fc, alpha=0.92))
        ax.text(x + 0.2, y + 3.0, name, ha="left", va="top", fontsize=13,
                fontweight="bold", color=tc)
        for i, it in enumerate(aibm.SWOT[name]):
            ax.text(x + 0.25, y + 2.55 - i * 0.62, "• " + _wrap(it, 46),
                    ha="left", va="top", fontsize=8.6, color=tc)
    ax.text(5.0, 6.95, "Analisi SWOT dell'AI-BM", ha="center", va="bottom",
            fontsize=13, fontweight="bold", color=NAVY)
    fig.savefig(FIG / "fig_aibm3_swot.png"); plt.close(fig)


# ---------------------------------------------------- fig 4: transition + chain
def fig_transition():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")

    ax.text(6.0, 7.7, "Transition model: da logiche asset-based/episodiche a sistemi adattivi data-driven",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=GREEN)

    y0 = 6.9
    for i, d in enumerate(aibm.TRANSITION):
        y = y0 - i * 0.60
        ax.text(0.25, y, d["dimensione"], ha="left", va="center", fontsize=9.5,
                fontweight="bold", color=NAVY)
        ax.add_patch(FancyBboxPatch((3.0, y - 0.20), 3.05, 0.42,
                                    boxstyle="round,pad=0.008,rounding_size=0.03",
                                    linewidth=1.2, edgecolor=GREY, facecolor="white"))
        ax.text(4.52, y, d["da"], ha="center", va="center", fontsize=7.8, color=GREY)
        _arrow(ax, (6.15, y), (6.72, y), color=GREEN, lw=1.8)
        ax.add_patch(FancyBboxPatch((6.8, y - 0.20), 4.35, 0.42,
                                    boxstyle="round,pad=0.008,rounding_size=0.03",
                                    linewidth=1.2, edgecolor=GREEN, facecolor=LIGHT))
        ax.text(8.97, y, d["a"], ha="center", va="center", fontsize=7.8,
                color=GREEN, fontweight="bold")

    # data -> value chain (bottom-left band)
    ax.text(0.25, 2.85, "Catena dato -> informazione -> valore", ha="left", va="center",
            fontsize=9.8, fontweight="bold", color=NAVY)
    cx = 0.35
    for s in aibm.DATA_VALUE_CHAIN:
        ax.add_patch(FancyBboxPatch((cx, 1.35), 2.35, 1.05,
                                    boxstyle="round,pad=0.01,rounding_size=0.04",
                                    linewidth=1.3, edgecolor=NAVY, facecolor=LIGHT2))
        ax.text(cx + 1.175, 2.14, s["stadio"], ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=NAVY)
        ax.text(cx + 1.175, 1.68, _wrap(s["fonte"], 26), ha="center", va="center",
                fontsize=6.6, color=GREY, linespacing=1.15)
        if cx > 0.5:
            _arrow(ax, (cx - 0.33, 1.87), (cx, 1.87), color=NAVY, lw=1.6)
        cx += 2.70

    # tensions (bottom-right), spacing accounts for 2-line wrap
    ax.text(8.7, 2.85, "Tensioni sistemiche", ha="left", va="center",
            fontsize=9.8, fontweight="bold", color=RED)
    for i, t in enumerate(aibm.TENSIONS):
        ax.text(8.7, 2.45 - i * 0.62, "• " + _wrap(t, 34), ha="left", va="top",
                fontsize=7, color=GREY, linespacing=1.15)

    fig.savefig(FIG / "fig_aibm4_transition.png"); plt.close(fig)


# ---------------------------------------------------- fig 5: validazione economica
def fig_finanza():
    f = aibm.financials()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 4.4),
                                        gridspec_kw={"width_ratios": [1.2, 0.8, 0.9]})

    # benefici netti annui vs costi incrementali
    items = list(aibm.ANNUAL_BENEFITS.items())
    labels = [_wrap(k.split("(")[0].strip(), 20) for k, _ in items]
    vals = [v for _, v in items]
    ax1.barh(range(len(vals)), vals, color=GREEN, edgecolor="white")
    ax1.barh([len(vals)], [-aibm.ANNUAL_INCREMENTAL_COSTS], color=RED, edgecolor="white")
    ax1.set_yticks(list(range(len(vals))) + [len(vals)],
                   labels + [_wrap("Costi incrementali", 20)], fontsize=7.6)
    ax1.axvline(0, color=GREY, lw=0.8)
    ax1.set_xlabel("k EUR / anno")
    ax1.set_title(f"Benefici netti annui: {f['beneficio_netto_annuo']:.0f} k EUR",
                  fontsize=11, fontweight="bold", color=NAVY)
    ax1.spines[["top", "right"]].set_visible(False)

    # ROI + payback (livello di progetto)
    ax2.axis("off"); ax2.set_xlim(0, 1); ax2.set_ylim(0, 1)
    ax2.text(0.5, 0.97, f"Investimento {f['investimento']:.0f} k EUR", ha="center",
             va="top", color=GREY, fontsize=9)
    ax2.add_patch(Circle((0.5, 0.54), 0.30, facecolor=GREEN, edgecolor="none"))
    ax2.text(0.5, 0.585, f"{f['roi_pct']:.0f}%", ha="center", va="center",
             color="white", fontsize=24, fontweight="bold")
    ax2.text(0.5, 0.45, "ROI annuo", ha="center", va="center", color="white", fontsize=10)
    ax2.text(0.5, 0.12, f"Payback: {f['payback_anni']:.1f} anni", ha="center",
             va="center", color=NAVY, fontsize=12, fontweight="bold")

    # ROA di gruppo (contesto) con contributo marginale dell'AI-BM
    base = f["roa_gruppo_pct"]; contrib = f["contributo_roa_pp"]
    ax3.bar(["ROA di gruppo"], [base], color=GREY, edgecolor="white", width=0.5)
    ax3.bar(["ROA di gruppo"], [contrib], bottom=[base], color=GREEN, edgecolor="white",
            width=0.5)
    ax3.text(0, base / 2, f"~{base:.0f}%", ha="center", va="center", color="white",
             fontsize=12, fontweight="bold")
    ax3.annotate(f"+{contrib:.2f} pp\n(AI-BM, marginale)", xy=(0.25, base + contrib),
                 xytext=(0.55, base + 3.2), fontsize=9, color=GREEN, fontweight="bold",
                 ha="left", arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.4))
    ax3.set_ylim(0, base * 1.35); ax3.set_xlim(-0.7, 1.4)
    ax3.set_ylabel("ROA (%)")
    ax3.set_title("ROA di gruppo (contesto)", fontsize=11, fontweight="bold", color=NAVY)
    ax3.text(0.5, -0.16, "il ritorno dell'AI-BM e a livello di progetto (ROI)",
             transform=ax3.transAxes, ha="center", va="top", fontsize=8.5,
             color=GREY, style="italic")
    ax3.spines[["top", "right"]].set_visible(False)

    fig.suptitle("Validazione economica dell'AI-BM (valori rappresentativi)",
                 fontsize=12.5, fontweight="bold", color=NAVY, y=1.03)
    fig.tight_layout()
    fig.savefig(FIG / "fig_aibm5_finanza.png"); plt.close(fig)


def main():
    fig_metodo()
    fig_bmc()
    fig_swot()
    fig_transition()
    fig_finanza()
    print("Figure RP 7.10 generate in", FIG)


if __name__ == "__main__":
    main()
