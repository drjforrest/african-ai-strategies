# African AI strategies × WHO digital-health competencies

Quantitatively maps African national **AI strategies** onto the competency
domains of the **WHO Global Strategy on Digital Health** (2020–2027), using
multilingual sentence-transformer embeddings, and visualises the result as
heatmaps.

For each country, the strategy text is chunked into passages, every passage is
embedded and compared (cosine similarity) against each WHO competency-domain
description, and the passage scores are aggregated into one score per
(country, competency). The output is a country × competency alignment matrix.

> **What the score means.** It measures how strongly a document *engages with the
> WHO digital-health competencies in text* — not a country's real-world
> digital-health capability, and not AI-strategy quality in general. A horizontal
> AI policy that barely mentions health will score low even for a country that
> leads in digital health in practice (see *Two analysis tracks* below).

---

## Two analysis tracks

The corpus contains two genres of document, analysed separately so they stay
comparable:

| Track | Corpus | What it answers |
|---|---|---|
| **Primary** | National **AI strategies** (`data/national_strategies/`) | How much does each country's AI strategy engage digital health? |
| **Secondary** | Dedicated **digital-health / eHealth strategies** (`data/digital_health_strategies/`) | How well do purpose-built digital-health strategies align with the WHO framework? |

A digital-health document aligns with WHO *digital-health* competencies almost by
construction, so mixing the two genres breaks comparability. Keeping them
separate is what makes each track interpretable. **Rwanda is the canonical
example:** its horizontal *National AI Policy* ranks last in the primary track
(0.43 — it barely mentions health), while its dedicated *Digital Health Strategy*
scores 0.61 in the secondary track. Same country, two documents, two correct
answers.

---

## Quickstart

```bash
# Environment (this repo was developed with uv; plain venv works too)
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt      # or: pip install -r requirements.txt

# 1. Extract text from source PDFs into the .txt files the pipeline reads.
python -m scripts.extract_pdfs          # national + WHO reference
                                        # (also caches <country>_dh.txt for secondary)

# 2. Primary track: national AI strategies -> scores + heatmaps.
python run_pipeline.py

# 3. Secondary track: digital-health strategies -> outputs/secondary/.
python run_secondary.py
```

No source PDFs yet? `python -m scripts.make_sample_data` writes synthetic
strategy texts so the pipeline runs end-to-end (it never overwrites real files).

### Outputs

Primary (`outputs/`):
- `alignment_scores.csv` — long form: `country, competency_id, similarity_score`
- `strategy_chunks.csv` — every chunk fed to the model (traceability)
- `heatmaps/alignment_heatmap.png`, `heatmaps/clustered_heatmap.png`

Secondary (`outputs/secondary/`):
- `alignment_scores.csv`, `heatmaps/secondary_heatmap.png`

### Primary-track CLI options

```bash
python run_pipeline.py --aggregation max      # mean | max | top_k_mean | top_frac_mean (default)
python run_pipeline.py --top-fraction 0.15    # fraction of chunks for top_frac_mean
python run_pipeline.py --top-k 3              # k for the fixed-k top_k_mean
python run_pipeline.py --normalise global     # rescale heatmap colours: global|row|column
python run_pipeline.py --no-plots             # scores only
```

Raw semantic scores compress into a high band (~0.4–0.65 — every AI-strategy
document is broadly on-topic), so `--normalise column` is usually the more
readable view for comparing countries within a domain.

---

## The WHO competency domains

`data/who_strategy/competencies.csv` holds **9 domains** taken (near-verbatim)
from the **nine core components of a national digital health strategy** that WHO
enumerates in Strategic Objective 2 of the 2020–2027 global strategy:

| ID | Domain |
|----|--------|
| C1 | Leadership & governance |
| C2 | Investment & operations |
| C3 | Services & applications for scaling up |
| C4 | Integration & sustainability |
| C5 | Standards & interoperability |
| C6 | Flexible digital infrastructure |
| C7 | Adaptable health workforce |
| C8 | Legislation, ethics & compliance |
| C9 | People-centred approach |

