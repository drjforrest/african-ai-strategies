# Corpus update — 25 September 2026

**Summary:** Two new national AI strategies added to the primary track. The corpus grows from 13 to 15 active countries. All figures regenerated.

---

## New additions

| Country | Source documents | Passages | Notes |
|---|---|---|---|
| **Tanzania** | Tanzania National AI Strategy Framework (Draft v0.6, July 2025) | 172 | Single PDF; genuine national AI strategy |
| **Ethiopia** | Digital Ethiopia 2025 Strategy + Digital Ethiopia 2030 Vision | 495 + 206 (701 total) | Two linked documents concatenated into one text file, consistent with pipeline convention for multi-part strategies; largest entry in corpus |

**Uganda** (also found in inbox: *Digital Transformation Roadmap 2023/2024–2027/2028*) was reviewed and **excluded** from the primary corpus. The document is a broad ICT/digital transformation roadmap, not an AI strategy — it explicitly calls for Uganda to *develop* a National AI Strategy as a future action. Retained in `data/inbox/` for the record. To be noted in the paper.

---

## Updated corpus (primary track)

15 active countries (Algeria, Namibia, Tunisia remain absent — no qualifying text files). 3,362 total passages.

| Rank | Country | Mean alignment | Operationalization breadth | Passages |
|---|---|---|---|---|
| 1 | Côte d'Ivoire | 0.546 | 0.333 | 138 |
| 2 | Senegal | 0.503 | 0.167 | 365 |
| **3** | **Tanzania** *(new)* | **0.494** | **0.667** | **172** |
| 4 | Morocco | 0.490 | 0.167 | 113 |
| 5 | Benin | 0.488 | 0.667 | 138 |
| **6** | **Ethiopia** *(new)* | **0.484** | **0.500** | **701** |
| 7 | South Africa | 0.477 | 0.500 | 214 |
| 8 | Ghana | 0.470 | 0.333 | 251 |
| 9 | Kenya | 0.466 | 0.333 | 220 |
| 10 | Zimbabwe | 0.464 | 0.833 | 180 |
| 11 | African Union | 0.457 | 0.333 | 201 |
| 12 | Nigeria | 0.451 | 0.667 | 200 |
| 13 | Egypt | 0.447 | 0.500 | 207 |
| 14 | Mauritius | 0.446 | 0.167 | 216 |
| 15 | Rwanda | 0.432 | 0.833 | 46 |

---

## WHO alignment scores — full matrix

Scores are `top_frac_mean` cosine similarities (default aggregation, fraction=0.10, floor=3). Range across all cells: 0.384–0.591.

| Country | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | C9 |
|---|---|---|---|---|---|---|---|---|---|
| Côte d'Ivoire | 0.527 | 0.530 | **0.545** | 0.564 | 0.535 | **0.582** | **0.520** | 0.562 | 0.544 |
| Senegal | 0.492 | 0.528 | 0.483 | 0.529 | 0.508 | 0.539 | 0.465 | 0.494 | 0.487 |
| **Tanzania** | 0.513 | 0.503 | 0.455 | 0.523 | 0.487 | 0.536 | 0.439 | 0.521 | 0.469 |
| Morocco | 0.509 | 0.487 | 0.432 | 0.533 | 0.477 | 0.557 | 0.439 | 0.499 | 0.475 |
| Benin | 0.529 | 0.530 | 0.486 | 0.512 | 0.474 | 0.500 | 0.425 | 0.472 | 0.467 |
| **Ethiopia** | 0.520 | 0.472 | 0.471 | **0.567** | 0.420 | **0.591** | 0.416 | 0.407 | 0.492 |
| South Africa | 0.491 | 0.499 | 0.438 | 0.487 | 0.462 | 0.502 | 0.407 | **0.556** | 0.455 |
| Ghana | 0.486 | 0.465 | 0.453 | 0.515 | 0.439 | 0.522 | 0.418 | 0.465 | 0.471 |
| Kenya | 0.490 | 0.501 | 0.442 | 0.484 | 0.432 | 0.491 | 0.425 | 0.475 | 0.458 |
| Zimbabwe | 0.509 | 0.494 | 0.433 | 0.476 | 0.456 | 0.476 | 0.408 | 0.480 | 0.444 |
| African Union | 0.464 | 0.474 | 0.420 | 0.456 | 0.452 | 0.477 | 0.414 | 0.492 | 0.466 |
| Nigeria | 0.473 | 0.476 | 0.391 | 0.473 | 0.443 | 0.458 | 0.413 | 0.523 | 0.410 |
| Egypt | 0.472 | 0.488 | 0.410 | 0.449 | 0.477 | 0.457 | 0.384 | 0.480 | 0.405 |
| Mauritius | 0.434 | 0.467 | 0.452 | 0.448 | 0.404 | 0.475 | 0.445 | 0.429 | 0.461 |
| Rwanda | 0.448 | 0.443 | 0.398 | 0.447 | 0.428 | 0.457 | 0.392 | 0.456 | 0.418 |

