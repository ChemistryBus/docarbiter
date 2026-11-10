# v0.1.0 — First Public Preview

`docarbiter` is a Chinese/English-first **document-extraction arbiter**: it does not build its own extractors; instead it routes among MinerU, Docling, liteparse, MarkItDown, RapidOCR, OCRmyPDF, pdfplumber, pdftotext, and other tools based on "input type / text layer / language / target output", and provides a fallback chain on failure.

## Included

- Single-entry skill `docarbiter`, 12 thin tool wrappers, `registry.json` for 18 tools;
- Executable router `scripts/route.py` + `--selftest` (14/14);
- `install.sh` / `doctor.sh` / `bench.py` / `bench_abstract.py` / `bench_policy.py`;
- Chinese + English README, architecture diagram, licensing FAQ, migration and harness integration docs;
- Synthetic bilingual fixtures, real CC BY-SA samples, CID/traditional-Chinese/two-column/vertical-writing edge samples;
- Real high-frequency table routing: complex tables → Docling, bad text layer/symbol tables → MinerU, simple grids → pdfplumber;
- P0 policy comparison, P1 verify negative results, P2 real-table conclusions, P3 default policy, P4 Claude Code/DSH trigger records.

## Install

```bash
git clone https://github.com/ChemistryBus/docarbiter.git
cd docarbiter
./scripts/install.sh --profile core
./scripts/doctor.sh --check-conflicts
```

Register skills only, without installing tools:

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

## Verification scope

- Tested on macOS arm64 + Python 3.11;
- core 7-package versions pinned per `requirements-core.lock`;
- Clean venv + `doctor.sh` passes;
- Chinese/English implicit triggering passes on Claude Code / DSH;
- Linux verified by CI; Windows not verified.

## Known limitations

- Not "all PDFs are accurate": the routing gain comes from "not choosing the wrong tool + switching tools on failure", not from a stronger algorithm;
- True vertical writing, real two-column full text, real-table per-cell CER, and symbol-table original-glyph fidelity are still incomplete;
- First/last pages of dense two-column book tables such as the China Food Composition Tables may still have misaligned rows and must be spot-checked;
- `extra` / `full` not individually tested; Windows not verified;
- Triggering tests for ZCode / Codex / MiniMax are not complete; configure after release per `docs/harness-integration.md`;
- PDFs in real workspaces without independent answer keys report only agreement/coverage, not accuracy.

## License

This repository is MIT-licensed and contains only original documentation, wrappers, and install scripts; it contains no upstream code or model weights. Upstream tools are installed by the user and retain their own licenses. See `THIRD_PARTY_NOTICES.md` for MinerU's additional terms and the AGPL tool notes.
