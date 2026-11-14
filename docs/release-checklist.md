# Pre-Release Checklist

> Status: **v0.1.3 — Chinese Corpus Routing Fixes released** (2026-11-14). `v0.1.0` was the first public release; `v0.1.1` added harness compatibility; `v0.1.2` updated Docling and evidence; `main` now also includes hidden-OCR, FzBookMaker, and Chinese-language routing fixes.
> See [`docs/release-plan.md`](release-plan.md) for the release plan and execution log.
> Current progress (2026-11-11): 11 bilingual synthetic samples + 4 real CC BY-SA Wikipedia samples + CID/traditional-Chinese/interleaved two-column/true vertical-writing edge samples + 6 text-layer tools + 2 OCR paths + clean venv install + read-only sampling of 8,444 real PDFs in the workspace (48+24 samples, 4-file smoke) + P0 policy benchmark (22 documents with answer keys) + 5 real high-frequency tables (WS/T 578.1, GB 28050, DRIs 2023, GB 2760, China Food Composition Tables) are complete; P1 verify negative results are not published, P2 real-table routing is complete (Docling/MinerU/pdfplumber), P3 default policy is set, Claude Code P4 real triggering is complete (old doc-extract backed up and disabled), DSH headless triggering passed and was permanently switched (global .agents old route backed up), ZCode / MiniMax top-level fully passed, Codex conditionally passed (full skill-set capacity limit); real-table per-cell CER is complete for WS/T 578.1 p8, GB 28050 p6, and GB 2760 p13; full-text two-column CER is complete for BERT, Cell Perspective, ResNet, Nature Communications, and PLOS Computational Biology; full true-vertical writing, full-text CER on more papers, the remaining real tables, and extension-layer tools are not yet complete.
> The goal of this checklist: turn "it runs" into "reproducible, explainable, maintainable."

## 0. Release gates (decide first)

- [x] Version: `v0.1.3 — Chinese Corpus Routing Fixes` (v0.1.0 was the First Public Preview; v0.1.1 was the Harness Compatibility Patch; v0.1.2 was the Docling/evidence update)
- [ ] Support scope documented clearly: tested on macOS arm64; Linux x86_64 pending verification; Windows not verified
- [ ] Python versions: 3.10 / 3.11 / 3.12; 3.11.11 tested
- [ ] Default install profile: `core`; `extra` / `full` marked "not individually tested"
- [ ] No AGPL / Proprietary tool code or models are distributed
- [x] `README.md` (Chinese, GitHub default) and `README.en.md` (English) have identical content, switchable at the top
- [ ] All "pending test" items are visible in the release notes, not hidden

## 1. Clean-environment install

- [x] macOS arm64 clean venv: `/tmp/docarbiter-release-venv`, Python 3.11 (rerun 2026-11-10)
- [x] Core pin set installed in a fresh venv: MinerU 4.1.7 / Docling 2.150.0 / liteparse 2.18.0 / MarkItDown 0.1.9 / RapidOCR 3.10.0 / OCRmyPDF 17.12.1 / pdfplumber 0.11.10; `pip check` clean; route selftest 32/32 (2026-11-14; it was 24/24 when the venv was built on 2026-11-12). The earlier `install.sh --profile core` run used Docling 2.149.0.
- [x] `install.sh` does not upgrade already-installed Homebrew formulae (`skip (no upgrade)` for poppler etc.)
- [x] Isolated HOME + `install.sh --skills-only`: wrapper + symlink created successfully
- [x] `doctor.sh` exits 0 under isolated HOME, no MISSING in core (MinerU model not downloaded is expected)
- [x] `install.sh --force` backs up + symlinks; without `--force` it skips with a warning
- [ ] Record each failure of `./scripts/install.sh --profile extra` individually (not required to be all green)
- [ ] Run the same set on Linux x86_64 (Docker/VM); record differences
- [ ] For Windows / WSL, at least record "not verified" or known issues
- [ ] With paths containing spaces, Chinese characters, or parentheses, the wrapper and `bench.py` still work
- [ ] For offline environments: provide model pre-download / offline install instructions (at least MinerU / Docling)

