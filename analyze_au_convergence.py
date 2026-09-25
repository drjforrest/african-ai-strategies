"""AU convergence: how closely does each national strategy mirror the continental vision?

Reads the WHO-competency alignment matrix (``outputs/alignment_scores.csv`` from
run_pipeline.py, run WITH the African Union wired into config.COUNTRY_FILES) and
measures each country's *emphasis profile* against the AU Continental AI Strategy's
profile across the nine WHO digital-health competency domains.

Why standardise first: raw cosine scores sit in a narrow high band (~0.4-0.65 -
every strategy is broadly on-topic), so an un-standardised profile similarity makes
every country look identical to the AU. We therefore z-score each competency across
the national set, place the AU on that same scale, and compare *relative emphasis*.

Convergence framing: this is a cross-sectional, harmonisation-to-a-standard measure
(regional-standards / accreditation argument, i.e. Paper 2), NOT a longitudinal one.
For the longitudinal Paper-1 story, converge the Oxford readiness scores over time
(sigma/beta convergence) - a separate script.

Outputs (outputs/au_convergence/):
  au_convergence.csv        country, profile_r_to_AU, cosine_to_AU, distance_to_AU, rank
  au_convergence_bar.png    profile alignment to the AU vision, by country
  au_gap_heatmap.png        signed emphasis gap (country - AU) per competency;
                            accreditation-critical domains (C5, C7, C8) flagged.

Usage:
  python analyze_au_convergence.py
  python analyze_au_convergence.py --scores outputs/alignment_scores.csv --anchor "African Union"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

from src import config

# Accreditation-critical WHO domains for the standards/accreditation argument:
# standards & interoperability, adaptable health workforce, legislation/ethics.
ACCREDITATION_CRITICAL = {"C5", "C7", "C8"}
# Diverging map: two hues + neutral-grey midpoint (per data-viz rules; no rainbow).
_DIVERGING = LinearSegmentedColormap.from_list(
    "gap", ["#2166AC", "#D9D9D9", "#B2182B"]
)
INK, MUTED = "#222222", "#6b6b6b"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scores", type=Path, default=config.ALIGNMENT_SCORES_CSV,
                   help="WHO alignment scores CSV (country, competency_id, similarity_score).")
    p.add_argument("--competencies", type=Path, default=config.COMPETENCIES_CSV,
                   help="competencies.csv, for domain display names.")
    p.add_argument("--anchor", default="African Union",
                   help="row name of the regional anchor in the scores file.")
    p.add_argument("--outdir", type=Path, default=config.OUTPUTS_DIR / "au_convergence")
    return p.parse_args()


def _style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=9)


def main() -> int:
    args = parse_args()
    if not args.scores.exists():
        print(f"Alignment scores not found: {args.scores}\n"
              "Run run_pipeline.py first, with the African Union added to config.COUNTRY_FILES.")
        return 1

    long = pd.read_csv(args.scores)
    mat = long.pivot(index="country", columns="competency_id", values="similarity_score")
    comp_ids = list(mat.columns)

    if args.anchor not in mat.index:
        print(f"Anchor '{args.anchor}' not in the scores. Present: {list(mat.index)}\n"
              "Add \"African Union\": \"african_union_ai.txt\" to config.COUNTRY_FILES and re-run the pipeline.")
        return 1

    names = {}
    if args.competencies.exists():
        cdf = pd.read_csv(args.competencies)
        names = dict(zip(cdf["competency_id"], cdf["name"]))

    countries = [c for c in mat.index if c != args.anchor]
    if len(countries) < 2:
        print("Need at least two countries besides the anchor.")
        return 1

    # z-score each competency across the national set; place the anchor on that scale.
    mu = mat.loc[countries].mean(axis=0)
    sd = mat.loc[countries].std(axis=0, ddof=0).replace(0, 1.0)
    z = (mat - mu) / sd
    anchor_vec = z.loc[args.anchor, comp_ids].to_numpy(dtype=float)

    rows = []
    for c in countries:
        v = z.loc[c, comp_ids].to_numpy(dtype=float)
        # Pearson r of emphasis profiles (centre each profile across competencies).
        vc, ac = v - v.mean(), anchor_vec - anchor_vec.mean()
        denom = np.linalg.norm(vc) * np.linalg.norm(ac)
        r = float(vc @ ac / denom) if denom else np.nan
        cos = float(v @ anchor_vec / (np.linalg.norm(v) * np.linalg.norm(anchor_vec))) \
            if np.linalg.norm(v) and np.linalg.norm(anchor_vec) else np.nan
        dist = float(np.linalg.norm(v - anchor_vec))
        rows.append({"country": c, "profile_r_to_AU": r, "cosine_to_AU": cos, "distance_to_AU": dist})

    conv = pd.DataFrame(rows).sort_values("profile_r_to_AU", ascending=False).reset_index(drop=True)
    conv["rank"] = conv.index + 1
    args.outdir.mkdir(parents=True, exist_ok=True)
    conv.to_csv(args.outdir / "au_convergence.csv", index=False)
    print(f"Wrote {args.outdir / 'au_convergence.csv'}")

    # --- bar: profile alignment to the AU vision ---
    fig, ax = plt.subplots(figsize=(8, 5.5))
    order = conv.sort_values("profile_r_to_AU")
    colours = ["#0072B2" if v >= 0 else "#D55E00" for v in order["profile_r_to_AU"]]
    ax.barh(order["country"], order["profile_r_to_AU"], color=colours, zorder=3)
    ax.axvline(0, color=MUTED, lw=1)
    _style(ax)
    ax.set_xlabel("Profile alignment to the AU Continental AI Strategy (Pearson r of standardised emphasis)", fontsize=9, color=MUTED)
    ax.set_title("Convergence to the continental vision, by country", fontsize=13, color=INK, weight="bold")
    fig.tight_layout()
    fig.savefig(args.outdir / "au_convergence_bar.png", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"Wrote {args.outdir / 'au_convergence_bar.png'}")

    # --- heatmap: signed emphasis gap (country - AU) per competency ---
    gap = z.loc[countries, comp_ids].subtract(pd.Series(anchor_vec, index=comp_ids), axis=1)
    gap = gap.loc[conv.sort_values("profile_r_to_AU", ascending=False)["country"]]
    vmax = float(np.nanmax(np.abs(gap.to_numpy()))) or 1.0
    fig, ax = plt.subplots(figsize=(1.1 * len(comp_ids) + 3, 0.5 * len(countries) + 2))
    im = ax.imshow(gap.to_numpy(), cmap=_DIVERGING, norm=TwoSlopeNorm(0, -vmax, vmax), aspect="auto")
    ax.set_xticks(range(len(comp_ids)))
    # Readable axis labels: full domain names are too long to sit side by side
    # at nine columns, so use deliberate abbreviations rather than a blind
    # character truncation (which produced "Legislation, eth").
    SHORT = {
        "C1": "Leadership &\ngovernance",
        "C2": "Investment &\noperations",
        "C3": "Services &\nscale-up",
        "C4": "Integration &\nsustainability",
        "C5": "Standards &\ninteroperability",
        "C6": "Digital\ninfrastructure",
        "C7": "Health\nworkforce",
        "C8": "Legislation,\nethics & compliance",
        "C9": "People-centred\napproach",
    }
    labels = [f"{cid}{'*' if cid in ACCREDITATION_CRITICAL else ''}\n"
              f"{SHORT.get(cid, names.get(cid, ''))}" for cid in comp_ids]
    ax.set_xticklabels(labels, fontsize=8)
    for i, cid in enumerate(comp_ids):
        if cid in ACCREDITATION_CRITICAL:
            ax.get_xticklabels()[i].set_color("#B2182B")
            ax.get_xticklabels()[i].set_fontweight("bold")
    ax.set_yticks(range(len(gap.index)))
    ax.set_yticklabels(gap.index, fontsize=9)
    ax.set_title("Emphasis gap vs the AU vision (blue = under-emphasised, red = over-emphasised)\n* accreditation-critical domains: standards/interoperability, workforce, legislation/ethics",
                 fontsize=10, color=INK)
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="standardised gap (country - AU)")
    fig.tight_layout()
    fig.savefig(args.outdir / "au_gap_heatmap.png", dpi=150, facecolor="white")
    plt.close(fig)
    print(f"Wrote {args.outdir / 'au_gap_heatmap.png'}")

    print("Done. Framing note: this is regional harmonisation-to-a-standard (Paper 2), "
          "not the longitudinal readiness-convergence (Paper 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
