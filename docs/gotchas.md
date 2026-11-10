# Tested Pitfalls

> Each entry includes how to reproduce it. Environment: macOS 26 / M2 Pro / Python 3.11.11 (2026-11-09).
> Other platforms are marked "unverified." Do not treat these conclusions as general upstream behavior—they were measured on this machine and this version.

---

## 1. liteparse enables OCR by default and hangs for about 123 seconds when it fails

**Symptom**: Calling `LiteParse().parse("file.pdf")` directly produces no output for a long time, then reports a tessdata download failure.

**Cause**: Upstream defaults to `ocr_enabled=True`, tries to download tessdata from GitHub, and blocks when the network is unavailable.

**Fix**: Use this repository's `liteparse-doc` (forces `ocr_enabled=False`); if OCR is genuinely needed, add `--ocr` and configure tessdata first.

**Reproduce**:

```bash
python3 -c "from liteparse import LiteParse; LiteParse().parse('benchmarks/fixtures/demo-zh.pdf')"
time liteparse-doc benchmarks/fixtures/demo-zh.pdf >/dev/null
```

---

## 2. docling inlines images as base64 by default, bloating Markdown

**Symptom**: One page of Markdown grows from about 2.6k characters to about 69k.

**Cause**: `--image-export-mode` embeds images in the document by default.

**Fix**: Always add `--image-export-mode placeholder`.

```bash
docling convert file.pdf --to md --output out/ --image-export-mode placeholder
```

---

## 3. MinerU uses the current working directory for its parse cache, leaving blobs/ and lock files

**Symptom**: After running `mineru server start` in the project directory, `blobs/` and `.mineru-service.lock` appear. On 2026-11-10 they appeared again under `~/Documents/Claude`, measured at **200MB**; the contents are a parse cache bucketed by SHA, not project files.

**Cause**: MinerU uses the CWD as its parse cache directory; the `mineru-doc` wrapper pins `cd "$HOME/.mineru"`, but running `mineru server start` bare by hand does not.

**Fix**: Use `mineru-doc`; when starting the server manually, you must `cd ~/.mineru` first. Existing `blobs/` can be deleted directly (the cache can be rebuilt); before deleting, confirm no `mineru` process is running.

```bash
# wrong
mineru server start
# right
(cd "$HOME/.mineru" && mineru server start)

# clean up caches created by mistake
rm -rf blobs .mineru-service.lock
```

> This repository's `.gitignore` already includes `blobs/` and `.mineru-service.lock`; but they still should not appear in the working directory. Do not run `mineru server start` bare in tests/scripts.

---

## 4. Two-column: synthetic plain text not reproduced; real papers (with figures) get scrambled

**Synthetic plain text, content stream interleaved line by line**: CER for markitdown / pdftotext / liteparse / MinerU is all **0**; pdfplumber **60%–68%**. So "markitdown definitely cannot handle two columns" is **not reproduced** on clean synthetic samples.

**Real paper (ResNet, arXiv:1512.03385, 3 pages, local `benchmarks/private/`)**: markitdown outputs many Markdown tables/axis labels, and the abstract is scrambled; pdfplumber loses spaces and mixes in axis labels; the abstracts from MinerU / Docling / liteparse are readable. This one has no answer key, so no CER is computed, only a qualitative reading-order check.

**Real CC BY two-column paper (BERT, ACL Anthology N19-1423, abstract CER)**: MinerU **0.44%**; pdftotext / liteparse / Docling **0.65%**; markitdown / pdfplumber **73%**. no-punct is still 73%, so it is reading order/mixed layout, not punctuation. This completely separates "passes synthetic two-column" from "passes real two-column."

**Conclusion**: Do not say "markitdown definitely does / definitely does not handle two columns." It passes clean text columns; it breaks on real papers with figures, axis labels, and text boxes. For real two-column, prefer `mineru` / `docling` / `liteparse`; do not use `pdfplumber` to extract full text directly.

**Reproduce**: Synthetic samples are in `benchmarks/fixtures/edge/`; the real paper uses `benchmarks/private/resnet-3p.pdf` (kept locally, not distributed with the repository).

---

