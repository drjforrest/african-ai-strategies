"""Embedding backends.

Primary backend is a sentence-transformer (``config.MODEL_NAME``). If
``sentence-transformers`` is not installed and ``config.ALLOW_TFIDF_FALLBACK``
is on, a deterministic TF-IDF backend is used instead so the pipeline still
produces a full alignment matrix offline.

Both backends return L2-normalised vectors, so a plain dot product equals
cosine similarity downstream.

Interface (per spec):
    model = load_embedding_model(model_name)
    vecs  = embed_texts(texts, model=model)   # -> np.ndarray [n, dim]

TF-IDF caveat: TF-IDF vectors are only meaningful relative to a fixed
vocabulary, so the backend must see the *whole* corpus before encoding. Call
``model.fit(all_texts)`` once (a no-op for the transformer backend) before any
``encode``. The pipeline in ``run_pipeline`` handles this for you.
"""

from __future__ import annotations

import warnings
from typing import Protocol, Sequence

import numpy as np

from . import config


def _l2_normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (mat / norms).astype(np.float32)


class EmbeddingBackend(Protocol):
    name: str

    def fit(self, corpus: Sequence[str]) -> "EmbeddingBackend": ...
    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class SentenceTransformerBackend:
    """Wraps a sentence-transformers model. Stateless; ``fit`` is a no-op."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer  # lazy, heavy

        self.name = f"sentence-transformers:{model_name}"
        self._model = SentenceTransformer(model_name)

    def fit(self, corpus: Sequence[str]) -> "SentenceTransformerBackend":
        return self

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if len(texts) == 0:
            dim = self._model.get_sentence_embedding_dimension() or 0
            return np.empty((0, int(dim)), dtype=np.float32)
        vecs = self._model.encode(
            list(texts),
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vecs.astype(np.float32)


class TfidfBackend:
    """Deterministic offline fallback. Must be ``fit`` on the full corpus."""

    def __init__(self):
        from sklearn.feature_extraction.text import TfidfVectorizer

        self.name = "tfidf-fallback"
        self._vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_features=8192,
        )
        self._fitted = False

    def fit(self, corpus: Sequence[str]) -> "TfidfBackend":
        self._vectorizer.fit(list(corpus))
        self._fitted = True
        return self

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError(
                "TfidfBackend must be fit on the full corpus before encoding. "
                "Call model.fit(all_texts) first."
            )
        if len(texts) == 0:
            return np.empty((0, len(self._vectorizer.vocabulary_)), dtype=np.float32)
        sparse = self._vectorizer.transform(list(texts))
        mat = np.asarray(sparse.todense(), dtype=np.float32)  # type: ignore[union-attr]
        return _l2_normalize(mat)


def load_embedding_model(model_name: str = config.MODEL_NAME) -> EmbeddingBackend:
    """Return the best available backend.

    Tries sentence-transformers first; on ImportError falls back to TF-IDF when
    allowed, emitting a clear warning.
    """
    try:
        return SentenceTransformerBackend(model_name)
    except ImportError:
        if not config.ALLOW_TFIDF_FALLBACK:
            raise
        warnings.warn(
            "sentence-transformers not installed — falling back to the TF-IDF "
            "backend. Results run end-to-end but are lexical, not semantic; "
            "`pip install sentence-transformers` for the real model.",
            RuntimeWarning,
            stacklevel=2,
        )
        return TfidfBackend()


def embed_texts(
    texts: Sequence[str], model: EmbeddingBackend | None = None
) -> np.ndarray:
    """Embed a list of texts, loading a default model if none is supplied.

    Note: passing a fresh default TF-IDF model here means it is fit on
    ``texts`` alone. Prefer supplying a corpus-fit model for cross-document
    comparability.
    """
    if model is None:
        model = load_embedding_model()
        model.fit(texts)
    return model.encode(texts)
