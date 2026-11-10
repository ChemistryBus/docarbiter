# P4：Codex / ZCode / DSH 触发验收（2026-11-10）

> 范围：DSH 已永久切换；ZCode / Codex / MiniMax 做技能发现/入口检查。
> 结论先说（2026-11-10 晚）：**DSH 完全通过；MiniMax 顶层完全通过（中英文）；ZCode 子代理通过、待 App 重启顶层确认；Codex 条件通过（显式/最小集可用，全量技能容量限制）。**
> Claude Code 的单测见 [`docs/p4-claude-code.md`](p4-claude-code.md)。

## 结果矩阵

| Harness | 技能目录 | 旧 doc-extract | 发现 docarbiter | 隐式触发 | 结论 |
|---|---|---|---|---|---|
| Claude Code | `~/.claude/skills` | 已备份停用 | 是 | 中/英文通过 | 已完成（见 p4-claude-code） |
| DSH | `~/.dsh/skills` + `~/.agents/skills` | 已备份停用 | 是 | 中文/英文通过 | **已永久切换**（旧路由可回滚） |
| ZCode | `~/.zcode/skills` + `~/.agents/skills` | 已移走 → `~/.local/share/docarbiter-migration-backup/` | 是 | **子代理通过** | 待 App 重启后的顶层会话确认 |
| Codex | `~/.codex/skills` | 已移走 | 是（symlink 和普通文件都识别） | **条件通过** | 全量 620 技能时隐式失败；最小集 17 技能时隐式通过；显式调用通过 |
| MiniMax | `~/.agents/skills` + `~/.codex/skills`（观察） | 已移走 | 是 | **完全通过** | 顶层新会话，中英文均 docarbiter → MinerU；整目录软链可用 |

## 晚间复测（ZCode / MiniMax / Codex）

- **ZCode**：子代理在 `/tmp` 新上下文里调用了 `docarbiter`，路由 MinerU；旧 `doc-extract` 已移走。严格性还差“重启 ZCode App 后的顶层新会话”，目前记为**有条件通过**。
- **MiniMax（完全通过）**：重启后的顶层新会话，中文和英文隐式提示都调用 `docarbiter`，路由 MinerU；旧路由器已移走。关键发现：MiniMax 扫描 `~/.agents/skills`，也观察到了 `~/.codex/skills`；它跳过“目录 + SKILL.md 文件软链”，只识别实体文件或**整目录软链**。
- **Codex（条件通过）**：`~/.codex/skills/docarbiter/SKILL.md` 已安装、旧 `doc-extract` 已移走。诊断结论：symlink 可识别；全量环境 619–620 个技能，其中 371–380 个未进入模型可见列表、描述被移除，隐式提示绕过 `docarbiter`；最小技能集（17 个，只保留 `docarbiter` + `mineru`）隐式提示实际读取 `docarbiter` 并路由 MinerU；显式说“使用 docarbiter”在全量环境也通过。**结论：安装正确，隐式触发受 Codex 技能容量影响。**
- **安装器修复**：`install.sh` 现在对 `~/.agents/skills`、`~/.codex/skills`、`~/.minimax/skills` 自动用整目录软链；Claude/DSH/ZCode 保持文件软链。可用 `--skill-mode dir|file` 强制。已有 `~/.local/bin` wrapper 会先备份为 `.bak.<timestamp>`。

## DSH：实测通过

### 1) 旧路由在场

安装 `~/.dsh/skills/docarbiter/SKILL.md` 后，用：

```bash
cd /tmp/p4-dsh
dsh --profile headless "我有个中文扫描版 PDF，想提取成带页码的 Markdown。应该用哪个工具？只路由，不提取。"
```

DSH 的 session 日志显示它**同时调用了两个 skill**：

```
skill {"name":"docarbiter"}
skill {"name":"doc-extract"}
```

最终路由仍正确（MinerU），但这是双路由共存：上下文被两份决策表同时占用，行为不可审计。

### 2) 旧路由临时停用

把 `~/.dsh/skills/doc-extract` 移到 `~/.dsh/skill-backups/` 后，同一提示只调用：

```
skill {"name":"docarbiter"}
bash  {"command":"for t in mineru-doc ...; do command -v $t; done"}
```

中文和英文都正确路由到 **MinerU**，并检查了本机工具可用性。

### 3) 永久切换（已完成）

DSH 不只读 `~/.dsh/skills`，还读 `~/.agents/skills`。只移 `~/.dsh/skills/doc-extract` 不够，英文提示仍会从全局目录加载旧路由。永久切换做了三件事：

1. `~/.dsh/skills/doc-extract` → `~/.dsh/skill-backups/doc-extract.20261110-125933`；
2. 全局 `~/.agents/skills/doc-extract` → `~/.agents/skill-backups/doc-extract.20261110-130247`；
3. Codex / ZCode 自己的旧路由 symlink 改指向该全局备份，避免把它们弄坏。

