# Handoff — docarbiter maintenance

Last updated: 2026-11-11.

## What this project is

`docarbiter` is a Chinese/English document-extraction **routing skill** over a curated
toolset. It does not implement extraction itself. It probes the input, chooses a tool,
and gives a fallback chain. The repository contains original docs, thin shells, wrappers,
fixtures, and install scripts; no upstream code or model weights.

- Repo: https://github.com/ChemistryBus/docarbiter
- Local repo: `/Users/wubolong/Documents/Claude/Document Extraction Skills/document-extraction-skills`
- Latest release: `v0.1.1 — Harness Compatibility Patch`
- First release: `v0.1.0 — First Public Preview`
- Default branch: `main`; CI: `validate` on Ubuntu + macOS.

## User context

- The user is a PhD student who publishes tools he needed during his PhD.
- Highest-frequency harnesses: **Claude Code, ZCode, DSH**. MiniMax is tested; Codex is
  used but its large skill catalog is a known constraint.
- The user cares about not overstating accuracy. Real PDFs without independent answer keys
  are reported as agreement/coverage, never "accuracy".
- Release titles and version labels should be English. README default is English; Chinese
  is `README.zh-CN.md`.
- Do not create a GitHub profile README; keep the profile simple.

## Current harness state

| Harness | Current shape | Status |
|---|---|---|
| Claude Code | `~/.claude/skills/docarbiter/SKILL.md` → local repo file symlink | full pass |
| DSH | `~/.dsh/skills/docarbiter/SKILL.md` → local repo file symlink | full pass |
| ZCode | `~/.zcode/skills/docarbiter/SKILL.md` → `~/.local/share/docarbiter/...` | full pass (top-level, zh/en) |
| MiniMax | `~/.agents/skills/docarbiter` → `~/.local/share/docarbiter/skills/docarbiter` (whole-dir symlink) | full pass (top-level, zh/en) |
| Codex | `~/.codex/skills/docarbiter/SKILL.md` regular file (`--skill-mode copy`) | conditional: explicit works; 600+ skills can hide descriptions; minimal set works |

`doctor.sh` now reports each harness's shape, whether it is the same source as this
checkout, whether the content matches, and whether the version is behind. Refresh a
`DIFFERS`/`DRIFT` copy with `install.sh --skill-mode copy --skills-dir ~/.codex/skills`;
another clone needs `git pull`.

Do not delete old `doc-extract` backups. They are outside the skill directories:
`~/.claude/skill-backups/`, `~/.dsh/skill-backups/`, `~/.agents/skill-backups/`.
One document-extraction router per harness.

## Updating

- Clone-based installs: `cd ~/.local/share/docarbiter && ./scripts/update.sh`, then start a
  new session/restart the app.
- Local-repo symlinks (Claude/DSH): `git pull --ff-only` in the local repo, then new session.
- Codex regular file: `git pull`, then copy the new `SKILL.md` into
  `~/.codex/skills/docarbiter/SKILL.md` (or `update.sh --force --skill-mode dir`).
- Full update details: `docs/updating.md`.

## Maintenance rules

1. Check `git status`, `git log -1`, `gh release list`, and `gh run list` before changing.
2. Run before every push:

   ```bash
   python3 -I scripts/validate.py
   python3 -I scripts/check_skill_consistency.py
   python3 -I scripts/check_skill_consistency.py --check-git
   python3 -I scripts/route.py --selftest   # all pass; currently 24 checks
   python3 -I scripts/check_pagemarkers.py  # real MinerU page-marker regression; skips if MinerU is absent
   for f in bootstrap.sh scripts/*.sh scripts/wrappers/*.sh; do bash -n "$f"; done
   ```

   `check_skill_consistency.py` checks that every `--goal` and routed tool in
   `route.py` is documented in `SKILL.md`, that README versions match, and that
   camelot has not returned to the default chain. `--check-git` also fails when
   `SKILL.md` changed against `origin/main` without a version bump.

3. Push to `main` only when the change is ready; watch the Ubuntu + macOS CI matrix.
4. Patch release for install/docs/compatibility fixes (e.g. `v0.1.1`); do not move or
   delete published tags.
5. Public release/tag requires the user's explicit approval.
6. Never upload user documents; keep `benchmarks/private/` gitignored; do not add secrets,
   real user PDFs, or upstream code.
7. If a harness doesn't see the skill, check the install shape before reinstalling:
   MiniMax needs a whole-directory symlink; Codex uses a regular file copy
   (`--skill-mode copy`) and a smaller catalog; Claude/DSH/ZCode file symlinks work.
8. If a tool is missing, read `docs/install-routed-tools.md`, ask permission, then install
   the upstream package/tool. Do not silently clone arbitrary skill repositories.
9. The weekly `probe-upstream` workflow runs `check_updates.py` and opens/updates an issue
   labelled `upstream-probe` when a routed tool is behind. A pin change is a code change:
   read the release notes, re-run the benchmark suite, and update docs with the result.