> During the 2026-11-10 clean install, direct PyPI access was very slow, so the Tsinghua mirror was used; versions are still pinned by `requirements-core.lock`, and the mirror only affects download speed. The release process does not depend on the mirror.

## 2. Chinese and English corpora

### Chinese

- [ ] Normal text-layer PDF
- [ ] CID subset fonts / no ToUnicode
- [ ] Scanned documents (one at 300dpi, one at 150dpi)
- [x] Interleaved two-column (synthetic, content stream interleaved line by line; markitdown failure not reproduced, pdfplumber fails)
- [x] Real CC BY two-column paper abstract CER (BERT, ACL N19-1423; markitdown/pdfplumber 73%)
- [x] Real two-column full-text CER on BERT (ar5iv), Cell 2020 MoTrPAC Perspective (PMC JATS), ResNet (ar5iv), Nature Communications 2026 (PMC JATS), and PLOS Computational Biology 2026 (PMC JATS); abstract + main body, references/figures/tables excluded
- [ ] Full-text CER on more papers and layouts (Cell/Nature Communications/PLOS coverage is 1.08–1.30 because their output includes figure/SI text; the Nature 2024 MoTrPAC flagship needs a full-article scope because its Methods/Extended Data exceed the main-body scope)
- [x] Ruled / merged-cell cell accuracy (pdfplumber 1.000; merge semantics still need manual spot checks)
- [x] Borderless tables: default detects 0 tables; text strategy 1.000/0.917, but merged cells drop to 0.667/0.583; strategy must be chosen per page with spot checks
- [x] Real high-frequency table structure and spot checks (WS/T 578.1, GB 28050, DRIs 2023, GB 2760, China Food Composition Tables; routed to Docling/MinerU/pdfplumber)
- [x] Real-table per-cell CER on WS/T 578.1 p8, GB 28050 p6, and GB 2760 p13 (hand-checked truth; WS/T 0.0000 for pdfplumber default / Docling / MinerU; GB 28050 Docling 0.0000, MinerU 0.1237, pdfplumber default 0.3010; GB 2760 pdfplumber default / Docling 0.0000, MinerU 0.1071 nopunct CER)
- [ ] Real-table per-cell CER on the remaining real tables and other editions (do not generalise the three-page result)
- [ ] Symbol tables (●/○) fidelity: currently both MinerU/Docling preserve only binary state, not the original glyphs
- [x] Traditional Chinese (`zh-traditional`)
- [ ] Mixed traditional and simplified Chinese
- [ ] True vertical writing (vertical writing mode, columns right to left; currently only a one-character-per-line simulation)
- [x] Footnotes / figure captions (synthetic)

### English

- [ ] Normal text-layer PDF
- [ ] Two-column papers
- [ ] Table pages
- [ ] Hyphenated line breaks / quotation marks / em dashes
- [ ] Scanned documents
- [ ] Header/footer interference

### Answer keys and metrics

- [ ] Each sample has an independent answer key (source text / manual proofreading / CC BY-SA source text)
- [ ] **No** `pdftotext` output is used as the answer key
- [ ] CER normalization rules fixed (NFC, whitespace removed, punctuation retained)
- [ ] Report per-page CER, median, IQR, **worst page**
- [ ] Cold start and warm start kept separate
- [ ] Record tool versions, corpus commit, machine

## 3. Tool coverage

### core (8 by default)

- [ ] MinerU: ≥ 2 samples each for Chinese and English
- [ ] Docling: Office / HTML / PDF / chunks / LaTeX
- [ ] liteparse: text-layer PDFs; punctuation-normalization behavior documented
- [ ] MarkItDown: single-column; two-column failure not reproduced (synthetic), real two-column pending test; scanned documents unsupported
- [ ] RapidOCR: Chinese images / screenshots
- [ ] OCRmyPDF: scanned document → searchable PDF → MinerU
- [ ] pdfplumber: tables / coordinates; interleaved two-column 60%–68% (documented)
- [ ] pdftotext: baseline / text-layer probe

