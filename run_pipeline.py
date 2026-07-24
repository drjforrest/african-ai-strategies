"""End-to-end driver: competencies + strategies -> alignment scores + heatmaps.

    python run_pipeline.py                       # full run, defaults from config
    python run_pipeline.py --aggregation max     # override aggregation
    python run_pipeline.py --normalise global    # rescale heatmap colours
    python run_pipeline.py --no-plots            # scores only

The run degrades gracefully: any country lacking a text file in
data/national_strategies/ is skipped with a warning, and the rest still
process. Run ``python -m scripts.make_sample_data`` first if you have no real
strategy texts yet.
"""

from __future__ import annotations

import argparse

from src import alignment, competencies, config, visualize
from src.models import load_embedding_model


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default=config.MODEL_NAME, help="sentence-transformers model name")
    p.add_argument(
        "--aggregation",
        default=config.AGGREGATION_METHOD,
        choices=["mean", "max", "top_k_mean", "top_frac_mean"],
        help="chunk->country aggregation",
    )
    p.add_argument("--top-k", type=int, default=config.TOP_K, help="k for top_k_mean")
    p.add_argument(
        "--top-fraction", type=float, default=config.TOP_FRACTION,
        help="fraction of chunks for top_frac_mean (floored at config.TOP_FRAC_FLOOR)",
    )
    p.add_argument(
        "--normalise",
        default=None,
        choices=["global", "row", "column"],
        help="optional heatmap colour rescaling (default: raw cosine)",
    )
    p.add_argument("--no-plots", action="store_true", help="skip heatmap generation")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    config.ensure_dirs()

    # 1. Competencies ------------------------------------------------------- #
    comp_df = competencies.load_competencies()
    print(f"Loaded {len(comp_df)} WHO competency domains.")

    # 2. Strategy chunks ---------------------------------------------------- #
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

    chunk_frame.to_csv(config.CHUNK_METADATA_CSV, index=False)

    # 3. Model + corpus fit ------------------------------------------------- #
    model = load_embedding_model(args.model)
    print(f"Embedding backend: {model.name}")
    corpus = competencies.embedding_texts(comp_df) + chunk_frame["chunk_text"].tolist()
    model.fit(corpus)  # no-op for transformer backend; fits vocab for TF-IDF

    # 4. Embed + align ------------------------------------------------------ #
    comp_embeds = competencies.embed_competencies(comp_df, model)
    scores_df = alignment.build_alignment_scores(
        chunk_frame, comp_df, comp_embeds, model,
        method=args.aggregation, top_k=args.top_k, top_fraction=args.top_fraction,
    )
    out = alignment.save_alignment_scores(scores_df)
    print(f"Wrote alignment scores -> {out}")

    # 5. Visualise ---------------------------------------------------------- #
    if not args.no_plots:
        pivot = visualize.to_pivot(
            scores_df, competency_order=comp_df["competency_id"].tolist()
        )
        hm = visualize.plot_heatmap(
            pivot, normalise=args.normalise,
            save_path=config.HEATMAP_DIR / "alignment_heatmap.png",
        )
        print(f"Wrote heatmap -> {hm}")
        cm = visualize.plot_clustered_heatmap(
            pivot, normalise=args.normalise,
            save_path=config.HEATMAP_DIR / "clustered_heatmap.png",
        )
        if cm:
            print(f"Wrote clustered heatmap -> {cm}")
        else:
            print("  ! Skipped clustered heatmap (need >=2 countries and competencies).")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