**Skill version discipline:** when `skills/docarbiter/SKILL.md` changes, bump its
`version:` line and the README/README.zh-CN versions in the same commit, then run
`check_skill_consistency.py`. Refresh the Codex copy with
`install.sh --skill-mode copy --skills-dir ~/.codex/skills`; other clones need
`git pull`/`update.sh`. Harnesses load the skill only at the start of a new session.

## Current work (2026-11-11)

Fixed in this round:

- `route.py`: availability and generated commands share one entry point; RapidOCR path
  interpolation; pdfplumber passes the path as argv (no shell-quoting `NameError`);
  fallback tools are selected when the primary is missing; per-page sampling with
  `empty` / `scan` / `garbled` / `usable` / `mixed` / `probe-error`; sparse-text table
  goals; `--page` for page-specific commands.
- `mineru-doc`: respects `MINERU_HOME`; `--tier flash` skips the server; a missing engine
  configuration exits immediately instead of retrying 10 times; only recoverable states
  retry; the first diagnostic is preserved.
- `install.sh`: `~/.agents/skills` is detected first; paths are normalized; same-source
  old copies are backed up and normalized automatically; Codex uses `--skill-mode copy`;
  post-install self-check fails fast with a fix command.
- `doctor.sh`: includes `~/.agents/skills`; reports shape, same-source, content match,
  version drift, and catalog size per harness.
- `scripts/check_pagemarkers.py`: real MinerU regression for page order, blank-page
  preservation, and selected-page numbering (passes on the repository's 4-page fixture).
- `scripts/bench.py`: the misnamed `per_page.csv` is now `per_document.csv`.
- `scripts/bench_real_tables.py`: per-cell CER on two real, hand-checked tables.
  WS/T 578.1 p8 — pdfplumber default / Docling / MinerU all 0.0000 `nopunct` CER;
  GB 28050 p6 — Docling 0.0000, MinerU 0.1237, pdfplumber default 0.3010,
  pdfplumber `text` 0.9916. Truth was drafted from Docling and hand-checked, so
  Docling's zero is a ceiling check; the pdfplumber/MinerU numbers are independent.
  These are two pages only.
- `scripts/bench_fulltext.py`: full-text CER on three real two-column papers with
  independent truth (PMC JATS / ar5iv). BERT — Docling 0.0656, MinerU 0.0773,
  liteparse 0.1398, pdftotext 0.2108 `nopunct`; Cell Perspective — pdftotext
  0.0349, MinerU 0.0953, Docling 0.1099; ResNet — MinerU 0.1214, Docling
  0.1537, liteparse 0.2287, pdftotext 0.4212. The Cell figures contain text, so
  Docling/MinerU coverage is 1.08–1.10 and the ranking is not directly comparable.
  Nature 2024 MoTrPAC was downloaded and tested but excluded: its Methods/Extended
  Data exceed the main-body scope, so all tools fail alignment. These are three
  papers only.
- English README install prompt; user-facing docs translated to English.

Still open:

- Per-cell CER on the remaining real tables and other editions (WS/T p8 and
  GB 28050 p6 are done).
- Full-text CER on more papers and layouts (BERT, Cell Perspective, and ResNet
  are done; the Cell figure-text caveat still needs a cleaner scope, and the
  Nature flagship needs a full-article scope).
- True vertical text; all tools are weak.
- `extra` tools (PaddleOCR/Marker/Unstructured/olmOCR) not fully benchmarked.
- Mixed-document detection is implemented, but end-to-end OCR recall on mixed documents
  still needs a real-document benchmark.
- Keep the current claim boundary: structural/spot-check results are not "accuracy",
  and two-page per-cell CER or two-paper full-text CER is not a general accuracy claim.

Deferred from the harness feedback:

- A `harnesses` section in `registry.json` as the single source of truth for skill
  directories, expected shapes, and status. The mapping is currently repeated in
  `install.sh`, `doctor.sh`, and the docs; consolidating it is the next cleanup.
- Updating the `doc-extract` references inside `~/.agents/skills/mineru/SKILL.md` and
  `~/.agents/skills/docling/SKILL.md`. Those are separate skill repositories and were
  intentionally not modified.

## Useful entry points

- `README.md` / `README.zh-CN.md`: user-facing overview.
- `docs/updating.md`: update matrix.
- `docs/harness-integration.md`: per-harness install/switch/test cards.
- `docs/p4-other-harnesses.md`: harness test history.
- `docs/policy.md`, `docs/benchmarks.md`: routing and benchmark evidence.
- `docs/install-routed-tools.md`: upstream links and install commands.
- `scripts/update.sh`, `bootstrap.sh`: update/install commands.
- `scripts/check_pagemarkers.py`: real MinerU page-structure regression (skips without MinerU).
- `scripts/bench_real_tables.py`: real-table per-cell CER (private PDFs/truth, gitignored; CI only py_compiles it).
- `scripts/bench_fulltext.py`: real two-column full-text CER (PMC JATS / ar5iv truth; private inputs; CI only py_compiles it).
- `scripts/check_updates.py`: upstream probe; the weekly `probe-upstream` workflow opens/updates an issue when a routed tool is behind.