## 5. Running OCR on a PDF with a text layer is a negative optimization

**Symptom**: Text that was originally in the correct order gets scrambled in two columns after OCR; measured character-order similarity drops from 97% to 40%.

**Cause**: OCR re-detects text boxes and outputs by image position rather than original reading order.

**Fix**: Run `docarbiter`'s text-layer probe first; when `bad_ratio` is low and `chars` is sufficient, do not OCR.

---

## 6. liteparse paragraphs are interrupted by headers

**Symptom**:

```
...whereas 80% is derived from the
D. Ylli et al.                      ← header mixed into the middle of the paragraph
monodeiodination of T4 by 5'-deiodinase...
```

**Cause**: liteparse does not filter headers/footers; it outputs the page text stream.

**Fix**: To produce a finished manuscript, use `mineru`; when using liteparse, clean by header string, or take only body pages.

---

## 7. liteparse heading levels are misjudged

**Symptom**: Some same-level headings output `###`, others output `####`.

**Cause**: Heading levels rely on font/size heuristics and drift across pages or when styles are inconsistent.

**Fix**: For finished manuscripts use `mineru`; when using liteparse, post-process by font size/font and do not trust Markdown levels directly.

---

## 8. liteparse normalizes full-width punctuation to ASCII

**Symptom**: Source text `“”‘’` becomes `""''`, and `——` becomes `--`. On a 1-page Chinese demo, CER rises from 0 to 0.61% (8 substitutions).

**Cause**: liteparse's text normalization/output layer maps some full-width punctuation to ASCII.

**Fix**: When doing punctuation-sensitive proofreading, compare against the original PDF first; `bench.py` reports both `cer_text` and `cer_raw`, the latter not stripping Markdown, but the difference is still visible.

**Reproduce**:

```bash
liteparse-doc benchmarks/fixtures/demo-zh.pdf | grep -n '第一段'
pdftotext benchmarks/fixtures/demo-zh.pdf - | grep -n '第一段'
```

---

## 9. MinerU `--tier flash` has no structure

**Symptom**: Output is plain text only, with no `## Heading`, figure captions, or page anchors.

**Cause**: The flash tier is a service-free fast plain-text mode.

**Fix**: For finished manuscripts use the default tier (basic/standard) or `mineru-doc`; flash is only for quick previews.

---

## 10. `liteparse-doc --help` was once treated as a filename

**Symptom**: `liteparse-doc --help` throws `FileNotFoundError: --help`.

**Cause**: The old wrapper treated the first argument unconditionally as a path.

**Fix**: This repository's wrapper has an `-h/--help` branch; if you are using the old wrapper, run it with no arguments to see usage.

---

## 11. Using `pdftotext` as the answer makes the benchmark meaningless

**Symptom**: `pdftotext`'s CER is always 0, and every other tool looks "inaccurate."

**Cause**: The answer is `pdftotext`'s own output, so it measures "who looks more like pdftotext," not accuracy.

**Fix**: The answer must come from an independent source (text we wrote ourselves / the source text of a CC BY-SA article / a public-domain proofread text). This repository's demo uses source text as the answer, so `pdftotext`'s 0 is real, not circular.

---

## 12. English end-of-line hyphens inflate CER

**Symptom**: `docu-\nment` is preserved by the tool as `docu-ment`, counted as 1 substitution + 1 insertion when compared with the answer `document`.

**Cause**: End-of-line word division in PDFs; `pdftotext` / `liteparse` keep the hyphen and do not dehyphenate.

**Fix**: `bench.py` merges `[A-Za-z]-\n[A-Za-z]` during normalization. But **true hyphens** such as `well-known` must not be merged (they have no line break), so manual spot checks are needed.

**Reproduce**: Find an English two-column PDF, search for words where `-` is immediately followed by a newline; compare with the original.

---

## 13. Full-width punctuation normalized to ASCII inflates CER

**Symptom**: MinerU outputs full-width `：` / `；` as `:` / `;`; liteparse outputs `“”‘’` as `""''`; markitdown also changes English quotes/dashes.

