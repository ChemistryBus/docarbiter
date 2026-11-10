# Harness 接入：一条技能目录命令

> 目标：发布后不依赖某个 harness 的 hook，也不把配置写死。每个 harness 只做两件事：
> **把 `docarbiter/SKILL.md` 放进它的技能目录** + **确保只有一个文档提取路由器**。

## 1. 通用安装

优先用仓库脚本，指定目标 harness 的技能目录：

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

`--skills-dir` 可以重复；`--profile core` 只注册 `docarbiter`，不会注册 12 个工具技能。

如果不想让脚本同时更新 `~/.local/bin` wrapper，只建一个**整目录软链**即可（比“目录 + SKILL.md 软链”兼容）：

```bash
DIR="$HOME/.claude/skills"          # 换成目标 harness
ln -sfn "$PWD/skills/docarbiter" "$DIR/docarbiter"
```

`install.sh --skill-mode auto` 会对 `~/.agents/skills`、`~/.codex/skills`、`~/.minimax/skills` 用整目录软链；对 Claude Code / DSH / ZCode 保持文件软链。需要强制时用 `--skill-mode dir|file`。

## 2. 已知 harness 的目录

| Harness | 技能目录 | 额外读取 | 状态 |
|---|---|---|---|
| Claude Code | `~/.claude/skills` | — | 已切换；旧路由备份停用 |
| DSH | `~/.dsh/skills` | `~/.agents/skills`（全局，`DSH_AGENTS_HOME` 可改） | 已切换；全局旧路由已移出 |
| ZCode | `~/.zcode/skills` | `~/.agents/skills`（会重复发现） | 子代理验收通过；待 App 重启后顶层会话确认 |
| Codex | `~/.codex/skills` | 可能也读 `~/.agents` | **条件通过**：全量技能时隐式受容量影响；显式调用通过，最小集隐式通过 |
| MiniMax | `~/.agents/skills`（不是 `~/.minimax/skills`） | 项目 `.agents/skills`；`.minimax/skills` 不被扫描 | 子会话验收通过；需整目录软链 |

> **术语：条件通过** = 安装正确，且在受限条件（子代理/子会话、最小技能集、显式调用）下通过；但默认的顶层新会话或全量技能环境尚未稳定通过。条件通过可以继续用，但不能在发布说明里写成“全量环境已验证”。
>
> **DSH 的坑**：只移 `~/.dsh/skills/doc-extract` 不够，它还会读 `~/.agents/skills`。
> **ZCode 的坑**：`~/.zcode/skills` 和 `~/.agents/skills` 会各发现一次；切换要同时处理。
> **MiniMax / Codex 的坑**：MiniMax 跳过“目录 + SKILL.md 文件软链”，只识别实体文件或整目录软链。MiniMax 实测：实体文件 ✅、SKILL.md 软链 ❌、整目录软链 ✅。Codex 能识别两种链接，但全量 600+ 技能时 `docarbiter` 可能因技能容量不可见；此时用显式“使用 docarbiter”，或精简技能目录。
>
> **Codex 大技能目录的改进**：在全局或项目 `AGENTS.md` 加一句
> `For any PDF/document extraction task, load the docarbiter skill first.`
> 这比依赖 description 竞争更稳定；或者只保留 `docarbiter` + 实际要用的工具技能（最小集 17 个时实测隐式通过）。
>
> **ZCode 顶层确认**：子代理通过是强证据，但严格验收要 App 重启后的顶层新会话；如果顶层失败，检查 `.zcode/skills/docarbiter` 和 `.agents/skills/docarbiter` 的双份发现，保留一份或显式调用。
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

### 给 agent 的完整话术（可直接粘）

```text
请先判断这个任务该用哪个文档提取工具：
我有个中文扫描版 PDF，想提取成带页码的 Markdown。
只告诉我路由判断和一条可复制命令，不要实际提取。
完成后另起一段，报告你实际调用了哪个技能/工具（如果界面能看到名字），
以及最终选择的工具；如果没有调用任何技能，也明确说“没有调用技能”。
```

### 固定回传模板

```text
Harness: ZCode / Codex / MiniMax
版本/模型:
安装方式: install.sh --skills-only --skills-dir ...
旧 doc-extract: 已移走 / 仍在 / 不确定
界面显示的技能名: docarbiter / doc-extract / 内置 pdf / 没显示
完整回答:
错误或异常:
```

返回时不要只写“成功了”；把完整回答和技能名一起贴回来。没有技能名时，至少贴完整回答，并说明界面是否显示工具调用。

## 7. 本机当前状态（2026-11-10）

| Harness | 当前路由器 | 旧路由位置 | 备注 |
|---|---|---|---|
| Claude Code | `docarbiter` | `~/.claude/skill-backups/doc-extract.20261110-121227`（指向 `~/.agents` 备份） | 中英文触发通过 |
| DSH | `docarbiter` | `~/.dsh/skill-backups/doc-extract.20261110-125933`；全局 `~/.agents/skill-backups/doc-extract.20261110-130247` | 中英文 headless 通过 |
| ZCode | `docarbiter` | `~/.local/share/docarbiter-migration-backup/doc-extract` → 全局备份 | 子代理验收通过；待 App 重启后顶层确认 |
| Codex | `docarbiter` | 旧路由已移走 | 安装成功但未触发；诊断 symlink/容量 |
| MiniMax | `docarbiter` | 旧路由已移走 | 子会话通过；扫描 `~/.agents/skills`，需整目录软链 |
