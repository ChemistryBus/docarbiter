# v0.1.3 — Chinese Corpus Routing Fixes

Released 2026-11-14.

This patch fixes three real failures found in a 63-file Chinese document corpus:
language misclassification, hidden vendor OCR layers, and custom FzBookMaker encoding. It
also fixes a MinerU crash on filenames containing `:`. It does **not** change the goal
mapping, the default tool set, or any pinned tool version.

## Fixed

- **Language detection uses CJK share, not a raw count comparison.** A Chinese paper with
  a long English abstract or reference list can contain more Latin letters than CJK
  characters; the old `cjk > latin` rule then selected `--language eng` for OCR. The rule
  is now `cjk_share >= 0.35` → `zh`, `<= 0.05` → `en`, otherwise `mixed`. Five Chinese
  papers in the audit moved from `en` to `zh`; the five genuinely English papers stayed
  `en`.
- **Hidden OCR layers are detected and re-OCR'd.** Some scanned PDFs ship a vendor text
  layer with fonts such as `HiddenHorzOCR` / `HiddenVertOCR`. `pdftotext` reads that layer,
  so the output can look clean while containing silent character substitutions. In one
  168-page thesis it produced 二秸酚 / 原产千 / 井有 instead of 二萜酚 / 原产于 / 并有.
  `route.py` now reports `status=hidden-ocr` and routes to MinerU. A sample re-OCR
  recovered the correct forms.
- **Custom FzBookMaker encoding is detected.** Two standards produced valid-looking but
  unrelated CJK glyphs (`犅犑犛２０２１０２` instead of `BJS 202102`, `犌犅／犜１．１`
  instead of `GB/T 1.1`) with a near-zero bad-character ratio. `route.py` now reports
  `status=custom-encoding` and routes to MinerU; a one-page re-OCR recovered the titles.
- **MinerU accepts filenames containing `:`.** The MinerU server rejects `:` in the
  uploaded basename, and many CNKI filenames contain it. `mineru-doc` now copies those
  inputs to a safe temporary name before parsing; the original path and output path are
  unchanged.
- **Long OCR documents get a page-range warning.** Documents over 50 pages with a scan,
  mixed, garbled, hidden-OCR, or custom-encoding layer now warn to start with a 10–20
  page range and extend after a spot check. The audit includes seven files of 78–214 pages
  and seven sampling rules of 322–417 pages.
- **Probe output exposes the new signals.** `--json` and the human output now include
  `cjk_share`, `fonts_total`, `fonts_no_unicode`, `hidden_ocr`, and `suspect_encoding`.
  The skill's inline probe snippet and decision table match the executable router.

## Evidence

The audit covered 63 private PDFs in two batches: 43 journal articles and theses (122 MB,
largest 214 pages), plus 20 standards and regulations (including two pure scans, seven
322–417 page sampling rules, and a 34-page landscape standard). It is a routing/probe
audit, not an accuracy benchmark. Results across 63 files: 38 usable text layers, 19 mixed
documents, 3 pure scans, 2 custom-encoding documents, and 1 hidden OCR layer. Four scanned
theses had 30/81, 71/108, 4/88, and 124/214 pages above the 10% bad/control-character
threshold. See [`docs/benchmarks.md`](benchmarks.md) section 5-14.

The private PDFs are gitignored and are not redistributed. No CER or table-accuracy score
is claimed for this corpus.

## Verified

- `python3 -I scripts/route.py --selftest` (32/32)
- Re-probe of all 63 PDFs: no English paper was moved to `zh`; only the hidden-OCR and
  custom-encoding documents changed status
- MinerU on a filename containing `:` succeeds through the safe-copy path and returns the
  correct `GB/T 1.1—2020` title
- `python3 -I scripts/validate.py`
- `python3 -I scripts/check_skill_consistency.py`
- `bash -n` on all shell scripts; `py_compile` on all Python files

## Known limitations

- The corpus is private and does not generalise to arbitrary Chinese scans, layouts, or
  publishers.
- Hidden-OCR detection relies on font names. A vendor that names its OCR layer differently
  will not be caught; spot-check suspicious scans.
- FzBookMaker detection is vendor-specific. Other custom encodings may still look usable;
  spot-check a page before trusting a long extraction.
- Japanese is not supported: one 46-page notification contains 15,997 kana but is
  classified `zh`; the Chinese/English OCR presets are not a Japanese solution.
- MinerU OCR is not error-free: the sample page still had a 肉苁蓉 / 肉从蓉 confusion.
- Scans, CID fonts, mixed traditional/simplified text, and the remaining real tables
  remain open.

See [`docs/benchmarks.md`](benchmarks.md) and [`docs/decisions.md`](decisions.md) for
scope and caveats.