**Consequence**: On the 11-document bilingual smoke corpus, **no-punct CER = 0.0000** for all tools, but `cer_text` is as high as 3.85%. These are not typos; it is punctuation normalization.

**Fix**:

- Report both `cer_text` and `cer_nopunct` (`bench.py` already outputs both columns);
- When doing punctuation-sensitive proofreading, compare against the original PDF;
- Do not use a single CER to assert "the tool extracted it wrong."

**Reproduce**:

```bash
mineru-doc benchmarks/fixtures/zh-footnote.pdf | grep '第一段'
pdftotext benchmarks/fixtures/zh-footnote.pdf - | grep '第一段'
```

---

## 14. Do not default to Tesseract chi_sim for Chinese scans

**Symptom**: After `ocrmypdf --language chi_sim+eng` adds a text layer and `pdftotext` runs, Chinese CER is **10.1%**; on the same scan:

| Path | Chinese CER |
|---|---:|
| RapidOCR | 1.16% |
| Docling | 1.01% |
| MinerU | 1.59% |
| OCRmyPDF (Tesseract chi_sim) | **10.1%** |

On English scans Tesseract is normal (0.20%), so the problem is not OCRmyPDF itself but the `chi_sim` Chinese model.

**Fix**: For Chinese scans prefer `rapidocr` / `mineru` / `docling`; use OCRmyPDF for English or as a fallback.

**Reproduce**:

```bash
ocrmypdf --language chi_sim+eng --output-type pdf --quiet zh-scan.pdf /tmp/zh-scan-ocr.pdf
python3 -I scripts/bench.py /tmp/zh-scan-ocr.pdf --truth benchmarks/fixtures/zh-scan.txt \
  --tools pdftotext --out /tmp/ocr-check
```

---

## 15. CID / no ToUnicode outputs control characters—it is not a "scan"

**Symptom**: `pdftotext` outputs control characters like `\x01\x02\x03...`; `markitdown` / `pdfplumber` output longer garbage (CER > 1); Docling is also garbled. MinerU, by contrast, can OCR, with CER 4.95%.

**Cause**: The font has glyphs but no `/ToUnicode` mapping; the text layer "has characters" but is unusable. Looking only at character count would misjudge 68 control characters as "has a text layer."

**Fix**:

- Add `ctrl_ratio` to the probe (control characters as a proportion of non-whitespace characters); `> 10%` is judged garbled;
- Do not force extraction with `pdftotext` / `liteparse` / `markitdown` / `pdfplumber`;
- Use MinerU / RapidOCR / olmOCR; this kind of PDF needs OCR, so "if it has a text layer, do not OCR" does not apply.

**Reproduce**:

```bash
python3 -I benchmarks/fixtures/edge/make_edge.py
pdftotext benchmarks/fixtures/edge/zh-cid-no-tounicode.pdf - | head -3
python3 -I scripts/bench.py benchmarks/fixtures/edge/zh-cid-no-tounicode.pdf \
  --tools pdftotext,markitdown,mineru,docling --out /tmp/cid-check
```

---

## 16. Vertical-text simulation: liteparse / MinerU scramble one-character-per-line order

**Measured**: On `zh-vertical-sim.pdf` (one character per line, top to bottom), pdftotext / markitdown / pdfplumber / Docling CER is 0; liteparse 34.78%, MinerU 13.04%.

**Note**: This is only a **simulation**, not true vertical writing mode; real vertical text (columns right to left, rotated punctuation) has not been tested. Do not treat this as a conclusion about real vertical text.

**Fix**: For real vertical text, first extract with MinerU/Docling and manually check column order; do not assume any tool can handle vertical text.

---

## 17. pdfplumber returns 0 tables for borderless tables by default

**Measured**: On the bordered / merged-cell fixture, `extract_tables()` cell accuracy is 1.000; **on the borderless fixture, `tables=0`, cell accuracy 0.000**.

**Cause**: pdfplumber's default table detection relies on ruling lines; without lines, the default strategy finds no table.

**Fix**:

- Set `table_settings` (`vertical_strategy=text` + `horizontal_strategy=text`), or switch to Camelot;
- But the text strategy is not a free lunch: on the same fixture batch, borderless rises from 0 to **1.000/0.917**, while merged cells drop from 1.000 to **0.667/0.583**, and English is also truncated (`half z`);
- In practice, run both default and text strategies on the same page and choose the one with the more sensible row/column structure, or spot-check manually;
- Do not understand "pdfplumber supports tables" as "it can extract any table"; the 1.000 on merged cells does not prove semantic correctness either.

**Reproduce**:

```bash
python3 -I benchmarks/fixtures/tables/make_tables.py
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

---

## 18. MinerU may drop English abstracts/author information on page 1 of Chinese journals

**Measured (real Chinese article in the workspace, 2-page smoke)**:

| Page | pdftotext chars | MinerU chars | Latin chars pdftotext→MinerU | Chinese pdftotext→MinerU |
|---|---:|---:|---|---|
| Page 1 | 2,299 | **1,480** | 1,257 → **675** | 664 → 531 |
| Page 2 | 2,012 | 2,009 | 521 → 518 | 1,016 → 1,016 |

MinerU is missing about **35%** of the content on page 1, mainly Latin characters; page 2 is almost identical. This looks very much like the **English abstract/author information/references** of a Chinese journal being dropped.

**Fix**:

- For Chinese journals, do not look only at the Chinese body text; check the Latin character coverage on the first page.
- Cross-check page 1 with pdftotext/liteparse; if the English abstract matters, do not use MinerU alone.
- When there is no independent answer key, report the `bag` (bag of characters) difference, not just order CER.

**Reproduce**: `python3 -I scripts/survey_pdfs.py --root <workspace> --dirs "<dir1,dir2>"` to sample Chinese documents, then `scripts/sample_real.py --root <workspace>` for the 2-page smoke; details in `benchmarks/private/real-smoke.md` (gitignored).

---

## 19. pdfplumber detecting a table ≠ correct cell text

**Measured (real standard tables)**:

- WS/T 578.1—2017 p8: the `lines` strategy finds 27×13, but the three-level merged header is flattened; the `text` strategy becomes 50×13, and the Chinese cell `重(III)` is split into two columns.
- GB 28050—2025 p6: the `lines` strategy finds 29×4 with the right row count, but multi-line cells are in scrambled reading order; the Chinese cell text (Chinese sample: "单不饱和脂肪（或单不饱和脂肪酸）") is split and interleaved; the `text` strategy becomes 76×6.
- China Food Composition Tables, 6th edition, volume 1, p246: `lines` finds 0 tables; `text` finds 45×4, still unusable.

**Fix**: For complex merged headers/multi-line cells prefer `docling`; pdfplumber is only for simple grids/coordinates. For borderless Chinese tables you can try `vertical_strategy="text"`, but accept that merged cells will be split.

**Reproduce**: See the "Real high-frequency tables" subsection in `docs/benchmarks.md`.

---

## 20. Docling tables: use `--no-ocr` for a clean text layer, enable OCR only for a bad one

**Measured**:

- GB 28050 p6, GB 2760 p13, WS/T 578.1 p8: `--no-ocr` gives the best structure and reading order (3–5s/page).
- DRIs 2023 p65: the text layer itself turns ● into `.` and ○ into `。`; `--no-ocr` copies the wrong characters verbatim. Enabling OCR restores the Chinese names, but the symbols still do not retain their original glyphs.
- China Food Composition Tables p246: `--no-ocr` outputs many wrong characters (Chinese sample: "宣物丢", "十酸"); only after enabling OCR is it usable, but lines at the top/bottom of pages are still misaligned.
- Chinese borderless table (`zh-table-borderless.pdf`): Docling outputs 0 tables; `pdfplumber`'s text strategy instead gives 1.000.

**Fix**: Run the text-layer probe first; use `--no-ocr` for a clean text layer and the default OCR for a bad text layer/scan. For books, run only `--page-range`; create the `--output` directory with `mkdir -p` first, otherwise output goes to the current directory.

**Reproduce**: See the "Real high-frequency tables" subsection in `docs/benchmarks.md`.

---

## 21. Symbol tables (●/○): no tool preserves them perfectly

**Measured (DRIs 2023 p65 "Minerals Overview / Vitamins Overview")**:

| Tool | Chinese names | ●/○ distinction | Original symbols |
|---|---|---|---|
| MinerU | Correct | blank / O | No |
| Docling no-OCR | 5 mineral names wrong | `.` / `O` | No |
| Docling OCR | Correct | `.` / `O` | No |
| pdfplumber | — | 0 tables / 69×9 unusable | No |

**Fix**: For symbol tables, use only "established/not established/not covered" as binary/ternary states; do not claim the ●/○ glyphs are preserved; spot-check against the original page manually before delivery. When exact symbols are needed, use a page screenshot or manual transcription.

**Reproduce**: `docling convert FILE --page-range 65 --no-ocr ...` and `mineru parse FILE --pages 65 ...`.

---

## 22. A page with only one small table may be judged a scan by the text-layer probe

**Measured**: `zh-table-merged.pdf` has only a 4×3 table with a 47-character text layer; `route.py`'s threshold is `chars < 50` → `status=scan` → routed to MinerU. It is actually a text-layer table.

**Fix**: The probe is a heuristic, not a verdict. When you confirm the PDF has a text layer (`pdftotext` produces text, `bad_ratio` is low), call `pdfplumber` / `docling` directly for the table goal; do not force OCR just because `status=scan`. Conversely, for a real scan, do not trust the text layer even if OCR yields a few characters.

**Reproduce**: `python3 -I scripts/route.py benchmarks/fixtures/tables/zh-table-merged.pdf --goal table-structure`.

---

## 23. Routing a whole book looks only at the first 3 pages and cannot represent later table pages

**Measured**: The first 3 pages of DRIs 2023 have a usable text layer, and `route.py --goal table-structure` selects Docling; but the text layer on page 65's ●/○ symbol table is bad, and Docling `--no-ocr` copies the wrong characters verbatim, so you must enable OCR on the **target page** or switch to MinerU.

**Fix**: Do not run a book/standard directly with a whole-book routing result; locate the target page first, run a small probe on that page with `pdftotext -f PAGE -l PAGE` or `pdfplumber`, then decide between `--no-ocr` / OCR / MinerU. Routing is a file-level heuristic, not a page-level verdict.

**Reproduce**: Compare `pdftotext -f 65 -l 65 FILE -` with `mineru parse FILE --pages 65 ...`.

## 24. Unquoted `: ` in SKILL.md frontmatter can silently remove the skill

**Measured**: Appending ` English: Chinese/English-first ...` to the `description` value produced invalid YAML. Claude Code still loaded the skill, but DSH's catalog omitted `docarbiter` entirely: a headless English prompt routed to Docling instead, and the session log had 0 mentions of `docarbiter`. After replacing the colon with a dash and front-loading the English description, the same prompt loaded `docarbiter` and routed MinerU.

**Fix**: Keep frontmatter values free of an unquoted `: `; use a dash or quote the value. `scripts/validate.py` now rejects an unquoted `: ` in any skill's frontmatter. Treat "skill silently absent from one harness" as a YAML/catalog-parse issue before debugging the harness.

**Reproduce**: Put `description: test: value` in a SKILL.md, start a new DSH session, and check the available-skills catalog; then change it to `description: test - value` and repeat.

---

## Unverified / to be added

- [ ] Behavior on Linux / Windows (especially the MinerU service and PaddleOCR installation)
- [x] CER of Tesseract `chi_sim` vs RapidOCR on Chinese scans (RapidOCR 1.16% / Tesseract 10.1%)
- [x] Synthetic interleaved two-column, traditional Chinese, CID/no ToUnicode, vertical-text simulation
- [x] Structure and spot checks of 5 real frequently used tables (WS/T 578.1, GB 28050, DRIs 2023, GB 2760, China Food Composition Tables)
- [ ] Cell-by-cell CER for real tables (currently only structure/spot checks; cannot be called accuracy)
- [ ] CER for real English two-column, headers and footers (synthetic interleaved two-column already tested)
- [ ] Chinese and English performance of Marker / Surya / olmOCR
- [x] `liteparse` behavior on Chinese PDFs without ToUnicode (garbled)