切换后重新跑中文、英文：

```
skill {"name":"docarbiter"}
bash  {"command":"command -v mineru-doc ..."}
```

两次都只调用 `docarbiter`，没有 `doc-extract`；路由 MinerU。**DSH 当前是 docarbiter 单入口。**

回滚：

```bash
mv ~/.dsh/skill-backups/doc-extract.20261110-125933 ~/.dsh/skills/doc-extract
mv ~/.agents/skill-backups/doc-extract.20261110-130247 ~/.agents/skills/doc-extract
# 再把 Codex / ZCode 的 doc-extract symlink 指回 ~/.agents/skills/doc-extract
```

## ZCode：发现通过，触发被模型选择卡住

ZCode app 的 CLI 在 bundle 内，不在 PATH：

```bash
node /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs --help
```

`skills list` 能发现安装到 `~/.zcode/skills/docarbiter` 的技能：

```
- docarbiter (user/zcode)
  ~/.zcode/skills/docarbiter/SKILL.md
```

但 `--prompt` 报：

```
Error: Select a model before sending a message
```

CLI 帮助里没有 `--model`；模型选择在 TUI / 桌面端配置里。尝试 `/model GLM-5.2` 作为 prompt 前缀仍报同一错误。**本轮没有完成 ZCode 隐式触发，不把它算通过。**

ZCode 同时扫描 `~/.zcode/skills` 和 `~/.agents/skills`。DSH 切换时已把全局 `~/.agents/skills/doc-extract` 移走，并让 `~/.zcode/skills/doc-extract` 指向备份；所以 ZCode 现在只有 `user/zcode` 这一份旧路由。将来切换 ZCode 只需要备份 `~/.zcode/skills/doc-extract`，再装 docarbiter。

## Codex：条件通过（技能容量限制）

2026-11-10 晚，用 Codex CLI `0.167.0-alpha.3.2` / `gpt-6-astra` 在两个环境复测：

| 环境 | 可见技能 | docarbiter 可见 | 隐式触发 | 显式触发 |
|---|---:|---|---|---|
| 全量 | 619–620 | 是 | **失败**（371–380 个技能未进入模型可见列表，描述被移除） | **通过** |
| 最小集 | 17 | 是 | **通过**（实际读取 `docarbiter/SKILL.md`） | 通过 |

结论：

- **安装和 symlink 都没问题**；Codex 能识别文件 symlink 和普通文件。
- 全量环境的问题是**技能容量/索引**：大量技能未进入模型可见列表，`docarbiter` 的 description 被裁掉，隐式提示自然绕过它。
- **显式调用可用**：说“使用 docarbiter 技能”会读取并路由。
- 要让隐式触发稳定：精简 Codex 技能目录，或使用最小技能集；不要把 600+ 技能和 docarbiter 混在一起后期待它稳定被选中。

本机当前 `~/.codex/skills/docarbiter/SKILL.md` 是普通文件；旧 `doc-extract` 已移走。

## 结论

1. **一个 harness 只能留一个文档提取路由器。** Claude Code 已证明旧路由会赢；DSH 证明旧路由会让模型同时加载两份技能。ZCode 也会从两个目录重复发现旧路由。
2. **DSH 已永久切换。** 旧路由停用、全局 `.agents` 旧路由移出后，中英文都只触发 docarbiter；Codex / ZCode 的旧路由副本保留，未被破坏。
3. **ZCode 子代理通过。** 子代理调用 docarbiter 并路由 MinerU；待 App 重启后的顶层会话确认。CLI 的 `--prompt` 仍需默认模型，但子代理不依赖它。
4. **Codex 条件通过。** 安装和 symlink 均正确；全量 620 技能时隐式触发被容量挤掉，最小集 17 技能时隐式通过，显式调用通过。使用建议：精简技能目录，或显式说“使用 docarbiter”。
5. **MiniMax 完全通过。** 顶层中英文都命中 docarbiter；它跳过文件 symlink，必须用整目录软链。

## 复现命令

```bash
# DSH
dsh --profile headless "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由。"

# ZCode 技能发现
node /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs skills list | grep -A2 docarbiter

# 查看 DSH session 里的实际 tool call
# ~/.dsh/sessions/--private-tmp-p4-dsh-final-zh--/*/session.jsonl.zstd
# zstd -dc ... | grep '"name":"skill"'
```

## 未完成

- [x] DSH 永久切换（2026-11-10，旧路由备份可回滚）
- [x] ZCode 子代理触发（docarbiter → MinerU）
- [ ] ZCode App 重启后的顶层新会话确认
- [x] Codex 的 symlink/容量诊断（显式通过；最小集隐式通过；全量隐式受容量影响）
- [x] MiniMax 顶层新会话触发（中文/英文 docarbiter → MinerU）
- [ ] 三个 harness 的真实文件路由 / 实际提取端到端
