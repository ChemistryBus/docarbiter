# Design Decisions and Evidence

> Status: 2026-11-11. This document records settled decisions, verified external facts, and items still pending verification.

## 1. Settled Decisions

| # | Decision | Conclusion |
|---:|---|---|
| 1 | Distribution model | Thin-shell pull. The repository contains only self-authored documentation and install scripts, no upstream code |
| 2 | Anthropic `pdf` skill | Link only, not included (Proprietary) |
| 3 | PyMuPDF | Excluded (AGPL-3.0), link only |
| 4 | Repository license | MIT |
| 5 | Repository name | `ChemistryBus/docarbiter` (no exact same-name repository on GitHub) |
| 6 | Dispatcher skill name | **`docarbiter`** (available as GitHub user/repository, on PyPI, and on npm) |
| 7 | Packaging topology | By default only one skill, `docarbiter`, is registered; tool thin shells live in `skills/_tools/`; only `install.sh --profile full` registers standalone skills |
| 8 | First-release scope | 12 primary tools + 6 optional supplements; AGPL and commercial APIs appear only in the "not included" table |
| 9 | Chinese corpus | Synthetic PDFs + CC BY-SA Chinese Wikipedia + public-domain Wikisource; user-owned files are used only for local smoke tests |
| 10 | Language coverage | **Both Chinese and English are guaranteed**; corpus, CER, routing, and tool docs all cover both languages |
| 11 | Collection scale | The tool set can keep growing; `registry.json` is the source of truth; by default only one dispatcher is registered; adding a tool in an existing category does not change the dispatcher |
| 12 | Release cadence | **Do not release yet**; first verify against `docs/release-checklist.md`; README in Chinese and English + illustrations |
| 13 | Using MinerU | This project is non-profit, provides no online service, and does not redistribute code/models; current usage does not trigger the additional terms; the original text is kept in notices |

## 2. Naming Evidence (2026-11-09)

`docarbiter` search results:

| Location | Result |
|---|---|
| GitHub user/org `github.com/docarbiter` | 404 |
| GitHub repository `github.com/docarbiter/docarbiter` | 404 |
| GitHub repository search `docarbiter in:name` | 0 results |
| PyPI `docarbiter` | 404 |
| npm `docarbiter` | 404 |
| Web search | No project with the same name |

Meaning: `docarbiter` = document + arbiter. It does not extract by itself; it adjudicates among competing tools, which matches the dispatcher's role.

> Note: GitHub already has `misbahsy/doc-router` (document OCR routing), `MeZyV/doc_extraction_router` (OpenWebUI document parsing routing), `horizon123104/PdfRouter`, and `yidingwanglnsy-boop/PDFROUTER`. The concepts are similar, but all the names differ; do **not** use `doc-router` / `docrouter` / `pdfrouter`.

## 3. Verified Local Facts

| Tool | Local version | License (package metadata) | CLI |
|---|---|---|---|
| liteparse | 2.18.0 | Apache-2.0 | `liteparse-doc` |
| markitdown | 0.1.9 | MIT | `markitdown` |
| mineru | 4.1.7 | `LicenseRef-MinerU-Open-Source-License` | `mineru-doc` / `mineru` |
| docling | 2.149.0 | MIT | `docling` |
| rapidocr | 3.10.0 | Apache-2.0 | Python API |
| ocrmypdf | 17.12.1 | MPL-2.0 | `ocrmypdf` |
| pdfplumber | 0.11.10 | MIT | Python API |
| pdftotext (Poppler) | 26.11.0 (26.08.0 at measurement time; Homebrew upgraded it during a clean install) | GPL-2.0-only OR GPL-3.0-only | `pdftotext` |
| pymupdf | 1.28.2 | AGPL-3.0 / commercial dual license | Python API (not included) |

## 4. GitHub Snapshot (stars / license, 2026-11-09)

