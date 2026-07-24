"""Cross-walk driver: score the strategy corpus against ANY normative reference.

This generalises ``run_pipeline.py``. The primary pipeline maps each national AI
strategy onto the WHO digital-health competency domains; this runner applies the
*same* instrument to any reference framework supplied as a competency-style CSV
(columns: ``competency_id, name, description`` - identical schema to
``data/who_strategy/competencies.csv``). That keeps one embedding method behind
every mapping the project needs:

  * WHO GSDH competencies          -> the paper's spine (run_pipeline.py)
  * Oxford AI-Readiness dimensions -> ecosystem-context / discriminant cross-walk
                                      (data/.../oxford_dimensions_2021_2024_embed.csv)
  * a future IMIA / HELINA health-informatics competency template
                                      -> the workforce / accreditation tier

Because the reference is just a CSV, adding a framework is a data change, not a
code change. Chunk embeddings are cached per country by the shared pipeline, so
re-scoring the same corpus against a new reference is cheap.

Usage:
  # Oxford readiness cross-walk (default reference)
  python run_reference_alignment.py

  # explicit reference + label
  python run_reference_alignment.py \
      --reference data/oxford_readiness_indices/oxford_dimensions_2021_2024_embed.csv \
      --label oxford_2021_2024

  # a different framework later (e.g. an HI competency template)
  python run_reference_alignment.py --reference data/who_strategy/imia_helina.csv --label imia_helina

Outputs (under outputs/reference_alignment/<label>/):
  <label>_alignment_scores.csv   long form: country, competency_id, similarity_score
  <label>_alignment_heatmap.png  country x reference-construct heatmap (unless --no-plots)
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src import alignment, competencies, config, visualize
from src.models import load_embedding_model

DEFAULT_REFERENCE = (
    config.DATA_DIR / "oxford_readiness_indices" / "oxford_dimensions_2021_2024_embed.csv"
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument(
        "--reference", type=Path, default=DEFAULT_REFERENCE,
        help="reference framework CSV (competency_id,name,description). "
             "Default: the Oxford 2021-2024 dimension definitions.",
    )
    p.add_argument(
        "--label", default=None,
        help="short name for outputs (default: reference filename stem).",
    )
    p.add_argument("--model", default=config.MODEL_NAME, help="sentence-transformers model name")
    p.add_argument(
        "--aggregation", default=config.AGGREGATION_METHOD,
        choices=["mean", "max", "top_k_mean", "top_frac_mean"],
        help="chunk->country aggregation (keep it the SAME as the WHO run so the "
             "two matrices are comparable).",
    )
    p.add_argument("--top-k", type=int, default=config.TOP_K, help="k for top_k_mean")
    p.add_argument(
        "--top-fraction", type=float, default=config.TOP_FRACTION,
        help="fraction of chunks for top_frac_mean (floored at config.TOP_FRAC_FLOOR)",
    )
    p.add_argument(
        "--normalise", default="column", choices=["global", "row", "column"],
        help="heatmap colour rescaling (default column: compare countries within a "
             "construct, since raw cosines sit in a narrow high band).",
    )
    p.add_argument("--no-plots", action="store_true", help="skip heatmap generation")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config.ensure_dirs()

    reference = args.reference
    if not reference.exists():
        print(f"Reference framework not found: {reference}")
        return 1
    label = args.label or reference.stem

    out_dir = config.OUTPUTS_DIR / "reference_alignment" / label
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Reference framework (reuses the WHO competency loader/validator) ----- #
    ref_df = competencies.load_competencies(reference)
    print(f"Loaded {len(ref_df)} reference constructs from {reference.name} (label: {label}).")

    # 2. Strategy chunks (identical corpus + chunking as the WHO run) --------- #
    chunk_frame = alignment.build_chunk_frame()
    skipped = chunk_frame.attrs.get("skipped", [])
    n_countries = chunk_frame["country"].nunique()
    print(f"Chunked {len(chunk_frame)} passages across {n_countries} countries.")
    if skipped:
        print(f"  ! Skipped {len(skipped)} country/ies with no text file: {', '.join(skipped)}")
    if chunk_frame.empty:
        print(
            "No strategy texts found. Add files to data/national_strategies/ "
            "or run:  python -m scripts.make_sample_data"
        )
        return 1

    # 3. Model + corpus fit (fit matters only for the TF-IDF fallback) ------- #
    model = load_embedding_model(args.model)
    print(f"Embedding backend: {model.name}")
    corpus = competencies.embedding_texts(ref_df) + chunk_frame["chunk_text"].tolist()
    model.fit(corpus)  # no-op for the transformer backend; fits vocab for TF-IDF

    # 4. Embed + align ------------------------------------------------------- #
    # Cache reference embeddings under the label so we never clobber the WHO .npy.
    ref_embeds = competencies.embed_competencies(
        ref_df, model, save_path=out_dir / f"{label}_reference_embeddings.npy"
    )
    scores_df = alignment.build_alignment_scores(
        chunk_frame, ref_df, ref_embeds, model,
        method=args.aggregation, top_k=args.top_k, top_fraction=args.top_fraction,
    )
    scores_path = out_dir / f"{label}_alignment_scores.csv"
    alignment.save_alignment_scores(scores_df, scores_path)
    print(f"Wrote alignment scores -> {scores_path}")

    # 5. Visualise ----------------------------------------------------------- #
    if not args.no_plots:
        pivot = visualize.to_pivot(
            scores_df, competency_order=ref_df["competency_id"].tolist()
        )
        hm = visualize.plot_heatmap(
            pivot, normalise=args.normalise,
            save_path=out_dir / f"{label}_alignment_heatmap.png",
        )
        print(f"Wrote heatmap -> {hm}")

    print("Done. Reminder: keep --aggregation identical to the WHO run so the "
          "competency matrix and this cross-walk stay on the same footing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
