<p align="right"><a href="README.md"><img src="https://img.shields.io/badge/Chinese-README-2f81f7?style=flat-square" alt="Chinese"></a></p>

<h1 align="center">docarbiter</h1>

<p align="center"><strong>One routing layer for Chinese and English document extraction.</strong></p>
<p align="center">Probe the file, pick the right tool, and keep an explainable fallback when it fails.</p>
<p align="center"><strong>v0.1.3 — Chinese Corpus Routing Fixes</strong></p>

<p align="center">
  <a href="https://github.com/ChemistryBus/docarbiter/actions/workflows/validate.yml"><img src="https://github.com/ChemistryBus/docarbiter/actions/workflows/validate.yml/badge.svg" alt="validate"></a>
  <a href="https://github.com/ChemistryBus/docarbiter/releases/tag/v0.1.3"><img src="https://img.shields.io/github/v/release/ChemistryBus/docarbiter?color=blue&cacheSeconds=300" alt="release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10--3.12-blue" alt="Python 3.10-3.12">
</p>

![docarbiter overview](docs/assets/overview-en.svg)

## What it is

There is no shortage of extractors. The hard part is knowing **which one to use for this file**.

`docarbiter` is not another PDF extractor and not a model. It is a thin **routing skill**: probe the file, choose a tool, and return the next step when that tool fails. It covers eight core tools and registers eighteen in total. The repository contains original documentation, wrappers, and install scripts only; it does not redistribute upstream code or model weights.

It addresses four recurring failures:

- a text-layer PDF and a scan need different tools;
- Chinese and English fail differently: CID fonts, OCR models, reading order, full-width punctuation, merged cells;
- a tool that wins on one table can scramble the next one;
- with several look-alike skills installed, the agent picks by description and the result stops being reproducible.

## 30-second start

### Option 1: let your agent install it

Paste this into Claude Code, Codex, ZCode, or MiniMax:

```text
Ask me whether you may install docarbiter on this machine, and wait for my permission. Then run:
curl -fsSL https://raw.githubusercontent.com/ChemistryBus/docarbiter/main/bootstrap.sh | bash
If the current harness already has doc-extract, back it up outside the skills directory before installing docarbiter.
After installation, run ./scripts/doctor.sh --check-conflicts and tell me which tools are missing.
Do not upload or read my documents.
```

`bootstrap.sh` only clones this repository and runs `scripts/install.sh`. It does not clone third-party skill repositories. Upstream tools may download their own model weights on first run. To inspect the script first, see [`bootstrap.sh`](bootstrap.sh).

### Option 2: manual install

```bash
git clone https://github.com/ChemistryBus/docarbiter.git
cd docarbiter
./scripts/install.sh --profile core
./scripts/doctor.sh --check-conflicts
```

### Try one route

```bash
python3 -I scripts/route.py your-file.pdf --goal manuscript
```

No PDF at hand? Use the bundled scan fixture:

```bash
python3 -I scripts/route.py benchmarks/fixtures/zh-scan.pdf --goal manuscript
# expected: intended=mineru, because there is no usable text layer
```

The router only decides. It does not extract for you; run the suggested command after you agree with it.

## How it routes

<table width="960">
  <colgroup><col width="360"><col width="220"><col width="380"></colgroup>
  <thead>
    <tr>
      <th width="360" align="left">What you have</th>
      <th width="220" align="left">Default route</th>
      <th width="380" align="left">Why</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="360" align="left">Clean text layer, speed matters</td>
      <td width="220" align="left"><strong>liteparse</strong> / <strong>pdftotext</strong></td>
      <td width="380" align="left">Fast, local, no OCR</td>
    </tr>
    <tr>
      <td width="360" align="left">Paper or book, needs headings and page anchors</td>
      <td width="220" align="left"><strong>MinerU</strong></td>
      <td width="380" align="left">Structured Markdown plus page anchors</td>
    </tr>
    <tr>
      <td width="360" align="left">Scan, CID font, or garbled text layer</td>
      <td width="220" align="left"><strong>MinerU</strong></td>
      <td width="380" align="left">OCR plus layout; do not trust the text layer</td>
    </tr>
    <tr>
      <td width="360" align="left">Complex table: merged headers, multi-line cells, book table</td>
      <td width="220" align="left"><strong>Docling</strong></td>
      <td width="380" align="left">Best structure on the tested real tables</td>
    </tr>
    <tr>
      <td width="360" align="left">Simple bordered table or coordinates</td>
      <td width="220" align="left"><strong>pdfplumber</strong></td>
      <td width="380" align="left">Fast cells; not for complex book tables</td>
    </tr>
    <tr>
      <td width="360" align="left">Office, HTML, EPUB, audio/video, RAG chunks</td>
      <td width="220" align="left"><strong>Docling</strong></td>
      <td width="380" align="left">Broad format coverage</td>
    </tr>
    <tr>
      <td width="360" align="left">Image or screenshot</td>
      <td width="220" align="left"><strong>RapidOCR</strong></td>
      <td width="380" align="left">Lightweight, Chinese-first OCR</td>
    </tr>
  </tbody>