| Repository | ★ | SPDX |
|---|---:|---|
| microsoft/markitdown | 194,491 | MIT |
| PaddlePaddle/PaddleOCR | 92,460 | Apache-2.0 |
| opendatalab/MinerU | 83,343 | NOASSERTION (custom: Apache-2.0 + additional terms) |
| tesseract-ocr/tesseract | 77,417 | Apache-2.0 |
| docling-project/docling | 70,315 | MIT |
| datalab-to/marker | 40,822 | Apache-2.0 |
| ocrmypdf/OCRmyPDF | 35,272 | MPL-2.0 |
| datalab-to/surya | 21,587 | Apache-2.0 |
| allenai/olmocr | 19,818 | Apache-2.0 |
| Unstructured-IO/unstructured | 15,701 | Apache-2.0 |
| run-llama/liteparse | 13,020 | Apache-2.0 |
| jsvine/pdfplumber | 10,884 | MIT |
| py-pdf/pypdf | 10,291 | BSD-3-Clause (GitHub marks NOASSERTION) |
| opendatalab/PDF-Extract-Kit | 10,075 | AGPL-3.0 |
| RapidAI/RapidOCR | 8,486 | Apache-2.0 |
| pdfminer/pdfminer.six | 7,048 | MIT |
| qpdf/qpdf | 5,563 | Apache-2.0 |
| camelot-dev/camelot | 3,849 | MIT |

## 5. Licensing Points

### MinerU

The package metadata is `LicenseRef-MinerU-Open-Source-License`; the text is Apache-2.0 + additional terms. The actual content of the additional terms:

- Commercial use is permitted by default; however, when consolidated MAU > 100 million or monthly revenue > 20 million USD, a separate commercial license must be obtained.
- When providing an **online service** to third parties based on MinerU, you must prominently state that MinerU is used, in the interface or public documentation.
- Violating the above two conditions automatically terminates the license.

`THIRD_PARTY_NOTICES.md` must include the original text (English + Chinese); it cannot merely say "Apache-2.0 + additional terms".

### RapidOCR

Apache-2.0, but the model weights come from PaddleOCR / Baidu, and the package also contains `MODEL_LICENSES.md`. Distribution or redistribution must retain the model source and copyright notice. This repository only calls it and does not redistribute the models.

### Poppler / pdftotext

GPL-2.0-only OR GPL-3.0-only. This repository only invokes the command line through the system package, without modification or redistribution; the repository's own MIT license is unaffected. If the `pdftotext` binary is packaged into a distribution, this must be evaluated separately.

### pypdf

GitHub identifies the license as NOASSERTION; the actual `LICENSE` is BSD-3-Clause style (copyright header + three clauses). The original text in `THIRD_PARTY_NOTICES.md` is authoritative.

## 6. Corrections to the Handoff Document

### Correction 1: Chinese evaluation cannot use "order similarity vs pdftotext"

- Chinese has no spaces, so word-level similarity is unusable; use **CER (character error rate)** instead.
- `pdftotext` is another tool, not ground truth; agreeing with it ≠ accuracy.

### Correction 2: The text-layer detection threshold is insufficient

"> 200 characters = has a text layer" is fooled by damaged CID fonts: the character count passes but the content is garbled. Detection must report all of:

- character count;
- share of `U+FFFD` and private-use-area characters;
- coverage of common Chinese characters (first 3 pages);
- conclusion: usable / suspected garbled / scanned.

### Correction 3: 8 top-level skills would recreate "a mess"

Changed to a single default entry point `docarbiter` + optional registration via `--profile full`. The 7+ tool docs live in `skills/_tools/` and do not participate in harness skill discovery.

### Correction 4: `install.sh` must pin versions

Thin-shell commands are tested against local versions; without pinned versions, an upstream parameter change causes drift. `requirements.lock` + `doctor.sh` version checks.

### Correction 5: markitdown two-column — not reproduced on synthetic plain text, breaks on real papers with figures

- **Synthetic plain text, content stream interleaved line by line**: on 0.1.9 markitdown CER **0**; pdftotext / liteparse / MinerU 0; **pdfplumber 60%–68%**. So "markitdown never handles two columns" was not reproduced on a clean sample.
- **Real paper (ResNet, arXiv:1512.03385, 3 pages, local private)**: markitdown outputs many Markdown tables/axis labels, and the abstract is broken up; pdfplumber loses spaces and mixes in axis labels; the abstract from MinerU / Docling / liteparse is readable. No answer key, so no CER.
- Conclusion: do not overgeneralize in either direction. It passes on clean two-column; it breaks on real two-column with figures. Prefer MinerU / Docling / liteparse for real two-column.

