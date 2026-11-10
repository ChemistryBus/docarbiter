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
| Codex | `~/.codex/skills/docarbiter/SKILL.md` regular file | conditional: explicit works; 600+ skills can hide descriptions; minimal set works |

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
   python3 -I scripts/route.py --selftest   # expected 14/14
   for f in bootstrap.sh scripts/*.sh scripts/wrappers/*.sh; do bash -n "$f"; done
   ```

3. Push to `main` only when the change is ready; watch the Ubuntu + macOS CI matrix.
4. Patch release for install/docs/compatibility fixes (e.g. `v0.1.1`); do not move or
   delete published tags.
5. Public release/tag requires the user's explicit approval.
6. Never upload user documents; keep `benchmarks/private/` gitignored; do not add secrets,
   real user PDFs, or upstream code.
7. If a harness doesn't see the skill, check the install shape before reinstalling:
   MiniMax needs a whole-directory symlink; Codex may need a regular file and a smaller
   catalog; Claude/DSH/ZCode file symlinks work.
8. If a tool is missing, read `docs/install-routed-tools.md`, ask permission, then install
   the upstream package/tool. Do not silently clone arbitrary skill repositories.

## Remaining technical work

- Real-table per-cell CER with human truth: WS/T 578.1 p8 and GB 28050 p6.
- Real two-column full-body CER (currently only BERT abstract).
- True vertical text; all tools are weak.
- `extra` tools (PaddleOCR/Marker/Unstructured/olmOCR) not fully benchmarked.
- Keep the current claim boundary: structural/spot-check results are not "accuracy".

## Useful entry points

- `README.md` / `README.zh-CN.md`: user-facing overview.
- `docs/updating.md`: update matrix.
- `docs/harness-integration.md`: per-harness install/switch/test cards.
- `docs/p4-other-harnesses.md`: harness test history.
- `docs/policy.md`, `docs/benchmarks.md`: routing and benchmark evidence.
- `docs/install-routed-tools.md`: upstream links and install commands.
- `scripts/update.sh`, `bootstrap.sh`: update/install commands.
