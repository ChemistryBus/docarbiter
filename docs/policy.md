# Routing strategy evaluation (P0–P3)

> Corpus: 22 documents with independent answer keys (11 synthetic + 5 edge + BERT + 4 real CC BY-SA).
> Metrics: CER (character error rate), success rate, total runtime. **Real workspace PDFs without an answer key are not counted in CER.**
> Details: `benchmarks/private/policy.md` / `policy.json` (gitignored).

## P0: fixed tools vs routing vs oracle

| Strategy | n | Success | Median CER | Worst CER | Total runtime |
|---|---:|---:|---:|---:|---:|
| Fixed pdftotext | 22 | 86.4% | 0.0000 | 0.7810 | 0.80s |
| Fixed liteparse | 22 | 86.4% | 0.0073 | 0.9048 | 3.93s |
| Fixed markitdown | 22 | 86.4% | 0.0000 | 7.8911 | 20.04s |
| Fixed pdfplumber | 13 | 92.3% | 0.0005 | 7.8911 | 0.66s |
| Fixed MinerU | 22 | **100%** | 0.0115 | 0.2952 | 61.98s |
| Fixed Docling | 22 | 95.5% | 0.0108 | 1.0198 | 219.42s |
| **router:quality** | 22 | **100%** | 0.0079 | **0.2952** | 60.04s |
| **router:speed** | 22 | **100%** | 0.0063 | 0.9048 | **7.06s** |
| **router:text** | 22 | **100%** | **0.0000** | 0.7810 | **4.73s** |
| verify:quality | 22 | 100% | 0.0079 | 0.3478 | 59.31s |
| oracle (theoretical upper bound) | 22 | 100% | 0.0000 | 0.2667 | 47.17s |

### How to read this table

- **Fixed tools are not universal**: pdftotext / liteparse / markitdown all fail on scans/CID, with a success rate of only 86.4%; pdfplumber breaks on CID/two-column; Docling is slow but has a high success rate.
- **router:text**: clean text layers go to pdftotext, scans/CID go to MinerU, simple grid tables go to pdfplumber. **100% success, median CER 0, 4.73s** — **13×** faster than fixed MinerU, with a lower median CER, but its worst page (true vertical writing) is 0.781, worse than MinerU's 0.295.
- **router:speed**: text layers go to liteparse, scans/CID go to MinerU, simple grid tables go to pdfplumber. 100% success, 7.06s, median CER 0.0063; **8.8×** faster than fixed MinerU, with a lower median CER; the worst is still true vertical writing at 0.9048.
- **router:quality**: text layers/scans/CID go to MinerU, simple grid tables go to pdfplumber. 100% success, median 0.0079, worst 0.2952, 60s — essentially on par with fixed MinerU, slightly faster.
- **oracle**: picks the tool with the lowest CER for each document; this is the theoretical upper bound. Routing cannot exceed oracle; the gap comes mainly from true vertical writing and a few tool choices.

### Conclusion

1. **Efficiency**: it can be improved, and the data is clear. `router:text` 4.73s vs fixed MinerU 61.98s; `router:speed` 7.06s.
2. **Accuracy**:
   - On a **mixed corpus**, routing can achieve 100% success with a median CER no worse than the strongest fixed tool; `router:text` has a median CER of 0, better than fixed MinerU's 0.0115.
   - But it **cannot exceed oracle**, nor can it guarantee beating the strongest single tool on every document; the worst page (true vertical writing) is still worse under routing.
   - The accuracy gain comes from "not choosing the wrong tool" and "switching tools on failure", not from a stronger algorithm.
3. **What not to claim**: do not say "more accurate than MinerU"; the correct claim is "on a mixed corpus it has a higher success rate, is faster, and has a median CER that is no worse; the worst page is still bounded by the tools' limits".

> `table` in P0 is the **simple grid fast path** (pdfplumber), kept so results remain comparable with the existing 22-document run. Real complex tables use the separate `table-structure` route (Docling), see P2; do not compare the two together.

## P1: verify mode (negative result)

The current `verify:quality` uses only runtime-visible signals (status / chars_pred / ctrl_ratio) to decide whether to switch tools:

- median CER 0.0079, no improvement;
- worst 0.3478, worse than `router:quality`'s 0.2952;
- on `zh-vertical-sim` it switches from MinerU 0.1304 to liteparse 0.3478, which is a **wrong switch**.

