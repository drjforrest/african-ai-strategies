"""Figure 1: within-competency standardised alignment of national AI strategies
to the nine WHO digital-health competency domains.

This reproduces Figure 1 of the manuscript *from the pipeline outputs*, so the
figure is regenerable rather than a hand-made artefact.

What it plots
-------------
Each cell is the within-competency z-score of a strategy's alignment score:

    z(country, domain) = (raw - mean_national(domain)) / sd_national(domain)

where the mean and standard deviation are taken over the TWELVE national
strategies only (the African Union is excluded from the standardisation and
shown as a separate anchor row, exactly as the caption describes). Rows are
ordered by mean z across the nine domains, descending; the AU anchor is
appended last.

Raw cosine similarities sit in a narrow high band (~0.38-0.58) because every
strategy is broadly on-topic, which is why the figure standardises and why the
raw magnitudes are not interpreted directly.

Usage
-----
    python plot_figure1.py
    python plot_figure1.py --out outputs/figures_for_manuscript/Figure1.png

Inputs : outputs/alignment_scores.csv   (country, competency_id, similarity_score)
         data/who_strategy/competencies.csv
Output : outputs/heatmaps/figure1_competency_zscores.png (default)
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

from src import config

ANCHOR = "African Union"
CID = [f"C{i}" for i in range(1, 10)]
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--scores", type=Path, default=config.ALIGNMENT_SCORES_CSV,
                   help="long-form alignment scores from run_pipeline.py")
    p.add_argument("--competencies", type=Path, default=config.COMPETENCIES_CSV)
    p.add_argument("--out", type=Path,
                   default=config.HEATMAP_DIR / "figure1_competency_zscores.png")
    return p.parse_args()


def build_z(scores: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (z-matrix ordered for display, raw matrix)."""
    long = pd.read_csv(scores)
    mat = long.pivot(index="country", columns="competency_id",
                     values="similarity_score")[CID]

    national = mat.drop(index=ANCHOR, errors="ignore")
    mu = national.mean(axis=0)
    sd = national.std(axis=0, ddof=0).replace(0, 1.0)
    z = (mat - mu) / sd                      # AU standardised on the national scale

    order = (z.drop(index=ANCHOR, errors="ignore")[CID]
              .mean(axis=1).sort_values(ascending=False).index.tolist())
    order = order + ([ANCHOR] if ANCHOR in z.index else [])
    return z.loc[order, CID], mat.loc[order, CID]


def domain_labels(competencies: Path) -> list[str]:
    """Two-line C-id + wrapped domain name, for readable x-axis ticks."""
    cdf = pd.read_csv(competencies)
    names = dict(zip(cdf["competency_id"], cdf["name"]))
    short = {
        "C1": "Leadership &\ngovernance",
        "C2": "Investment &\noperations",
        "C3": "Services &\nscale-up",
        "C4": "Integration &\nsustainability",
        "C5": "Standards &\ninterop.",
        "C6": "Digital\ninfrastructure",
        "C7": "Health\nworkforce",
        "C8": "Legislation,\nethics",
        "C9": "People-\ncentred",
    }
    return [f"{c}\n{short.get(c, names.get(c, ''))}" for c in CID]
def main() -> int:
    args = parse_args()
    if not args.scores.exists():
        print(f"Alignment scores not found: {args.scores}\nRun run_pipeline.py first.")
        return 1

    z, raw = build_z(args.scores)
    labels = domain_labels(args.competencies)
    n_nat = len(z) - (1 if ANCHOR in z.index else 0)

    vmax = float(np.nanmax(np.abs(z.to_numpy()))) or 1.0
    fig, ax = plt.subplots(figsize=(11.0, 8.4))
    im = ax.imshow(z.to_numpy(), cmap="RdBu_r",
                   norm=TwoSlopeNorm(0, -vmax, vmax), aspect="auto")

    ax.set_xticks(range(len(CID)))
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_yticks(range(len(z)))
    ax.set_yticklabels(
        [f"{c}\n(anchor)" if c == ANCHOR else c for c in z.index], fontsize=10)

    # value labels
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            v = z.iat[i, j]
            ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=8.5,
                    color="white" if abs(v) > 0.62 * vmax else "#222222")

    # visual break between the national block and the anchor row
    if ANCHOR in z.index:
        ax.axhline(n_nat - 0.5, color="#222222", lw=2.0)

    ax.set_xticks(np.arange(-0.5, len(CID), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(z), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=2.0)
    ax.tick_params(which="minor", length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label(f"Within-competency z-score\n(relative to the {n_nat} national strategies)",
                 fontsize=9)
    ax.set_xlabel("WHO competency domain", fontsize=10, labelpad=8)
    ax.set_title("AI-strategy alignment with WHO digital-health competencies",
                 fontsize=13, weight="bold", pad=12)

    fig.tight_layout()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig)

    print(f"Wrote {args.out}")
    print(f"  rows: {len(z)} ({n_nat} national + "
          f"{'1 anchor' if ANCHOR in z.index else '0 anchor'})")
    print(f"  z range: {z.to_numpy().min():+.2f} to {z.to_numpy().max():+.2f}")
    print(f"  row order (mean z, desc): {', '.join(z.index[:4])} ... "
          f"{', '.join(z.index[-3:])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
