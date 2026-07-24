"""Load and embed the WHO competency domains.

The competency reference lives in ``data/who_strategy/competencies.csv`` with
columns ``competency_id, name, description``. Each domain's ``description`` is
what gets embedded — keep it a focused 2–4 sentence statement of the domain.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config
from .models import EmbeddingBackend

REQUIRED_COLUMNS = ("competency_id", "name", "description")


def load_competencies(path: str | Path = config.COMPETENCIES_CSV) -> pd.DataFrame:
    """Load and validate the competency reference table."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"competencies.csv not found at {path}. "
            "A seeded version ships in data/who_strategy/."
        )
    df = pd.read_csv(path, dtype=str).fillna("")
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"competencies.csv missing columns: {missing}")
    df["competency_id"] = df["competency_id"].str.strip()
    df["description"] = df["description"].str.strip()
    if df["competency_id"].duplicated().any():
        dupes = df.loc[df["competency_id"].duplicated(), "competency_id"].tolist()
        raise ValueError(f"Duplicate competency_id(s): {dupes}")
    return df.reset_index(drop=True)


def embedding_texts(df: pd.DataFrame) -> list[str]:
    """Text to embed per competency: name + description (name adds a strong
    topical anchor the description alone can lack)."""
    return [f"{n}. {d}".strip(". ") for n, d in zip(df["name"], df["description"])]


def embed_competencies(
    df: pd.DataFrame,
    model: EmbeddingBackend,
    *,
    save_path: str | Path | None = config.COMPETENCY_EMBEDDINGS_NPY,
) -> np.ndarray:
    """Embed each competency description; optionally cache to ``.npy``.

    Returns an array of shape ``[n_competencies, dim]``.
    """
    embeddings = model.encode(embedding_texts(df))
    if save_path is not None:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(save_path, embeddings)
    return embeddings