Conclusion: **the current verify heuristic is not acceptable and is not released.** A useful verify needs output-level comparison (bag of characters/bigrams/coverage) and better switching signals, not just character counts/control characters.

## P2: real high-frequency tables (no composition; partitioned routing instead)

On 2026-11-10 we ran supplementary tests with real high-frequency tables from this machine (read-only, not uploaded, no body text saved):

| Real document (page) | Expected structure | pdfplumber `lines` | pdfplumber `text` | MinerU | Docling |
|---|---|---|---|---|---|
| WS/T 578.1—2017 p8 | 22 data rows × 13 columns, 3-level header (25 rows including the 3 header rows) | 27×13; header spans correct; 2 note rows trimmed | 26×13 after dropping empty rows; broken | 27×13; `rowspan/colspan` correct; 2 note rows trimmed | 25×13; header expanded correctly |
| GB 28050—2025 p6 | 28 data rows × 4 columns, multi-line cells | 29×4; cells out of order | 72×6 after dropping empty rows; broken | 29×4; 6 multi-line cells interleaved | 29×4; exact after normalization |
| DRIs 2023 p65 | 2 symbol tables: 15×6, 14×6 | 0 tables | 69×9; unusable | 15×6 + 14×6; Chinese names correct, ●/○ become "empty/O" | Names wrong (no-OCR); with OCR on, names correct, ●→`.`, ○→`O` |
| GB 2760—2024 p13 | 26 data rows × 4 columns | 27×4; spot-check correct | 84×3; broken | 27×4; characters interleaved in 4 multi-line cells | 27×4; spot-check correct |
| China Food Composition Tables, 6th ed., Vol. 1, p246 | 65 entries, two-column book table | 0 tables | 45×4; unusable | 6 columns; 65 entries; first 3 rows misaligned | With OCR on, 7 columns, most rows correct; bottom 3 rows misaligned; no-OCR unusable |

Per-cell CER (2026-11-11, hand-checked truth; two pages only): WS/T p8 — pdfplumber default / Docling / MinerU all 0.0000 micro CER after normalization; GB 28050 p6 — Docling 0.0000, MinerU 0.1237, pdfplumber default 0.3010, pdfplumber text 0.9916. Truth was drafted from Docling and hand-checked, so Docling's 0.0000 is a ceiling check; the pdfplumber/MinerU figures are independent. Details: `docs/benchmarks.md` section 5-12.

Conclusion:

1. **Complex merged headers/multi-line cells → Docling.** WS/T 578.1, GB 28050, and GB 2760 have the best structure and reading order; per-cell CER on GB 28050 p6 confirms it (Docling 0.0000 vs MinerU 0.1237 vs pdfplumber 0.3010), and WS/T p8 is a clean grid where all three match exactly. This is the current default quality path for real tables (`--goal table-structure`).
2. **Bad text layers/symbol tables/scans → MinerU.** The DRIs 2023 page 65 text layer itself turns ● into `.` and ○ into `。`; MinerU recovers the Chinese names and distinguishes ●/○ as "empty/O", but **does not preserve the original symbols**, so spot-checking is mandatory.
3. **pdfplumber is only for simple grids/coordinates.** It is fast (single page <0.5s), but multi-line cells in real book tables/standards tables come out scrambled; the `text` strategy rescues borderless tables but inflates 29×4 into 76×6 raw (72×6 after dropping empty rows).
4. **composition has no supporting evidence; do not do it.** No single real table showed "MinerU drops structure + pdfplumber has good cells"; Docling already provides both structure and readable cells. Adding another composition layer only adds complexity and new failure points.
5. **Dense two-column book tables are still not guaranteed.** On the 65-entry two-column table on p246 of the China Food Composition Tables, both Docling OCR and MinerU show row misalignment at the top/bottom of the page; such tables must be manually spot-checked, and "the whole table is accurate" cannot be claimed.
6. **Routing is file-level, not page-level.** `route.py` only looks at the first 3 pages; for DRIs 2023 the first 3 pages have a usable text layer, but the page 65 symbol table's text layer is bad. For books/standards, first locate the target page, then use `pdftotext -f PAGE -l PAGE` or pdfplumber as a page-level probe.

