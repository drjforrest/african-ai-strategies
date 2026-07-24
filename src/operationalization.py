"""Policy operationalization index.

The WHO-competency alignment measures *rhetorical* similarity — and washes out,
because every strategy shares the digital-policy register. This module measures
something the embeddings cannot: how *operational* a strategy is, i.e. whether
it commits to timelines, money, named owners, legal instruments, monitoring, and
implementation mechanics, versus stating aspirations ("build capacity").

Method — deliberately transparent and reproducible (unlike opaque embeddings):
each of six sub-dimensions is a hand-audited lexicon/regex detector. We count
matches and normalise by document length (hits per 1,000 words) to remove the
same length bias that plagued the alignment matrix. The headline
``operationalization_index`` is then a *breadth* measure — the fraction of the
six execution levers a strategy addresses at above-median intensity for the
sample — which avoids both failure modes of a naive composite: per-1k-word
density over-rewards terse implementation matrices, while raw counts over-reward
long documents. A secondary ``focus_index`` (mean of min-max densities) captures
how execution-dense the prose is. Both are *within-sample relative* measures.

Bilingual by design: several strategies are in French (notably Senegal and Côte
d'Ivoire). An English-only lexicon would under-count them and fabricate an
"anglophone = more operational" artifact, so every detector carries EN + FR
terms, plus language-agnostic markers (years, fiscal years, currency amounts).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from . import config, preprocess

# --------------------------------------------------------------------------- #
# Sub-dimension detectors  (case-insensitive; EN + FR + language-agnostic)
# --------------------------------------------------------------------------- #
# Each pattern targets a concrete, auditable signal of operationalization. Kept
# as raw strings with inline notes so the exact rules can go in a methods table.

_DETECTORS: dict[str, str] = {
    # 1. Time-bound commitments: target years, fiscal years, quarters, phases,
    #    "by/d'ici/à l'horizon 20XX", short/medium/long-term horizons.
    "timelines": r"""
        \b20(?:2[3-9]|3[0-5])\b                         # target years 2023–2035
      | \bFY\s?\d{2}\s?[/-]\s?\d{2}\b                    # FY23/24
      | \b20\d{2}\s?[/-]\s?\d{2}\b                       # 2023/24
      | \b(?:by|d['’]ici|(?:à\s+l['’])?horizon)\s+20\d{2}\b
      | \b(?:Q[1-4]|quarter|trimestre)\b
      | \bphase\s+(?:\d+|[IVX]+)\b
      | \b(?:short|medium|long)[-\s]term\b
      | \b(?:court|moyen|long)\s+terme\b
    """,
    # 2. Financing: currency amounts (symbols + African currency codes), scale
    #    words, and budget vocabulary.
    "budget": r"""
        (?:US\$|\$|€|£|USD|EUR|GBP)\s?\d
      | \b(?:RWF|KES|NGN|GHS|ZAR|EGP|MAD|DZD|TND|MUR|XOF|FCFA|CFA)\s?\d
      | \b\d[\d,.\s]*\s?(?:million|billion|milliard|thousand|bn|mn)\b
      | \b(?:budget|funding|financing|fiscal|allocation|investment)\b
      | \b(?:financement|investissement|coût|enveloppe|dotation|budgétaire)\b
    """,
    # 3. Named owners / accountability: who is responsible for delivery.
    "agencies": r"""
        \bMinistry\s+of\s+[A-Z]
      | \bminist[èe]re\s+(?:de|du|des|chargé)
      | \b(?:Authority|Agency|Commission|Directorate|Taskforce|Task\s+Force|Secretariat)\b
      | \b(?:autorité|agence|commission|direction|secrétariat)\b
      | \b(?:responsible\s+(?:institution|agency|for)|lead\s+(?:agency|institution|ministry))\b
      | \b(?:shall\s+be\s+responsible|in\s+charge\s+of|mandated\s+to|accountable\s+for)\b
      | \b(?:responsable\s+(?:de|du)|chargé\s+de|sous\s+la\s+responsabilité)\b
    """,
    # 4. Legal / regulatory instruments: statutes, decrees, formal frameworks.
    "regulatory": r"""
        \b(?:Act|Bill|Law|Decree|Regulations?|Statute|Legislation|Ordinance|Gazette)\b
      | \b(?:loi|décret|arrêté|règlement|législation|ordonnance)\b
      | \b(?:legal|regulatory|statutory)\s+framework\b
      | \bcadre\s+(?:juridique|réglementaire|légal)\b
      | \b(?:shall\s+establish|enact|promulgat\w+)\b
      | \bautorité\s+de\s+régulation\b
    """,
    # 5. Monitoring & evaluation: indicators, targets, baselines, M&E frameworks.
    "monitoring": r"""
        \bmonitoring\s+and\s+evaluation\b | \bM\s?&\s?E\b
      | \b(?:indicator|KPI|key\s+performance|baseline|milestone|logframe|log\s+frame)\b
      | \bresults[-\s](?:framework|based)\b
      | \b(?:suivi[-\s](?:et[-\s])?évaluation|indicateur|jalon|cadre\s+de\s+résultats)\b
      | \b(?:cible|référence)\b
      | \b(?:evaluation|évaluation)\b
    """,
    # 6. Implementation / procurement mechanics: plans, roadmaps, tenders, pilots.
    "implementation": r"""
        \b(?:implementation|action)\s+plan\b | \broadmap\b
      | \b(?:procurement|tender|vendor|pilot(?:\s+project)?|deployment|roll[-\s]?out)\b
      | \bphased\s+implementation\b
      | \b(?:plan\s+d['’](?:action|actions)|plan\s+de\s+mise\s+en\s+œuvre|feuille\s+de\s+route)\b
      | \b(?:marché\s+public|appel\s+d['’]offres|projet\s+pilote|déploiement|mise\s+en\s+œuvre)\b
    """,
}

DIMENSIONS: list[str] = list(_DETECTORS)

_COMPILED: dict[str, re.Pattern] = {
    name: re.compile(pat, re.IGNORECASE | re.VERBOSE) for name, pat in _DETECTORS.items()
}


# --------------------------------------------------------------------------- #
# Scoring
# --------------------------------------------------------------------------- #
def score_document(text: str) -> dict[str, float]:
    """Raw match count and per-1,000-word density for each sub-dimension.

    Returns a flat dict: ``n_words`` plus ``<dim>_count`` and ``<dim>_density``
    for every dimension. Density (per 1,000 words) is the length-normalised
    signal used downstream; raw counts are kept for auditing.
    """
    cleaned = preprocess.clean_text(text)
    n_words = max(len(cleaned.split()), 1)
    out: dict[str, float] = {"n_words": float(n_words)}
    for dim, rx in _COMPILED.items():
        hits = len(rx.findall(cleaned))
        out[f"{dim}_count"] = float(hits)
        out[f"{dim}_density"] = 1000.0 * hits / n_words
    return out


def build_index(
    countries: list[str] | None = None, *, skip_missing: bool = True
) -> pd.DataFrame:
    """Build the country × operationalization-dimension table + composite indices.

    Two indices, both within-sample and length-robust, capturing distinct facets:

    * ``operationalization_index`` (PRIMARY — *breadth*): the fraction of the six
      execution levers a strategy addresses at above-median intensity for the
      sample. Robust to document length and interpretable — it neither rewards a
      terse implementation matrix for its brevity (which per-1k-word density
      does) nor a long strategy for its bulk (which raw counts do). A dimension
      counts as "addressed" when its density exceeds the cross-country median.
    * ``focus_index`` (SECONDARY — *execution focus*): mean of the min-max scaled
      densities — how execution-dense the prose is. Reported alongside because a
      compact implementation plan (e.g. Rwanda) scores high here while covering
      fewer levers; the two together tell the fuller story.

    Columns: ``country``, ``n_words``, per dimension ``<dim>_count``,
    ``<dim>_density``, ``<dim>_norm`` (min-max), ``<dim>_covered`` (0/1 above
    median), plus ``operationalization_index`` and ``focus_index``.

    Rows are sorted by the primary index (focus_index breaks ties), descending.
    ``.attrs['skipped']`` lists countries with no text file.
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
        rec: dict[str, object] = {"country": country}
        rec.update(score_document(preprocess.load_text(path)))
        rows.append(rec)

    df = pd.DataFrame(rows)
    if df.empty:
        df.attrs["skipped"] = skipped
        return df

    for dim in DIMENSIONS:
        col = df[f"{dim}_density"]
        # Secondary: min-max scaled density ([0, 1]); degenerate dim -> 0.0.
        span = col.max() - col.min()
        df[f"{dim}_norm"] = 0.0 if span == 0 else (col - col.min()) / span
        # Primary building block: addressed above the sample-typical level.
        df[f"{dim}_covered"] = (col > col.median()).astype(int)

    covered_cols = [f"{dim}_covered" for dim in DIMENSIONS]
    norm_cols = [f"{dim}_norm" for dim in DIMENSIONS]
    df["operationalization_index"] = df[covered_cols].mean(axis=1)  # breadth
    df["focus_index"] = df[norm_cols].mean(axis=1)                  # execution focus

    df = df.sort_values(
        ["operationalization_index", "focus_index"], ascending=False
    ).reset_index(drop=True)
    df.attrs["skipped"] = skipped
    return df


def save_index(df: pd.DataFrame, path: str | Path | None = None) -> Path:
    path = Path(path) if path else config.OPERATIONALIZATION_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path
