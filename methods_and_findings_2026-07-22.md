# African National AI Strategies and Digital-Health Core Competencies

**Methods and findings narrative**
Status: working analysis summary, 22 July 2026. Numbers below were computed on the real corpus in this repository using the multilingual embedding backend; figures referenced live under `outputs/`.

---

## 1. Purpose and framing

This project quantifies the extent to which African national artificial-intelligence (AI) strategies engage the core competencies of digital health, using multilingual natural-language processing (NLP) applied to the full text of national strategy documents. The normative reference is the World Health Organization (WHO) Global Strategy on Digital Health 2020 to 2027, whose nine competency domains are treated as a digital-health core-competency template. Two secondary reference frames are used: the Oxford Insights Government AI Readiness Index (GAIRI), as an external, independently measured indicator of AI readiness, and the African Union (AU) Continental AI Strategy of July 2024, as a continental normative anchor.

The work is deliberately not framed as an independent evaluation of the Oxford index, nor as a general longitudinal study of AI preparedness. Its purpose is to characterise how national strategy environments articulate digital-health and health-informatics competencies, in order to inform later work on regional standards and accreditation.

## 2. Two-paper structure

The analyses are organised into two complementary papers that share one corpus and one pipeline but answer different questions for different readerships.

**Paper 1 (target: BMJ Global Health) — the longitudinal NLP investigation.** This paper asks whether and how African national AI strategies engage health and the components of readiness, and whether strategic rhetoric tracks independently measured capability. Its engine is the multilingual NLP method, the Oxford readiness cross-walk and its longitudinal trajectories, and the rhetoric-versus-readiness analysis. The digital-health competency lens keeps it a global-health paper rather than a governance paper; the Oxford index functions as external context and validation, not as the subject.

**Paper 2 (target: International Journal of Medical Informatics) — the competency and standards paper.** This paper asks the extent to which national and continental AI strategies articulate the digital-health and health-informatics core-competency domains on which regional standards and accreditation would rest, and where the gaps lie. It foregrounds the accreditation-critical WHO domains (standards and interoperability, adaptable health workforce, and legislation, ethics and compliance), uses the AU strategy as a regional-standard prototype, and connects to the workforce competency frameworks (for example IMIA and HELINA) that accreditation certifies.

A methodological thread from the wider research programme runs through both: every measuring instrument has a visibility gradient, and strategy text reveals articulated intent rather than implemented competency or accreditation infrastructure. This distinction is treated as an analytic step, not a limitations footnote.

## 3. Data

**Strategy corpus.** Twelve national AI strategies (Benin, Côte d'Ivoire, Egypt, Ghana, Kenya, Mauritius, Morocco, Nigeria, Rwanda, Senegal, South Africa, Zimbabwe), extracted to plain text. The corpus is multilingual: several strategies (for example Senegal, Morocco, Côte d'Ivoire) are in French. The AU Continental AI Strategy is included as a thirteenth document serving as the regional anchor.

**WHO digital-health competency template.** Nine domains taken near-verbatim from the nine core components of a national digital-health strategy in the WHO Global Strategy on Digital Health: leadership and governance; investment and operations; services and applications for scaling up; integration and sustainability; standards and interoperability; flexible digital infrastructure; adaptable health workforce; legislation, ethics and compliance; and a people-centred approach. Domain descriptions are held in `data/who_strategy/competencies.csv` and are the reviewable heart of the mapping.

**Oxford Government AI Readiness Index.** Public datasets for 2021, 2022, 2023, 2024 and 2025. The 2021 to 2024 editions share one framework (three pillars: Government, Technology Sector, Data and Infrastructure; nine public dimensions), forming a comparable four-year panel. The 2025 edition is a structural break (six pillars, fourteen dimensions, explicit weightings, a new exam question) and is treated as a separate cross-section rather than a fifth time point. Definitions for both eras are catalogued in `data/oxford_readiness_indices/oxford_construct_definitions.csv`; embed-ready dimension definitions mirror the WHO competency schema.