## P2b: real two-column full-text CER (2026-11-11)

Three papers with independent truth:

- BERT, NAACL 2019 (arXiv:1810.04805) → ar5iv HTML.
- Cell 2020 MoTrPAC Perspective (PMC8800485) → PMC JATS XML.
- ResNet, CVPR 2016 (arXiv:1512.03385) → ar5iv HTML.

Scope: abstract plus main body, excluding references, figure/table content and captions, and appendices. A row is valid only with `start+end` alignment and coverage 0.5–1.5.

| Paper | pdftotext | liteparse | Docling | MinerU |
|---|---:|---:|---:|---:|
| BERT | 0.2108 | 0.1398 | **0.0656** | 0.0773 |
| Cell | **0.0349** | — (alignment failed) | 0.1099 | 0.0953 |
| ResNet | 0.4212 | 0.2287 | 0.1537 | **0.1214** |

Values are `nopunct` CER; coverage and text-CER are in `docs/benchmarks.md` section 5-13.

- **BERT and ResNet are the cleaner comparisons.** Docling/MinerU are consistently the top two, but which one wins varies: Docling on BERT, MinerU on ResNet. liteparse is third and pdftotext last. `pdftotext -layout` is invalid on two-column because it preserves physical order.
- **Cell has a scope caveat.** pdftotext is lowest, but Docling/MinerU coverage is 1.08–1.10 because this Perspective has text inside its figures, which the truth excludes. Their CER includes extra figure text, so the ranking is not directly comparable. Do not read this as "pdftotext always wins".
- **Nature 2024 MoTrPAC (PMC11062907) was downloaded and tested but is not in the table.** The 35-page flagship includes Methods/Extended Data and figure legends; the main-body truth scope is too narrow, so all tools fail alignment (coverage 2.3–2.6). It needs a full-article scope.
- Three papers only; full-text CER is sensitive to figure text, headers/footers, and caption stripping. Do not generalise.

Runtime (this machine, M2 Pro, models warm): pdfplumber <0.5s per page; MinerU about 2.5s per page; Docling about 3–5s/page with no-OCR, about 10–12s/page with OCR.

## P3: recommended defaults

| User goal | Default strategy | Rationale |
|---|---|---|
| Only accurate body/citation text needed | **router:text** | 100% success, median CER 0, 4.73s; scans/CID automatically go to MinerU |
| Finished manuscript/heading/paragraph structure needed | **router:quality** | 100% success, worst 0.2952, 60s; close to MinerU, better tables |
| Quick browsing/retrieval | **router:speed** | 100% success, 7.06s; median 0.0063, but worst on true vertical writing |
| True vertical writing | **manual** | All tools are poor; even oracle is only 0.2667 |
| Simple bordered grids / CSV or coordinates needed | **pdfplumber** | <0.5s per page; merged headers/multi-line cells come out scrambled |
| Complex tables: merged headers / multi-line cells / book tables | **docling** (`--goal table-structure`) | Measured: best structure on WS/T, GB 28050, GB 2760; 3–5s/page, OCR 10–12s/page |
| Scans / bad text layers / symbol tables | **mineru** | OCR + tables; symbols do not retain original glyphs, must spot-check |
| Chinese borderless tables | pdfplumber `text` strategy + manual spot-check | Docling measured 0 tables; the text strategy damages merged cells |
| verify | **off** | P1 negative result; switching signals are not reliable enough |

**One-line positioning**:

> This project is not "more accurate than every extractor"; it is "on mixed documents, make the right tool do the work, avoid the catastrophic failure of a single fixed tool, and bring the speed up".

### Boundaries we can state publicly

- Can state: on a mixed corpus, success rate, speed, and median CER are better than a fixed single tool (with environment/version/corpus).
- Can state: on the 5 tested real high-frequency tables, Docling has the best structure and reading order for complex merged headers; MinerU is best for bad text layers/symbol tables; pdfplumber is fastest for simple grids.
- Cannot state: every document beats the strongest single tool; all tables are accurate; true vertical writing/arbitrary borderless tables are guaranteed accurate; symbol tables preserve original glyphs; "accuracy" on real PDFs without an answer key.
- Real workspace PDFs have no independent answer key, so we can only report coverage / bag / consistency, not accuracy.