### extra / optional

- [ ] PaddleOCR: Chinese OCR / PP-Structure
- [ ] Marker: once each on GPU / CPU; Chinese CER
- [ ] Unstructured: multi-format partitioning; Chinese language code
- [ ] olmOCR: GPU; Chinese CER
- [ ] Surya / Camelot / Tesseract / qpdf / pypdf / pdfminer.six: at least a smoke test
- [ ] Tools that are not installed / fail are marked optional in `doctor.sh` and do not block core

## 4. Router tests

- [ ] Chinese text-layer PDF → expect `liteparse` / `mineru`
- [ ] Chinese scanned document → expect `ocrmypdf` → `mineru`
- [ ] English two-column PDF → expect `mineru` / `docling`, not `markitdown`
- [ ] Simple grid table → expect `pdfplumber` (`--goal table`)
- [ ] Complex merged headers/multi-row cells → expect `docling` (`--goal table-structure`)
- [ ] Scanned / bad text-layer tables → expect `mineru`
- [ ] Office → expect `docling`
- [ ] Images → expect `rapidocr`
- [ ] User explicitly specifies a tool → bypasses the router
- [ ] Tool missing → provide install command + fallback plan, no silent failure
- [ ] Unsatisfactory result → fallback chain is explainable
- [ ] Sensitive documents are not sent to cloud APIs by default

## 5. Harness compatibility

Four harnesses on this machine: Claude Code / Codex / zcode / DSH.

- [x] `docarbiter` is discovered correctly in Claude Code (2026-11-10, `docs/p4-claude-code.md`)
- [x] In Claude Code, the description triggers on Chinese/English prompts "extract PDF", "convert to Markdown", "which tool should I use" (Haiku, neutral directory)
- [x] Claude Code does not also activate the old `doc-extract` (backed up and disabled; other harnesses untouched)
- [x] DSH permanently switched: old `doc-extract` backed up and disabled; Chinese/English headless prompts trigger only `docarbiter` (2026-11-10)
- [x] DSH also handled the global `~/.agents/skills/doc-extract`; the old-route copies for Codex / ZCode are preserved and not broken
- [x] ZCode top-level fully passed: Chinese/English implicit triggering of `docarbiter` → MinerU
- [x] Codex conditionally passed: explicit invocation passes; implicit passes with a minimal skill set; implicit is affected by capacity with all 620 skills
- [x] MiniMax top-level fully passed: Chinese/English implicit triggering of `docarbiter` → MinerU; scans `.agents/skills`, requires a whole-directory symlink
- [ ] Upgrade verification of `install.sh --skill-mode auto|dir|file` on existing Claude/DSH/ZCode installs (currently only new directories are verified)
- [ ] After `--profile full` registers 12 tool skills, no name conflicts
- [x] `doctor.sh --check-conflicts` detects same-name skills and dual routing (run in isolated HOME + on this machine)
- [x] Coexistence / replacement / rollback steps for the old `doc-extract` have been verified on Claude Code / DSH (`docs/migration.md`)
- [x] README explains "harness-native routing vs docarbiter" (see `docs/harness-routing.md`)
- [x] User's old router is not deleted automatically; replacement requires user confirmation (confirmed this time; only symlinks were moved)
- [x] Uninstall/rollback steps are documented (`docs/p4-claude-code.md`, `docs/migration.md`)

## 6. Compliance audit