### Correction 6: The dispatcher must also be included in name-collision/dual-router detection

The machine already has `doc-extract` active in four harnesses. `docarbiter` overlaps with it functionally but is not a same-name collision; `doctor.sh --check-conflicts` must detect both:

- same-name tool skills;
- two document-extraction routers active at the same time.

## 7. MinerU Usage Conclusion (2026-11-09)

Question: MinerU is Apache-2.0 + additional terms; can we use it?

Conclusion: **Yes.** The additional terms are triggered only in two cases:

1. consolidated MAU > 100 million, or monthly revenue > 20 million USD → a commercial license is required;
2. providing an online service to third parties based on MinerU → prominent attribution is required.

This project is non-profit, provides no online service, and does not redistribute MinerU code or models; it only invokes the CLI on the user's local machine. Current usage therefore does not trigger the additional terms. If an online service is built in the future, MinerU must be credited in the interface/docs; if the thresholds are reached, contact the MinerU team.

The original text is included in `THIRD_PARTY_NOTICES.md`; a plain-language explanation is in `docs/licensing-faq.md`.

## 8. Language and Scale (added 2026-11-09)

- **Language**: Chinese and English are both first-class citizens. For Chinese, test CID/ToUnicode, scans, traditional/simplified, and vertical text; for English, also test two-column layout, hyphens, quotes/dashes, and headers/footers. Scores from testing only one language cannot be extrapolated.
- **Scale**: tools can keep being added, but by default only one skill, `docarbiter`, is registered. A new tool = one record in `registry.json` + an optional thin shell; only a new category changes the dispatcher. This way N tools do not produce N² cross-references, and N top-level skills do not compete for work.
- **Release**: currently a skeleton, not a release. It must pass `docs/release-checklist.md` before release; the README must have both Chinese and English versions, with illustrations explaining the problem and the target audience.

## 9. Still to Be Verified

- [ ] Chinese and English CER for the 12 primary tools (text layer / scan / two-column / tables / mixed traditional-simplified)
- [ ] CLI entry points and Chinese/English performance for Marker / Surya / Unstructured / olmOCR
- [ ] Separate licenses for MinerU / Marker / Surya model weights
- [ ] `liteparse` behavior on Chinese PDFs without ToUnicode
- [ ] `docling` default OCR backend and Chinese model
- [ ] Official English URL of the MinerU additional terms (for notices citation)
- [ ] Real CC BY-SA articles, CID/no-ToUnicode, and traditional-simplified/vertical samples

## 10. New Conclusions This Round (2026-11-09, v0.3)

### Corpus and Metrics

- 11-document bilingual synthetic smoke corpus: text layer / two-column / tables / footnotes / scans / English end-of-line hyphens.
- For all tools **no-punct CER = 0.0000**; the residual in `cer_text` comes entirely from punctuation normalization (MinerU full-width colon/semicolon → ASCII, liteparse/markitdown quotes/dashes → ASCII). `bench.py` therefore outputs both `cer_text` and `cer_nopunct`.
- Empty output/scans: `pdftotext` and `markitdown` error on both scanned documents, `liteparse` empty; MinerU/Docling can OCR directly. `bench.py` adds coverage < 5% → `empty`, excluded from CER aggregation.

### Edge Samples (CID / Traditional / Interleaved Two-Column / Simulated Vertical)

- **CID/no ToUnicode**: pdftotext / liteparse / markitdown / pdfplumber / Docling all garbled; MinerU can OCR, CER 4.95%. The probe must include the control-character ratio, not just the character count.
- **Traditional Chinese**: all tools basically correct; MinerU's 1.72% is punctuation normalization.
- **Interleaved two-column**: pdftotext / liteparse / markitdown / MinerU 0; pdfplumber 60%–68%; Docling 2%–3%. This corrected the earlier claim that "markitdown fails on two-column".
- **Simulated vertical**: pdftotext / markitdown / pdfplumber / Docling 0; liteparse 34.78%, MinerU 13.04%. This is simulated, not true vertical text.
- Generation script: `benchmarks/fixtures/edge/make_edge.py`; CID depends on LibreOffice + pypdf and is used only to generate fixtures.

### True Vertical / Real Two-Column / Tables (2026-11-09)

