# Harness 原生调度 vs docarbiter

> 结论先说：**harness 通常能发现和调用技能，但一般没有「按文档类型 + 语言 + 文字层 + 目标产出」做确定性路由的能力。**
> 它靠模型读 `description` 做语义选择；同类技能一多，就变成竞争。`docarbiter` 补的是这一层领域路由策略。

## 1. 原生能力大致是什么

| 能力 | 典型实现 | 是否确定性 | 说明 |
|---|---|---|---|
| 技能发现 | 扫描技能目录，读 `SKILL.md` / frontmatter | 是 | 发现是确定的；选谁不是 |
| 技能选择 | 模型读 `description` 后决定 | **否** | 多个描述都匹配时，可能选错、可能问用户 |
| 显式调用 | `/skill-name`、命令、工具名 | 是 | 用户或脚本指定时才确定 |
| 子代理 | 独立上下文 + 工具集 | 否 | 子代理自己也会选工具 |
| 插件命名空间 | `plugin:skill` | 是（命名） | 减少重名，但不解决「选哪个」 |
| MCP 工具 | tool description / tool search | 否 | 工具多时同样竞争 |
| Hook | 在工具调用前后注入/拦截 | 是（可编程） | 与 harness 强绑定，不可移植 |

以 Claude Code 为例：技能通过 `SKILL.md` 的 `description` 被发现，模型根据描述和当前任务选择；没有内置的「PDF 有文字层 → 用 A，没有 → 用 B」规则。Codex、zcode、DSH 的具体实现各版本可能不同，但本机四套都是「技能目录 + 模型选择」的模式，不是领域路由器。

## 2. 为什么原生选择不够

- **不懂文档领域。** 模型不知道 CID 子集字体、ToUnicode、中文 OCR 模型、双栏阅读顺序、合并单元格；这些需要探针和规则。
- **没有降级链。** 原生选择是一次性的；结果不满意时，模型可能换一个工具，也可能重复同一个。
- **同类技能竞争。** 三个「PDF 提取」技能的 description 都匹配，选中哪个不可复现。
- **不可审计。** 很难回答「为什么这次选了 Marker 而不是 MinerU」。

## 3. docarbiter 补的是什么

```
输入 → 分类（格式/语言） → 探针（文字层是否可用） → 路由（目标产出） → 抽检 → 降级
```

- **规则显式**：决策表写在技能里，可 review、可测试。
- **领域知识**：文字层探针、CID/乱码判断、中文/英文差异、表格/扫描件分支。
- **降级链**：失败后按顺序换，并说明为什么换。
- **跨 harness**：一份技能，四套目录软链；不依赖某个 harness 的 hook。
- **可审计**：输出里写明「路由到谁、为什么、失败后换谁」。

## 4. 能不能让 harness 确定性地调用 docarbiter？

可以，但方式因 harness 而异：

- **显式调用**：用户说「用 docarbiter」，或建一个 `/docarbiter` slash command 包装。
- **Hook**：在 harness 支持的前提下，用 `PreToolUse` 注入路由提示；缺点是绑定 harness、可移植性差。
- **默认语义触发**：靠 `description` 里的「提取 PDF / 不确定用哪个 / 结果乱码」等短语；这是当前方式，跨 harness 最稳。

本项目的选择：**默认语义触发 + 可选显式调用**。不把核心逻辑绑在某个 harness 的 hook 上。

### Claude Code 实测（2026-11-10）

- 旧 `doc-extract` 和 `docarbiter` 同时存在时，中英文隐式提示都选中了 `doc-extract`；**description 再优化也抢不过一个同类路由器**。
- 把旧 `doc-extract` 的 symlink 移出 `~/.claude/skills` 后，中文 / 英文在 `/tmp` 中立目录都能触发 `docarbiter`。
- 测试要在中立目录跑：在仓库根目录，模型可能直接 `Read SKILL.md`，看起来像“没触发”，其实是被 cwd 的文件吸引。
- 结论：**一个 harness 只保留一个文档提取路由器**；先备份、再停用旧路由、再验收。完整记录见 [`docs/p4-claude-code.md`](p4-claude-code.md)。

### 其他 harness（2026-11-10）

| Harness | 发现 | 隐式触发 | 备注 |
|---|---|---|---|
| DSH | 是 | 中文/英文通过（旧路由临时停用） | 旧路由在场时同时加载两个 skill；测试后已恢复旧状态 |
| ZCode | 是（`skills list`） | 未完成 | `--prompt` 报 `Select a model`；需 TUI/桌面端设默认模型 |
| Codex | 未测 | 未完成 | 未找到 `codex` CLI 可执行文件 |

DSH 的结果再次说明：**共存不是“可能选错”，而是可能同时加载两份决策表**，比单选更不可审计。完整记录见 [`docs/p4-other-harnesses.md`](p4-other-harnesses.md)。

## 5. 它不做什么

- 不替代 harness 的工具调用、权限、沙箱。
- 不保证模型一定先调用它；只是把「调用后怎么选」写清楚。
- 不解决所有技能发现问题；同类工具技能仍建议用 `--profile full` 之外的方式管理（见 `docs/migration.md`）。

## 6. 给其他 harness 维护者的建议

如果你在自己的 harness 里做原生调度，最少需要：

1. 文件类型 / 语言检测；
2. PDF 文字层探针（字符数 + 替换符 + CJK 覆盖率）；
3. 目标产出分类（速度 / 成稿 / 表格 / 复杂表格 / RAG / OCR）；
4. 工具可用性与版本检查；
5. 降级链与可解释输出。

这五步就是 `docarbiter` 的核心；可以直接复用 `registry.json` 和 `docs/architecture.md` 的结构。
