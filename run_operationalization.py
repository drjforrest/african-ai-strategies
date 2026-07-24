"""Build the policy operationalization index and its figures.

    python run_operationalization.py

Reads data/national_strategies/*.txt, writes:
    outputs/operationalization/operationalization_index.csv
    outputs/operationalization/operationalization_ranking.png   (composite bar)
    outputs/operationalization/operationalization_breakdown.png (country×dim heatmap)

This is a *differentiating* axis: unlike the WHO-competency alignment (which
measures shared rhetoric and compresses), it separates strategies by how much
they commit to execution — timelines, budgets, named owners, legal instruments,
monitoring, and implementation mechanics.
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import seaborn as sns  # noqa: E402

from src import config, operationalization  # noqa: E402


def main() -> int:
    config.OPERATIONALIZATION_DIR.mkdir(parents=True, exist_ok=True)

    df = operationalization.build_index()
    skipped = df.attrs.get("skipped", [])
    if df.empty:
        print("No strategy texts found in", config.NATIONAL_DIR)
        return 1

    out = operationalization.save_index(df)
    print(f"Scored {len(df)} strategies across {len(operationalization.DIMENSIONS)} "
          f"operationalization dimensions.")
    if skipped:
        print(f"  ! Skipped (no text file): {', '.join(skipped)}")
    print(f"Wrote index -> {out}\n")

    # Console ranking: primary breadth index + secondary execution-focus.
    show = df[["country", "operationalization_index", "focus_index"]].copy()
    show = show.rename(columns={"operationalization_index": "breadth", "focus_index": "focus"})
    show["breadth"] = show["breadth"].round(3)
    show["focus"] = show["focus"].round(3)
    print(show.to_string(index=False))

    # --- Figure 1: primary breadth ranking bar ---------------------------- #
    order = df.sort_values("operationalization_index")
    fig, ax = plt.subplots(figsize=(8, 0.45 * len(order) + 1))
    ax.barh(order["country"], order["operationalization_index"], color="#4C72B0")
    ax.set_xlabel("Operationalization (breadth): share of 6 execution levers "
                  "addressed above sample median")
    ax.set_xlim(0, 1)
    ax.set_title("Policy operationalization of national AI strategies")
    ax.margins(y=0.01)
    fig.tight_layout()
    rank_path = config.OPERATIONALIZATION_DIR / "operationalization_ranking.png"
    fig.savefig(rank_path, dpi=150)
    plt.close(fig)
    print(f"\nWrote ranking  -> {rank_path}")

    # --- Figure 2: country × dimension breakdown heatmap ------------------ #
    norm_cols = [f"{d}_norm" for d in operationalization.DIMENSIONS]
    heat = df.set_index("country")[norm_cols]
    heat.columns = [d.capitalize() for d in operationalization.DIMENSIONS]
    fig, ax = plt.subplots(figsize=(8, 0.5 * len(heat) + 1.5))
    sns.heatmap(heat, annot=True, fmt=".2f", cmap="magma", vmin=0, vmax=1,
                cbar_kws={"label": "normalised density"}, ax=ax)
    ax.set_title("Operationalization signals by dimension (min-max normalised)")
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.yticks(rotation=0)
    fig.tight_layout()
    breakdown_path = config.OPERATIONALIZATION_DIR / "operationalization_breakdown.png"
    fig.savefig(breakdown_path, dpi=150)
    plt.close(fig)
    print(f"Wrote breakdown-> {breakdown_path}")
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
