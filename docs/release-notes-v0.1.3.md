# v0.1.3 — Chinese Corpus Routing Fixes

Released 2026-11-14.

This patch fixes two real failures found in a 43-file Chinese document corpus:
language misclassification and hidden vendor OCR layers. It does **not** change the goal
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
- **Long OCR documents get a page-range warning.** Documents over 50 pages with a scan,
  mixed, garbled, or hidden-OCR layer now warn to start with a 10–20 page range and extend
  after a spot check. Seven files in the audit were 78–214 pages.
- **Probe output exposes the new signals.** `--json` and the human output now include
  `cjk_share`, `fonts_total`, `fonts_no_unicode`, and `hidden_ocr`. The skill's inline
  probe snippet and decision table match the executable router.

## Evidence

The audit covered 43 private PDFs: 122 MB, mostly Chinese journal articles plus nine
long theses (largest 214 pages). It is a routing/probe audit, not an accuracy benchmark.
Results: 31 usable text layers, 10 mixed documents, 1 pure scan, and 1 hidden OCR layer.
Four scanned theses had 30/81, 71/108, 4/88, and 124/214 pages above the 10%
bad/control-character threshold. See [`docs/benchmarks.md`](benchmarks.md) section 5-14.

The private PDFs are gitignored and are not redistributed. No CER or table-accuracy score
is claimed for this corpus.

## Verified

- `python3 -I scripts/route.py --selftest` (31/31)
- Re-probe of all 43 PDFs: no English paper was moved to `zh`; only the hidden-OCR thesis
  changed status
- `python3 -I scripts/validate.py`
- `python3 -I scripts/check_skill_consistency.py`
- `bash -n` on all shell scripts; `py_compile` on all Python files

## Known limitations

- The corpus comes from one review topic and does not generalise to arbitrary Chinese
  scans, layouts, or publishers.
- Hidden-OCR detection relies on font names. A vendor that names its OCR layer differently
  will not be caught; spot-check suspicious scans.
- MinerU OCR is not error-free: the sample page still had a 肉苁蓉 / 肉从蓉 confusion.
- Scans, CID fonts, mixed traditional/simplified text, and the remaining real tables
  remain open.

See [`docs/benchmarks.md`](benchmarks.md) and [`docs/decisions.md`](decisions.md) for
scope and caveats.
