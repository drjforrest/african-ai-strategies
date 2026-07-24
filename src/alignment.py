"""Strategy chunk embedding, similarity, and country-level aggregation.

Pipeline within a country:
    text -> clean -> chunk -> embed chunks
    cosine(chunk_embeds, competency_embeds)  -> [n_chunks, n_competencies]
    aggregate over chunks                     -> [n_competencies] score vector

Aggregating over chunks matters: a strategy rarely addresses a competency in
every paragraph, so ``mean`` over all chunks dilutes real coverage. ``max`` is
the strongest single passage (sensitive to noise); ``top_k_mean`` averages the
k best-matching passages — a robust middle ground and the default.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import config, preprocess
from .models import EmbeddingBackend


# --------------------------------------------------------------------------- #
# Chunk extraction
# --------------------------------------------------------------------------- #
def build_chunk_frame(
    countries: list[str] | None = None,
    *,
    skip_missing: bool = True,
) -> pd.DataFrame:
    """Load, clean and chunk every available country strategy.

    Returns a long DataFrame: ``country, chunk_id, chunk_text``. Countries with
    no text file are skipped (with a note in ``.attrs['skipped']``) unless
    ``skip_missing`` is False, in which case a FileNotFoundError propagates.
    """
    countries = countries or config.COUNTRIES
    rows: list[dict] = []
    skipped: list[str] = []

    for country in countries:
        path = config.country_path(country)
        if not path.exists():
            if skip_missing:
                skipped.append(country)
                continue
            raise FileNotFoundError(f"Missing strategy for {country}: {path}")
        chunks = preprocess.load_and_chunk(path)
        for i, chunk in enumerate(chunks):
            rows.append({"country": country, "chunk_id": i, "chunk_text": chunk})

    frame = pd.DataFrame(rows, columns=["country", "chunk_id", "chunk_text"])
    frame.attrs["skipped"] = skipped
    return frame


# --------------------------------------------------------------------------- #
# Similarity + aggregation
# --------------------------------------------------------------------------- #
def compute_similarity(
    chunk_embeds: np.ndarray, comp_embeds: np.ndarray
) -> np.ndarray:
    """Cosine similarity matrix, shape ``[n_chunks, n_competencies]``.

    Both inputs are expected L2-normalised (the backends guarantee this), so a
    dot product is the cosine. We normalise defensively anyway to stay correct
    if raw vectors are ever passed in.
    """
    if chunk_embeds.ndim != 2 or comp_embeds.ndim != 2:
        raise ValueError("Both embedding arrays must be 2-D [n, dim].")
    if chunk_embeds.shape[1] != comp_embeds.shape[1]:
        raise ValueError(
            f"Embedding dims differ: {chunk_embeds.shape[1]} vs "
            f"{comp_embeds.shape[1]}. Same backend must embed both."
        )

    def _norm(m: np.ndarray) -> np.ndarray:
        n = np.linalg.norm(m, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return m / n

    # NumPy 2.x on macOS/arm64 with the Accelerate BLAS emits spurious
    # divide-by-zero/overflow/invalid warnings from *any* matmul, even on clean
    # finite inputs (numpy/numpy#24188). Inputs here are verified finite and
    # unit-normalised, so these flags are false positives — silence them.
    with np.errstate(divide="ignore", over="ignore", under="ignore", invalid="ignore"):
        return _norm(chunk_embeds) @ _norm(comp_embeds).T


def aggregate_scores(
    sim_matrix: np.ndarray,
    method: str = config.AGGREGATION_METHOD,
    *,
    top_k: int = config.TOP_K,
    top_fraction: float = config.TOP_FRACTION,
    top_frac_floor: int = config.TOP_FRAC_FLOOR,
) -> np.ndarray:
    """Collapse a ``[n_chunks, n_competencies]`` matrix to ``[n_competencies]``.

    method: "mean" | "max" | "top_k_mean" | "top_frac_mean"

    ``top_frac_mean`` averages the strongest ``top_fraction`` of a strategy's
    chunks per competency (never fewer than ``top_frac_floor``). Because the
    passage count scales with document length, short and long strategies are
    scored on comparable footing — unlike a fixed ``top_k``, whose "best k of N"
    rises with N and so systematically favours longer documents.
    """
    if sim_matrix.size == 0:
        return np.zeros(sim_matrix.shape[1] if sim_matrix.ndim == 2 else 0)

    if method == "mean":
        return sim_matrix.mean(axis=0)
    if method == "max":
        return sim_matrix.max(axis=0)
    if method == "top_k_mean":
        k = min(top_k, sim_matrix.shape[0])
        # Partition the k largest per column, then mean them.
        part = np.partition(sim_matrix, -k, axis=0)[-k:, :]
        return part.mean(axis=0)
    if method == "top_frac_mean":
        n = sim_matrix.shape[0]
        # k = fraction of chunks, floored at top_frac_floor, clamped to n.
        k = max(min(top_frac_floor, n), int(round(top_fraction * n)))
        k = max(1, min(k, n))
        part = np.partition(sim_matrix, -k, axis=0)[-k:, :]
        return part.mean(axis=0)
    raise ValueError(f"Unknown aggregation method: {method!r}")


# --------------------------------------------------------------------------- #
# End-to-end alignment matrix
# --------------------------------------------------------------------------- #
def build_alignment_scores(
    chunk_frame: pd.DataFrame,
    competencies_df: pd.DataFrame,
    comp_embeds: np.ndarray,
    model: EmbeddingBackend,
    *,
    method: str = config.AGGREGATION_METHOD,
    top_k: int = config.TOP_K,
    top_fraction: float = config.TOP_FRACTION,
    top_frac_floor: int = config.TOP_FRAC_FLOOR,
    cache_embeddings: bool = True,
) -> pd.DataFrame:
    """Produce the long-form alignment table.

    Returns ``country, competency_id, similarity_score`` with one row per
    (country, competency) pair.
    """
    comp_ids = competencies_df["competency_id"].tolist()
    records: list[dict] = []

    for country_key, group in chunk_frame.groupby("country", sort=False):
        country = str(country_key)
        chunks = group["chunk_text"].tolist()
        chunk_embeds = model.encode(chunks)

        if cache_embeddings and chunk_embeds.size:
            config.EMBEDDINGS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
            safe = config.COUNTRY_FILES[country].replace(".txt", "")
            np.save(
                config.EMBEDDINGS_CACHE_DIR / f"{safe}_chunk_embeddings.npy",
                chunk_embeds,
            )

        sim = compute_similarity(chunk_embeds, comp_embeds)
        scores = aggregate_scores(
            sim, method=method, top_k=top_k,
            top_fraction=top_fraction, top_frac_floor=top_frac_floor,
        )
        for cid, score in zip(comp_ids, scores):
            records.append(
                {
                    "country": country,
                    "competency_id": cid,
                    "similarity_score": float(score),
                }
            )

    return pd.DataFrame(records, columns=["country", "competency_id", "similarity_score"])


def save_alignment_scores(
    scores_df: pd.DataFrame, path: str | Path = config.ALIGNMENT_SCORES_CSV
) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scores_df.to_csv(path, index=False)
    return path