- **True vertical** (Chrome `writing-mode: vertical-rl`): all tools perform poorly. Docling 26.7%, MinerU 29.5%, markitdown 41.9%, pdftotext 78.1%, liteparse 90.5%, pdfplumber 97.1%. Conclusion: do not assume any tool is usable for true vertical text; manual inspection is required. Re-ran 2026-11-12 with the current versions: identical CERs (Docling 26.67%, MinerU 29.52%, markitdown 41.90%, pdftotext 78.10%, liteparse 90.48%, pdfplumber 97.14%).
- **Real two-column paper** (ResNet, arXiv:1512.03385, 3 pages, local `benchmarks/private/`): the abstract from MinerU / Docling / liteparse is readable; markitdown is broken up by figures/axis labels; pdfplumber loses spaces between words. No answer key, so no CER.
- **Table cell level** (pdfplumber, 6 fixtures): under the default strategy, bordered / merged **1.000**; borderless **0 tables / 0.000**. The `text` strategy rescues borderless (**1.000/0.917**), but merged drops to **0.667/0.583**, and English is also truncated (`half z`). No one-size-fits-all setting; in practice, run both strategies on the same page and spot-check. The 1.000 for merged only proves row/column alignment, not merge semantics.
- Machine constraints: still 16GB / no GPU; no extension layer installed. Chrome is used only to generate the true-vertical fixture and exits when done.

### Real CC BY Two-Column Paper Abstract CER (BERT, 2026-11-09)

- Source: BERT, NAACL 2019, ACL Anthology N19-1423, CC BY 4.0; the first 2 pages of the PDF + the HTML abstract as the answer key.
- Results: MinerU 0.44%; pdftotext / liteparse / Docling 0.65%; **markitdown / pdfplumber 73%** (no-punct still 73%; it is reading order/mixed layout, not punctuation).
- Only the abstract is scored; full text, figures, tables, and references are not scored.

### Real CC BY-SA Samples (4 documents)

- 2 Chinese and 2 English Wikipedia articles, excerpted at about 2,200 / 3,200 characters and rendered as 1–2 page text-layer PDFs.
- `no-punct CER` all **0.0000**; `cer_text` 0.02%–2.5%, with the residual also being punctuation (MinerU worst at 2.51%, no-punct 0).
- These four fixtures are **CC BY-SA 4.0**, not MIT; attribution and sources are in `benchmarks/fixtures/real/SOURCES.md`.

### Machine Constraints

- This machine: Apple M2 Pro / 16GB RAM / 10 cores / 119GB free disk.
- PaddleOCR, Marker, Unstructured, and olmOCR are not installed; they bring heavy dependencies or GPU requirements, so the flow is first validated with the installed core 8 + RapidOCR/OCRmyPDF.
- All heavy tools (MinerU / Docling) run sequentially in a single process with `nice -n 10`, not concurrently.

### OCR Paths

| Path | Chinese scan CER | English scan CER |
|---|---:|---:|
| RapidOCR | 1.16% | 0.10% |
| MinerU | 1.59% | 0.20% |
| Docling | 1.01% | 7.12% |
| OCRmyPDF (Tesseract chi_sim+eng) | **10.1%** | 0.20% |

Conclusion: do not default to Tesseract `chi_sim` for Chinese scans; prefer RapidOCR / MinerU / Docling. OCRmyPDF is usable for English scans.

### Routing and Migration

- Added `docs/harness-routing.md`: harnesses can discover/invoke skills, but selection is usually the model choosing by description semantics, not deterministic domain routing; `docarbiter` adds probes, a decision table, and a fallback chain.
- Added `docs/migration.md`: the old `doc-extract` is **untouched this round**; the default is coexist first, verify, then replace; the same advice is given to other users (detect → trial in a single harness → replace → roll back).
- User confirmed: the `docarbiter` name is usable; local development continues; verification is required before release; README in Chinese and English + illustrations.

### Engineering Acceptance (2026-11-09, v0.9)

- Added `scripts/route.py`: executable routing, outputting probe / intended / selected / reason / command / fallback.
- `--selftest` covers: text layer, scans, CID, traditional Chinese, interleaved two-column, real CC BY, tables; runnable in CI.
- User chose **A: core-only**, not installing PaddleOCR / Marker / Unstructured / olmOCR; Camelot is also not installed. Tables are routed within core: simple grids to pdfplumber; complex merged tables to Docling; scans/bad text layers to MinerU.

