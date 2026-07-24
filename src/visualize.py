"""Heatmap and clustered-heatmap visualisations of the alignment matrix."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe; must precede pyplot import
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from . import config  # noqa: E402


def load_scores(path: str | Path = config.ALIGNMENT_SCORES_CSV) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found — run the alignment pipeline first."
        )
    return pd.read_csv(path)


def to_pivot(
    scores_df: pd.DataFrame,
    *,
    competency_order: list[str] | None = None,
    country_order: list[str] | None = None,
) -> pd.DataFrame:
    """Long -> wide: rows=country, cols=competency_id, values=similarity."""
    pivot = scores_df.pivot(
        index="country", columns="competency_id", values="similarity_score"
    )
    if competency_order:
        cols = [c for c in competency_order if c in pivot.columns]
        pivot = pivot[cols]
    if country_order:
        rows = [c for c in country_order if c in pivot.index]
        pivot = pivot.reindex(rows)
    return pd.DataFrame(pivot)


def _normalise(pivot: pd.DataFrame, how: str | None) -> pd.DataFrame:
    """Optional per-axis min-max scaling to 0–1.

    how: None (raw), "global", "row", or "column".
    Raw cosine scores are often bunched in a narrow band, so a global or
    per-competency rescale can make relative differences readable — at the cost
    of absolute interpretability. Off by default.
    """
    if how in (None, "none"):
        return pivot
    if how == "global":
        lo, hi = pivot.min().min(), pivot.max().max()
        return (pivot - lo) / (hi - lo) if hi > lo else pivot
    if how == "row":
        return pivot.sub(pivot.min(axis=1), axis=0).div(
            (pivot.max(axis=1) - pivot.min(axis=1)).replace(0, 1), axis=0
        )
    if how == "column":
        return (pivot - pivot.min()) / (pivot.max() - pivot.min()).replace(0, 1)
    raise ValueError(f"Unknown normalisation: {how!r}")


def plot_heatmap(
    pivot: pd.DataFrame,
    *,
    cmap: str = "viridis",
    annotate: bool = True,
    normalise: str | None = None,
    title: str = "AI-strategy alignment with WHO digital-health competencies",
    save_path: str | Path | None = None,
) -> Path | None:
    """Render a country × competency heatmap."""
    data = _normalise(pivot, normalise)
    height = max(4.0, 0.5 * len(data.index) + 2)
    width = max(6.0, 0.9 * len(data.columns) + 3)

    fig, ax = plt.subplots(figsize=(width, height))
    sns.heatmap(
        data,
        cmap=cmap,
        annot=annotate,
        fmt=".2f",
        linewidths=0.5,
        linecolor="white",
        cbar_kws={"label": "similarity" if normalise in (None, "none") else f"{normalise}-scaled"},
        ax=ax,
    )
    ax.set_title(title, pad=12)
    ax.set_xlabel("WHO competency domain")
    ax.set_ylabel("Country")
    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)
    fig.tight_layout()

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return save_path
    plt.close(fig)
    return None


def plot_clustered_heatmap(
    pivot: pd.DataFrame,
    *,
    cmap: str = "magma",
    annotate: bool = False,
    normalise: str | None = None,
    save_path: str | Path | None = None,
):
    """Hierarchically cluster countries and competencies, then heatmap.

    Needs at least 2 rows and 2 columns of non-degenerate data; returns None if
    that isn't met (clustering can't run on a single row/column).
    """
    data = _normalise(pivot, normalise).dropna(how="all").dropna(axis=1, how="all")
    if data.shape[0] < 2 or data.shape[1] < 2:
        return None

    grid = sns.clustermap(
        data,
        cmap=cmap,
        annot=annotate,
        fmt=".2f",
        linewidths=0.5,
        figsize=(max(7.0, 0.9 * data.shape[1] + 3), max(6.0, 0.5 * data.shape[0] + 3)),
        cbar_kws={"label": "similarity"},
    )
    grid.ax_heatmap.set_xlabel("WHO competency domain")
    grid.ax_heatmap.set_ylabel("Country")

    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        grid.savefig(save_path, dpi=150, bbox_inches="tight")
        plt.close(grid.figure)
        return save_path
    plt.close(grid.figure)
    return None
