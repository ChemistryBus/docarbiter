# Chinese document extraction benchmark: method and corpus

> This document defines "how to measure"; it does not publish scores that have not been re-tested.
> Every score must be accompanied by: machine, OS, tool versions, corpus version, and normalization rules.

## 1. Three principles

1. **The answer must be an independent source, not another tool's output.**
   Using `pdftotext` as the ground truth only tests "which tool is more like pdftotext".
2. **Use CER for Chinese, not word-level similarity.**
   Chinese has no spaces; token/word-level metrics hide missing characters, wrong characters, and out-of-order text.
3. **Report the worst page, not just the average score.**
   A tool averaging 97% may score only 40% on a certain kind of table page; averages lead users into traps.

## 2. Corpus design

### A. Synthetic samples (exact answers, public, reproducible)

Generated with `reportlab` + Source Han Sans/Serif; the source text is written to `.txt` as the answer.

| Sample | Construction | Failure mode to expose |
|---|---|---|
| `zh-text-layer.pdf` | Normal Chinese body text + mixed Chinese/English + numbers + full-width punctuation | Basic correctness, punctuation, mixed script |
| `zh-cid-no-tounicode.pdf` | Embed a subset font and remove the ToUnicode mapping | Garbled text, blanks, replacement characters |
| `zh-two-column.pdf` | Two-column academic layout + header/footer | Column interleaving, reading order |
| `zh-table.pdf` | Merged cells, no borders, header spanning columns | Table structure, cell misalignment |
| `zh-scan.pdf` | Text rendered as an image and wrapped into a PDF | OCR model, resolution, confidence |
| `zh-traditional.pdf` | Traditional characters + variant characters | Character set coverage |
| `zh-vertical.pdf` | Vertical layout + right-to-left | Reading order (optional, v0.2) |
| `zh-footnote.pdf` | Footnotes, margin notes, figure captions | Reading order, paragraph merging |

English counterparts (same categories, different failure modes):

| Sample | Construction | Failure mode to expose |
|---|---|---|
| `en-text-layer.pdf` | Normal English body text + numbers + quotes/dashes | Basic correctness, punctuation normalization |
| `en-two-column.pdf` | Two columns + header/footer | Column interleaving, reading order |
| `en-table.pdf` | Bordered / borderless tables | Table structure, cell misalignment |
| `en-scan.pdf` | Text rendered as an image and wrapped into a PDF | OCR model, resolution |
| `en-hyphenation.pdf` | End-of-line hyphenation (`docu-\nment`) | dehyphenation, inflated CER |
| `en-footnote.pdf` | Footnotes, margin notes, figure captions | Reading order, paragraph merging |

> The current demo only generates 1 page each of `demo-zh.pdf` / `demo-en.pdf`; the table above is the complete set to fill in before release.

### B. Real samples (clean license, obtainable answers)

| Source | License | Answer | Use |
|---|---|---|---|
| Chinese Wikipedia article → rendered PDF | CC BY-SA 4.0 | article plain text | Real long text, two-column/single-column, internal links and tables |
| English Wikipedia article → rendered PDF | CC BY-SA 4.0 | article plain text | English two-column/tables, hyphenation, quotes |
| Public-domain Chinese classics on Wikisource → rendered PDF | Public domain | proofread text | Traditional characters, vertical layout, variant characters |
| Open-access Chinese papers (CC BY) | Per the original | publisher HTML/XML full text | Real academic layout, formulas, tables |

> The rendering pipeline itself must be version-pinned and recorded, otherwise "the PDF changed" makes scores unreproducible.

### C. Private samples (run locally only)

Users put their own PDFs in `benchmarks/private/`, excluded by `.gitignore`. `bench.py` only writes reports locally; it does not upload or write public scores.

## 3. Metrics

### 1. CER (character error rate)

```
CER = (S + D + I) / N
```

- `S` substitutions, `D` deletions, `I` insertions; `N` is the number of characters in the answer.
- Edit distance is computed over Unicode code points; Chinese punctuation counts as an independent character.
- Report both **raw CER** and **normalized CER**.

### 2. Normalization (hard-coded in `bench.py`)

- Unicode **NFC** (no NFKC; full-width/half-width differences are preserved).
- English end-of-line hyphenation (`docu-\nment`) is merged into `document`; Chinese is unaffected.
- Remove all whitespace characters (spaces, newlines, tabs).
- Punctuation is preserved; an "ignore punctuation" variant is reported separately.
- No traditional/simplified conversion; mixed traditional/simplified samples are reported separately.

### 3. Per-category metrics

| Metric | Description |
|---|---|
| Han character CER | Counts only CJK unified ideographs |
| Punctuation CER | Full-width/half-width punctuation counted separately |
| Digit/English CER | Mixed-script scenarios |
| Reading order | Block-order accuracy on two-column samples (manually labeled block IDs) |
| Table cell accuracy | Cell text + row/column position; merged cells listed separately |
| Speed | Seconds/page; cold start listed on its own line |
| OCR confidence | Tool-reported mean; reference only, not accuracy |

### 4. Aggregation

Each tool outputs:

- one row per page: `page, chars, cer, substitutions, deletions, insertions, seconds`
- per-document summary: `median CER`, `IQR`, `worst_page`, `worst_page_cer`
- cross-document summary: grouped by sample type, not merged into a single total score

## 4. Report format

`bench.py` outputs:

```
benchmarks/results/<timestamp>/
├── environment.json      # OS, CPU, memory, Python, tool versions
├── per_document.csv      # per-document/tool metrics (page structure is checked separately)
├── summary.md            # human-readable: grouped median/IQR/worst
└── raw/                  # raw output from each tool (optional, --keep-raw)
```

The top of `summary.md` must state:

> These results come from `<machine>` / `<os>` / `<tool versions>` / `<corpus commit>`.
> Changing the machine, version, or files changes them. Run `bench.py` on your own files.

## 5. Reference values (English samples, order-of-magnitude reference only)

Source: 3 pages of Hackney, 3rd edition, on this machine (macOS / M2 Pro). **Do not extrapolate to Chinese.**

| Page type | liteparse | MinerU | Docling |
|---|---|---|---|
| Body text | 0.24 s / 98.3% | 1.58 s / 96.6% | — |
| Table page | 0.09 s / 92.0% | 1.40 s / 91.4% | — |
| Cold start | none | +16 s | — |

Note: the table above is a **historical English reference**; the metric is "order similarity to pdftotext", not CER. A bilingual Chinese/English demo now exists (see below), but the sample size is insufficient to replace this table, so it is kept as a historical reference.

## 5-2. First bilingual Chinese/English demo (1 synthetic page each, 2026-11-09)

Corpus: `benchmarks/fixtures/demo-zh.pdf` and `demo-en.pdf` (generated by `make_demo.py`; the answers are the source text, not pdftotext output).
Machine: macOS 26 / M2 Pro / Python 3.11.11.

| Tool | Version | Chinese time (range of 3 runs) | Chinese CER | English time (range of 3 runs) | English CER | Notes |
|---|---|---:|---:|---:|---:|---|
| pdftotext | Poppler 26.08.0 (at measurement time) | 0.03 s | 0.0000 | 0.04 s | 0.0000 | Baseline; matches the source text |
| liteparse | 2.18.0 | 0.13–0.42 s | 0.0061 | 0.14 s | 0.0079 | Fastest; quotes/dashes normalized to ASCII |
| markitdown | 0.1.9 | 0.98–1.19 s | 0.0061 | 0.90–0.98 s | 0.0185 | Usable for single column; most visible English punctuation normalization |
| mineru | 4.1.7 | 1.0–9.6 s | **0.0046** | 1.0–3.9 s | **0.0013** | Lowest CER in both Chinese and English runs; ranges include cold/warm start |
| docling | 2.149.0 | 9.5–19.3 s | 0.0061 | 9.5–12.2 s | 0.0093 | Slowest; usable for both Chinese and English |

Interpretation:

- This is **two synthetic pages**, not the full picture of the Chinese/English benchmark; do not rank tools based on it.
- The 0.6%–1.9% gap comes mainly from punctuation normalization (`“”` → `""`, `——` → `--`), not character errors; see item 8 in `gotchas.md`.
- MinerU's `raw CER` is high because Markdown markup (`#`, `|`, table separator rows) is counted; `cer_text` strips it. **raw CER values from different output formats are not directly comparable.**
- Runtime is strongly affected by cold/warm start: MinerU across three runs 1.0–9.6 s, Docling 9.5–19.3 s. Before release, report cold start and warm start separately; do not use one number to represent everything.
- The next round should add real CC BY-SA articles, CID/no-ToUnicode, mixed traditional/simplified, and vertical layout, and separate cold from warm start.

Reproduce:

```bash
python3 -I benchmarks/fixtures/make_demo.py
python3 -I scripts/bench.py \
  benchmarks/fixtures/demo-zh.pdf benchmarks/fixtures/demo-en.pdf \
  --tools pdftotext,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-demo --keep-raw
```

## 5-3. 11-document bilingual smoke corpus (5 tools, 2026-11-09)

Corpus: `benchmarks/fixtures/zh-*.pdf` and `en-*.pdf`, generated by `make_corpus.py`; the answers are the source text. Coverage: text layer, two-column, tables, footnotes, scans, English end-of-line hyphenation.

| Tool | ok | empty/error | median CER | median no-punct CER | worst file | worst CER | median s |
|---|---:|---:|---:|---:|---|---:|---:|
| pdftotext | 9 | 2 | 0.0000 | 0.0000 | zh-footnote.pdf | 0.0000 | 0.04 |
| markitdown | 9 | 2 | 0.0000 | 0.0000 | en-hyphenation.pdf | 0.0066 | 0.89 |
| liteparse | 9 | 2 | 0.0130 | 0.0000 | zh-footnote.pdf | 0.0385 | 0.15 |
| mineru | 11 | 0 | **0.0030** | 0.0000 | zh-footnote.pdf | 0.0385 | 1.00 |
| docling | 11 | 0 | 0.0130 | 0.0000 | en-scan.pdf | 0.0712 | 10.06 |

Interpretation:

- **Both empty/error = 2 cases are the two scans**: `pdftotext` / `markitdown` have no text layer, and `liteparse` outputs about 0 characters. MinerU / Docling can OCR scans directly, hence ok=11.
- **no-punct CER is 0.0000 for every tool**: the remaining CER all comes from punctuation normalization (MinerU turns full-width `：`/`；` into ASCII; liteparse/markitdown turn quotes/dashes into ASCII), not character errors. This is why both `cer_text` and `cer_nopunct` must be reported.
- **MinerU has the lowest median CER (0.0030) across the 11 documents in this round, but its worst page is still zh-footnote (0.0385, punctuation)**; Docling's worst is en-scan (0.0712, OCR errors).
- Runtimes are warm starts with the model already loaded; the first cold start is noticeably longer (see the previous section).
- `pdfplumber` has a text CER of 0.0000 on the two simple table fixtures; for the structure/spot checks of real merged tables see 5-8. Per-cell CER is now measured on two real pages (section 5-12), but **that is not a general table-accuracy claim**; the other real tables still have only structure/spot checks.
- **The two-column fixture is too gentle**: reportlab writes the two columns into the content stream in "left column → right column" order, and `markitdown` reads it correctly too. It does not force "one line from the left, one from the right" interleaving, so it cannot prove that real two-column PDFs pass. The next round should construct a PDF whose content stream interleaves line by line.
- This is still a synthetic corpus and cannot replace real PDFs; the next round adds real CC BY-SA articles and CID/no-ToUnicode samples.

Reproduce:

```bash
python3 -I benchmarks/fixtures/make_corpus.py
python3 -I scripts/bench.py benchmarks/fixtures/zh-*.pdf benchmarks/fixtures/en-*.pdf \
  --tools pdftotext,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-corpus --keep-raw
```

## 5-4. OCR path comparison (2 scans, 2026-11-09)

Corpus: `zh-scan.pdf` / `en-scan.pdf` (150 dpi, no text layer). The OCRmyPDF row is "Tesseract chi_sim+eng adds a text layer → pdftotext".

| Path | Chinese CER | English CER | Median runtime | Notes |
|---|---:|---:|---:|---|
| **RapidOCR** | **0.0116** | **0.0010** | 2.41 s | Direct OCR; strong in both Chinese and English |
| MinerU | 0.0159 | 0.0020 | 1.44 s | Direct parse/OCR |
| Docling | 0.0101 | 0.0712 | 16.82 s | Good Chinese, clearly poor on English scans |
| OCRmyPDF (Tesseract) | 0.1012 | 0.0020 | 3.81 s | Chinese an order of magnitude worse; English good |
| pdfplumber | error | error | — | No text layer; expected to fail |

Interpretation:

- **Chinese scans**: RapidOCR / Docling / MinerU are all in the 1%–1.6% range; Tesseract `chi_sim` is about 10%, clearly worse. Do not default to OCRmyPDF for Chinese scans.
- **English scans**: RapidOCR / MinerU / OCRmyPDF are all in the 0.1%–0.2% range; Docling is 7.1% this time, so spot-check English scans.
- **pdfplumber requires a text layer**: failing on scans is correct behavior, not a bug.
- These are 150 dpi synthetic scans; low resolution, skew, or handwriting will change the ranking.

Reproduce:

```bash
python3 -I scripts/bench.py benchmarks/fixtures/zh-scan.pdf benchmarks/fixtures/en-scan.pdf \
  --tools rapidocr,ocrmypdf,pdfplumber,mineru,docling \
  --out /tmp/docarbiter-ocr --keep-raw
```

## 5-5. Real CC BY-SA samples (4 articles, 2026-11-09)

Corpus: 2 Chinese and 2 English Wikipedia articles each, excerpted at about 2,200 / 3,200 characters and rendered as 1–2 page text-layer PDFs. For sources, modifications, and CC BY-SA 4.0 attribution see `benchmarks/fixtures/real/SOURCES.md`.

| Tool | ok | median CER | median no-punct CER | worst file | worst CER | median s |
|---|---:|---:|---:|---|---:|---:|
| pdftotext | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0017 | 0.04 |
| pdfplumber | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0017 | 0.05 |
| markitdown | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0021 | 0.98 |
| liteparse | 4 | 0.0014 | 0.0000 | zh-ocr.pdf | 0.0082 | 0.25 |
| docling | 4 | 0.0020 | 0.0000 | zh-ocr.pdf | 0.0046 | 10.27 |
| mineru | 4 | 0.0074 | 0.0000 | zh-ocr.pdf | 0.0251 | 4.99 |

Interpretation:

- **no-punct CER is still 0.0000 across the board**: the residual on real articles is also mainly punctuation normalization (especially MinerU's full-width punctuation → ASCII). This shows that "content correctness" is already high on these clean text-layer samples.
- MinerU has the highest `cer_text` (zh-ocr 2.51%), but no-punct is 0; do not use text CER alone to claim it "extracted it wrong".
- The speed order matches the synthetic samples: `pdftotext`/`pdfplumber` < `liteparse` < `markitdown` < MinerU < Docling.
- These are **text-layer** PDFs, not scans; they also lack CID/no-ToUnicode, two-column, and vertical layout. Real-world hard samples still need to be added.
- CC BY-SA 4.0: these four fixtures are not MIT; when redistributing, keep the attribution and license in `SOURCES.md`.

Reproduce:

```bash
python3 -I benchmarks/fixtures/real/make_real.py
python3 -I scripts/bench.py benchmarks/fixtures/real/*.pdf \
  --tools pdftotext,pdfplumber,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-real --keep-raw
```

## 5-6. Edge samples (CID / traditional / interleaved two-column / simulated vertical, 2026-11-09)

Corpus: `benchmarks/fixtures/edge/`, generated by `make_edge.py`. The CID samples use LibreOffice to generate a normal Chinese PDF, then pypdf to remove `/ToUnicode`; vertical layout is **simulated** (one character per line), not a true vertical writing mode.

| Sample | pdftotext | liteparse | markitdown | pdfplumber | MinerU | Docling |
|---|---:|---:|---:|---:|---:|---:|
| `zh-cid-no-tounicode` | garbled | garbled | garbled | garbled | **4.95%** | garbled |
| `zh-traditional` | 0 | 0 | 0 | 0 | 1.72% | 0 |
| `zh-two-column-interleaved` | 0 | 0 | 0 | **67.94%** | 1.53% | 2.29% |
| `en-two-column-interleaved` | 0 | 0 | 0 | **60.36%** | 0 | 3.18% |
| `zh-vertical-sim` | 0 | **34.78%** | 0 | 0 | **13.04%** | 0 |

Interpretation:

- **CID / no ToUnicode**: all text-layer tools (pdftotext / liteparse / markitdown / pdfplumber / Docling) are garbled; **MinerU can OCR and gets 4.95%**. This is the typical "glyphs but no character mapping" case: do not trust the text layer; go to MinerU / RapidOCR / olmOCR.
- **Traditional Chinese**: all tools are basically correct; MinerU's 1.72% is still punctuation normalization (no-punct is 0).
- **Interleaved two-column**: `pdftotext` / `liteparse` / `markitdown` / MinerU all read it correctly; **`pdfplumber` 60%–68%**, because it reads by content stream/position, and after interleaving the reading order is unusable; Docling 2%–3% with slight problems.
  - This **refutes** the claim in the handoff document that "markitdown does not handle two-column" (at least it did not reproduce on 0.1.9 + this synthetic sample). Do not keep asserting it in README/gotchas; real two-column still needs testing.
- **Simulated vertical**: pdftotext / markitdown / pdfplumber / Docling are correct; liteparse 34.78% and MinerU 13.04% scramble the one-character-per-line order. **Note: this is only a simulation, not true vertical typesetting**; true vertical (vertical writing mode, columns advancing right to left) has not been tested yet.

Reproduce:

```bash
python3 -I benchmarks/fixtures/edge/make_edge.py
python3 -I scripts/bench.py benchmarks/fixtures/edge/*.pdf \
  --tools pdftotext,liteparse,markitdown,pdfplumber,mineru,docling \
  --out /tmp/docarbiter-edge --keep-raw
```

> The CID samples in `make_edge.py` require LibreOffice `soffice`; `pypdf` is used to remove `/ToUnicode`. Neither is a runtime dependency; both are only used to generate fixtures.

## 5-7. Real two-column paper (qualitative, 2026-11-09)

Source: ResNet, arXiv:1512.03385, first 3 pages, saved in `benchmarks/private/resnet-3p.pdf` (local testing only, not distributed with the repository; there is no answer key, so no CER).

Observations (same 3 pages):

| Tool | Observation |
|---|---|
| MinerU | abstract / title clean, body readable; best |
| Docling | abstract readable; figure captions slightly early, usable overall |
| liteparse | abstract readable; paragraph merging fairly good |
| pdftotext | abstract readable; body needs column-order checking |
| markitdown | **many Markdown tables/axis labels, abstract broken up**; unreliable on real two-column pages containing figures |
| pdfplumber | spaces between words lost (`presentaresiduallearning...`), axis labels mixed in |

Conclusions:

- markitdown passes clean text-only two-column (synthetic); **markitdown breaks on real papers containing figures/axis labels**. Do not treat "synthetic two-column passes" as "real two-column passes".
- For real two-column, prefer MinerU / Docling / liteparse; use pdfplumber only for tables, not for extracting the full text directly.
- We tried PLOS ONE `10.1371/journal.pone.0296319` (CC BY 4.0): page 2 is a left sidebar + right body text, not a classic academic two-column layout; it is not used as a two-column CER fixture.
- Done in section 5-13 (2026-11-11/12): BERT, Cell 2020 MoTrPAC Perspective, ResNet, Nature Communications 2026, and PLOS Computational Biology 2026, with independent PMC JATS / ar5iv truth and full-text CER.

## 5-8. Table cell-level accuracy (pdfplumber, 2026-11-09)

Corpus: `benchmarks/fixtures/tables/`, generated by `make_tables.py`; the truth is `<fixture>.json`. Covers three categories: bordered, merged cells, and borderless.

| fixture | Tables found | truth rows×columns | extracted rows×columns | Cell accuracy | Row accuracy |
|---|---:|---|---|---:|---:|
| zh/en-table-grid | 1 | 4×3 | 4×3 | **1.000** | 1.000 |
| zh/en-table-merged | 1 | 4×3 | 4×3 | **1.000** | 1.000 |
| zh/en-table-borderless | **0** | 4×3 | 0×0 | **0.000** | 0.000 |

Interpretation:

- **Bordered tables**: pdfplumber's default `extract_tables()` gives 100% on both cells and rows.
- **Merged cells**: in the test the covered cells have an empty truth and also extract as empty, hence 1.000; this proves row/column alignment and text position, **not that it understands merge semantics**. Real merged headers still need manual checking.
- **Borderless tables**: pdfplumber's default finds **0 tables**; the `table_settings` text strategy is needed, or switch to Camelot. Do not promise borderless table support on the default path.
- Only pdfplumber was tested; Camelot is not installed.

### Cost of the text strategy (same batch of fixtures)

The `text` strategy = `vertical_strategy=text` + `horizontal_strategy=text` + deleting all-empty rows:

| fixture | default cell accuracy | text cell accuracy |
|---|---:|---:|
| zh-table-grid | 1.000 | 1.000 |
| en-table-grid | 1.000 | 0.917 |
| zh-table-merged | 1.000 | 0.667 |
| en-table-merged | 1.000 | 0.583 |
| zh-table-borderless | 0.000 | **1.000** |
| en-table-borderless | 0.000 | **0.917** |

Conclusion: **no single setting works for everything**. The default suits bordered/merged; the text strategy rescues borderless but splits merged cells apart and drops some English (`half z`). In practice, run both strategies on the same page and pick the one with the more sensible row/column structure, or spot-check manually.

### Real high-frequency tables (2026-11-10, private local files, read-only)

The above are synthetic fixtures. To answer "whether real book tables/standards tables are usable", we also tested 5 high-frequency PDFs from this machine. **These files are not in the repository, are not uploaded, and their body text is not saved.** For WS/T 578.1 p8 and GB 28050 p6 we now also have per-cell CER (section 5-12); the other three remain structure/spot-check only.

| Real document (page) | Expected structure | pdfplumber `lines` | pdfplumber `text` | MinerU | Docling |
|---|---|---|---|---|---|
| WS/T 578.1—2017 p8 | 22 data rows × 13 columns, 3-level header (25 rows including the 3 header rows) | 27×13; header spans correct; 2 note rows trimmed | 26×13 after dropping empty rows; broken | 27×13; rowspan/colspan correct; 2 note rows trimmed | 25×13; header expanded correctly |
| GB 28050—2025 p6 | 28 data rows × 4 columns, multi-line cells | 29×4; cells out of order | 72×6 after dropping empty rows; broken | 29×4; 6 multi-line cells interleaved | 29×4; exact after normalization |
| DRIs 2023 p65 | 2 symbol tables 15×6, 14×6 | 0 tables | 69×9; unusable | 15×6 + 14×6; Chinese names correct, ●/○ → empty/O | Names require OCR; ●→`.`, ○→`O` |
| GB 2760—2024 p13 | 26 data rows × 4 columns | 27×4; spot-check correct | 84×3; broken | 27×4; 4 cells interleaved | 27×4; spot-check correct |
| China Food Composition Tables, 6th ed., Vol. 1, p246 | 65 entries, two-column book table | 0 tables | 45×4; unusable | 6 columns; 65 entries; first 3 rows misaligned | 7 columns after OCR; bottom 3 rows misaligned |

Interpretation:

- **Complex merged headers/multi-line cells → Docling.** WS/T 578.1, GB 28050, and GB 2760 have the best structure and reading order; this is the basis for `--goal table-structure`.
- **Bad text layers/symbol tables → MinerU.** The DRIs 2023 text layer turns ● into `.` and ○ into `。`; MinerU recovers the Chinese names and distinguishes ●/○ as "empty/O", but **does not preserve the original symbols**.
- **pdfplumber is only for simple grids/coordinates.** Under 0.5s per page; multi-line cells in real book tables come out scrambled, and the `text` strategy inflates 29×4 into 76×6.
- **Dense two-column book tables are still not guaranteed.** On the 65-entry two-column table on p246 of the Food Composition Tables, both Docling OCR and MinerU misalign rows at the top/bottom of the page; manual spot-checking is mandatory. **Do not treat "table detected" as "cells correct".**

Runtime (M2 Pro, models warm): pdfplumber <0.5s/page; MinerU ≈2.5s/page; Docling 3–5s/page with no-OCR, 10–12s/page with OCR.

Reproduce (replace `FILE` / `PAGE` with your files; do not put real files in the repository):

```bash
# pdfplumber: run both strategies and compare rows/columns
python3 -I -c 'import pdfplumber,sys; p=pdfplumber.open(sys.argv[1]).pages[int(sys.argv[2])-1]; print(p.extract_tables()); print(p.extract_tables(table_settings={"vertical_strategy":"text","horizontal_strategy":"text"}))' FILE PAGE

# Docling: use --no-ocr for a clean text layer; default OCR for bad text layers/scans; add --page-range for books
mkdir -p /tmp/table-out
docling convert FILE --from pdf --to md --page-range PAGE --no-ocr --output /tmp/table-out --image-export-mode placeholder

# MinerU: the server must be started in ~/.mineru, otherwise blobs/ is generated in the current directory
(cd "$HOME/.mineru" && mineru server start)
mineru parse FILE --pages PAGE --force --output /tmp/table-out/page.md --json
```

Reproducing the synthetic fixtures:

```bash
python3 -I benchmarks/fixtures/tables/make_tables.py
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

## 5-9. Real CC BY two-column paper abstract CER (BERT, 2026-11-09)

Source: Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019, ACL Anthology `N19-1423`, **CC BY 4.0**. The first 2 PDF pages are used as the real two-column fixture; the answer is the abstract from the ACL Anthology HTML, and CER is computed only on the abstract segment after partial alignment with rapidfuzz. For sources and attribution see `benchmarks/fixtures/real/SOURCES.md`.

| Tool | CER | no-punct CER | Alignment score | Runtime |
|---|---:|---:|---:|---:|
| MinerU | **0.0044** | 0.0000 | 99.8 | 18.40 s |
| pdftotext | 0.0066 | 0.0012 | 99.7 | 0.05 s |
| liteparse | 0.0066 | 0.0000 | 99.7 | 0.11 s |
| Docling | 0.0066 | 0.0012 | 99.7 | 11.23 s |
| markitdown | **0.7303** | 0.7344 | 56.6 | 1.13 s |
| pdfplumber | **0.7303** | 0.7344 | 56.8 | 0.16 s |

Interpretation:

- **MinerU is best on the real two-column abstract (0.44%)**; pdftotext / liteparse / Docling are about 0.65%.
- **markitdown / pdfplumber have CER 73% on the real two-column abstract**: this is not a punctuation problem (no-punct is still 73%) but a reading order / text-mixing problem. This differs from the synthetic text-only two-column result, showing that "synthetic two-column passes" cannot be extrapolated to real papers.
- Only the abstract was evaluated, not the full text; figures, tables, and references were not scored. Full-text CER is still to be done.
- This is a real CC BY 4.0 paper, so a 2-page excerpt can be distributed with the repository; the complete 16 pages are only in `benchmarks/private/`.

Reproduce:

```bash
python3 -I scripts/bench_abstract.py --out /tmp/docarbiter-abstract
```

## 5-10. Real workspace PDF sampling (read-only, 2026-11-10)

Read-only scan of this machine's workspace, deduplicated by SHA-256; body text is not saved and nothing is uploaded. Details are in `benchmarks/private/survey*.md` / `survey*.json` / `real-smoke.md` (gitignored).

### Inventory and sampling

| Directory | PDF count | After dedup | Random sample |
|---|---:|---:|---:|
| Doctoral Dissertation | 189 | 177 | 12 |
| CPET Data Analysis | 399 | 396 | 12 |
| Bioinformatics Data Analysis | 16 | 14 | 12 |
| Metabolomics Data Analysis | 7,862 | 7,857 | 12 |
| **Total** | **8,466** | **8,444** | **48** |

- Random 48: **all have a usable text layer**; 47 English / 1 Chinese; 0 source files with the same name; page-count distribution: 25 with 1–3 pages, 10 with 4–20 pages, 13 with 21+ pages.
- 24 Chinese-filename samples (sampled from 397 Chinese filenames in CPET + 35 in Dissertation): all have a usable text layer; 18 English / **6 Chinese** content.
- Conclusion: the workspace is mainly an **English journal library + clean text layers**; it is suitable for validating routing, English text-layer extraction, and performance, but **by nature does not cover scans/CID/vertical layout**.

### Real 4-file smoke (2 pages/file)

Selected 2 Chinese + 2 English and ran pdftotext / liteparse / MinerU:

- All three tools succeeded; pdftotext/liteparse about 0.03–0.13s, MinerU about 1–1.5s after cold start (42s the first time).
- **Order CER 0.05–0.65, but the bag-of-characters difference is only 0.1%–2.6%**: in most cases the content is all there; the difference is reading order/paragraphing, not missing characters.
- **One real risk**: on page 1 of a Chinese article, pdftotext has 2,299 characters and MinerU only 1,480; Latin characters 1,257→675, Chinese 664→531; page 2 is almost identical between the two (2,012 vs 2,009). This looks like MinerU losing the English abstract/author information on page 1. **Do not assume MinerU is always complete on the first page of a Chinese journal article.**

### Implications for the project

- The real workspace samples validated: routing probes, text-layer extraction, and performance.
- They do not naturally cover: scans, CID/no ToUnicode, true vertical layout, complex tables — these are still handled by the synthetic/edge fixtures.
- For real PDFs without an independent answer key, we can only report **agreement / coverage / bag differences**, not accuracy.
- Next step: check Latin content coverage page by page on Chinese journal samples; for those with same-name source files, compute local CER.

## 5-11. Page-structure regression (2026-11-11)

Page structure and OCR character error rate are separate measurements. `per_document.csv`
holds one row per document/tool pair; page structure is checked by
`scripts/check_pagemarkers.py`.

The script builds a 4-page sample from repository fixtures only:

| Page | Source | Expected |
|---:|---|---|
| 1 | `zh-scan.pdf` | scanned image, non-empty body |
| 2 | `edge/zh-empty.pdf` | blank page, preserved as blank |
| 3 | `zh-scan.pdf` | scanned image, non-empty body |
| 4 | `zh-scan.pdf` | scanned image, non-empty body |

It runs MinerU twice:

- full export (`--pages all`): markers must be `1,2,3,4` with total `4`; page 2 must stay blank;
- selected export (`--pages 3-4`): markers must be `3,4` with total `4` (original PDF page
  numbers, not renumbered), and each selected page body must match the corresponding
  full-export body after whitespace normalization (similarity ≥ 0.90).

Result on 2026-11-11: **PASS** (`full markers [1, 2, 3, 4]`, `selected markers [3, 4]`,
blank page preserved). The script skips with exit 0 when MinerU is not installed, so CI can
run it on machines without the model.

## 5-12. Real-table per-cell CER (2026-11-11/12)

This is the per-cell follow-up to the structure/spot-check table above. Three
single-page PDFs were isolated from private local standards (not redistributed):

- WS/T 578.1—2017 p8 (PDF page 8): 3-level header, 22 data rows, 13 columns.
- GB 28050—2025 p6 (PDF page 6): 4 columns, 28 data rows, multi-line cells.
- GB 2760—2024 p13 (PDF page 13): 4 columns, 26 data rows, 4 multi-line cells.

Truth was written as a cell matrix and hand-checked against the rendered page.
A merged cell keeps its text in the top-left position and `""` in covered
positions. Extra note rows are trimmed to the truth dimensions. Normalisation
removes whitespace and unifies dash/quote variants; `nopunct` additionally
removes Unicode punctuation. CER is edit distance divided by truth length.

| Page | Tool / strategy | Predicted | micro CER (text / nopunct) | Exact content cells (nopunct) |
|---|---|---|---|---|
| WS/T p8 | pdfplumber default | 27×13 | 0.0000 / 0.0000 | 1.000 |
| WS/T p8 | pdfplumber text | 26×13 | 0.6246 / 0.7311 | 0.027 |
| WS/T p8 | Docling JSON | 25×13 | 0.0000 / 0.0000 | 1.000 |
| WS/T p8 | MinerU Markdown/HTML | 27×13 | 0.0000 / 0.0000 | 1.000 |
| GB 28050 p6 | pdfplumber default | 29×4 | 0.3106 / 0.3010 | 0.612 |
| GB 28050 p6 | pdfplumber text | 72×6 | 0.9975 / 0.9916 | 0.000 |
| GB 28050 p6 | Docling JSON | 29×4 | 0.0101 / 0.0000 | 1.000 |
| GB 28050 p6 | MinerU Markdown | 29×4 | 0.1162 / 0.1237 | 0.948 |
| GB 2760 p13 | pdfplumber default | 27×4 | 0.0668 / 0.0000 | 1.000 |
| GB 2760 p13 | pdfplumber text | 59×3 | 0.8893 / 0.9293 | 0.061 |
| GB 2760 p13 | Docling JSON | 27×4 | 0.0193 / 0.0000 | 1.000 |
| GB 2760 p13 | MinerU Markdown | 27×4 | 0.1178 / 0.1071 | 0.951 |

Interpretation:

- **WS/T p8 is a clean grid.** After normalisation, pdfplumber's default
  strategy, Docling, and MinerU all reproduce every cell; the `text` strategy
  breaks the header/row structure.
- **GB 28050 p6 is the multi-line-cell stress case.** Docling is the only tool
  with zero `nopunct` CER. MinerU is about 12.4%, pdfplumber's default strategy
  about 30.1%, and pdfplumber's `text` strategy about 99.2%. The remaining
  MinerU errors are exactly the interleaved multi-line cells (`n-3`,
  mono/polyunsaturated fat, the vitamin A/E units, and the folate unit);
  pdfplumber's default strategy instead merges header/unit text into data cells.
- **GB 2760 p13 is another clean grid.** pdfplumber default and Docling
  reproduce every content cell after `nopunct` normalisation; MinerU is 10.71%
  because its 4 multi-line cells (rows 11, 14, 20, 22) are interleaved;
  pdfplumber `text` breaks the grid to 59×3.
- **Caveats.** WS/T and GB 28050 truth was drafted from Docling and hand-checked,
  so their Docling 0.0000 is a ceiling/sanity check; GB 2760 truth was written
  from the rendered page. This covers three pages and three editions only. It is
  cell-text CER, not proof that merged-cell semantics are understood. Do not
  generalise it to another edition, page, or tool version.
- **Earlier structure-only note corrected.** The earlier table recorded "21 data
  rows" and a flattened pdfplumber header. The isolated-page rerun with
  pdfplumber 0.11.10 finds 22 data rows (25 rows including the 3 header rows)
  and correct header spans.

Reproduce with private inputs (PDFs and truth stay gitignored):

```bash
python3 -I scripts/bench_real_tables.py \
  --dir benchmarks/private/tables --tools pdfplumber,docling,mineru
```

CI only `py_compile`s this script; it does not run it, because the PDFs and truth
are private and gitignored.

## 5-13. Full-text CER on five real two-column papers (2026-11-11/12)

Scope: abstract plus main body (section headings and paragraphs). References,
figure/table content and captions, and appendices are excluded. Truth comes from
an independent source, not from a tool under test:

- Cell 2020 MoTrPAC Perspective, PMC8800485 → PMC JATS XML;
- BERT, NAACL 2019 (arXiv:1810.04805) → ar5iv HTML;
- ResNet, CVPR 2016 (arXiv:1512.03385) → ar5iv HTML;
- Nature Communications 2026, PMC13482395 → PMC JATS XML;
- PLOS Computational Biology 2026, PMC13529250 → PMC JATS XML.

Tool output is stripped of Markdown/HTML, cut at acknowledgments/references, and
aligned to the truth's first/last anchors before CER. A row is valid only with
`start+end` (or a clear last-paragraph fallback) alignment and coverage 0.5–1.5.

| Paper | Tool | CER (text) | CER (nopunct) | Coverage | Valid |
|---|---|---|---:|---:|---|
| BERT | pdftotext | 0.2280 | 0.2108 | 1.047 | yes |
| BERT | liteparse | 0.1569 | 0.1398 | 1.059 | yes |
| BERT | Docling | **0.0766** | **0.0656** | 1.014 | yes |
| BERT | MinerU | 0.0930 | 0.0773 | 1.035 | yes |
| BERT | pdftotext `-layout` | — | — | 1.663 | no (whole-document alignment) |
| Cell | pdftotext | **0.0386** | **0.0349** | 1.008 | yes |
| Cell | Docling | 0.1159 | 0.1099 | 1.099 | yes |
| Cell | MinerU | 0.1010 | 0.0953 | 1.084 | yes |
| Cell | liteparse | — | — | 1.189 | no (start-only) |
| Cell | pdftotext `-layout` | — | — | 0.954 | no (start-only) |
| ResNet | pdftotext | 0.4343 | 0.4212 | 1.012 | yes |
| ResNet | liteparse | 0.2464 | 0.2287 | 1.048 | yes |
| ResNet | Docling | 0.1587 | 0.1537 | 0.927 | yes |
| ResNet | MinerU | **0.1339** | **0.1214** | 1.004 | yes |
| ResNet | pdftotext `-layout` | — | — | 1.003 | no (whole-document alignment) |
| Nature Communications | pdftotext | 0.1760 | 0.1733 | 1.110 | yes |
| Nature Communications | liteparse | 0.1290 | 0.1259 | 1.111 | yes |
| Nature Communications | Docling | **0.1244** | **0.1209** | 1.110 | yes |
| Nature Communications | MinerU | 0.1373 | 0.1322 | 1.128 | yes |
| Nature Communications | pdftotext `-layout` | 0.7876 | 0.7759 | 1.101 | yes (last-paragraph) |
| PLOS Computational Biology | pdftotext | 0.2081 | 0.1976 | 1.202 | yes (last-paragraph) |
| PLOS Computational Biology | liteparse | 0.2133 | 0.1950 | 1.207 | yes |
| PLOS Computational Biology | Docling | **0.1634** | **0.1586** | 1.162 | yes |
| PLOS Computational Biology | MinerU | 0.3022 | 0.2552 | 1.295 | yes |
| PLOS Computational Biology | pdftotext `-layout` | 0.2429 | 0.2294 | 1.242 | yes (last-paragraph) |

Interpretation:

- **BERT is the cleaner comparison.** Docling (6.56%) is best, MinerU (7.73%)
  close, liteparse (13.98%) worse, pdftotext (21.08%) worst. `pdftotext -layout`
  is invalid because it preserves physical two-column order.
- **Cell needs a scope caveat.** pdftotext is 3.49%, MinerU 9.53%, Docling
  10.99%; but Docling/MinerU coverage is 1.08–1.10 because this Perspective has
  text inside its figures, which the main-body truth excludes. Their CER
  therefore includes extra figure text. pdftotext's low CER is partly a clean
  text layer and reading order, not a general win.
- **ResNet (CVPR) is a second clean comparison.** MinerU is best (12.14%),
  Docling close (15.37%), liteparse worse (22.87%), pdftotext worst (42.12%);
  `-layout` is invalid.
- **Nature Communications is a close race.** Docling 12.09%, liteparse 12.59%,
  MinerU 13.22%, pdftotext 17.33%; coverage 1.11 means the tool output includes
  figure legends/SI text that the main-body truth excludes.
- **PLOS Computational Biology is equation/table-heavy.** Docling is best
  (15.86%), liteparse 19.50%, pdftotext 19.76%, MinerU worst (25.52%);
  coverage 1.16–1.30 also includes extra figure/SI text.
- **No universal winner.** Docling is the most consistent (best on BERT, Nature
  Communications, PLOS; second on Cell/ResNet). MinerU wins ResNet and is strong
  on BERT/Cell, but is worst on the equation-heavy PLOS paper. liteparse is
  usually mid; pdftotext is last except on the clean Cell text layer.
- **Nature 2024 MoTrPAC (PMC11062907) was also downloaded and tested but is not
  in the table.** The 35-page flagship includes Methods/Extended Data and figure
  legends; the main-body truth scope is too narrow, so all tools fail alignment
  (coverage 2.3–2.6). It needs a full-article scope.
- **Five papers only.** Full-text CER is still sensitive to figure text,
  headers/footers, and caption stripping; coverage above 1.1 means the CER
  includes some extra text. Do not generalise to another paper, publisher
  layout, or tool version.
- The script is `scripts/bench_fulltext.py`; private PDFs and truth are
  gitignored, and CI only `py_compile`s the script.

## 6. Anti-patterns (enforced in CI)

- ❌ Using `pdftotext` output as ground truth.
- ❌ Reporting only one total score, not the worst page.
- ❌ Inferring Chinese results from English samples' scores.
- ❌ Testing only body-text pages and skipping tables/scans/two-column.
- ❌ Not recording tool versions and corpus version.
- ❌ Treating model-reported confidence as accuracy.

## 7. TODO

- [x] Generate 11 bilingual synthetic samples + answer text (`make_corpus.py`)
- [x] Write `scripts/bench.py` (CER, no-punct CER, coverage, empty-output detection)
- [x] Run the 5 primary tools + the two OCR paths RapidOCR/OCRmyPDF
- [x] Add the "worst page" samples to `gotchas.md` (punctuation, Chinese scan OCR)
- [x] 4 real CC BY-SA Wikipedia articles (2 Chinese / 2 English)
- [x] CID/no-ToUnicode, traditional, interleaved two-column, simulated-vertical edge samples
- [x] True vertical (Chrome `vertical-rl`) + real two-column qualitative (ResNet 3 pages)
- [x] Real CC BY two-column paper abstract CER (BERT, ACL N19-1423)
- [x] Table cell-level accuracy (bordered/merged 1.000; borderless default 0 tables)
- [x] Structure and spot checks of 5 real high-frequency tables (Docling / MinerU / pdfplumber routing)
- [ ] Per-cell CER on real tables (currently only structure and spot checks)
- [ ] `table_settings` / Camelot strategy for borderless tables
- [ ] Mixed traditional/simplified + public-domain classics samples (optional)
- [ ] Run all 12 primary tools (including the extension layer)
- [ ] Separate cold/warm start and write into reporting