C1 Leadership & governance · C2 Investment & operations · C3 Services & applications · C4 Integration & sustainability · C5 Standards & interoperability · C6 Flexible digital infrastructure · C7 Adaptable health workforce · C8 Legislation, ethics & compliance · C9 People-centred approach

---

## Operationalization index

Six execution levers scored bilingually (EN/FR). Breadth = share of levers above-median intensity; focus = mean scaled density.

| Country | Breadth | Focus | Timelines | Budget | Agencies | Regulatory | Monitoring | Implementation |
|---|---|---|---|---|---|---|---|---|
| Rwanda | 0.833 | 0.751 | ✓ | ✓ | ✓ | — | ✓ | ✓ |
| Zimbabwe | 0.833 | 0.369 | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Nigeria | 0.667 | 0.290 | ✓ | ✓ | — | — | ✓ | ✓ |
| **Tanzania** | **0.667** | **0.280** | — | — | ✓ | ✓ | ✓ | ✓ |
| Benin | 0.667 | 0.252 | ✓ | — | ✓ | ✓ | ✓ | — |
| South Africa | 0.500 | 0.304 | ✓ | — | — | ✓ | — | ✓ |
| **Ethiopia** | **0.500** | **0.282** | ✓ | ✓ | ✓ | — | — | — |
| Egypt | 0.500 | 0.270 | ✓ | ✓ | — | ✓ | — | — |
| Ghana | 0.333 | 0.271 | — | — | ✓ | ✓ | — | — |
| Côte d'Ivoire | 0.333 | 0.194 | ✓ | — | — | — | ✓ | — |
| African Union | 0.333 | 0.164 | — | ✓ | — | ✓ | — | — |
| Kenya | 0.333 | 0.139 | — | — | ✓ | — | — | ✓ |
| Morocco | 0.167 | 0.154 | — | — | — | — | — | ✓ |
| Senegal | 0.167 | 0.112 | — | — | — | — | ✓ | — |
| Mauritius | 0.167 | 0.100 | — | ✓ | — | — | — | — |

✓ = lever covered at above-median intensity; — = below median.

---

## Notes on new countries

**Tanzania** enters with a notably strong profile for a draft strategy. Its WHO alignment (0.494, rank 3) places it above Morocco, Benin, and Ethiopia despite the document being a 2025 draft. Operationalization breadth is 0.667 — it addresses regulatory, agencies, monitoring, and implementation levers, though timelines and budget are thin (below median), which is typical of draft documents still under negotiation.

**Ethiopia**'s two documents together produce 701 passages (495 from the 2025 Strategy, 206 from the 2030 Vision) — the largest single-country entry in the corpus by a wide margin (next largest: Senegal at 365). Alignment is solid (0.484, rank 6), with the highest single-cell score in the corpus at C6 (Flexible digital infrastructure, 0.591) and a strong C4 (Integration & sustainability, 0.567), consistent with a strategy that emphasises digital infrastructure and connectivity. Operationalization breadth is 0.500: timelines, budget, and agencies levers are well-covered, but monitoring and implementation signal levers are weaker, which may reflect the 2025 document's focus on vision-setting and the 2030 document's emphasis on long-horizon goals rather than near-term accountability mechanisms. The `top_frac_mean` aggregation scales with passage count so Ethiopia's large corpus does not artificially inflate its scores relative to shorter strategies.

**Quadrant position:** Both new countries sit in the upper-right quadrant (high alignment, high operationalization) relative to corpus medians — a stronger combined profile than the majority of existing strategies.

---

## Figures

All figures regenerated and written to `outputs/`:

| File | Description |
|---|---|
| `heatmaps/alignment_heatmap.png` | Raw scores, all 15 countries × 9 competencies |
| `heatmaps/clustered_heatmap.png` | Hierarchically clustered version |
| `heatmaps/alignment_heatmap_colnorm.png` | Column-normalised (best view for within-competency comparison) |
| `heatmaps/alignment_vs_operationalization.png` | Scatter: mean alignment × operationalization breadth, new countries highlighted |
| `operationalization/operationalization_ranking.png` | Breadth index bar chart |
| `operationalization/operationalization_breakdown.png` | Country × lever profile heatmap |
