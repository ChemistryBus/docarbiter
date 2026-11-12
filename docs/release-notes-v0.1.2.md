# v0.1.2 — Maintenance and Evidence Update

Released 2026-11-12.

This release updates the Docling pin to **2.150.0** and records the maintenance checks and
evidence added since v0.1.1. It does **not** change the goal mapping or the default routing
chain.

## Changed

- **Docling 2.150.0** replaces 2.149.0 in `requirements-core.lock`, `registry.json`,
  `doctor.sh`, and the tool docs. The pin set was installed in a fresh venv with MinerU
  4.1.7, OCRmyPDF 17.12.1, liteparse 2.18.0, MarkItDown 0.1.9, RapidOCR 3.10.0, and
  pdfplumber 0.11.10; `pip check` is clean and `route.py --selftest` is 24/24.
- **Harness registry as the single source of truth.** `registry.json` now describes each
  harness directory and install shape. `install.sh` and `doctor.sh` read it through
  `scripts/harness_registry.py`, so adding a harness no longer requires editing two shell
  scripts.
- **Router/skill consistency check.** `scripts/check_skill_consistency.py` verifies that
  every router goal appears in `SKILL.md`, every routed tool is mentioned, README versions
  match, and Camelot is not in the default simple-table chain.
- **Weekly upstream probe.** `.github/workflows/probe-upstream.yml` runs every Monday and
  opens or updates an `upstream-probe` issue when a pinned tool is behind PyPI or GitHub
  releases. `scripts/check_updates.py` lists known blockers next to each pinned tool.
- **MinerU wrapper forward compatibility.** `mineru-doc` now recognises the MinerU 4.2.1
  "No basic, standard, or advanced engine available" message (including the comma form)
  as a configuration error and exits 3 immediately instead of retrying.

## Held pins

| Tool | Pinned | Why it is held |
|---|---|---|
| MinerU | 4.1.7 | 4.2.1 `--tier flash` works and the 4.1.7 server accepts the 4.2.1 client, but an isolated 4.2.1 server could not find a parse engine even after configuring the managed tier. The server path is unvalidated. |
| OCRmyPDF | 17.12.1 | 17.14.1 improves scan CER from 0.1012 to 0.0708 on the `zh-scan` fixture, but requires Pillow>=13 while MinerU's gradio requires Pillow<13. The two cannot coexist in the core environment. |
| PaddleOCR / Marker / Unstructured / olmOCR | not installed | Intentionally skipped; they remain documented optional routes. |

## Evidence added

- **Full-text CER on five real two-column papers**, with independent PMC JATS or ar5iv
  truth: BERT, Cell 2020 MoTrPAC Perspective, ResNet, Nature Communications 2026, and PLOS
  Computational Biology 2026. Figures, tables, and references are excluded, and
  `start+end` anchor validity plus a 0.5–1.5 coverage gate must pass.
- **Per-cell CER on three real table pages** with hand-checked truth: WS/T 578.1 p8
  (25×13), GB 28050 p6 (29×4), and GB 2760 p13 (27×4). Merged cells use `""` for covered
  positions.
- **True vertical rerun** on the Chrome `vertical-rl` fixture reproduced the 2026-11-09
  values: Docling 26.67%, MinerU 29.52%, MarkItDown 41.90%, pdftotext 78.10%, liteparse
  90.48%, pdfplumber 97.14%. No tool is usable without manual review.
- **Docling 2.150.0 recheck** produced identical real-table and full-text CERs to 2.149.0.

## Verified

- `python3 -I scripts/validate.py`
- `python3 -I scripts/check_skill_consistency.py`
- `python3 -I scripts/route.py --selftest` (24/24)
- `python3 -I scripts/check_pagemarkers.py`
- `bash -n` on all shell scripts; `py_compile` on all Python files
- macOS arm64, Python 3.11.11; the GitHub Actions `validate` workflow covers Ubuntu and
  macOS. Windows is not verified.

## Known limitations

- Five papers and three table pages are evidence, not a general accuracy claim. Results do
  not transfer to arbitrary scans, layouts, or editions.
- Scans, CID/no-ToUnicode fonts, mixed traditional/simplified text, and the remaining real
  tables are still open.
- `extra` / `full` profiles are not individually benchmarked.
- Codex with a very large skill catalog may still need an explicit "use docarbiter" or a
  smaller catalog.

See [`docs/benchmarks.md`](benchmarks.md) for the full numbers and caveats, and
[`docs/decisions.md`](decisions.md) for the upgrade evaluation.
