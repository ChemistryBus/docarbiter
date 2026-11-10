# P4：Codex / ZCode / DSH 触发验收（2026-11-10）

> 范围：DSH 已永久切换；ZCode / Codex / MiniMax 只做技能发现/入口检查，不永久改。
> 结论先说：**DSH 中英文 headless 触发通过并已切换；ZCode 能发现技能但 CLI 缺模型选择；Codex 未找到 CLI 可执行文件；MiniMax 有技能目录、未测试。**
> Claude Code 的单测见 [`docs/p4-claude-code.md`](p4-claude-code.md)。

## 结果矩阵

| Harness | 技能目录 | 旧 doc-extract | 发现 docarbiter | 隐式触发 | 结论 |
|---|---|---|---|---|---|
| Claude Code | `~/.claude/skills` | 已备份停用 | 是 | 中/英文通过 | 已完成（见 p4-claude-code） |
| DSH | `~/.dsh/skills` + `~/.agents/skills` | 已备份停用 | 是 | 中文/英文通过 | **已永久切换**（旧路由可回滚） |
| ZCode | `~/.zcode/skills` + `~/.agents/skills` | `~/.zcode` 仍有 | 是（`skills list`） | **未完成** | CLI `--prompt` 报 `Select a model`；需 TUI/桌面端选模型 |
| Codex | `~/.codex/skills` | 有（指向备份） | 未测 | 未完成 | 未找到 `codex` CLI 可执行文件 |
| MiniMax | `~/.minimax/skills` | 无 | 未测 | 未完成 | 目录存在；未找到 CLI/无头入口 |

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

## Codex：未找到 CLI

本机检查：

```bash
command -v codex        # 空
find /Applications ~/Applications ~/Library/Application\ Support/Codex -maxdepth 4 -name codex
```

没有找到 `codex` 可执行文件；`~/.codex/skills` 存在，旧 `doc-extract` symlink 现在指向 DSH 切换时留下的全局备份（仍然有效），`~/.codex/config.toml` 也有配置，但无法从命令行发起非交互 prompt。**本轮未测试 Codex 触发**；需要先确认 Codex 的 CLI/桌面入口。

## 结论

1. **一个 harness 只能留一个文档提取路由器。** Claude Code 已证明旧路由会赢；DSH 证明旧路由会让模型同时加载两份技能。ZCode 也会从两个目录重复发现旧路由。
2. **DSH 已永久切换。** 旧路由停用、全局 `.agents` 旧路由移出后，中英文都只触发 docarbiter；Codex / ZCode 的旧路由副本保留，未被破坏。
3. **ZCode 需要先解决模型选择。** 技能发现没问题；CLI `--prompt` 需要 TUI/桌面端设置默认模型，才能做无头触发。切换时只需备份 `~/.zcode/skills/doc-extract`。
4. **Codex 先解决入口。** 没有 CLI 就无法做非交互验收；旧路由仍保留，不要在未测试的情况下声称兼容。
5. **MiniMax 暂不写死。** `~/.minimax/skills` 存在，但本轮没找到无头入口；发布后按 `docs/harness-integration.md` 的 `--skills-dir` 方式接。

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
- [ ] ZCode 设置默认模型后的中英文触发
- [ ] Codex 的 CLI/桌面入口与中英文触发
- [ ] MiniMax 的无头入口与触发
- [ ] 三个 harness 的真实文件路由 / 实际提取端到端
