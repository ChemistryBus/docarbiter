# 架构：为什么「工具很多」仍然能调度

> 相关文件：`skills/docarbiter/SKILL.md`（调度器）、`registry.json`（机器可读注册表）、`skills/_tools/*.md`（薄壳）。
> 图：`docs/assets/overview-zh.svg` / `overview-en.svg`。

## 一、三层分离

```
        ┌──────────────────────────────────────────┐
        │ 1. 调度器  skills/docarbiter/SKILL.md     │
        │    分类 → 探针 → 路由 → 降级              │
        │    只写「规则」，不写每个工具的细节          │
        └──────────────────┬───────────────────────┘
                           │ 读取
        ┌──────────────────▼───────────────────────┐
        │ 2. 注册表  registry.json                  │
        │    id / tier / languages / input_types /  │
        │    output_types / best_for / avoid_when / │
        │    install / upstream / status            │
        └──────────────────┬───────────────────────┘
                           │ 对应
        ┌──────────────────▼───────────────────────┐
        │ 3. 薄壳  skills/_tools/<id>.md            │
        │    定位 / 装 / 用 / 坑 / 上游              │
        │    每个 15–40 行，只写本工具              │
        └──────────────────────────────────────────┘
```

**规则只写一份。** 调度器不需要知道 18 个工具的完整命令；它只需要知道「什么输入、什么目标、哪一类工具」以及「缺工具时怎么降级」。工具细节在薄壳里，工具清单在注册表里。

## 二、为什么不是「每个工具一个顶层技能」

默认安装只注册 `docarbiter` 一个技能。原因：

- 如果 18 个工具各注册一个顶层技能，18 个 `description` 都会匹配「提取 PDF」，agent 会随机挑；这正是项目要解决的问题。
- 顶层技能越多，重名/冲突/维护成本越高（N 个工具 → O(N²) 的交叉引用）。
- 默认单入口 + `--profile full` 可选注册，兼顾「普通用户不乱」和「专家可直调」。

## 三、怎么加第 19 个工具

### 情况 A：属于已有类别（推荐）

例如新增一个「中文表格 OCR」工具，它仍然属于「表格 / 扫描件」类别。

1. 在 `registry.json` 的 `tools` 里加一条记录（复制现有条目，填 `id`、`tier`、`languages`、`input_types`、`output_types`、`best_for`、`avoid_when`、`install`、`upstream`、`status`）。
2. 加 `skills/_tools/<id>.md` 薄壳（定位 / 装 / 用 / 坑 / 上游）。
3. **不改调度器**，除非它的优先级高于现有首选。如果优先级更高，只改决策表里对应的一行 + 降级链。
4. 跑 `python3 -I scripts/validate.py` 和 `./scripts/doctor.sh --check-conflicts`。

### 情况 B：引入新类别

例如新增「字幕 / 音频转写」类别。

1. 在 `docarbiter` 的分类逻辑里加一行输入类型分支。
2. 在决策表里加一行「目标 → 首选 → 备选」。
3. 在降级链里加一条。
4. 其余同情况 A。

### 情况 C：许可证不允许默认安装

例如 AGPL 工具。

- 只进 `registry.json` 的 `excluded`，或进 `tools` 但 `tier: "excluded"` + `install` 写「不自动安装」。
- `THIRD_PARTY_NOTICES.md` 给链接与原因。
- 调度器可以「建议用户自行安装」，但不得自动装。

## 四、调度器的判断顺序

```
1. 用户是否明确指定工具？
   是 → 直接调用（最多提示一句风险），结束。
2. 输入格式？
   PDF / Office / 图片 / 音视频 / HTML / EPUB...
3. 语言？（中文 / 英文 / 混排）
   中文额外看 CJK 覆盖率；英文看替换符与乱码率。
4. PDF 文字层可用吗？
   可用 → 按目标路由
   扫描 / 乱码 → OCR 或 MinerU，再回到 4
5. 目标产出？
   速度 / 成稿 / 纯文字 / 表格（简单网格 / 复杂合并） / RAG / LaTeX / OCR
6. 工具在不在？
   不在 → 给安装命令 + 已装工具的降级方案
7. 选中工具；失败或结果不满意 → 降级链
```

## 五、可用性检查

调度器不能路由到没装的工具。检查方式：

```bash
command -v mineru-doc
command -v liteparse-doc
command -v docling
python3 -c "import rapidocr"
python3 -c "import pdfplumber"
```

缺工具时：

1. 给出精确安装命令（版本固定）；
2. 给出一个已装工具的替代路径；
3. 不静默失败。

## 六、反模式

- ❌ 在每个薄壳里复制完整路由表 → 规则漂移。
- ❌ 默认把每个工具注册成顶层技能 → 回到「一锅粥」。
- ❌ 在调度器里硬编码 18 个工具的完整命令 → 每次上游改参数都要改调度器。
- ❌ 只按 star 数排序 → 中文扫描件会被路由到不适合的工具。
- ❌ 拿 `pdftotext` 当答案 → 基准变成循环论证。
- ❌ 自动安装 AGPL / 自动调用云 API → 许可与隐私风险。

## 七、可执行镜像

`scripts/route.py` 是同一套决策表的可执行版本：

```bash
python3 -I scripts/route.py file.pdf --goal manuscript
python3 -I scripts/route.py --selftest
```

它做同样的 PDF 探针（字符数 / CJK / 控制字符 / 乱码率），输出 `intended` / `selected` / `reason` / `command` / `fallback`。区别：

- `docarbiter` 给 agent 用，能问澄清问题、读薄壳、解释降级；
- `route.py` 给脚本 / CI / 非 agent 用户用，输出确定、可断言。

`--selftest` 是工程验收：文字层 / 扫描件 / CID / 繁体 / 交错双栏 / 真实 CC BY / 表格 / 复杂表格，路由必须和预期一致。CI 会跑它。

## 八、扩展检查清单

- [ ] `registry.json` 能解析，`id` 唯一
- [ ] core / extra 工具都有对应薄壳
- [ ] 薄壳有「定位 / 装 / 用 / 坑 / 上游」
- [ ] 新工具的中文/英文状态标「实测」或「待测」，不吹
- [ ] 新类别的降级链已写
- [ ] `THIRD_PARTY_NOTICES.md` 已补
- [ ] `validate.py` 通过
- [ ] `doctor.sh --check-conflicts` 通过
