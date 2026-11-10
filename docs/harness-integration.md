# Harness integration: one skill-directory command

> Goal: after release, do not depend on a harness-specific hook and do not hard-code
> configuration. Each harness only needs two things: **put `docarbiter/SKILL.md` in its
> skill directory** and **keep exactly one document-extraction router**.

## 1. Generic install

Prefer the repository script and pass the target harness's skill directory:

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

`--skills-dir` can be repeated; `--profile core` registers `docarbiter` only, not the
12 tool shells.

If you do not want the script to update the `~/.local/bin` wrappers as well, create a
**whole-directory symlink** instead (more compatible than "directory + symlinked SKILL.md"):

```bash
DIR="$HOME/.claude/skills"          # change to the target harness
ln -sfn "$PWD/skills/docarbiter" "$DIR/docarbiter"
```

`install.sh --skill-mode auto` maps known directories as follows:

| Skill directory | Auto mode | Why |
|---|---|---|
| `~/.agents/skills` | `dir` (whole-directory symlink) | shared global root for pi-agent harnesses, including MiniMax Code |
| `~/.codex/skills` | `copy` (real `SKILL.md`) | Codex is known to work with a real file; `update.sh` refreshes it |
| `~/.claude/skills`, `~/.dsh/skills`, `~/.zcode/skills` | `file` (symlinked `SKILL.md`) | tested shape for these harnesses |
| `~/.minimax/skills` | not used | MiniMax Code does not scan it; use `~/.agents/skills` |
| any other directory | explicit error | pass `--skill-mode dir|file|copy` |

After registration, `install.sh` self-checks three things and exits non-zero on failure:

1. `SKILL.md` exists at the target;
2. frontmatter `name` is `docarbiter`;
3. the shape matches the selected mode (`dir` = whole-directory symlink, `file` =
   symlinked `SKILL.md`, `copy` = real directory + real `SKILL.md`).

The failure message includes a copy-paste fix command.

## 2. Known harness directories

| Harness | Skill directory | Also reads | Status |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | — | full pass; old router backed up and disabled |
| DSH | `~/.dsh/skills` | `~/.agents/skills` (global; `DSH_AGENTS_HOME` can change it) | full pass; old global router moved out |
| ZCode | `~/.zcode/skills` | `~/.agents/skills` (duplicate discovery) | full pass (top-level, zh/en); subagents also pass |
| Codex | `~/.codex/skills` | may also read `~/.agents` | **conditional pass**: explicit call works; a full catalog of 600+ skills can hide descriptions; a minimal set also works implicitly |
| MiniMax | `~/.agents/skills` (not `~/.minimax/skills`) | project `.agents/skills`; also observed reading `~/.codex/skills` | full pass (top-level, zh/en); needs a whole-directory symlink |

> **Conditional pass** means the install is correct and works under constrained conditions
> (subagent/sub-session, minimal skill set, or explicit call), but the default top-level
> new session with a full catalog is not yet stable. You can keep using it, but release
> notes must not say "verified in the full environment".
>
> **DSH trap**: removing `~/.dsh/skills/doc-extract` is not enough; DSH also reads
> `~/.agents/skills`.
> **ZCode trap**: `~/.zcode/skills` and `~/.agents/skills` each discover the skill once;
> handle both when switching.
> **MiniMax trap**: MiniMax skips "directory + symlinked SKILL.md" and only recognizes a
> real file or a whole-directory symlink. Tested shapes: real file ✅, symlinked
> `SKILL.md` ❌, whole-directory symlink ✅. A new session re-scans the skill directory;
> restarting the app is not required. The catalog has a budget: one machine showed 173
> visible skills against 536 discoverable skill names, with `Skill descriptions were
> shortened to fit the catalog budget.` Keep the `docarbiter` entry or call it explicitly
> when the catalog is large. If several copies are installed, the `Location:` header of
> `skill({name})` shows which copy was loaded.
> **Codex large-catalog mitigation**: add this line to the global or project `AGENTS.md`:
> `For any PDF/document extraction task, load the docarbiter skill first.`
> This is more stable than competing on description text; alternatively keep only
> `docarbiter` plus the tool skills you actually use (a minimal set of 17 passed
> implicitly in one test). Codex works with a real `SKILL.md` copy; refresh it with
> `install.sh --skill-mode copy` or `update.sh`.
> **ZCode double discovery**: both the subagent and the top-level new session after an app
> restart pass; zh and en both call `docarbiter`. `.zcode/skills` and `.agents/skills`
> discover the same skill twice, which does not affect use; keep one copy or call it
> explicitly to reduce duplicates.
> **Shared-directory trap**: `~/.agents/skills` is shared by several harnesses. Before
> changing it, confirm each harness has a usable copy of the old router.

## 3. Switch steps (once per harness)

```bash
# 0) Check conflicts first
./scripts/doctor.sh --check-conflicts

# 1) Back up the old router outside the skills directory (do not leave .bak inside skills/)
mkdir -p ~/.claude/skill-backups
mv ~/.claude/skills/doc-extract ~/.claude/skill-backups/doc-extract.$(date +%Y%m%d-%H%M%S)

# 2) Install docarbiter
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills

# 3) Restart the harness session (not just another chat: the skill directory must be rescanned)

# 4) Test implicit triggering from a neutral directory (not the repository root)
cd /tmp
# Claude Code example:
claude -p "I have a scanned Chinese PDF and need page-anchored Markdown. Which tool should I use? Only route it."
```

