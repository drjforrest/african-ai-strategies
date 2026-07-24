"""Fast, dependency-light tests for the alignment pipeline.

These exercise the pure logic (chunking, similarity, aggregation, pivoting) and
one small end-to-end pass on the TF-IDF backend, so they run without the heavy
sentence-transformers stack and without any real strategy data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src import alignment, competencies, operationalization, preprocess, visualize
from src.models import TfidfBackend


# --------------------------------------------------------------------------- #
# preprocess
# --------------------------------------------------------------------------- #
def test_clean_text_strips_artifacts():
    raw = "Page 12\nHealth  strategy\ffor\ninter-\noperability   here"
    cleaned = preprocess.clean_text(raw)
    assert "Page 12" not in cleaned
    assert "interoperability" in cleaned          # hyphen line-break rejoined
    assert "  " not in cleaned                     # whitespace collapsed


def test_clean_text_repairs_ai_ligature_misread():
    # PDF extraction misreads the "AI" ligature as "Al"; repair it...
    raw = "Al governance and Al/ML and Al-relevant skills"
    cleaned = preprocess.clean_text(raw)
    assert cleaned == "AI governance and AI/ML and AI-relevant skills"


def test_clean_text_preserves_arabic_proper_names():
    # ...but never corrupt genuine "al-" article names.
    for name in ("Al Jazari Institute", "Al-Azhar University", "Al Jazeera"):
        assert preprocess.clean_text(name) == name


def test_chunk_text_respects_max_tokens():
    text = " ".join(f"word{i}" for i in range(500))
    chunks = preprocess.chunk_text(text, max_tokens=100, overlap=10, min_tokens=5)
    assert len(chunks) >= 5
    assert all(len(c.split()) <= 100 for c in chunks)


def test_chunk_text_drops_tiny_chunks():
    chunks = preprocess.chunk_text("too short", max_tokens=150, min_tokens=25)
    assert chunks == []


# --------------------------------------------------------------------------- #
# similarity + aggregation
# --------------------------------------------------------------------------- #
def test_compute_similarity_shape_and_identity():
    rng = np.random.default_rng(0)
    comp = rng.random((3, 8)).astype(np.float32)
    sim = alignment.compute_similarity(comp, comp)
    assert sim.shape == (3, 3)
    # self-similarity on the diagonal is ~1 after normalisation
    assert np.allclose(np.diag(sim), 1.0, atol=1e-5)


def test_compute_similarity_dim_mismatch_raises():
    with pytest.raises(ValueError):
        alignment.compute_similarity(np.zeros((2, 4)), np.zeros((3, 5)))


@pytest.mark.parametrize("method", ["mean", "max", "top_k_mean", "top_frac_mean"])
def test_aggregate_methods(method):
    sim = np.array([[0.1, 0.9], [0.9, 0.1]])  # 2 chunks x 2 competencies
    scores = alignment.aggregate_scores(sim, method=method, top_k=2)
    assert scores.shape == (2,)
    if method == "max":
        assert np.allclose(scores, [0.9, 0.9])
    if method == "mean":
        assert np.allclose(scores, [0.5, 0.5])


def test_top_frac_mean_is_length_robust():
    # A short and a long document with the SAME similarity distribution should
    # score the same under top_frac_mean — the fix for the length bias that a
    # fixed top_k exhibits (best-k-of-N rises with N).
    rng = np.random.default_rng(0)
    short = rng.random((40, 1))            # 40 chunks, 1 competency
    long = np.repeat(short, 10, axis=0)    # same values, 10x the rows (400 chunks)

    s_short = alignment.aggregate_scores(short, method="top_frac_mean")
    s_long = alignment.aggregate_scores(long, method="top_frac_mean")
    assert np.allclose(s_short, s_long, atol=1e-6)

    # Fixed top_k, by contrast, does NOT stay stable: the long doc's best-5 are
    # all near its maximum, so it scores at least as high as the short doc's.
    k_short = alignment.aggregate_scores(short, method="top_k_mean", top_k=5)
    k_long = alignment.aggregate_scores(long, method="top_k_mean", top_k=5)
    assert k_long >= k_short


def test_aggregate_unknown_method_raises():
    with pytest.raises(ValueError):
        alignment.aggregate_scores(np.zeros((2, 2)), method="median")


# --------------------------------------------------------------------------- #
# TF-IDF backend + end-to-end
# --------------------------------------------------------------------------- #
def test_tfidf_requires_fit():
    backend = TfidfBackend()
    with pytest.raises(RuntimeError):
        backend.encode(["hello world"])


def test_end_to_end_tfidf(tmp_path):
    comp_df = pd.DataFrame(
        {
            "competency_id": ["C1", "C2"],
            "name": ["Data governance", "Infrastructure"],
            "description": [
                "data protection privacy security consent personal data",
                "broadband connectivity electricity data centres cloud infrastructure",
            ],
        }
    )
    chunk_frame = pd.DataFrame(
        {
            "country": ["A", "A", "B", "B"],
            "chunk_id": [0, 1, 0, 1],
            "chunk_text": [
                "data protection and privacy safeguards for personal data",
                "consent and security of personal data records",
                "broadband connectivity and cloud infrastructure electricity",
                "data centres and network coverage infrastructure",
            ],
        }
    )

    backend = TfidfBackend()
    corpus = competencies.embedding_texts(comp_df) + chunk_frame["chunk_text"].tolist()
    backend.fit(corpus)
    comp_embeds = competencies.embed_competencies(comp_df, backend, save_path=None)
    assert comp_embeds.shape[0] == 2

    scores = alignment.build_alignment_scores(
        chunk_frame, comp_df, comp_embeds, backend, cache_embeddings=False
    )
    assert set(scores.columns) == {"country", "competency_id", "similarity_score"}
    assert len(scores) == 4  # 2 countries x 2 competencies
    assert scores["similarity_score"].notna().all()

    # Country A should align more with C1 (data), country B more with C2 (infra).
    pivot = visualize.to_pivot(scores)
    assert pivot.loc["A", "C1"] > pivot.loc["A", "C2"]
    assert pivot.loc["B", "C2"] > pivot.loc["B", "C1"]

    out = alignment.save_alignment_scores(scores, tmp_path / "scores.csv")
    assert out.exists()


# --------------------------------------------------------------------------- #
# operationalization index
# --------------------------------------------------------------------------- #
def test_score_document_detects_signals():
    text = (
        "By 2027 the Digital Health Authority shall implement the plan. "
        "A budget of USD 5 million is allocated. Ministry of Health is "
        "responsible. The AI Act establishes monitoring and evaluation with "
        "KPI indicators and an implementation roadmap and procurement plan."
    )
    s = operationalization.score_document(text)
    for dim in operationalization.DIMENSIONS:
        assert s[f"{dim}_count"] >= 1, f"{dim} should fire on a rich sentence"


def test_score_document_is_bilingual():
    # French operational vocabulary must be detected, or francophone strategies
    # (Senegal, Côte d'Ivoire) would be spuriously scored as non-operational.
    fr = (
        "D'ici 2027, le ministère de la Santé est responsable du financement. "
        "Un décret fixe le cadre juridique. Le suivi-évaluation utilise des "
        "indicateurs. La feuille de route prévoit un appel d'offres."
    )
    s = operationalization.score_document(fr)
    for dim in ("timelines", "budget", "agencies", "regulatory", "monitoring", "implementation"):
        assert s[f"{dim}_count"] >= 1, f"{dim} should fire on French text"


def test_build_index_bounded_and_length_robust():
    # A short doc that is ALL operational content and a long doc with the same
    # operational sentence repeated should not be ranked purely by length.
    op = "By 2027 the Ministry of Health budget of USD 5 million funds the M&E plan."
    filler = " ".join(f"vision{i}" for i in range(2000))
    # Direct scoring path (no filesystem): exercise the public scorer + bounds.
    short = operationalization.score_document(op)
    long = operationalization.score_document(op + " " + filler)
    # Density must be higher for the concentrated doc (length normalisation works)
    assert short["timelines_density"] > long["timelines_density"]
    # Indices are bounded [0, 1] whenever build_index runs on real data.
    real = operationalization.build_index()
    if not real.empty:
        assert real["operationalization_index"].between(0, 1).all()
        assert real["focus_index"].between(0, 1).all()
        assert real["operationalization_index"].is_monotonic_decreasing
