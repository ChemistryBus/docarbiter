# v0.1.1 — Harness Compatibility Patch

Released 2026-11-11.

This patch makes `docarbiter` install reliably across harnesses. It does **not** change the
routing algorithm, tables, CER results, or tool registry.

## Fixed

- **Whole-directory skill links** for `~/.agents/skills`, `~/.codex/skills`, and
  `~/.minimax/skills`. MiniMax and some pi-agent scanners skip a symlinked `SKILL.md` file;
  the installer now uses `--skill-mode auto` to choose the compatible layout.
- **Wrapper backups**: existing `~/.local/bin/mineru-doc` / `liteparse-doc` are copied to
  `.bak.<timestamp>` before replacement.
- **New update path**: `scripts/update.sh` pulls the repo and refreshes registered skills.
- **Bootstrap**: `bootstrap.sh` clones the repo and runs the installer from one command.

## Harness status

| Harness | Result |
|---|---|
| Claude Code | Full pass |
| DSH | Full pass |
| ZCode | Full pass (top-level, Chinese/English) |
| MiniMax | Full pass (top-level, Chinese/English) |
| Codex | Conditional pass: explicit invocation and a small skill set work; a 600+ skill catalog can hide `docarbiter` descriptions |

See [`docs/harness-integration.md`](harness-integration.md) and
[`docs/updating.md`](updating.md).

## Unchanged

- Core routing: MinerU / Docling / liteparse / MarkItDown / RapidOCR / OCRmyPDF /
  pdfplumber / pdftotext.
- `--goal table` (pdfplumber) and `--goal table-structure` (Docling).
- Benchmark results and known limitations in `docs/policy.md` and `docs/benchmarks.md`.

## Known limitations

- Codex with a very large skill catalog may need explicit “use docarbiter” or a smaller
  catalog.
- `extra` / `full` profiles are not fully benchmarked.
- True vertical text, full-body two-column CER, and per-cell CER on real tables remain
  open.
