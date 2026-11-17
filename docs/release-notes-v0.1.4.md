# v0.1.4 — Dependency Refresh and Probe Hygiene

Release candidate prepared 2026-11-17.

This patch updates two verified core pins and reduces noise from the weekly upstream probe.
It does **not** change routing goals, tool selection logic, or the MinerU/OCRmyPDF pins.

## Changed

- **Docling 2.150.1** replaces 2.150.0. `pip check` is clean and `route.py --selftest` is 32/32. The 3 real-table pages still have `nopunct` CER 0.0000; the 5 full-text papers have identical CERs to 2.150.0.
- **liteparse 2.19.0** replaces 2.18.0. Full-text `nopunct` CER is unchanged on BERT, Nature Communications, PLOS, and ResNet; the Cell alignment remains invalid as before.
- **Probe hygiene.** `check_updates.py --ci` now marks installed versions as `n/a (CI)` instead of falsely reporting every core tool as not installed on the GitHub runner. The workflow skips a comment when the normalized probe output has not changed. Blocker text is now version-range based (`4.2.x`, `17.14.x`).

## Held

| Tool | Pinned | Why |
|---|---|---|
| MinerU | 4.1.7 | 4.2.x flash works, but the isolated server/engine path is not validated. |
| OCRmyPDF | 17.12.1 | 17.14.x requires Pillow>=13; MinerU's gradio requires Pillow<13. |

## Verified

- `python3 -I scripts/validate.py`
- `python3 -I scripts/route.py --selftest` (32/32)
- `python3 -I scripts/check_pagemarkers.py`
- `pip check` clean in the isolated venv
- Docling table benchmark: 3 pages, identical results
- Full-text benchmark: 5 papers, identical Docling and liteparse CERs
- `bash -n` on all shell scripts; `py_compile` on all Python files

## Known limitations

- The table and full-text evidence covers the same 3 table pages and 5 papers; it is not a general accuracy claim.
- MinerU 4.2.x and OCRmyPDF 17.14.x remain open.
- The private corpus and benchmark PDFs are not redistributed.

See [`docs/benchmarks.md`](benchmarks.md), [`docs/decisions.md`](decisions.md), and [`docs/updating.md`](updating.md).
