"""Multi-line time-series figures for the Oxford AI Readiness panel (2021-2024).

Reads the tidy panel produced during ingestion
(``data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv``:
columns ``country, year, level, metric, score``) and renders two views:

  A. Small multiples - one panel per country, each with four lines
     (Overall + the three pillars). Best for reading a single country's shape.
  B. Pillar panels - one panel per metric (Overall + three pillars), all twelve
     countries drawn, with a chosen few highlighted in colour and the rest greyed.
     Best for "who is moving" comparisons without a 12-colour spaghetti plot.

Design notes: colours are the Okabe-Ito colourblind-safe set, assigned in fixed
order (never cycled); >8 series are handled by small multiples / highlight-and-grey
rather than generated hues; 2px lines, recessive grid, one legend, direct end
labels on highlighted series.

Usage:
  python scripts/plot_oxford_trajectories.py \
      --panel data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv \
      --outdir outputs/oxford \
      --highlight "Rwanda,Senegal,Benin,Nigeria,Egypt"
"""
from __future__ import annotations
import argparse, os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

METRIC_ORDER = ["Overall", "Government", "Technology Sector", "Data and Infrastructure"]
METRIC_COLOURS = {                       # Okabe-Ito, validated CVD-safe
    "Overall": "#0072B2",
    "Government": "#D55E00",
    "Technology Sector": "#009E73",
    "Data and Infrastructure": "#E69F00",
}
HILITE_PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]
GREY = "#C7C7C7"
INK, MUTED = "#222222", "#6b6b6b"


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.grid(True, axis="y", color="#e8e8e8", lw=0.8, zorder=0)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_axisbelow(True)


def load_panel(path):
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    m = df[df["level"].isin(["overall", "pillar"])].copy()
    m["metric"] = m["metric"].replace({"Overall": "Overall"})
    return m


def fig_country_small_multiples(df, outpath):
    countries = sorted(df["country"].unique())
    ncol, nrow = 4, 3
    fig, axes = plt.subplots(nrow, ncol, figsize=(13, 8.5), sharex=True, sharey=True)
    ymin = max(0, df["score"].min() - 5)
    ymax = min(100, df["score"].max() + 5)
    for ax, country in zip(axes.flat, countries):
        sub = df[df["country"] == country]
        for metric in METRIC_ORDER:
            s = sub[sub["metric"] == metric].sort_values("year")
            if s.empty:
                continue
            ax.plot(s["year"], s["score"], color=METRIC_COLOURS[metric], lw=2,
                    marker="o", markersize=4.5, markerfacecolor=METRIC_COLOURS[metric],
                    markeredgecolor="white", markeredgewidth=0.6, zorder=3)
        _style(ax)
        ax.set_ylim(ymin, ymax)
        ax.set_title(country, fontsize=10, color=INK, pad=4)
    for ax in axes.flat[len(countries):]:
        ax.set_visible(False)
    handles = [plt.Line2D([0], [0], color=METRIC_COLOURS[m], lw=2, marker="o",
               markersize=5, markeredgecolor="white") for m in METRIC_ORDER]
    fig.legend(handles, METRIC_ORDER, loc="lower center", ncol=4, frameon=False,
               fontsize=9.5, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("Government AI Readiness trajectories by country, 2021-2024",
                 fontsize=14, color=INK, x=0.5, y=0.985, ha="center", weight="bold")
    fig.text(0.5, 0.955, "Overall score and the three pillars. Scores are min-max normalised within each edition, so read shape and movement, not absolute level.",
             fontsize=9, color=MUTED, ha="center")
    fig.supylabel("Readiness score (0-100)", fontsize=10, color=MUTED)
    fig.tight_layout(rect=[0.02, 0.05, 1, 0.94])
    fig.savefig(outpath, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_pillar_panels(df, outpath, highlight):
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), sharex=True)
    colour = {c: HILITE_PALETTE[i % len(HILITE_PALETTE)] for i, c in enumerate(highlight)}
    for ax, metric in zip(axes.flat, METRIC_ORDER):
        sub = df[df["metric"] == metric]
        for country in sorted(sub["country"].unique()):
            if country in highlight:
                continue
            s = sub[sub["country"] == country].sort_values("year")
            ax.plot(s["year"], s["score"], color=GREY, lw=1.2, zorder=1)
        for country in highlight:
            s = sub[sub["country"] == country].sort_values("year")
            if s.empty:
                continue
            ax.plot(s["year"], s["score"], color=colour[country], lw=2.2,
                    marker="o", markersize=5, markeredgecolor="white",
                    markeredgewidth=0.6, zorder=3)
            last = s.iloc[-1]
            ax.annotate(country, (last["year"], last["score"]),
                        xytext=(4, 0), textcoords="offset points", va="center",
                        fontsize=8.5, color=colour[country], weight="bold")
        _style(ax)
        ax.set_title(metric, fontsize=11, color=INK, pad=4)
        ax.set_xlim(df["year"].min(), df["year"].max() + 0.6)
    fig.suptitle("Where movement is concentrated: highlighted countries vs the field, 2021-2024",
                 fontsize=14, color=INK, x=0.5, y=0.99, ha="center", weight="bold")
    fig.text(0.5, 0.945, "Grey lines are the other African strategy countries. Highlight set: " + ", ".join(highlight),
             fontsize=9, color=MUTED, ha="center")
    fig.supylabel("Readiness score (0-100)", fontsize=10, color=MUTED)
    fig.tight_layout(rect=[0.02, 0, 1, 0.93])
    fig.savefig(outpath, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv")
    ap.add_argument("--outdir", default="outputs/oxford")
    ap.add_argument("--highlight", default="Rwanda,Senegal,Benin,Nigeria,Egypt")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    df = load_panel(args.panel)
    highlight = [c.strip() for c in args.highlight.split(",") if c.strip()]
    fig_country_small_multiples(df, os.path.join(args.outdir, "oxford_trajectories_by_country.png"))
    fig_pillar_panels(df, os.path.join(args.outdir, "oxford_trajectories_by_pillar.png"), highlight)
    print("wrote figures to", args.outdir)


if __name__ == "__main__":
    main()
