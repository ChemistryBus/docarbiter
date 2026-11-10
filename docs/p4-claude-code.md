# P4：Claude Code 真实触发验收（2026-11-10）

> 范围：只测 **Claude Code**。Codex / zcode / DSH 未动，仍保留旧 `doc-extract`。
> 模型：`claude -p --model haiku`，非交互 `stream-json`；这是低成本触发测试，发布前应在 Sonnet / Opus 上复测。
> 安装：`~/.claude/skills/docarbiter/SKILL.md` 软链到本仓库；旧 `doc-extract` 的 symlink 已移到 `~/.claude/skill-backups/doc-extract.20261110-121227`，源目录 `~/.agents/skills/doc-extract` 未动。

## 结果

| 测试 | 旧 doc-extract | 实际调用 | 结论 |
|---|---|---|---|
| 技能发现 | 有 | — | 新会话能列出 `docarbiter`，返回 YES |
| 中文隐式触发 | 有 | `Skill: doc-extract` | **旧路由器赢**，docarbiter 未被调用 |
| 英文隐式触发 | 有 | `Skill: doc-extract` | **旧路由器赢**，与语言无关 |
| 中文隐式触发 | 已停用 | `Skill: docarbiter` | 正确路由 `mineru`，给出 `mineru-doc` 命令 |
| 英文隐式触发（`/tmp` 中立目录） | 已停用 | `Skill: docarbiter` | 正确路由 `mineru`，中英双语描述都能触发 |
| 中文 + 真实文件路径（`zh-scan.pdf`） | 已停用 | `Skill: docarbiter` + Bash 探针 | 探针 `chars=0 cjk=0` → 正确路由 `mineru`，并检查了 `mineru-doc` / `ocrmypdf` 可用性 |
| 英文隐式触发（仓库根目录） | 已停用 | 未调用 Skill，直接 Read `SKILL.md` | 路由仍正确，但**不算干净的技能触发**；cwd 在仓库里会让模型改去读文件 |

## 结论

1. **共存不可接受。** 只要旧 `doc-extract` 还在 `~/.claude/skills`，中英文隐式提示都会选旧路由器；docarbiter 的 description 再写也抢不过。
2. **停用旧路由后，docarbiter 能接管。** 中文、英文在 `/tmp` 中立目录都能触发；给真实文件路径时，它会先跑文字层探针（`chars=0`），再正确路由扫描件 → MinerU，并检查 `mineru-doc` / `ocrmypdf` 是否可用。
3. **测试要在中立目录做。** 在仓库根目录跑 `claude -p`，模型会先 `ls` / `Read SKILL.md`，看起来“没触发”，其实是被 cwd 里的文件吸引。真实用户项目不会这样，但验收必须避免这个偏差。
4. **不自动删除旧技能。** 本次只移动 symlink 到 `~/.claude/skill-backups/`，源目录和其他 harness 保留；可随时恢复。
5. **触发是模型相关行为。** `haiku` 上通过不等于 Sonnet / Opus 上通过；发布前要复测，且不要把“某次触发成功”当成稳定保证。

## 复现

```bash
# 0) 确认 docarbiter 被发现
claude -p "当前可用技能里有没有 docarbiter？有就 YES。" \
  --model haiku --output-format json

# 1) 中文隐式触发（应在中立目录跑）
cd /tmp
claude -p "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由，不提取。" \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill,Read"

# 2) 英文隐式触发
claude -p "I have a scanned Chinese PDF and need page-anchored Markdown. Which tool? Use your routing skill; route only." \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill"

# 3) 查看是否调用了 Skill
#    在 stream-json 里找 "name":"Skill" 和 "skill":"docarbiter"
```

## 恢复旧路由（Claude Code）

```bash
mv ~/.claude/skill-backups/doc-extract.20261110-121227 ~/.claude/skills/doc-extract
```

恢复后，Claude Code 会重新和 `docarbiter` 抢触发；这是**回滚**，不是推荐状态。

## 未完成

- [ ] Sonnet / Opus 上复测中英文触发
- [x] 真实文件路由（`benchmarks/fixtures/zh-scan.pdf`，只路由，未提取）
- [ ] 真实文件的实际提取端到端测试（本轮只路由）
- [ ] Codex / zcode / DSH 的同类测试（本轮未动）
- [ ] 旧 `doc-extract` 在 Claude Code 的最终去留（当前是备份停用，不是删除）