### Reliability Acceptance (2026-11-10)

- **Clean HOME + `install.sh --skills-only`**: passed; the wrapper was written to disk and the `docarbiter` symlink was created successfully.
- **Found and fixed a real `install.sh` bug**: under `set -u`, `$resolved，` / `$target（` were treated by Bash as part of the variable name (full-width punctuation), triggering `unbound variable`; changed to `${resolved}` / `${target}`.
- **`doctor.sh --check-conflicts`**: with `docarbiter` + a fake `doc-extract` + a fake `mineru` skill in a temporary HOME, it reports `dual-router` and `conflict:mineru`.
- **`install.sh --force`**: backs up to `SKILL.md.bak.<timestamp>` before creating the symlink; without `--force` it skips and warns.
- **`route.py --selftest` 13/13**: added empty PDF, corrupt PDF, and paths with spaces/Chinese; none crashed, and routing matched expectations.
- These tests were all done in an isolated HOME under `/tmp`, with no changes to real configuration outside `~/.claude` / `~/.local`.
- **Full clean venv install**: `/tmp/docarbiter-clean-venv`, exit 0, all 7 core packages at the expected versions (mineru 4.1.7 / docling 2.149.0 / liteparse 2.18.0 / markitdown 0.1.9 / rapidocr 3.10.0 / ocrmypdf 17.12.1 / pdfplumber 0.11.10); `doctor.sh` core 14 items OK.
- **Dev dependencies separated**: `rapidfuzz` is not in core; `bench_abstract.py` automatically falls back to the stdlib `difflib` in a clean venv, so results run but the alignment score is not directly comparable with rapidfuzz. For stable alignment, `pip install -r requirements-dev.lock`.
- **Fixed the `install.sh` side effect of upgrading Homebrew dependencies**: installed formulas are now skipped, with `HOMEBREW_NO_AUTO_UPDATE=1`; apt uses `--no-upgrade`. After the fix, rerun logs confirmed `skip (no upgrade)`, exit 0.

### P0–P3 Policy Evaluation (2026-11-10)

- **P0 policy benchmark** (22 documents with answer keys):
  - Fixed MinerU: 100% success / median CER 0.0115 / 61.98s;
  - `router:text`: 100% / 0.0000 / 4.73s (about 13x faster than MinerU, lower median CER; worst true vertical 0.781);
  - `router:speed`: 100% / 0.0063 / 7.06s;
  - `router:quality`: 100% / 0.0079 / 60.04s;
  - oracle: median 0 / worst 0.2667 / 47.17s.
  - Conclusion: on a mixed corpus, routing improves success rate/speed/median CER; it cannot beat the oracle, and cannot guarantee beating the strongest single tool on every document.
