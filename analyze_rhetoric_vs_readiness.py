"""Rhetoric vs readiness: does what a strategy SAYS track what is MEASURED?

The spine of Paper 1. Joins two things about the same nine Oxford dimensions:

  * RHETORIC - text-derived emphasis: how strongly each national strategy engages
    each Oxford dimension, from run_reference_alignment.py using the Oxford
    dimension definitions (outputs/reference_alignment/<label>/..._alignment_scores.csv).
  * READINESS - measured score: the Oxford dimension score from the tidy panel
    (data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv).

Both are standardised within each dimension across countries (raw cosines sit in a
narrow high band; raw Oxford scores are min-max within-year), so the axes read as
"relative to peers." The quadrants are then: talk>walk (high rhetoric, low
readiness), walk>talk, aligned-high, aligned-low.

The circularity guard - IMPORTANT for the paper's validity claim: some Oxford
dimensions are scored partly by reading the strategy text itself (Vision's "National
AI Strategy" indicator; the "national ethics framework" desk-research indicator in
Governance & Ethics). Correlating rhetoric against THOSE is method agreement
(reliability), not evidence that strategies track capability. The genuine
rhetoric-reality test is against the dimensions built from independent secondary
data (infrastructure, data, talent, tech-sector). The script reports the two
subsets separately.

Outputs (outputs/rhetoric_vs_readiness/):
  rhetoric_vs_readiness.csv         country x dimension: rhetoric_z, readiness_z, quadrant
  per_dimension_correlation.csv     Pearson r per dimension + text-proximate flag
  quadrant.png                      pooled country x dimension scatter, 4 quadrants
  correlation_by_dimension.png      r per dimension, independent vs text-proximate

Usage:
  python analyze_rhetoric_vs_readiness.py                 # measured year defaults to 2024
  python analyze_rhetoric_vs_readiness.py --year mean     # average measured 2021-2024
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src import config

# text-derived reference id -> (measured dimension name, pillar, text_proximate?)
# text_proximate = Oxford scores that partly read the strategy text (reliability, not
# the rhetoric-reality gap): Vision (AI-strategy indicator) and Governance & Ethics
# (national-ethics-framework desk indicator). The other seven are secondary-data.
DIM_MAP = {
    "GOV_VISION":          ("Vision", "Government", True),
    "GOV_GOVERNANCE":      ("Governance and Ethics", "Government", True),
    "GOV_DIGITAL_CAPACITY":("Digital Capacity", "Government", False),
    "GOV_ADAPTABILITY":    ("Adaptability", "Government", False),
    "TECH_MATURITY":       ("Maturity", "Technology Sector", False),
    "TECH_INNOVATION":     ("Innovation Capacity", "Technology Sector", False),
    "TECH_HUMAN_CAPITAL":  ("Human Capital", "Technology Sector", False),
    "DATA_INFRASTRUCTURE": ("Infrastructure", "Data and Infrastructure", False),
    "DATA_AVAILABILITY":   ("Data Availability", "Data and Infrastructure", False),
}
PILLAR_COLOUR = {  # Okabe-Ito, CVD-safe
    "Government": "#0072B2",
    "Technology Sector": "#009E73",
    "Data and Infrastructure": "#E69F00",
}
INK, MUTED = "#222222", "#6b6b6b"

DEFAULT_RHETORIC = (config.OUTPUTS_DIR / "reference_alignment" /
                    "oxford_dimensions_2021_2024_embed" /
                    "oxford_dimensions_2021_2024_embed_alignment_scores.csv")
DEFAULT_PANEL = (config.DATA_DIR / "oxford_readiness_indices" / "processed" /
                 "oxford_panel_2021_2024_tidy.csv")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--rhetoric", type=Path, default=DEFAULT_RHETORIC,
                   help="text-derived Oxford emphasis scores (from run_reference_alignment.py).")
    p.add_argument("--panel", type=Path, default=DEFAULT_PANEL, help="tidy measured Oxford panel.")
    p.add_argument("--year", default="2024",
                   help="measured year to compare against, or 'mean' to average 2021-2024.")
    p.add_argument("--outdir", type=Path, default=config.OUTPUTS_DIR / "rhetoric_vs_readiness")
    return p.parse_args()


def _z(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd else s * 0.0


def _pearson(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    if len(a) < 3 or a.std() == 0 or b.std() == 0:
        return np.nan
    return float(np.corrcoef(a, b)[0, 1])


def main() -> int:
    args = parse_args()
    for pth, what in [(args.rhetoric, "rhetoric scores"), (args.panel, "measured panel")]:
        if not pth.exists():
            print(f"Missing {what}: {pth}")
            if what == "rhetoric scores":
                print("  Run: python run_reference_alignment.py "
                      "--reference data/oxford_readiness_indices/oxford_dimensions_2021_2024_embed.csv "
                      "--label oxford_dimensions_2021_2024_embed")
            return 1

    # rhetoric (text-derived emphasis) -> dimension
    rhet = pd.read_csv(args.rhetoric)
    rhet = rhet[rhet["competency_id"].isin(DIM_MAP)].copy()
    rhet["dimension"] = rhet["competency_id"].map(lambda c: DIM_MAP[c][0])
    rhet = rhet.rename(columns={"similarity_score": "rhetoric_raw"})[["country", "dimension", "rhetoric_raw"]]

    # measured readiness -> dimension for the chosen year (or mean)
    panel = pd.read_csv(args.panel)
    dims = panel[panel["level"] == "dimension"].copy()
    if args.year.lower() == "mean":
        meas = dims.groupby(["country", "metric"], as_index=False)["score"].mean()
    else:
        meas = dims[dims["year"].astype(str) == str(args.year)][["country", "metric", "score"]].copy()
    meas = meas.rename(columns={"metric": "dimension", "score": "readiness_raw"})

    # Country keys must be accent-folded on BOTH sides before the join: the
    # strategy corpus spells "Côte d'Ivoire" while the processed Oxford panel
    # uses the ASCII form "Cote d'Ivoire". Without this the inner join silently
    # drops Côte d'Ivoire, reducing the analysis from 12 countries to 11 and
    # biasing the pooled rhetoric-readiness correlation toward zero.
    def _fold(s: pd.Series) -> pd.Series:
        return (s.astype(str)
                 .str.normalize("NFKD")
                 .str.encode("ascii", "ignore")
                 .str.decode("ascii")
                 .str.strip())

    rhet["country"] = _fold(rhet["country"])
    meas["country"] = _fold(meas["country"])

    df = rhet.merge(meas, on=["country", "dimension"], how="inner")  # AU (no Oxford score) drops out
    if df.empty:
        print("No overlapping (country, dimension) rows after join. Check dimension names / year.")
        return 1
    n_dropped = rhet["country"].nunique() - df["country"].nunique()
    if n_dropped:
        missing = sorted(set(rhet["country"]) - set(df["country"]))
        print(f"  ! {n_dropped} corpus country/ies absent from the measured panel: {', '.join(missing)}")
    # The fold is a JOIN KEY only. Restore the accented display name afterwards
    # so figures, tables and the manuscript all spell the country identically.
    DISPLAY = {"Cote d'Ivoire": "Côte d'Ivoire"}
    df["country"] = df["country"].replace(DISPLAY)

    df["pillar"] = df["dimension"].map(lambda d: next(v[1] for v in DIM_MAP.values() if v[0] == d))
    df["text_proximate"] = df["dimension"].map(lambda d: next(v[2] for v in DIM_MAP.values() if v[0] == d))

    # standardise within dimension across countries
    df["rhetoric_z"] = df.groupby("dimension")["rhetoric_raw"].transform(_z)
    df["readiness_z"] = df.groupby("dimension")["readiness_raw"].transform(_z)
    df["quadrant"] = np.select(
        [(df.rhetoric_z >= 0) & (df.readiness_z < 0),
         (df.rhetoric_z < 0) & (df.readiness_z >= 0),
         (df.rhetoric_z >= 0) & (df.readiness_z >= 0)],
        ["talk>walk", "walk>talk", "aligned-high"], default="aligned-low")

    args.outdir.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.outdir / "rhetoric_vs_readiness.csv", index=False)

    # per-dimension correlation + circularity subsets
    perdim = (df.groupby(["dimension", "pillar", "text_proximate"])
                .apply(lambda g: _pearson(g.rhetoric_raw, g.readiness_raw), include_groups=False)
                .reset_index(name="pearson_r").sort_values("pearson_r"))
    perdim.to_csv(args.outdir / "per_dimension_correlation.csv", index=False)

    pooled = _pearson(df.rhetoric_z, df.readiness_z)
    ind = perdim[~perdim.text_proximate]["pearson_r"].mean()
    txt = perdim[perdim.text_proximate]["pearson_r"].mean()
    print(f"Pooled rhetoric-readiness r (standardised): {pooled:.3f}")
    print(f"Mean r on INDEPENDENT dimensions (the real gap test): {ind:.3f}")
    print(f"Mean r on TEXT-PROXIMATE dimensions (reliability):    {txt:.3f}")

    # --- quadrant scatter ---
    fig, ax = plt.subplots(figsize=(9, 7.5))
    ax.axhline(0, color=MUTED, lw=1); ax.axvline(0, color=MUTED, lw=1)
    for pil, sub in df.groupby("pillar"):
        ax.scatter(sub.rhetoric_z, sub.readiness_z, s=42, color=PILLAR_COLOUR.get(pil, "#888"),
                   edgecolor="white", linewidth=0.6, label=pil, zorder=3)
    # annotate the strongest talk>walk and walk>talk cells
    df["_off"] = df.rhetoric_z - df.readiness_z
    for _, r in pd.concat([df.nlargest(3, "_off"), df.nsmallest(3, "_off")]).iterrows():
        ax.annotate(f"{r.country}: {r.dimension}", (r.rhetoric_z, r.readiness_z),
                    xytext=(4, 4), textcoords="offset points", fontsize=7.5, color=MUTED)
    lim = max(2.2, float(np.nanmax(np.abs(df[["rhetoric_z", "readiness_z"]].to_numpy()))) + 0.3)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim)
    for (x, y, t, ha, va) in [(lim, -lim, "talk > walk", "right", "bottom"),
                              (-lim, lim, "walk > talk", "left", "top"),
                              (lim, lim, "aligned (high)", "right", "top"),
                              (-lim, -lim, "aligned (low)", "left", "bottom")]:
        ax.text(x*0.97, y*0.97, t, ha=ha, va=va, fontsize=9, color=MUTED, style="italic")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("Rhetoric: text-derived emphasis (z, within dimension)", fontsize=10, color=MUTED)
    ax.set_ylabel("Readiness: measured Oxford score (z, within dimension)", fontsize=10, color=MUTED)
    ax.set_title(f"Rhetoric vs readiness, by country and dimension (measured year: {args.year})\n"
                 f"pooled r = {pooled:.2f} across {len(df)} country-by-dimension cells "
                 f"({df['country'].nunique()} countries)", fontsize=12, color=INK, weight="bold")
    # Legend moved below the axes (horizontal, outside the plot area) so it no
    # longer collides with the "aligned (low)" quadrant label in the bottom-left corner.
    ax.legend(frameon=False, fontsize=9, loc="upper center",
              bbox_to_anchor=(0.5, -0.10), ncol=3, handletextpad=0.5, columnspacing=1.4)
    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig(args.outdir / "quadrant.png", dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)

    # --- correlation by dimension ---
    fig, ax = plt.subplots(figsize=(8, 5.5))
    colours = ["#CC79A7" if tp else "#0072B2" for tp in perdim.text_proximate]
    ax.barh(perdim.dimension, perdim.pearson_r, color=colours, zorder=3)
    ax.axvline(0, color=MUTED, lw=1)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_xlabel("Pearson r (rhetoric vs measured readiness across countries)", fontsize=9, color=MUTED)
    ax.set_title("Where saying it tracks having it, by dimension", fontsize=12, color=INK, weight="bold")
    ax.legend(handles=[plt.Line2D([0],[0],color="#0072B2",lw=6,label="independent (secondary data) - the gap test"),
                       plt.Line2D([0],[0],color="#CC79A7",lw=6,label="text-proximate (reads the strategy) - reliability")],
              frameon=False, fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(args.outdir / "correlation_by_dimension.png", dpi=150, facecolor="white")
    plt.close(fig)

    print(f"Wrote outputs to {args.outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
