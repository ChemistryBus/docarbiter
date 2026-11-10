# Harness 接入：一条技能目录命令

> 目标：发布后不依赖某个 harness 的 hook，也不把配置写死。每个 harness 只做两件事：
> **把 `docarbiter/SKILL.md` 放进它的技能目录** + **确保只有一个文档提取路由器**。

## 1. 通用安装

优先用仓库脚本，指定目标 harness 的技能目录：

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

`--skills-dir` 可以重复；`--profile core` 只注册 `docarbiter`，不会注册 12 个工具技能。

如果不想让脚本同时更新 `~/.local/bin` wrapper，只建一个软链即可：

```bash
DIR="$HOME/.claude/skills"          # 换成目标 harness
mkdir -p "$DIR/docarbiter"
ln -sfn "$PWD/skills/docarbiter/SKILL.md" "$DIR/docarbiter/SKILL.md"
```

## 2. 已知 harness 的目录

| Harness | 技能目录 | 额外读取 | 状态 |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | — | 已切换；旧路由备份停用 |
| DSH | `~/.dsh/skills` | `~/.agents/skills`（全局，`DSH_AGENTS_HOME` 可改） | 已切换；全局旧路由已移出 |
| ZCode | `~/.zcode/skills` | `~/.agents/skills`（会重复发现） | 旧路由仍在；CLI 需先设默认模型 |
| Codex | `~/.codex/skills` | 可能也读 `~/.agents` | 旧路由保留；未找到 CLI |
| MiniMax | `~/.minimax/skills` | 另有 `.builtin-skills` | 未测试；目录已存在 |

> **DSH 的坑**：只移 `~/.dsh/skills/doc-extract` 不够，它还会读 `~/.agents/skills`。
> **ZCode 的坑**：`~/.zcode/skills` 和 `~/.agents/skills` 会各发现一次；切换要同时处理。
> **共享目录的坑**：`~/.agents/skills` 被多个 harness 共用，动它之前先确认每个 harness 都有可用的旧路由副本。

## 3. 切换步骤（每个 harness 一次）

```bash
# 0) 先看冲突
./scripts/doctor.sh --check-conflicts

# 1) 备份旧路由器到技能目录之外（不要在 skills/ 里留 .bak，可能仍被发现）
mkdir -p ~/.claude/skill-backups
mv ~/.claude/skills/doc-extract ~/.claude/skill-backups/doc-extract.$(date +%Y%m%d-%H%M%S)

# 2) 安装 docarbiter
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills

# 3) 重启 harness 的会话（不是只重开一个聊天，要让技能目录重新扫描）

# 4) 在中立目录做隐式触发测试（不要在仓库根目录跑）
cd /tmp
# Claude Code 示例：
claude -p "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由。"
```

验收标准：日志/输出里出现 `docarbiter`，且**不再出现** `doc-extract`；路由结果合理；旧路由可回滚。

## 4. 回滚

```bash
rm -rf ~/.claude/skills/docarbiter
mv ~/.claude/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.claude/skills/doc-extract
```

DSH 的回滚还要考虑全局 `.agents`：

```bash
# 恢复 DSH 自己的旧路由
mv ~/.dsh/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.dsh/skills/doc-extract
# 如果当时也移了全局旧路由：
mv ~/.agents/skill-backups/doc-extract.YYYYMMDD-HHMMSS ~/.agents/skills/doc-extract
```

## 5. 发布策略

- **不把 harness 名称写死进核心逻辑**；`route.py` 和 `SKILL.md` 不依赖 Claude Code / DSH / ZCode 的私有 API。
- **不自动删除旧路由**；安装脚本只报告冲突，替换由用户确认。
- **不承诺“所有 harness 都已验证”**；发布说明按 `docs/release-checklist.md` 的实际状态写。
- 环境配置可以在发布后做：用户只需要知道自己的技能目录，然后一条 `--skills-dir` 命令。
- 需要无头验收的 harness，先确认它的 CLI 能选模型/发 prompt；否则标为“未验证”，不要用“技能能发现”冒充“触发通过”。

## 6. 手动验收卡（给用户在自己的 harness 里用）

装好技能、重启 harness、新开一个**中立目录**会话后，直接发：

```text
我有个中文扫描版 PDF，想提取成带页码的 Markdown。
应该用哪个工具？只告诉我路由判断和一条可复制命令，不要实际提取。
```

英文：

```text
I have a scanned Chinese PDF and need page-anchored Markdown.
Which tool should I use? Only route it and give one copyable command; do not extract anything.
```

**返回什么给我**：

1. 完整回答文本（不要截图里截一半）；
2. 如果 harness 显示工具/技能名，附上是否出现 `docarbiter`、是否出现旧 `doc-extract`；
3. 它选的工具和命令（预期：扫描件 → MinerU，命令含 `mineru-doc`）；
4. 如果回答来自内置 `pdf` 技能而不是 docarbiter，也直接说。

判断标准：**出现 docarbiter + 路由 MinerU** 才算触发通过；只是“回答看起来对”不算，因为旧路由器也可能答对。

## 7. 本机当前状态（2026-11-10）

| Harness | 当前路由器 | 旧路由位置 | 备注 |
|---|---|---|---|
| Claude Code | `docarbiter` | `~/.claude/skill-backups/doc-extract.20261110-121227` | 中英文触发通过 |
| DSH | `docarbiter` | `~/.dsh/skill-backups/doc-extract.20261110-125933`；全局 `~/.agents/skill-backups/doc-extract.20261110-130247` | 中英文 headless 通过 |
| ZCode | 旧 `doc-extract` | `~/.zcode/skills/doc-extract` → 全局备份 | 未切换；CLI 需先设模型 |
| Codex | 旧 `doc-extract` | `~/.codex/skills/doc-extract` → 全局备份 | 未找到 CLI；旧路由仍可用 |
| MiniMax | 未配置 | `~/.minimax/skills` 无旧路由 | 未测试；需要时按上面命令安装 |
