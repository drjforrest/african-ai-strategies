"""Central configuration for the AI-strategy x WHO-competency alignment pipeline.

Everything path- or parameter-related lives here so the modules stay free of
magic strings. Paths are resolved relative to the project root (the parent of
this ``src`` directory), so the pipeline works regardless of the current
working directory.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent

DATA_DIR = PROJECT_ROOT / "data"
WHO_DIR = DATA_DIR / "who_strategy"
NATIONAL_DIR = DATA_DIR / "national_strategies"
# Secondary corpus: dedicated digital-health / eHealth strategies. These are a
# different document genre from national AI strategies and are analysed on a
# separate track so they don't distort the apples-to-apples AI-strategy matrix.
DH_DIR = DATA_DIR / "digital_health_strategies"

COMPETENCIES_CSV = WHO_DIR / "competencies.csv"
WHO_STRATEGY_TXT = WHO_DIR / "who_gsdh.txt"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"
HEATMAP_DIR = OUTPUTS_DIR / "heatmaps"

# Secondary-track outputs (digital-health strategies).
SECONDARY_DIR = OUTPUTS_DIR / "secondary"
SECONDARY_HEATMAP_DIR = SECONDARY_DIR / "heatmaps"
SECONDARY_SCORES_CSV = SECONDARY_DIR / "alignment_scores.csv"

ALIGNMENT_SCORES_CSV = OUTPUTS_DIR / "alignment_scores.csv"
CHUNK_METADATA_CSV = OUTPUTS_DIR / "strategy_chunks.csv"
COMPETENCY_EMBEDDINGS_NPY = OUTPUTS_DIR / "competency_embeddings.npy"

# Differentiating-axis outputs (transparent lexicon indices, not embeddings).
OPERATIONALIZATION_DIR = OUTPUTS_DIR / "operationalization"
OPERATIONALIZATION_CSV = OPERATIONALIZATION_DIR / "operationalization_index.csv"

# Per-country cached chunk embeddings live here: <country>_chunk_embeddings.npy
EMBEDDINGS_CACHE_DIR = OUTPUTS_DIR / "embeddings"

# --------------------------------------------------------------------------- #
# Model / embedding parameters
# --------------------------------------------------------------------------- #
# Primary backend. The corpus is multilingual (several strategies are in
# French), so the default is a multilingual model that embeds English and French
# into a shared space. Swap for "sentence-transformers/all-MiniLM-L6-v2" if your
# corpus is English-only (smaller/faster).
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# When sentence-transformers is unavailable, fall back to a deterministic
# TF-IDF backend so the pipeline still runs. Scores are only comparable *within*
# a single backend, never across the two.
ALLOW_TFIDF_FALLBACK = True

# --------------------------------------------------------------------------- #
# Chunking
# --------------------------------------------------------------------------- #
CHUNK_SIZE_TOKENS = 150          # target paragraph size (whitespace tokens)
CHUNK_OVERLAP_TOKENS = 20        # sliding-window overlap to avoid cutting ideas
MIN_CHUNK_TOKENS = 25            # drop chunks shorter than this (headers, noise)

# --------------------------------------------------------------------------- #
# Aggregation of chunk->competency similarities to a country-level score
# --------------------------------------------------------------------------- #
AGGREGATION_METHOD = "top_frac_mean"  # "mean" | "max" | "top_k_mean" | "top_frac_mean"
TOP_K = 5                             # used when AGGREGATION_METHOD == "top_k_mean"

# top_frac_mean scores each competency from a strategy's strongest TOP_FRACTION
# of chunks (never fewer than TOP_FRAC_FLOOR). Scaling the passage count with
# document length removes the length bias a *fixed* TOP_K imposes: "best 5 of
# 365 chunks" beats "best 5 of 46", which alone dragged short strategies (e.g.
# Rwanda) down across every competency. See README methods note.
TOP_FRACTION = 0.10
TOP_FRAC_FLOOR = 3

# --------------------------------------------------------------------------- #
# Countries: display name -> strategy filename (in data/national_strategies/)
# --------------------------------------------------------------------------- #
COUNTRY_FILES: dict[str, str] = {
    "Algeria": "algeria_ai.txt",
    "Benin": "benin_ai.txt",
    "Côte d'Ivoire": "cote_divoire_ai.txt",
    "Egypt": "egypt_ai.txt",
    "Ghana": "ghana_ai.txt",
    "Kenya": "kenya_ai.txt",
    "Mauritius": "mauritius_ai.txt",
    "Morocco": "morocco_ai.txt",
    "Namibia": "namibia_ai.txt",
    "Nigeria": "nigeria_ai.txt",
    "Rwanda": "rwanda_ai.txt",
    "Senegal": "senegal_ai.txt",
    "South Africa": "south_africa_ai.txt",
    "Tunisia": "tunisia_ai.txt",
    "Zimbabwe": "zimbabwe_ai.txt",
    "African Union": "african_union_ai.txt",  # continental regional anchor
}

COUNTRIES: list[str] = list(COUNTRY_FILES.keys())


def country_path(country: str) -> Path:
    """Absolute path to a country's strategy text file."""
    return NATIONAL_DIR / COUNTRY_FILES[country]


def ensure_dirs() -> None:
    """Create every output directory the pipeline writes to."""
    for d in (OUTPUTS_DIR, HEATMAP_DIR, EMBEDDINGS_CACHE_DIR):
        d.mkdir(parents=True, exist_ok=True)
