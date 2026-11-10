# Migration: What to Do If You Already Have doc-extract / Single-Tool Skills

> Default policy: **coexist first, replace only after validation; never auto-delete any old skill.**
> 2026-11-10: Claude Code and DSH have completed P4 real-world testing and switched to `docarbiter`; the old `doc-extract` is backed up in `~/.claude/skill-backups/` and `~/.dsh/skill-backups/` respectively. DSH also reads `~/.agents/skills`, and that global old router has also been moved to `~/.agents/skill-backups/`; the old router copies for Codex / ZCode are kept. MiniMax is not configured.
> See [`docs/p4-claude-code.md`](p4-claude-code.md) for the test log.

## 1. Detect First

```bash
./scripts/doctor.sh --check-conflicts
```

You will see something like:

```
.claude    router    doc-extract
.codex     router    doc-extract
.zcode     router    doc-extract
.dsh       router    doc-extract
legacy-router  note  检测到旧 doc-extract；安装 docarbiter 后建议移除旧的
```

If both `docarbiter` and `doc-extract` are installed, it becomes:

```
dual-router  WARN  docarbiter 与旧 doc-extract 同时存在；建议只保留一个
```

## 2. Coexist (Recommended First Step)

Try `docarbiter` in **one** harness first, keeping the old router in the others:

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

Then ask in that harness:

- Chinese sample: 「提取这个 PDF，该用哪个工具？」 ("Which tool should I use to extract this PDF?")
- Chinese sample: 「这个中文扫描件怎么转 Markdown？」 ("How do I convert this Chinese scan to Markdown?")
- Chinese sample: 「两个工具结果不一样，换一个试试。」 ("The two tools gave different results; try another one.")

Watch whether it routes as expected and whether it competes with the old `doc-extract` for triggers. Once confirmed, expand to other harnesses.

> When two routers coexist, the model may choose the wrong one; this is the **testing period**, so do not publicly commit to two entry points at the same time.

## 3. Replace (After Validation Passes)

Using one harness as an example:

```bash
# 1) Back up the old router (do not rm it directly, and do not leave it in skills/, or it may still be discovered)
mkdir -p ~/.claude/skill-backups
mv ~/.claude/skills/doc-extract ~/.claude/skill-backups/doc-extract.$(date +%Y%m%d-%H%M%S)

# 2) Install docarbiter
cd docarbiter
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills

# 3) Health check
./scripts/doctor.sh --check-conflicts

# 4) Run a real trigger from a neutral directory such as /tmp (do not run from the repo root; the model will read SKILL.md). The -p prompt below is a Chinese sample.
cd /tmp
claude -p "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由。" \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill,Read"
```

For other harnesses, replace `~/.claude` with `~/.codex` / `~/.zcode` / `~/.dsh`.

### Rollback

```bash
rm -rf ~/.claude/skills/docarbiter
mv ~/.claude/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.claude/skills/doc-extract
```

`install.sh` only backs up same-named targets as `SKILL.md.bak.<timestamp>` when `--force` is used; on rollback, restore using the actual file name.

## 4. Single-Tool Skill Conflicts

If you already have single-tool skills for `liteparse` / `markitdown` / `docling` / `mineru`:

- **Default `--profile core`**: registers only `docarbiter`, not the tool skills, so there are no name collisions with them.
- **`--profile full`**: registers the 12 tools as standalone skills; on a name collision, `install.sh` skips them or (with `--force`) backs them up and overwrites. It is recommended to uninstall the old same-named skills first, or to use only `core`.
- `doctor.sh --check-conflicts` lists cases where "the same harness has both a tool skill and docarbiter"; under `--profile full` this is expected, but you should know what you are doing.

## 5. For Other Users

This is not unique to you. Anyone who has installed document-extraction skills will run into:

- old single-tool skills (`liteparse` / `markitdown` / `docling`);
- an old routing skill (`doc-extract` or another router);
- the newly installed `docarbiter`.

Default advice for users:

1. Run `doctor.sh --check-conflicts` first;
2. Try `docarbiter` in one harness with `--skills-only` first;
3. After confirming, replace the old router;
4. Keep the backup so you can roll back;
5. Do not publicly commit to two entry points at the same time.

## 6. Pre-Release Checklist

- [ ] The README "Before You Install" section documents the migration steps
- [ ] The release notes clearly state "choose one of docarbiter or the old doc-extract"
- [x] `doctor.sh --check-conflicts` runs in an environment that already has skills (2026-11-10)
- [x] The rollback steps were verified once ad hoc in Claude Code (moving/restoring a symlink)
- [x] Old user skills are not auto-deleted

> Current state on this machine (2026-11-10): Claude Code and DSH have only `docarbiter`; the old `doc-extract` is backed up in `~/.claude/skill-backups/doc-extract.20261110-121227` and `~/.dsh/skill-backups/doc-extract.20261110-125933`, and the global `~/.agents/skills/doc-extract` is backed up in `~/.agents/skill-backups/doc-extract.20261110-130247`. Codex / ZCode still keep the old `doc-extract` (pointing to the global backup); MiniMax is not configured.
>
> The `dual-router` from `doctor.sh --check-conflicts` is a cross-harness aggregate warning: `.claude/.dsh` have docarbiter and `.codex/.zcode` have doc-extract; it does not mean a single harness still has dual routers. Read conflicts by harness column.