- [x] `THIRD_PARTY_NOTICES.md` covers all installed tools (validate checks 18)
- [x] MinerU additional terms present in both English and the original Chinese
- [x] No `pdf` / `pymupdf` / `pdf-extract-kit` under `skills/`
- [x] `install.sh` does not auto-install AGPL tools (links/instructions only)
- [x] Commercial cloud APIs are not on the default path
- [x] README has a "no upstream code included" statement at the top
- [x] License grouping matches `registry.json`
- [x] Model weight provenance (RapidOCR / MinerU / Marker / Surya / olmOCR) is documented
- [x] If an online service is offered in future, the MinerU attribution obligation is already in the README

## 7. Security and privacy

- [x] No hardcoded secrets / tokens (2026-11-10 scan found none)
- [ ] Files are not uploaded to the cloud by default
- [ ] `bench.py` uses `python3 -I`, not hijacked by `json.py` etc. in the cwd
- [ ] Scripts in PDFs are not executed / external links are not opened
- [x] User-owned files go in `benchmarks/private/`; `.gitignore` takes effect
- [x] Logs do not print document body excerpts (or this is explicitly stated)
- [x] No personal absolute paths `/Users/<name>` anywhere in the repo; scripts use `--root` / `DOCARBITER_WORKSPACE`
- [x] `.gitignore` covers `benchmarks/private/`, `blobs/`, `.mineru-service.lock`

## 8. Documentation

- [x] `README.md` English: problem, quick start, routing, tools, verification, install, license
- [x] `README.en.md` English: consistent with Chinese, images in English
- [ ] Images: `docs/assets/overview-zh.svg` / `overview-en.svg` render correctly on GitHub
- [ ] Quick start works within 5 minutes
- [ ] Common failures (missing tool / no GPU / network failure) have troubleshooting paths
- [ ] `docs/architecture.md` explains "many tools can still be routed"
- [ ] Every entry in `docs/gotchas.md` is reproducible
- [ ] `docs/benchmarks.md` has a "don't trust my numbers" disclaimer
- [ ] `docs/licensing-faq.md` answers MinerU / AGPL / GPL questions
- [ ] Screenshots and images contain no real user document content

## 9. CI and repository hygiene

- [x] `python3 -I scripts/validate.py` passes
- [x] `python3 -I scripts/route.py --selftest` passes (all checks, including empty PDF / corrupted PDF / paths with spaces + Chinese; 24 at the time of writing)
- [x] All shell scripts pass `bash -n`
- [x] All Python files pass `py_compile`
- [x] `scripts/check_pagemarkers.py` passes with MinerU and skips cleanly without it
- [ ] `doctor.sh` drift check is clean (only `OTHER-CLONE` notes are acceptable)
- [ ] English docs contain no Chinese prose except labeled Chinese samples and verbatim CLI output
- [ ] CI runs validate + route selftest on push / PR (workflow written, pending remote run)
- [x] CI adds an `install.sh --skills-only` isolated-HOME smoke test (catches `set -u` issues)
- [x] No `__pycache__` / `.DS_Store` / large files (repo is 3.1MB)
- [ ] `registry.json` matches `skills/_tools/`
- [ ] `requirements-core.lock` matches tested versions
- [ ] `requirements-extra.lock` marked "not individually tested"

## 10. Release mechanics

- [ ] `git init` / commit / push only after explicit user consent
- [ ] Remote repository name confirmed (`ChemistryBus/docarbiter`)
- [ ] Default branch `main`
- [x] Tag `v0.1.3`; release notes list known limitations
- [ ] Release notes state: macOS tested, Linux/Windows not verified, extra not individually tested
- [ ] Release notes state: Anthropic `pdf`, PyMuPDF, PDF-Extract-Kit are not included
- [ ] After release, run `doctor.sh` + a two-page demo once to confirm the remote version is reproducible

## 11. Sign-off

| Item | Owner | Date | Result |
|---|---|---|---|
| Chinese corpus / CER | | | |
| English corpus / CER | | | |
| License audit | | | |
| Harness compatibility | | | |
| Documentation / figures | | | |
| Release confirmation | | | |