The descriptions are the tunable, reviewable heart of the analysis — edit them to
sharpen the mapping. Source text: WHO Global Strategy on Digital Health 2020–2027
(© WHO 2025, CC BY-NC-SA 3.0 IGO); the reference text is cached at
`data/who_strategy/who_gsdh.txt`.

> The 2025 document is titled *"Global strategy on digital health 2020–2027"* — an
> **extension** of the 2020–2025 strategy, not a new framework (≈88% identical
> text; same four strategic objectives, guiding principles, and framework for
> action). The competency set is therefore valid for both periods.

---

## Providing the source data

### Embedding model & languages

The default model is `paraphrase-multilingual-MiniLM-L12-v2` because the corpus
is **multilingual** — several strategies (Senegal, Morocco, Côte d'Ivoire) are in
French. The multilingual model embeds English and French into a shared space, so
French documents score in the same band as English ones. For an English-only
corpus, switch `MODEL_NAME` in `src/config.py` to `all-MiniLM-L6-v2` (smaller,
faster). If `sentence-transformers` is unavailable, the pipeline falls back to a
deterministic **TF-IDF** backend so it still runs — but TF-IDF is lexical and
does not cross languages; results from the two backends are not comparable.

### PDF extraction

`scripts/extract_pdfs.py` converts source PDFs to the `.txt` files the pipeline
reads, matching each PDF to a country by filename (with `FILENAME_OVERRIDES` for
PDFs whose name lacks the country, and accent-folding for French titles). When
**multiple PDFs map to one country they are concatenated** into that country's
single text file.

```bash
python -m scripts.extract_pdfs --list     # show the PDF -> country mapping only
python -m scripts.extract_pdfs            # extract what is missing
python -m scripts.extract_pdfs --force    # re-extract everything
```

Watch for two data-quality traps this project hit:
- **Wrong genre.** A general health policy or an eHealth strategy is *not* an AI
  strategy. Algeria's only file was a 2015 health policy — it was moved to
  `data/_rejected/`. Digital-health/eHealth strategies belong in the **secondary**
  corpus, not the primary one.
- **Scanned PDFs.** If extraction yields only a few hundred words, the PDF is
  image-based and needs OCR (e.g. `ocrmypdf`) before it is usable.

---

## Project layout

```
african-ai-policy/
├── data/
│   ├── who_strategy/            competencies.csv (9 domains) · who_gsdh.txt · WHO PDFs
│   ├── national_strategies/     <country>_ai.txt + source AI-strategy PDFs   (PRIMARY)
│   ├── digital_health_strategies/ <country>_dh.txt + DH/eHealth PDFs         (SECONDARY)
│   └── _rejected/               wrong-genre PDFs kept for the record
├── src/
│   ├── config.py         paths, model name, chunk/aggregation params, country map
│   ├── preprocess.py     load_text, clean_text, chunk_text
│   ├── models.py         embedding backends (multilingual ST | TF-IDF fallback)
│   ├── competencies.py   load + embed WHO domains
│   ├── alignment.py      chunk embeddings, cosine similarity, aggregation
│   ├── operationalization.py  differentiating axis 1: execution-lever index
│   └── visualize.py      heatmap + clustered heatmap
├── scripts/
│   ├── extract_pdfs.py       PDF -> text (country matching + concatenation)
│   └── make_sample_data.py   synthetic strategies for smoke-testing
├── notebooks/            01 explore competencies · 02 build alignment matrix
├── tests/test_pipeline.py
├── run_pipeline.py       PRIMARY driver (national AI strategies)
├── run_secondary.py      SECONDARY driver (digital-health strategies)
├── run_operationalization.py  differentiating axis 1 driver
└── outputs/              scores, embeddings, heatmaps ( + secondary/ + operationalization/ )
```

---

## Data coverage (current)

**Primary — 12 national AI strategies:** Benin, Côte d'Ivoire, Egypt, Ghana,
Kenya, Mauritius, Morocco, Nigeria, Rwanda, Senegal, South Africa, Zimbabwe.
**Missing:** Algeria (no published national AI strategy located — the file on
hand was a health policy), Tunisia (document not yet sourced).

**Secondary — 3 digital-health strategies:** Rwanda, Namibia, Mauritius.

---

## Aggregation methods

How per-chunk similarities collapse to one score per competency
(`AGGREGATION_METHOD` in `config.py`):

- **`mean`** — average over all chunks. Dilutes coverage.
- **`max`** — single strongest passage. Noise-sensitive.
- **`top_k_mean`** *(k=5)* — mean of the k best-matching passages. Rewards
  sustained coverage, **but a fixed k has a length bias**: "best 5 of 365 chunks"
  beats "best 5 of 46", so short strategies (e.g. Rwanda) were dragged down
  across *every* competency. Chunk count correlated with mean score at r≈0.55.
- **`top_frac_mean`** *(default, fraction=0.10, floor=3)* — mean of a strategy's
  strongest 10% of passages. Scaling the passage count with document length
  removes that bias (r≈0.55 → 0.14) while keeping the "best-passages" logic. This
  is the default; use `--top-fraction` / `--top-k` to override.

> **Extraction note.** PDF text extraction frequently misreads the "AI" ligature
> as "Al" (capital-I → lowercase-l), corrupting the corpus's most important
> token. `preprocess.clean_text` repairs standalone "Al" → "AI" while preserving
> genuine "al-" proper names (e.g. "Al Jazari", "Al-Azhar").

---

## Differentiating axes (beyond WHO alignment)

The WHO-competency alignment measures *rhetorical* similarity, and every AI
strategy shares the digital-policy register — so scores compress into a narrow
band and the heatmap mostly shows "everyone is broadly aligned." To separate
countries we add **differentiating axes** measured with transparent, auditable
lexicon detectors (not embeddings), each length-normalised and reported as a
within-sample index.

**Axis 1 — Policy operationalization** (`src/operationalization.py`):

```bash
python run_operationalization.py
```

Six execution levers are detected bilingually (EN + FR, so francophone
strategies aren't under-counted): **timelines, budget, agencies, regulatory,
monitoring, implementation**. Two complementary indices are produced:

- **`operationalization_index`** *(primary — breadth)*: the share of the six
  levers a strategy addresses at above-median intensity. Length-robust; neither
  rewards a terse implementation matrix for brevity nor a long strategy for bulk.
- **`focus_index`** *(secondary — execution focus)*: mean of the min-max scaled
  densities — how execution-dense the prose is.

Outputs land in `outputs/operationalization/`: the index CSV (raw counts,
densities, per-lever coverage, both composite indices), a breadth ranking bar,
and a country × lever profile heatmap. This axis is orthogonal to WHO alignment
— e.g. Rwanda's AI Policy is health-light yet highly operational (a detailed
fiscal-year implementation matrix), while several high-alignment strategies are
vision-heavy and thin on execution.

---

## Tests

```bash
python -m pytest
```

Covers chunking, the "AI"-ligature repair, similarity/aggregation logic
(including the length-robust `top_frac_mean`), the operationalization index
(bilingual detection, bounds), the TF-IDF backend, and one small end-to-end pass
— no heavy model or real data required.

---

## Interpreting results — caveats

- The score reflects **textual engagement** with digital-health competencies, not
  real-world implementation. Keep the primary and secondary tracks separate.
- Absolute cosine values are only meaningful **relative to each other** within one
  run and backend. Compare rows and columns, not raw magnitudes; use
  `--normalise` for readability.
- Competency descriptions strongly shape the mapping — treat `competencies.csv`
  as a reviewable artefact, not ground truth.
- Concatenating documents of different genres for one country (as done for
  Mauritius earlier) inflates its scores; the two-track split is the cleaner
  alternative.
