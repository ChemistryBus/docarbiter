# Updating docarbiter and installed skills

Skills are loaded when a harness starts a session. Updating files on disk does **not**
change the current conversation; start a new session (or restart the app) after updating.

## Update docarbiter

If the repository is the clone used by the skill:

```bash
cd ~/.local/share/docarbiter
./scripts/update.sh
```

`update.sh` does:

1. `git pull --ff-only`;
2. re-runs `install.sh --skills-only` to refresh the skill link and wrappers.

Pass installer flags if needed:

```bash
./scripts/update.sh --force --skill-mode dir
./scripts/update.sh --force --skill-mode copy --skills-dir ~/.codex/skills
```

`install.sh --skill-mode auto` now refreshes each known directory in its expected shape:
`~/.agents/skills` gets a whole-directory symlink, `~/.codex/skills` gets a real
`SKILL.md` copy, and Claude Code / DSH / ZCode keep a file symlink. A same-source old copy
is backed up and normalized automatically; `update.sh` is therefore idempotent.

If you installed from a different clone, run the same command in that clone:

```bash
cd /path/to/docarbiter
git pull --ff-only
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

## How each harness updates

| Harness | Installed shape | Update | Reload |
|---|---|---|---|
| MiniMax | `~/.agents/skills/docarbiter` → whole-directory symlink | `git pull` in the target repo | new session (no app restart required) |
| ZCode | `~/.zcode/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | restart app / new session |
| Claude Code | `~/.claude/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | new session |
| DSH | `~/.dsh/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | new headless/session |
| Codex | `~/.codex/skills/docarbiter/SKILL.md` → **regular file copy** | `git pull`, then run the installer with `--skill-mode copy` (backs up and refreshes) | new session |

Codex copy refresh:

```bash
./scripts/install.sh --skills-only --skill-mode copy --skills-dir ~/.codex/skills
# or, if you prefer a manual copy:
cp /path/to/docarbiter/skills/docarbiter/SKILL.md ~/.codex/skills/docarbiter/SKILL.md
```

`doctor.sh` compares a regular-file copy byte-for-byte with this checkout and reports it
as `DRIFT` when it is stale. `install.sh` always backs up the old file as
`SKILL.md.bak.<timestamp>` before replacing it.

Find where a link points:

```bash
readlink ~/.agents/skills/docarbiter
readlink ~/.zcode/skills/docarbiter/SKILL.md
readlink ~/.claude/skills/docarbiter/SKILL.md
readlink ~/.dsh/skills/docarbiter/SKILL.md
```

## How to know an update exists

For docarbiter:

```bash
cd ~/.local/share/docarbiter
git fetch origin
git log --oneline HEAD..origin/main
gh release list --repo ChemistryBus/docarbiter
```

Or watch **Releases** / **Commits** on GitHub. The README and `CHANGELOG`-style
release notes state the current version.

For other installed skills, each skill has its own upstream repository. There is no
universal updater: check the skill's `SKILL.md` / upstream URL, then `git pull` (or
reinstall) in that project. Do not update a skill merely because the harness catalog
shows a new version; read its release notes first.

## Upstream probe (fixed mechanism)

`scripts/check_updates.py` compares:

- docarbiter: local HEAD vs `origin/main` vs the latest GitHub release;
- routed Python tools: installed version vs `registry.json` pin vs latest PyPI;
- upstream GitHub releases for the same repositories.

Run it manually:

```bash
python3 -I scripts/check_updates.py --format markdown --exit-code
```

The weekly `probe-upstream` GitHub Actions workflow (Mondays 03:17 UTC) runs the same
probe and opens or updates an issue labelled `upstream-probe` when anything is behind.
It never installs or upgrades anything.

Before changing a pin, treat it as a code change: read the release notes, run
`validate.py`, `route.py --selftest`, `check_pagemarkers.py`, and the real-table /
full-text benchmarks, then update the pin and docs together. A `pinned-behind` result
is a prompt to evaluate, not an instruction to upgrade.

## Skill version discipline

`SKILL.md` is executable policy: changing it changes routing. When it changes:

1. bump the frontmatter `version:` and the README / README.zh-CN versions;
2. run `python3 -I scripts/check_skill_consistency.py` (and `--check-git` before push);
3. refresh the Codex copy with `install.sh --skill-mode copy --skills-dir ~/.codex/skills`;
4. start a new session in every harness (Claude/DSH/ZCode/MiniMax); Codex needs the copy
   refresh first.

`check_skill_consistency.py` fails when a `--goal` or routed tool exists in `route.py` but
not in `SKILL.md`, when README versions differ, or when `SKILL.md` changed against
`origin/main` without a version bump.

## After updating

```bash
./scripts/doctor.sh --check-conflicts
```

- Keep exactly one document-extraction router per harness.
- `doctor.sh` now reports each harness's shape (`dir-symlink` / `file-symlink` /
  `real-copy`), whether it is the same source as this checkout, whether its content
  matches, and whether its version is behind. `DIFFERS` or `DRIFT` means that copy needs
  a refresh: run the installer for that directory, or `git pull` in the other clone.
- Restart/new session; old sessions keep the old skill content. MiniMax re-scans on a new
  session and does not need an app restart.
- If a harness still does not see the updated skill, check `--skill-mode`:
  - MiniMax: whole-directory symlink;
  - Codex: regular file or directory symlink, plus a small enough skill catalog;
  - Claude/DSH/ZCode: file symlink is fine.