</table>

```bash
# Simple grid: fast path
python3 -I scripts/route.py file.pdf --goal table --json

# Real book or standard table: preserve structure
python3 -I scripts/route.py file.pdf --goal table-structure --json
```

The router reports `probe`, `intended`, `selected`, `reason`, `command`, and `fallback`. It samples the first pages only; for a long document, locate the target page first and probe that page with `--page`.

## Who it is for, and who it is not for

**Good fit:**

- researchers, graduate students, and knowledge workers who handle papers, standards, reports, and scans;
- converting PDFs into Markdown, plain text, tables, or page-anchored paragraphs;
- mixed inputs: text layers, scans, two-column layouts, tables, and bilingual documents;
- agent users who installed several extraction skills and get unstable choices;
- users who want local processing rather than a cloud API.

**Not a good fit:**

- plain-text preview only: `pdftotext` is enough;
- an online API or hosted batch service: this project is local by default;
- a promise of 100% accuracy with no review: no tool can do that;
- perfect handwriting, equations, or chemical structures: expect manual review;
- PDF merge, split, or forms only: use qpdf or pypdf, not this skill.

## Core tools

Eight tools are installed by default. The `full` profile registers twelve tool skills; the default install registers only `docarbiter`.

<table width="960">
  <colgroup><col width="230"><col width="730"></colgroup>
  <thead>
    <tr>
      <th width="230" align="left">Tool</th>
      <th width="730" align="left">Best at</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="230" align="left"><strong>MinerU</strong></td>
      <td width="730" align="left">Chinese and English PDF to structured Markdown, page anchors, OCR</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>Docling</strong></td>
      <td width="730" align="left">Office, HTML, EPUB, RAG, LaTeX, and complex merged tables</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>liteparse</strong></td>
      <td width="730" align="left">Fast text-layer PDF and word coordinates</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>MarkItDown</strong></td>
      <td width="730" align="left">Simple single-column PDF and Office files</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>RapidOCR</strong></td>
      <td width="730" align="left">Chinese-first image and screenshot OCR</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>OCRmyPDF</strong></td>
      <td width="730" align="left">Add a searchable text layer to scans</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>pdfplumber</strong></td>
      <td width="730" align="left">Simple bordered tables and character coordinates</td>
    </tr>
    <tr>
      <td width="230" align="left"><strong>pdftotext</strong></td>
      <td width="730" align="left">Plain-text baseline and text-layer probe</td>
    </tr>
  </tbody>
</table>

Full licenses, install commands, and exclusion reasons: [docs/tool-registry.md](docs/tool-registry.md) and [registry.json](registry.json).

## Evidence, not an accuracy claim

Validation so far:

- **Per-cell CER on real tables:** WS/T 578.1 p8, GB 28050 p6, and GB 2760 p13, with hand-checked truth;
- **Full-text CER on five real two-column papers:** BERT, Cell Perspective, ResNet, Nature Communications, and PLOS Computational Biology, with PMC JATS or ar5iv as independent truth;
- **P0 routing policy:** 22 documents with answer keys, checking route success, CER, and wall time;
- **Complex Chinese corpus audit:** 43 journal articles and theses plus 20 standards and regulations, covering scans, mixed text layers, hidden OCR, FzBookMaker custom encoding, and 200–400 page documents.

These results cover the tested samples only; they are not a general accuracy claim. Docling is the most consistent on the tested tables and most papers; MinerU is stronger on scans, page anchors, and some papers; pdfplumber is for simple tables. Full numbers, coverage, and caveats are in [docs/benchmarks.md](docs/benchmarks.md) and [docs/policy.md](docs/policy.md).

## Harness support

<table width="960">
  <colgroup><col width="260"><col width="700"></colgroup>
  <thead>
    <tr>
      <th width="260" align="left">Harness</th>
      <th width="700" align="left">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td width="260" align="left">Claude Code</td>
      <td width="700" align="left">Full pass (file symlink)</td>
    </tr>
    <tr>
      <td width="260" align="left">DSH</td>
      <td width="700" align="left">Full pass (file symlink)</td>
    </tr>
    <tr>
      <td width="260" align="left">ZCode</td>
      <td width="700" align="left">Full pass (file symlink)</td>
    </tr>
    <tr>
      <td width="260" align="left">MiniMax</td>
      <td width="700" align="left">Full pass (whole-directory symlink in <code>.agents/skills</code>)</td>
    </tr>
    <tr>
      <td width="260" align="left">Codex</td>
      <td width="700" align="left">Conditional: a very large skill catalog may require an explicit "use docarbiter"</td>
    </tr>
  </tbody>
