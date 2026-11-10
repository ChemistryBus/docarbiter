# 迁移：已有 doc-extract / 单工具技能怎么办

> 默认策略：**先共存，验证后再替换；不自动删除任何旧技能。**
> 2026-11-10：Claude Code 和 DSH 已完成 P4 实测并切换为 `docarbiter`；旧 `doc-extract` 分别备份在 `~/.claude/skill-backups/` 和 `~/.dsh/skill-backups/`。DSH 还会读 `~/.agents/skills`，该全局旧路由也已移到 `~/.agents/skill-backups/`；Codex / ZCode 的旧路由副本保留。MiniMax 未配置。
> 实测记录见 [`docs/p4-claude-code.md`](p4-claude-code.md)。

## 1. 先检测

```bash
./scripts/doctor.sh --check-conflicts
```

会看到类似：

```
.claude    router    doc-extract
.codex     router    doc-extract
.zcode     router    doc-extract
.dsh       router    doc-extract
legacy-router  note  检测到旧 doc-extract；安装 docarbiter 后建议移除旧的
```

如果同时装了 `docarbiter` 和 `doc-extract`，会变成：

```
dual-router  WARN  docarbiter 与旧 doc-extract 同时存在；建议只保留一个
```

## 2. 共存（推荐的第一步）

在**一个** harness 里先试 `docarbiter`，其他 harness 保持旧路由：

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

然后在这个 harness 里问：

- 「提取这个 PDF，该用哪个工具？」
- 「这个中文扫描件怎么转 Markdown？」
- 「两个工具结果不一样，换一个试试。」

观察它是否按预期路由、是否和旧 `doc-extract` 抢触发。确认后再扩展到其他 harness。

> 两个路由器同时存在时，模型可能选错；这是**测试期**，不要同时对外承诺两个入口。

## 3. 替换（验证通过后）

以一个 harness 为例：

```bash
# 1) 备份旧路由器（不要直接 rm，也不要留在 skills/ 里，否则仍可能被发现）
mkdir -p ~/.claude/skill-backups
mv ~/.claude/skills/doc-extract ~/.claude/skill-backups/doc-extract.$(date +%Y%m%d-%H%M%S)

# 2) 安装 docarbiter
cd docarbiter
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills

# 3) 体检
./scripts/doctor.sh --check-conflicts

# 4) 在 /tmp 等中立目录跑真实触发（不要在仓库根目录跑，模型会去读 SKILL.md）
cd /tmp
claude -p "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由。" \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill,Read"
```

其他 harness 把 `~/.claude` 换成 `~/.codex` / `~/.zcode` / `~/.dsh`。

### 回滚

```bash
rm -rf ~/.claude/skills/docarbiter
mv ~/.claude/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.claude/skills/doc-extract
```

`install.sh` 只在 `--force` 时备份同名目标为 `SKILL.md.bak.<时间>`；回滚时按实际文件名恢复。

## 4. 单工具技能冲突

如果你已经有 `liteparse` / `markitdown` / `docling` / `mineru` 单工具技能：

- **默认 `--profile core`**：只注册 `docarbiter`，不注册工具技能，不会和它们同名。
- **`--profile full`**：会把 12 个工具注册成独立技能；同名时 `install.sh` 会跳过或（`--force`）备份后覆盖。建议先卸载旧的同名技能，或只用 `core`。
- `doctor.sh --check-conflicts` 会列出「同一 harness 同时有工具技能和 docarbiter」的情况；`--profile full` 下属预期，但要知道自己在做什么。

## 5. 对其他用户

这不是你一个人的情况。任何装过文档提取技能的人都会遇到：

- 旧的单工具技能（`liteparse` / `markitdown` / `docling`）；
- 旧的调度技能（`doc-extract` 或别的路由器）；
- 新装的 `docarbiter`。

给用户的默认建议：

1. 先跑 `doctor.sh --check-conflicts`；
2. 先在一个 harness 用 `--skills-only` 试 `docarbiter`；
3. 确认后再替换旧路由器；
4. 保留备份，能回滚；
5. 不要同时对外承诺两个入口。

## 6. 发布前提醒

- [ ] README「安装前须知」已写迁移步骤
- [ ] Release notes 写清楚「docarbiter 与旧 doc-extract 二选一」
- [x] `doctor.sh --check-conflicts` 在已有技能环境能跑（2026-11-10）
- [x] 回滚步骤在 Claude Code 临时验证过一次（移动/恢复 symlink）
- [x] 不自动删除用户旧技能

> 本机现状（2026-11-10）：Claude Code 和 DSH 只有 `docarbiter`；旧 `doc-extract` 分别备份在 `~/.claude/skill-backups/doc-extract.20261110-121227`、`~/.dsh/skill-backups/doc-extract.20261110-125933`，全局 `~/.agents/skills/doc-extract` 备份在 `~/.agents/skill-backups/doc-extract.20261110-130247`。Codex / ZCode 仍保留旧 `doc-extract`（指向全局备份）；MiniMax 未配置。
>
> `doctor.sh --check-conflicts` 的 `dual-router` 是跨 harness 汇总警告：`.claude/.dsh` 是 docarbiter，`.codex/.zcode` 是 doc-extract，并不表示单个 harness 内部还有双路由。看冲突时要按 harness 分栏读。
