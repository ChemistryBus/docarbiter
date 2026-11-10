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
```

If you installed from a different clone, run the same command in that clone:

```bash
cd /path/to/docarbiter
git pull --ff-only
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

## How each harness updates

| Harness | Installed shape | Update | Reload |
|---|---|---|---|
| MiniMax | `~/.agents/skills/docarbiter` → whole-directory symlink | `git pull` in the target repo | new top-level session |
| ZCode | `~/.zcode/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | restart app / new session |
| Claude Code | `~/.claude/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | new session |
| DSH | `~/.dsh/skills/docarbiter/SKILL.md` → file symlink | `git pull` in the target repo | new headless/session |
| Codex | `~/.codex/skills/docarbiter/SKILL.md` → **regular file** | `git pull`, then copy the new file or reinstall with `--force --skill-mode dir` | new session |

Codex copy refresh:

```bash
cp /path/to/docarbiter/skills/docarbiter/SKILL.md ~/.codex/skills/docarbiter/SKILL.md
```

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

## After updating

```bash
./scripts/doctor.sh --check-conflicts
```

- Keep exactly one document-extraction router per harness.
- Restart/new session; old sessions keep the old skill content.
- If a harness still does not see the updated skill, check `--skill-mode`:
  - MiniMax: whole-directory symlink;
  - Codex: regular file or directory symlink, plus a small enough skill catalog;
  - Claude/DSH/ZCode: file symlink is fine.