Acceptance: the log/output contains `docarbiter` and **no longer** contains `doc-extract`;
the route is reasonable; the old router can be rolled back.

## 4. Rollback

```bash
rm -rf ~/.claude/skills/docarbiter
mv ~/.claude/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.claude/skills/doc-extract
```

DSH rollback also has to handle the global `.agents` directory:

```bash
# Restore DSH's own old router
mv ~/.dsh/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.dsh/skills/doc-extract
# If the global old router was moved as well:
mv ~/.agents/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.agents/skills/doc-extract
```

## 5. Release policy

- **Do not hard-code harness names into the core logic**; `route.py` and `SKILL.md` do not
  depend on private Claude Code / DSH / ZCode APIs.
- **Do not delete the old router automatically**; the installer only reports conflicts,
  and the user confirms replacement.
- **Do not claim "all harnesses verified"**; write release notes according to the actual
  state in `docs/release-checklist.md`.
- Environment configuration can happen after release: the user only needs to know their
  skill directory and run one `--skills-dir` command.
- For a harness that needs headless acceptance, first confirm its CLI can select a model
  and send a prompt; otherwise mark it "unverified". Do not substitute "the skill can be
  discovered" for "triggering passed".
- Update paths (`git pull` / `update.sh` / Codex copy / restart session) are in
  [`docs/updating.md`](updating.md).

## 6. Manual acceptance card (for the user's own harness)

Install the skill, restart the harness, open a **neutral-directory** session, then send:

```text
I have a scanned Chinese PDF and need page-anchored Markdown.
Which tool should I use? Only route it and give one copyable command; do not extract anything.
```

Chinese sample:

```text
我有个中文扫描版 PDF，想提取成带页码的 Markdown。
应该用哪个工具？只告诉我路由判断和一条可复制命令，不要实际提取。
```

**What to send back**:

1. the complete answer text (not a cropped screenshot);
2. whether the harness shows a tool/skill name, and whether `docarbiter` appears and the
   old `doc-extract` does not;
3. the tool and command it chose (expected: scan → MinerU, command contains `mineru-doc`);
4. if the answer came from a built-in `pdf` skill instead of docarbiter, say so directly.

Acceptance: **`docarbiter` appears + route is MinerU**. An answer that merely looks right
is not enough, because the old router could also answer correctly.

### Full prompt to paste

```text
First decide which document-extraction tool this task should use:
I have a scanned Chinese PDF and need page-anchored Markdown.
Only give me the routing decision and one copyable command; do not extract anything.
Then, in a separate paragraph, report which skill/tool you actually invoked (if the UI
shows the name) and the final tool choice; if you did not invoke a skill, say so explicitly.
```

### Fixed report template

```text
Harness: ZCode / Codex / MiniMax
Version/model:
Install: install.sh --skills-only --skills-dir ...
Old doc-extract: moved / still present / unsure
Skill name shown by the UI: docarbiter / doc-extract / built-in pdf / not shown
Full answer:
Errors or anomalies:
```

Do not reply with only "it worked"; include the full answer and the skill name. If no skill
name is shown, at least include the full answer and say whether the UI displayed a tool call.

## 7. Current machine state (2026-11-11)

| Harness | Current router shape | Old router location | Notes |
|---|---|---|---|
| Claude Code | `~/.claude/skills/docarbiter/SKILL.md` → local repo file symlink | `~/.claude/skill-backups/doc-extract.20261110-121227` | 2026-11-11 headless test: `Skill {"skill":"docarbiter"}`, routed MinerU |
| DSH | `~/.dsh/skills/docarbiter/SKILL.md` → local repo file symlink | `~/.dsh/skill-backups/doc-extract.20261110-125933`; global `~/.agents/skill-backups/doc-extract.20261110-130247` | 2026-11-11 headless test: session log shows `tool-call skill {"name":"docarbiter"}`, routed MinerU |
| ZCode | `~/.zcode/skills/docarbiter/SKILL.md` → `~/.local/share/docarbiter/...` file symlink | `~/.local/share/docarbiter-migration-backup/doc-extract` → global backup | full pass (top-level, zh/en); 307 discoverable skills in its catalog |
| MiniMax | `~/.agents/skills/docarbiter` → `~/.local/share/docarbiter/skills/docarbiter` whole-directory symlink | old router moved out | full pass (top-level, zh/en); 97 discoverable skills under `~/.agents` |
| Codex | `~/.codex/skills/docarbiter/SKILL.md` regular file | old router moved out | conditional; `doctor.sh` currently reports this copy as DRIFT until it is refreshed with `--skill-mode copy` |

Re-test after the frontmatter fix (2026-11-11, English prompt): Claude Code and DSH both
load `docarbiter` and route MinerU. Claude Code records `Skill {"skill":"docarbiter"}`;
DSH's session log records `skill({"name":"docarbiter"})` even though its stdout prints only
the final answer. Before the fix, DSH silently dropped the skill from its catalog because
the description contained an unquoted `: ` (see gotcha 24).

`doctor.sh` reports each harness's shape, whether it is the same source as this checkout,
whether its content matches, and whether its version is behind. It also prints the
discoverable skill count and warns above the catalog budget.
