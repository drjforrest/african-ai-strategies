"""Secondary-track analysis: dedicated digital-health / eHealth strategies.

These documents (e.g. Rwanda's Digital Health Strategy, Namibia's eHealth
Strategy, Mauritius's Digital Health Transformation Roadmap) are a different
genre from national AI strategies. A digital-health document aligns strongly
with the WHO digital-health competencies almost by construction, so mixing it
into the primary AI-strategy matrix breaks comparability. This track keeps them
separate while scoring them against the same 9 WHO competency domains.

    python run_secondary.py

Reads data/digital_health_strategies/*.pdf, caches <country>_dh.txt alongside,
and writes outputs/secondary/.
"""

from __future__ import annotations

import pandas as pd

from src import alignment, competencies, config, preprocess, visualize
from src.models import load_embedding_model
from scripts.extract_pdfs import extract_text, match_country


def build_dh_texts() -> dict[str, list]:
    """Group secondary PDFs by country (concatenating multiples) and cache text."""
    groups: dict[str, list] = {}
    for pdf in sorted(config.DH_DIR.glob("*.pdf")):
        country = match_country(pdf.name)
        if country is None:
            print(f"  ! could not match country for {pdf.name} — skipping")
            continue
        groups.setdefault(country, []).append(pdf)

    for country, pdfs in groups.items():
        slug = country.lower().replace(" ", "_").replace("'", "")
        txt = config.DH_DIR / f"{slug}_dh.txt"
        if not txt.exists():
            txt.write_text(extract_text(pdfs), encoding="utf-8")
    return groups


def build_chunk_frame(groups: dict[str, list]) -> pd.DataFrame:
    rows = []
    for country in groups:
        slug = country.lower().replace(" ", "_").replace("'", "")
        txt = config.DH_DIR / f"{slug}_dh.txt"
        for i, chunk in enumerate(preprocess.load_and_chunk(txt)):
            rows.append({"country": country, "chunk_id": i, "chunk_text": chunk})
    return pd.DataFrame(rows, columns=["country", "chunk_id", "chunk_text"])


def main() -> int:
    config.SECONDARY_HEATMAP_DIR.mkdir(parents=True, exist_ok=True)

    groups = build_dh_texts()
    if not groups:
        print(f"No PDFs in {config.DH_DIR}.")
        return 1
    chunk_frame = build_chunk_frame(groups)
    print(f"Secondary corpus: {len(groups)} digital-health strategies, "
          f"{len(chunk_frame)} chunks ({', '.join(groups)}).")

    comp_df = competencies.load_competencies()
    model = load_embedding_model()
    print(f"Embedding backend: {model.name}")
    corpus = competencies.embedding_texts(comp_df) + chunk_frame["chunk_text"].tolist()
    model.fit(corpus)
    comp_embeds = competencies.embed_competencies(comp_df, model, save_path=None)

    scores = alignment.build_alignment_scores(
        chunk_frame, comp_df, comp_embeds, model, cache_embeddings=False
    )
    alignment.save_alignment_scores(scores, config.SECONDARY_SCORES_CSV)
    print(f"Wrote secondary scores -> {config.SECONDARY_SCORES_CSV}")

    pivot = visualize.to_pivot(scores, competency_order=comp_df["competency_id"].tolist())
    hm = visualize.plot_heatmap(
        pivot, normalise="column",
        title="Digital-health strategies × WHO competencies (secondary track)",
        save_path=config.SECONDARY_HEATMAP_DIR / "secondary_heatmap.png",
    )
    print(f"Wrote secondary heatmap -> {hm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