</table>

Keep **exactly one** document-extraction router per harness. If `doc-extract` and `docarbiter` coexist, the agent may pick the old one. Migration and rollback: [docs/migration.md](docs/migration.md).

## Install options

```bash
# Recommended: core tools plus the single docarbiter entry point
./scripts/install.sh --profile core

# Register the skill only (quick trial; install tools separately)
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills

# Extra or full: heavy or GPU tools, not all benchmarked yet
./scripts/install.sh --profile extra
./scripts/install.sh --profile full

# Health check: missing tools, version drift, duplicate skills, dual routers
./scripts/doctor.sh --check-conflicts
```

> The installer does not clone third-party skill repositories. `--profile core` installs pinned Python packages and system dependencies through `pip`, `brew`, or `apt`; upstream tools may download their own models. `--skills-only` installs no tools. The twelve tool shells under `skills/_tools/` are original command and positioning notes, not copies of upstream repositories.

Other harnesses use the same command with their skill directory:

```bash
./scripts/install.sh --skills-only --skills-dir ~/.dsh/skills
./scripts/install.sh --skills-only --skills-dir ~/.zcode/skills
./scripts/install.sh --skills-only --skills-dir ~/.codex/skills
./scripts/install.sh --skills-only --skills-dir ~/.agents/skills   # MiniMax or shared agents directory
```

## FAQ

**Does it upload my documents?**  
No by default. The tools run locally, except for any cloud service or network behavior you explicitly use. The repository contains no telemetry.

**Can it handle scans?**  
Yes, but not perfectly. MinerU runs OCR directly; OCRmyPDF can add a text layer first; RapidOCR is for single images. Scan quality, skew, stamps, and handwriting all affect the result, so spot-check before publishing.

**Why can it not guarantee 100% accuracy?**  
Because no tool can. The router chooses a path and provides a fallback; the output still needs review for tables, equations, and proper nouns.

**Does it work on Windows?**  
The core is Python plus shell wrappers. macOS is tested, Linux is covered by CI, and Windows is not systematically verified. WSL may work; please report issues.

**What if the old doc-extract is still installed?**  
Back up the old directory outside the skills directory, install docarbiter, then run `./scripts/doctor.sh --check-conflicts`. Do not keep two routers.

**Which tool should I use for tables?**  
Simple bordered tables: `--goal table` (pdfplumber). Merged headers, multi-line cells, book or standard tables: `--goal table-structure` (Docling). Scanned tables: MinerU.

## Documentation

<table width="960">
  <colgroup><col width="280"><col width="680"></colgroup>
  <tbody>
    <tr>
      <td width="280" align="left">Architecture and registry</td>
      <td width="680" align="left"><a href="docs/architecture.md">docs/architecture.md</a> · <a href="docs/tool-registry.md">docs/tool-registry.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Benchmarks and policy</td>
      <td width="680" align="left"><a href="docs/benchmarks.md">docs/benchmarks.md</a> · <a href="docs/policy.md">docs/policy.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Failure modes and traps</td>
      <td width="680" align="left"><a href="docs/gotchas.md">docs/gotchas.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Harness integration</td>
      <td width="680" align="left"><a href="docs/harness-integration.md">docs/harness-integration.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Updating skills</td>
      <td width="680" align="left"><a href="docs/updating.md">docs/updating.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Migration and rollback</td>
      <td width="680" align="left"><a href="docs/migration.md">docs/migration.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Maintainer handoff</td>
      <td width="680" align="left"><a href="docs/handoff.md">docs/handoff.md</a></td>
    </tr>
    <tr>
      <td width="280" align="left">Release notes</td>
      <td width="680" align="left"><a href="https://github.com/ChemistryBus/docarbiter/releases/tag/v0.1.3">v0.1.3</a> · <a href="docs/release-notes-v0.1.3.md">docs/release-notes-v0.1.3.md</a></td>
    </tr>
  </tbody>
</table>

## License

This repository is **MIT**. It contains original documentation, wrappers, and install scripts only; it does not redistribute upstream code or model weights.

MinerU is Apache-2.0 with additional terms; the additional terms trigger at large commercial scale or when providing an online service based on MinerU. This project calls the CLI locally and does not redistribute it. Full terms and the AGPL / proprietary exclusions: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [docs/licensing-faq.md](docs/licensing-faq.md).