- **P1 verify**: the current heuristic is a negative result (median 0.0079 with no improvement, worst 0.3478 worse than quality's 0.2952, wrong switch on zh-vertical-sim). **Not released**; output-level bag/bigram comparison is needed.
- **P2 real high-frequency tables (supplementary test 2026-11-10, replacing the earlier "composition on hold")**: verified with five real local tables — WS/T 578.1 p8, GB 28050 p6, DRIs 2023 p65, GB 2760 p13, and China Food Composition Tables p246.
  - **Complex merged headers/multi-row cells → Docling**: best structure and reading order for the WS/T three-level header, the GB 28050 multi-row cells, and the large GB 2760 table; added `--goal table-structure`.
  - **Bad text layer/symbol tables → MinerU**: the ●/○ text layer in DRIs 2023 is broken; MinerU can recover the Chinese names and distinguish "empty/O", but does not preserve the original symbols.
  - **pdfplumber only for simple grids/coordinates**: <0.5s per page, but multi-row cells in real book tables get out of order; the `text` strategy inflates 29×4 into 76×6.
  - **No composition**: no single real table showed "MinerU loses structure + pdfplumber has good cells"; Docling already provides both structure and readable cells. Dense two-column food composition tables still have header/footer row misalignment and must be spot-checked.
- **P3 default policy**: accurate body text → `text`; finished structure → `quality`; quick browsing → `speed`; complex tables → `table-structure` (Docling); simple grids → `table` (pdfplumber); true vertical manual; verify off.
- Full report: `docs/policy.md`; details `benchmarks/private/policy.md`.

### P4 Claude Code Real Triggering (2026-11-10)

- Install: `~/.claude/skills/docarbiter/SKILL.md` symlinked to this repository; a new session can discover `docarbiter`.
- **Coexistence conflict**: while the old `doc-extract` was still in `~/.claude/skills`, both Chinese and English implicit prompts invoked `Skill: doc-extract` and docarbiter was not selected. This is not a description problem; it is "only one of two routers can stay".
- **After disabling the old router**: both Chinese and English in a neutral `/tmp` directory triggered `Skill: docarbiter`, correctly routing scans → `mineru` and giving the `mineru-doc` command.
- **Test bias**: running `claude -p` from the repository root, the English run had the model directly `Read SKILL.md` instead of invoking the Skill; routing was still correct, but it does not count as clean triggering. P4 acceptance must run from a neutral directory.
- **Action**: with user confirmation, only the Claude Code `doc-extract` symlink was moved to `~/.claude/skill-backups/doc-extract.20261110-121227`; the source directory `~/.agents/skills/doc-extract` and other harnesses were untouched and can be restored.
- **Incomplete**: Sonnet / Opus retest, end-to-end extraction on real files.
- **DSH (2026-11-10, permanently switched)**: `dsh --profile headless` is testable; with the old `doc-extract` present it **invoked both docarbiter and doc-extract**. After moving `~/.dsh/skills/doc-extract` to `~/.dsh/skill-backups/doc-extract.20261110-125933` and the global `~/.agents/skills/doc-extract` to `~/.agents/skill-backups/doc-extract.20261110-130247`, both Chinese and English invoked only docarbiter and routed to MinerU. The old router symlinks for Codex / ZCode now point to the global backup and still work.
- **ZCode (2026-11-10)**: `skills list` can discover docarbiter; `--prompt` reports `Select a model before sending a message`, and the CLI has no `--model`, so a model must be selected in the TUI/desktop app. After the DSH switch, `.agents` no longer has the old router, and ZCode has only one copy left at `~/.zcode/skills/doc-extract`; in the future only this one place needs backing up.
- **Codex (2026-11-10)**: `command -v codex` was empty, no CLI executable found; `~/.codex/skills/doc-extract` still points to the global backup and cannot be triggered non-interactively.
- **MiniMax (2026-11-10)**: has `~/.minimax/skills` and `.builtin-skills`, but no CLI/headless entry point was found; not tested and not changed this round.
- Full records: `docs/p4-claude-code.md`, `docs/p4-other-harnesses.md`, `docs/harness-integration.md`.

### Workspace Real PDF Sampling (2026-11-10)

- The workspace had 8,466 PDFs, 8,444 after deduplication (114MB); all 48 random samples had a usable text layer (47 en / 1 zh), and 24 samples with Chinese filenames (18 en / 6 zh).
- Real 4-file 2-page smoke: all three tools succeeded; order CER 0.05–0.65, but character-bag difference only 0.1%–2.6%, mostly reading-order/segmentation differences.
- **MinerU real risk**: on page 1 of a Chinese article, MinerU went 2,299→1,480 (35% fewer), Latin 1,257→675, with page 2 almost identical; suspected loss of the English abstract/author information. Recorded as gotcha 18.
- The workspace does not naturally cover scans/CID/vertical text; these are still covered by synthetic/edge fixtures.
- Details are written only to `benchmarks/private/` (gitignored); no body text is saved or uploaded.

### Release Status

- Released **v0.1.0 — First Public Preview**: https://github.com/ChemistryBus/docarbiter/releases/tag/v0.1.0; `main` initial commit `5e1f9fd`, CI `validate` green.
- Released **v0.1.1 — Harness Compatibility Patch**: the installer supports whole-directory symlinks and wrapper backups, added bootstrap/update docs, and documented the Codex capacity limit.
- Next steps: post-release configuration and testing for ZCode / Codex / MiniMax; full-text CER on real two-column papers; cell-by-cell CER on real tables; install and test the extension layer (PaddleOCR / Marker / Unstructured / olmOCR) as feasible; keep iterating against `docs/release-checklist.md`.

### MiniMax skill visibility (2026-11-11)

MiniMax Code (pi-agent base, App 3.1.12, MiniMax-M3.1-Flash) was tested with three install shapes in the same session:

| Shape | Result |
|---|---|
| Real directory + real `SKILL.md` | visible; `skill({name:"docarbiter"})` loads |
| Directory + symlinked `SKILL.md` | not visible; the scanner skips a symlinked `SKILL.md` |
| Whole-directory symlink | visible; `skill({name:"docarbiter"})` loads |

- The global skills root is `~/.agents/skills` (project `.agents/skills` is also read when the project is trusted). `~/.minimax/skills` is not scanned: installing there produced `Local skill not found: docarbiter` and no catalog entry.
- The skill name comes from the frontmatter `name`, not the directory name.
- A new session re-scans the skill directory; restarting the app is not required.
- The catalog has a budget: one machine showed 173 visible skills against 536 discoverable skill names, with `Skill descriptions were shortened to fit the catalog budget.` Keep the docarbiter entry or call it explicitly when the catalog is large.
- If several copies are installed, the `Location:` header of `skill({name})` shows which copy was loaded; MiniMax preferred `~/.codex/skills/docarbiter/SKILL.md` in one test.

Reproduce:
1. Install the skill in each shape under `~/.agents/skills/docarbiter`.
2. Start a new session (no app restart required).
3. Ask: "I have a scanned Chinese PDF and need page-anchored Markdown. Which tool should I use?"
4. Confirm `skill({name:"docarbiter"})` loads and `Location:` points at the expected copy.

Decision: use a whole-directory symlink for MiniMax; keep exactly one document-extraction router per harness.

### Real-table per-cell CER (2026-11-12)

- Inputs: WS/T 578.1—2017 p8 (isolated PDF page 8; 25×13 truth including 3 header rows and 22 data rows), GB 28050—2025 p6 (29×4 truth including the header and 28 data rows), and GB 2760—2024 p13 (27×4 truth including the header and 26 data rows). These are private local standards; they are not redistributed and their body text is not saved in the repository.
- Truth: a hand-checked cell matrix; a merged cell keeps its text in the top-left and `""` in covered positions; extra note rows are trimmed to the truth dimensions.
- Metric: per-cell CER after whitespace/dash normalisation; `nopunct` also removes Unicode punctuation. Script: `scripts/bench_real_tables.py`.
- Results (micro CER, `nopunct`):
  - WS/T p8: pdfplumber default 0.0000; Docling 0.0000; MinerU 0.0000. pdfplumber `text` 0.7311.
  - GB 28050 p6: Docling 0.0000; MinerU 0.1237; pdfplumber default 0.3010; pdfplumber `text` 0.9916.
  - GB 2760 p13: pdfplumber default 0.0000; Docling 0.0000; MinerU 0.1071; pdfplumber `text` 0.9293. MinerU's 4 multi-line cells are interleaved.
- Caveat: WS/T and GB 28050 truth was drafted from Docling and hand-checked, so their Docling zero is a ceiling check; GB 2760 truth was written from the rendered page. This covers three pages and three editions only; do not generalise to another edition, page, or tool version.
- Earlier structure-only notes were corrected: WS/T has 22 data rows (not 21), and pdfplumber 0.11.10's default strategy preserves the header spans.
- Decision: keep `--goal table-structure` → Docling for complex multi-line/merged tables; for clean grids, pdfplumber default and Docling both reproduce every content cell. This is now supported by per-cell CER on GB 28050 p6 and GB 2760 p13, not only structure/spot checks.

### Real two-column full-text CER (2026-11-12)

- Inputs: BERT, NAACL 2019 (16 pages, ACL two-column; ar5iv HTML truth), Cell 2020 MoTrPAC Perspective (11 pages; PMC8800485 JATS truth), ResNet, CVPR 2016 (12 pages, arXiv:1512.03385; ar5iv HTML truth), Nature Communications 2026 (PMC13482395 JATS truth), and PLOS Computational Biology 2026 (PMC13529250 JATS truth). Private PDFs; not redistributed.
- Scope: abstract plus main body (section headings and paragraphs); excludes references, figure/table content and captions, and appendices. Tool output is aligned to the truth's first/last anchors; a row is valid only with `start+end` (or a clear last-paragraph fallback) alignment and coverage 0.5–1.5.
- Results (`nopunct` CER):
  - BERT: Docling 0.0656; MinerU 0.0773; liteparse 0.1398; pdftotext 0.2108. `pdftotext -layout` invalid.
  - Cell: pdftotext 0.0349; MinerU 0.0953; Docling 0.1099; liteparse and `pdftotext -layout` invalid (alignment).
  - ResNet: MinerU 0.1214; Docling 0.1537; liteparse 0.2287; pdftotext 0.4212; `pdftotext -layout` invalid.
  - Nature Communications: Docling 0.1209; liteparse 0.1259; MinerU 0.1322; pdftotext 0.1733; coverage 1.11 (extra figure/SI text).
  - PLOS Computational Biology: Docling 0.1586; liteparse 0.1950; pdftotext 0.1976; MinerU 0.2552; coverage 1.16–1.30 (extra figure/SI text).
- Caveat: Docling is the most consistent quality path (best on BERT/Nature Communications/PLOS, second on Cell/ResNet); MinerU wins ResNet and is strong on BERT/Cell but worst on the equation/table-heavy PLOS paper. Cell/Nature Communications/PLOS coverage above 1.1 means their CER includes some extra figure/SI text, so cross-paper ranks are not exact.
- Nature 2024 MoTrPAC (PMC11062907) was downloaded and tested but is not in the table: the 35-page flagship includes Methods/Extended Data and figure legends, so the main-body truth scope is too narrow and all tools fail alignment (coverage 2.3–2.6). It needs a full-article scope.
- Decision: keep MinerU/Docling as the two-column quality paths; Docling is the most consistent, but no universal winner; do not claim pdftotext wins from the Cell result; collect more papers before changing any default.

### Core tool update evaluation (2026-11-12)

Triggered by the weekly upstream probe: MinerU 4.2.1, Docling 2.150.0, OCRmyPDF 17.14.1. All testing was in isolated venvs; the working environment was not modified.

- **Docling 2.150.0: safe.** A clean venv with MinerU 4.2.1 + OCRmyPDF 17.12.1 passes `pip check`; `route.py --selftest` is 24/24. Real-table Docling `nopunct` CER is unchanged on WS/T p8 (0.0000), GB 28050 p6 (0.0000), and GB 2760 p13 (0.0000). Full-text Docling is unchanged: BERT 0.0656, ResNet 0.1537, Nature Communications 0.1209, PLOS 0.1586.
- **MinerU 4.2.1: flash works, server path unvalidated.** `--tier flash` produces a correct page marker and Markdown. A one-page parse through the existing 4.1.7 server also succeeds (client compatibility). An isolated 4.2.1 server starts, but parsing reports "No basic, standard, or advanced engine available" even after `parse_server.local.managed_tier=basic`, `mode=managed`, and a models symlink. Hold the pin until the 4.2.1 engine setup is validated.
- **OCRmyPDF 17.14.1: blocked by a dependency conflict.** On the same `zh-scan.pdf` OCR command it improves CER from 0.1012 (17.12.1) to 0.0708 (17.14.1). But 17.14.1 requires Pillow>=13, while MinerU's gradio 6.31 requires Pillow<13; `pip check` fails. It cannot coexist with MinerU in the core environment. Hold, or split environments.
- **Wrapper fix.** MinerU 4.2.1 uses "No basic, standard, or advanced engine available" (commas); `mineru-doc.sh` now classifies this as a config error and exits 3 immediately instead of retrying 10 times. Tested against the isolated 4.2.1 server.
- **Proposed pin set validated.** A fresh venv with MinerU 4.1.7 + Docling 2.150.0 + OCRmyPDF 17.12.1 (plus liteparse 2.18.0, MarkItDown 0.1.9, RapidOCR 3.10.0, pdfplumber 0.11.10) installs cleanly, `pip check` reports no broken requirements, and `route.py --selftest` is 24/24.
- **Recommendation:** v0.1.2 should update **Docling 2.150.0 only**; keep MinerU 4.1.7 and OCRmyPDF 17.12.1. A MinerU 4.2.1 update needs a validated server/engine setup; OCRmyPDF 17.14.1 needs a separate environment or an upstream MinerU change.