**AU Continental AI Strategy.** The July 2024 continental strategy, organised around five focus areas (harnessing AI's benefits, building AI capabilities, minimising risks, stimulating investment, fostering cooperation) and fifteen action areas, aligned to Agenda 2063 and the Sustainable Development Goals. It is dense on governance, data, ethics and skills, names health as a priority sector, and is notably thin on interoperability (one mention) and silent on accreditation and certification.

## 4. Methods

**Preprocessing and chunking.** Each strategy is cleaned (including repair of the common "AI"-to-"Al" ligature misread) and segmented into overlapping passages of roughly 150 whitespace tokens, dropping very short fragments.

**Multilingual embedding and competency alignment.** Passages and competency descriptions are embedded with the multilingual sentence-transformer `paraphrase-multilingual-MiniLM-L12-v2`, which places English and French text in a shared space. For each country, cosine similarity is computed between every passage and every competency description, producing a passage-by-competency matrix that is aggregated to a single score per competency.

**Aggregation and the score-compression problem.** Aggregation uses `top_frac_mean`, the mean of a strategy's strongest ten percent of passages per competency (floored at three passages). Scaling the passage count with document length removes the length bias that a fixed top-k imposes. Because every strategy is broadly on-topic, raw cosine scores occupy a narrow high band (observed range 0.384 to 0.582, mean 0.472), so all downstream comparisons standardise within competency across countries; absolute cosine magnitudes are not interpreted.

**The reference-agnostic cross-walk.** The same instrument is generalised so the strategy corpus can be scored against any reference framework supplied as a competency-style CSV. This produces the WHO competency matrix, the Oxford readiness cross-walk, and, in future, a workforce competency matrix (IMIA or HELINA) for the accreditation tier, with no change to the code.

**Rhetoric versus readiness, with a circularity guard.** For Paper 1, the text-derived Oxford emphasis (what a strategy says about each Oxford dimension) is joined to the measured Oxford score for the same dimension, both standardised within dimension across countries, and read as four quadrants (talk exceeds walk, walk exceeds talk, aligned-high, aligned-low). A validity guard separates two subsets: the text-proximate dimensions, whose Oxford indicators partly read the strategy itself (Vision and Governance and Ethics), which test reliability; and the independent dimensions built from secondary datasets (infrastructure, data, talent, tech-sector), which are the genuine rhetoric-reality test.

**AU convergence.** For Paper 2, each country's nine-domain WHO competency profile is compared to the AU strategy's profile, after within-domain standardisation, using the Pearson correlation of standardised emphasis. A signed per-domain gap heatmap shows where each country over- or under-emphasises relative to the continental vision, with the accreditation-critical domains flagged.

**Policy operationalisation axis.** The repository also contains a complementary, transparent lexicon-based instrument (`run_operationalization.py`) that scores six bilingual execution levers (timelines, budget, agencies, regulatory, monitoring, implementation). It is orthogonal to the embedding-based alignment and was not re-run in this session; it remains available to both papers as a measure of execution intent.

## 5. Findings

**Corpus and coverage.** The pipeline processed thirteen strategies (twelve national plus the AU), yielding 2,489 passages. Three configured entries with no sourced text (Algeria, Namibia, Tunisia) were skipped, consistent with the documented corpus gaps.

**Competency alignment (WHO).** The alignment matrix confirms the expected compression: raw cosines fall in a narrow high band (0.384 to 0.582), so every strategy appears broadly engaged with the digital-health template and country differences emerge only after standardisation. The AU strategy is included as an anchor row in the heatmap.

**Rhetoric versus readiness (Paper 1).** Comparing text-derived emphasis to the measured 2024 Oxford scores, the circularity guard behaves as theorised. The two text-proximate dimensions show the strongest positive association with rhetoric (Vision r = +0.20; Governance and Ethics r = +0.18), consistent with the pipeline reproducing the human coding of strategy-reading indicators (a reliability result). The seven independent, secondary-data dimensions average r = -0.03, that is, effectively no relationship, with Infrastructure (-0.17), Human Capital (-0.13) and Data Availability (-0.08) negative. The pooled correlation across all country-by-dimension cells is r = 0.02. The substantive reading is that strategic rhetoric tracks the indicators that read strategies but does not track the capability measured by independent data, which is the rhetoric-reality gap shown rather than asserted.

Two cautions attach to this result. First, statistical power is limited: with a small number of countries per dimension, individual correlations have wide confidence intervals and none is significant on its own, so the finding rests on the pattern (text-proximate above independent) rather than any single coefficient. Second, the pattern is directional rather than clean, since two independent dimensions (Maturity r = +0.18; Adaptability r = +0.15) come out positive. Both cautions argue for the pooled and longitudinal views and for enlarging the country set.

**Known data-quality issue in this run.** The rhetoric-versus-readiness join matched eleven of the twelve countries. Côte d'Ivoire was dropped because the pipeline configuration spells it with a diacritic ("Côte d'Ivoire") while the processed Oxford panel uses the ASCII form ("Cote d'Ivoire"), so the inner join missed it. The one-line remedy is to accent-fold the country key on both sides of the join before merging; this was identified but not applied, and the reported rhetoric-versus-readiness numbers therefore reflect eleven countries. The AU convergence analysis is unaffected and uses all twelve.

**AU convergence (Paper 2).** Ranking national strategies by how closely their competency emphasis mirrors the continental vision, Rwanda is most convergent (profile r = +0.57), followed by Côte d'Ivoire (+0.43) and South Africa (+0.38), then Mauritius (+0.21) and Nigeria (+0.20). Egypt sits near neutral (+0.05). The most divergent are Benin (-0.60), Kenya (-0.28), Zimbabwe (-0.28), Morocco (-0.22), Ghana (-0.22) and Senegal (-0.16). Rwanda's position is consistent with its strong showing on execution intent and its steep Government-pillar trajectory in the readiness panel, so a coherent thread of Rwanda leading on both alignment and execution emerges across the analyses.

**Longitudinal readiness context.** Across the comparable 2021 to 2024 Oxford panel, the twelve countries move enough to carry real signal. The Government pillar in particular rises steeply for Rwanda (44 to 71), Senegal (a jump after 2022 to 60) and Benin (35 to 61), each broadly coincident with national strategy publication, while Zimbabwe and Morocco remain flat. These trajectories are descriptive and motivate a formal convergence analysis (see next steps).

## 6. Data provenance and comparability

Oxford scores are min-max normalised within each edition against that year's cohort, which grows over time, so cross-year comparisons of raw levels conflate real change with cohort and indicator changes; ranks or within-year standardised scores are preferred. Missing values are handled by peer-group mean imputation, and the public files carry final scores only, without imputation flags, so measured-versus-imputed status cannot be audited from them alone; indicator-level detail is available only for 2023 in the current data. Certain Oxford indicators (notably the national AI strategy and national ethics framework indicators) are scored by reading strategy documents, which is the basis for the circularity guard: validating text-derived emphasis against those indicators is method agreement, not independent validation.

## 7. Limitations

The alignment score reflects textual engagement with a competency template, not real-world implementation. The competency descriptions strongly shape the mapping and should be treated as a reviewable artefact. The country set is small, limiting statistical power. The corpus is a single snapshot per country and is deliberately non-exhaustive for large systems; three configured countries lack sourced text. The Côte d'Ivoire join issue noted above affects the rhetoric-versus-readiness counts in this run. Finally, the WHO domains are system-level digital-health competencies; the individual and workforce competencies that accreditation certifies are a distinct tier addressed only by the planned IMIA or HELINA reference.

## 8. Reproducibility

Environment: Python 3.12 virtual environment created with `uv`; key packages include `sentence-transformers`, `torch`, `pandas`, `scikit-learn` and `matplotlib`. The embedding model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; if `sentence-transformers` is unavailable the pipeline falls back to a lexical TF-IDF backend whose scores are not comparable to the transformer backend.

Run order (from the repository root, with the AU wired into `config.COUNTRY_FILES`):

```
python run_pipeline.py                                  # WHO competency matrix + heatmaps (incl. AU anchor)
python run_reference_alignment.py \
    --reference data/oxford_readiness_indices/oxford_dimensions_2021_2024_embed.csv \
    --label oxford_dimensions_2021_2024_embed           # text-derived Oxford emphasis
python analyze_rhetoric_vs_readiness.py                 # Paper 1: quadrant + circularity split (default year 2024)
python analyze_au_convergence.py                        # Paper 2: convergence to the continental vision
```

Keep the aggregation method identical across the WHO run and the Oxford cross-walk so the two matrices remain comparable.

## 9. Outputs and file map

- `outputs/alignment_scores.csv`, `outputs/heatmaps/` — WHO competency matrix and heatmaps.
- `outputs/reference_alignment/oxford_dimensions_2021_2024_embed/` — text-derived Oxford emphasis matrix and heatmap.
- `outputs/rhetoric_vs_readiness/` — quadrant, per-dimension correlation figure, and tidy join table.
- `outputs/au_convergence/` — convergence ranking, bar chart, and signed-gap heatmap.
- `data/oxford_readiness_indices/processed/oxford_panel_2021_2024_tidy.csv` — the comparable readiness panel.
- `data/oxford_readiness_indices/oxford_construct_definitions.csv` — full construct definitions for both Oxford framework eras.
- Drivers: `run_pipeline.py`, `run_reference_alignment.py`, `analyze_rhetoric_vs_readiness.py`, `analyze_au_convergence.py`, `scripts/plot_oxford_trajectories.py`.

## 10. Next steps

1. Apply the accent-fold fix to the rhetoric-versus-readiness join and re-run, restoring the full twelve-country set.
2. Build the sigma and beta convergence analysis of the measured Oxford scores across 2021 to 2024, the remaining longitudinal component of Paper 1.
3. Assemble an IMIA or HELINA workforce competency reference (for example the IMIA-derived template used by Were and colleagues) and run it through the reference-agnostic instrument to reach the accreditation tier for Paper 2.
4. Enlarge the country set and source the missing strategies (Algeria, Tunisia), and enumerate large systems more fully.
5. Add a small human validation of the competency mapping on a sample of high-scoring passages, and report robustness across aggregation methods and a second embedding model.
