# docarbiter

> 中英文优先的文档提取**仲裁器** + 工具合集：告诉你该装哪个、什么时候换哪个，以及每个工具在中文/英文文档上会在哪里翻车。

**中文** | [English](README.en.md)

**仓库：** `ChemistryBus/docarbiter`（首个公开版 `v0.1.0`）
**调度器技能：** `docarbiter`
**状态：** v0.1.0 / 首个公开预览（core 可运行）。`docarbiter`、12 个薄壳、wrappers、`route.py` 可执行路由、`bench.py` / `bench_abstract.py` / `bench_policy.py`、11 篇合成双语样本、4 篇真实 CC BY-SA 样本、CID/繁体/交错双栏/真竖排边缘样本、真实双栏论文定性 + BERT abstract CER、表格单元格级准确率与 default/text 策略对比、5 份真实高频表（WS/T 578.1 / GB 28050 / DRIs 2023 / GB 2760 / 中国食物成分表）分流测试、core 8 工具与 OCR 路径对比、干净 venv 安装与可靠性测试、工作区 8,444 个真实 PDF 的只读抽样与 4 文件 smoke、P0 policy benchmark、Claude Code / DSH P4 触发测试（旧 doc-extract 已备份停用）已落地；扩展层未装（按你选 A）。

![docarbiter overview](docs/assets/overview-zh.svg)

## 验证状态（摘要）

| 范围 | 状态 | 详情 |
|---|---|---|
| core 文字层 / 扫描 / CID / 双栏 | 已测 | [docs/benchmarks.md](docs/benchmarks.md) |
| 真实高频表（WS/T、GB 28050、DRIs、GB 2760、食物成分表） | 结构 + 抽检 | [docs/policy.md](docs/policy.md) P2 |
| P0 路由策略（22 个有答案文档） | 已测 | [docs/policy.md](docs/policy.md) |
| Claude Code / DSH 触发 | 已测 | [docs/p4-claude-code.md](docs/p4-claude-code.md) / [docs/p4-other-harnesses.md](docs/p4-other-harnesses.md) |
| ZCode / Codex / MiniMax 触发 | 未完成 | 发布后按 [docs/harness-integration.md](docs/harness-integration.md) 配 |
| Linux / Windows | Linux CI 待跑；Windows 未验证 | 发布说明会标出 |

完整的表格、失败页和最差样例放在 `docs/`；README 只保留摘要，避免把测试现场和安装说明混在一起。

---

## 为什么需要这个项目

GitHub 上高星的 PDF / 图片提取工具很多，但落到中文文档上，常见三种失败：

1. **装错工具。** 用户按 star 数或第一条搜索结果下载，不知道 MinerU、Docling、Marker、PaddleOCR、liteparse、MarkItDown 各自的边界。
2. **中文和英文的失败模式不同。** 中文 PDF 的坑是 CID 子集字体没有 ToUnicode、扫描件需要中文 OCR 模型、双栏/竖排/全角标点/无空格断行、合并单元格表格；英文的坑是连字符换行、双栏、页眉页脚、引号/破折号归一化。英文样本跑分高，不代表中文可用，反之亦然。
3. **同类技能互相打架。** 同一个 harness 里装了三四个「PDF 提取」技能，`description` 都匹配，agent 随机挑一个，结果不可复现。

本项目的答案不是再写一个提取器，而是三件事：

- 一份**经过中文语料实测**的工具清单（装哪个、不装哪个、为什么）；
- 一张**唯一的路由决策表**（什么输入、什么目标、走哪个工具）；
- 一组**薄壳技能**：只写定位、安装、命令、实测坑、上游链接，不复制上游代码。

## 适用于谁

| 人群 | 为什么需要 |
|---|---|
| **中文 / 英文文档工作者** | 论文、报告、扫描件、表格；不想记 12 个工具的命令和坑。 |
| **Agent / harness 用户** | 装了多个同类技能；需要唯一入口，避免随机挑工具。 |
| **工具维护者** | 新增工具 = 一个薄壳 + 一条 registry 记录；类别不变就不改调度器。 |

**不适用于：** 想要一个新 PDF 解析库的人；想要厂商 onboarding 包的人；默认把文件上传到云 API 的人。

## 它是什么 / 不是什么

**是：**

- 选型指南 + 调度技能 + 可复现的中文评测脚本
- 厂商无关：在互相竞争的开源工具之间做路由
- 薄壳分发：`scripts/install.sh` 调用上游，仓库内不含上游代码
- 默认只注册**一个**技能 `docarbiter`；专家可用 `--profile full` 注册独立工具技能

**不是：**

- 不是新的 PDF 解析库
- 不是某个厂商给自己产品做的 onboarding 包
- 不收录 Anthropic `pdf` 技能（Proprietary，只给链接）
- 不推荐 PyMuPDF / PDF-Extract-Kit（AGPL-3.0，只给链接并说明原因）

## 工具地图

### 核心层（默认安装，CPU 可跑，许可证宽松）

| 工具 | ★ | 许可证 | 角色 | 中英状态 |
|---|---:|---|---|---|
| **MinerU** | 83k | Apache-2.0 + 附加条款 | PDF → 结构化 Markdown、页码锚点 | 中英 demo 0.0046 / 0.0013；扫描 1.59% / 0.20% |
| **Docling** | 70k | MIT | Office / HTML / EPUB / 音视频 / RAG chunks / LaTeX / 复杂合并表格 | 中英 demo 0.0061 / 0.0093；扫描 1.01% / 7.12%；真实合并表结构与阅读顺序最好 |
| **liteparse** | 13k | Apache-2.0 | 最快的有文字层 PDF | 中英 demo 0.13–0.42 s / 0.0061；0.14 s / 0.0079 |
| **MarkItDown** | 195k | MIT | 单栏 / Office 快速转 Markdown | 中英 demo 0.0061 / 0.0185；合成纯文字双栏未复现；真实论文含图会打散；扫描件不适用 |
| **RapidOCR** | 8.5k | Apache-2.0 | 图片 / 截图 OCR | 中文扫描 1.16%；英文扫描 0.10% |
| **OCRmyPDF** | 35k | MPL-2.0 | 扫描 PDF 加文字层 | 中文扫描 10.1%；英文扫描 0.20% |
| **pdfplumber** | 11k | MIT | 简单有框线表格 / 字符坐标 | 合成有框线/合并 1.000；真实多行单元格会乱序；无框线 0 表，text 策略可到 1.000/0.917 但伤合并；交错双栏 60–68% |
| **pdftotext**（Poppler） | — | GPL-2.0/3.0 | 纯文字基线、文字层探测 | 中英文字层；CID/无 ToUnicode 会乱码 |

### 扩展层（按需安装；重依赖、GPU 或特殊场景）

| 工具 | ★ | 许可证 | 角色 | 中英备注 |
|---|---:|---|---|---|
| **PaddleOCR** | 92k | Apache-2.0 | 中文 OCR / PP-Structure | 中英 OCR；CER 待测；依赖 paddlepaddle，体积大 |
| **Marker** | 41k | Apache-2.0 | PDF → Markdown | 多语种；中英待测；GPU 推荐 |
| **Unstructured** | 16k | Apache-2.0 | 企业级多格式 ingestion | 中英待测；依赖重 |
| **olmOCR** | 20k | Apache-2.0 | VLM 扫描件 OCR | 多语种；中英待测；GPU 必需 |
| **Surya** | 22k | Apache-2.0 | OCR / 版面 / 阅读顺序 | 中英 OCR/版面；Marker 的底层模型；GPU 推荐 |
| **Camelot** | 3.8k | MIT | 表格提取 | 中英文字层表格；与 pdfplumber 互补 |
| **Tesseract** | 77k | Apache-2.0 | OCR 兜底 | `chi_sim+eng`；中文效果弱于 PaddleOCR |
| **qpdf / pypdf / pdfminer.six** | 5.6k / 10k / 7k | Apache-2.0 / BSD-3 / MIT | 拆分、合并、解密、底层文字 | 中英底层文字/PDF 操作，不做版式 |

### 考虑过但未纳入默认路径

| 工具 | 许可证 | 未纳入原因 |
|---|---|---|
| **PDF-Extract-Kit** | AGPL-3.0 | 传染性许可；只给链接，需要时用户自行安装 |
| **PyMuPDF** | AGPL-3.0 | 同上；需要底层控制时在 gotchas 里说明替代方案 |
| **Anthropic `pdf` 技能** | Proprietary | 不可再分发；只给链接；负责合并/拆分/表单，不做结构化提取 |
| **LlamaParse / Azure Document Intelligence / Google Document AI / Adobe PDF Extract / Mathpix** | 商业云 API | 数据离机、按页计费；不在本地默认路径，需要时单独说明 |

> 扫描件结论：中文优先 **RapidOCR / MinerU / Docling**（1%–1.6%），不要默认用 Tesseract `chi_sim`（约 10%）；英文可用 RapidOCR / MinerU / OCRmyPDF（0.1%–0.2%），Docling 英文扫描要抽检（本轮 7.1%）。
> 完整注册表（star、许可证、安装命令、中英实测状态、排除理由）见 [`docs/tool-registry.md`](docs/tool-registry.md)。
> `Surya` / `Camelot` / `Tesseract` / `qpdf` / `pypdf` / `pdfminer.six` 是可选补充，不单独写薄壳；需要时直接调用，或读上游文档。

## 默认路径：一个入口

默认安装只注册 `docarbiter` 一个技能。它**不自己提取**，只做四件事：

1. 判断输入类型（PDF / Office / 图片 / 音视频）；
2. 判断 PDF 有没有**可用的**文字层（不是只看字符数）；
3. 按「要速度 / 要成稿 / 要表格（简单网格或复杂合并表）/ 要 RAG / 要 OCR」路由；
4. 结果不满意时按降级链换工具，并说明为什么换。

12 个工具说明放在 `skills/_tools/`，由 `docarbiter` 按需读取，**不作为独立技能被 harness 发现**。想直接 `/mineru`、`/liteparse` 的用户装 `--profile full`。

工具集可以继续变大：规则在调度器，工具事实在 [`registry.json`](registry.json)，每个工具的细节在一条薄壳里。新增一个已有类别的工具，不需要重写调度器。详见 [`docs/architecture.md`](docs/architecture.md)。

## 可执行路由（可选）

给脚本 / 非 agent 用户一个可测试的入口，和 `docarbiter` 用同一套判断：

```bash
python3 -I scripts/route.py file.pdf --goal manuscript
python3 -I scripts/route.py file.pdf --goal table --json           # 简单网格 → pdfplumber
python3 -I scripts/route.py file.pdf --goal table-structure --json # 合并表头/多行单元格 → Docling
python3 -I scripts/route.py --selftest
```

输出包含：`probe`（字符数 / CJK / 控制字符 / 乱码率）、`intended` / `selected`、`reason`、`command`、`fallback`。`--selftest` 在仓库 fixture 上验收路由（文字层 / 扫描件 / CID / 繁体 / 交错双栏 / 真实 CC BY / 表格 / 复杂表格）。

## 中英双语的评测

这是本项目和普通「工具清单」的分界线。中文和英文都必须覆盖：只测一种语言，另一种语言的坑会被藏起来。

### 答案从哪来

技能能提取，但不能当答案。用工具 A 的输出当标准答案，只是在测「B 和 A 有多像」。答案来源：

1. **合成 PDF（中文 + 英文）**：我们自己写文本，用 CJK / Latin 字体渲染（demo 用 reportlab `STSong-Light` / `Helvetica`；计划加 Source Han Sans/Serif），源文本就是精确答案。中文覆盖正常文字层、CID/无 ToUnicode、双栏、表格、繁简混排；英文覆盖双栏、表格、连字符换行、引号/破折号。
2. **CC BY-SA 中文 / 英文维基百科**：取文章纯文本作答案，渲染成 PDF。真实内容，许可允许公开。
3. **公版中文古籍（Wikisource）**：源文本作答案，测繁体、竖排、异体字。
4. **用户自有 PDF**：放 `benchmarks/private/`（gitignore），只做本地 smoke test，不发布分数。

### 指标

- **CER（字符错误率）**，不是词级相似度。中文没有空格，word-level 指标会骗人；英文也用同一套 CER，避免跨工具的分词差异。
- 分项报告：汉字 / 标点 / 数字 / 英文混排 / 阅读顺序 / 表格单元格。
- 每页 CER + 每文档 CER，报告 median、IQR、**最差页**；不用单一总分掩盖灾难页。
- 归一化规则固定写进 `bench.py`：NFC、去空白、保留全角标点；另报 raw CER。
- 环境：macOS / M2 Pro 为实测环境；Linux / Windows 标「未验证」。
- 复现：`python3 -I scripts/bench.py 你的文档.pdf`。

参考值（英文样本，仅作量级参考，不可外推到中文）：

| 页型 | liteparse | MinerU | Docling |
|---|---|---|---|
| 正文 | 0.24 s | 1.58 s | — |
| 表格页 | 0.09 s | 1.40 s | — |
| 冷启动 | 无 | +16 s | — |

> 上表是单机单样本的参考值。**你的文件、你的机器会得出不同结果。**

首轮**中英双语 demo**（各 1 页，源文本作答案，2026-11-09）：

| 工具 | 中文耗时（3 次范围） | 中文 CER | 英文耗时（3 次范围） | 英文 CER |
|---|---:|---:|---:|---:|
| pdftotext | 0.03 s | 0.0000 | 0.04 s | 0.0000 |
| liteparse | 0.13–0.42 s | 0.0061 | 0.14 s | 0.0079 |
| markitdown | 0.98–1.19 s | 0.0061 | 0.90–0.98 s | 0.0185 |
| MinerU | 1.0–9.6 s | **0.0046** | 1.0–3.9 s | **0.0013** |
| Docling | 9.5–19.3 s | 0.0061 | 9.5–12.2 s | 0.0093 |

样本各只有一页，不能据此排序工具；耗时受冷/热启动影响。

**11 篇双语 smoke corpus（5 个工具，合成）**：MinerU median CER 0.0030；pdftotext / markitdown 0.0000；liteparse / Docling 0.0130。两份扫描件只有 MinerU / Docling 能出内容；所有工具的 **no-punct CER 都是 0.0000**，说明残差主要来自标点归一化，不是错字。

**4 篇真实 CC BY-SA 维基文章（1–2 页）**：no-punct CER 全部 0.0000；text CER 0.02%–2.5%，残差同样是标点；MinerU 最差 2.51%（zh-ocr）但 no-punct 0。来源、修改和 CC BY-SA 署名见 [`benchmarks/fixtures/real/SOURCES.md`](benchmarks/fixtures/real/SOURCES.md)。完整表与复现见 [`docs/benchmarks.md`](docs/benchmarks.md)。

**P0 策略对比（22 个有答案的文档）**：

| 策略 | 成功 | 中位 CER | 最差 CER | 总耗时 |
|---|---:|---:|---:|---:|
| 固定 MinerU | 100% | 0.0115 | 0.2952 | 61.98s |
| `router:text` | **100%** | **0.0000** | 0.7810 | **4.73s** |
| `router:speed` | **100%** | 0.0063 | 0.9048 | **7.06s** |
| `router:quality` | **100%** | 0.0079 | **0.2952** | 60.04s |
| oracle（理论上限） | 100% | 0.0000 | 0.2667 | 47.17s |

完整表、P1 verify 负结果、P2 真实表格 / P3 决策见 [`docs/policy.md`](docs/policy.md)。**不能据此说“每个文档都比最强工具准”；可以说混合语料上成功率/速度/中位 CER 更优。**

**边缘样本（CID / 繁体 / 交错双栏 / 真竖排）**：CID/无 ToUnicode 上文字层工具全部 garbled，**MinerU 4.95%**；合成纯文字交错双栏上 **pdfplumber 60%–68%**，而 pdftotext / liteparse / markitdown / MinerU 为 0；繁体基本全对；真竖排（Chrome vertical-rl）所有工具都差：Docling 26.7%、MinerU 29.5%、markitdown 41.9%、pdftotext 78.1%、liteparse 90.5%、pdfplumber 97.1%。

**真实双栏论文（ResNet arXiv:1512.03385，3 页，本地 private）**：MinerU / Docling / liteparse 的 abstract 可读；markitdown 被图表/坐标轴标签打散，pdfplumber 丢单词间空格。没有答案 key，只做定性，不做 CER。

**真实 CC BY 双栏论文 abstract CER（BERT, ACL Anthology N19-1423）**：MinerU **0.44%**；pdftotext / liteparse / Docling **0.65%**；markitdown / pdfplumber **73%**，no-punct 仍 73%——是阅读顺序/混排，不是标点。只评 abstract，不是全文；正文/图/表/参考文献未计分。

**表格单元格级**（pdfplumber，6 个 fixture）：有框线 / 合并单元格默认 **1.000**；无框线默认 **0 个表 / 0.000**，text 策略能救到 **1.000/0.917**，但合并单元格会掉到 **0.667/0.583**，英文还会被截断。没有一种设置通吃；合并的 1.000 只证明行列对齐，不证明语义。详见 [`docs/benchmarks.md`](docs/benchmarks.md)。

**真实高频表格（2026-11-10，本机 5 份，只读、不上传）**：

| 文档（页） | 结论 |
|---|---|
| WS/T 578.1—2017 p8（21×13，3 层表头） | **Docling** 把表头展开为“男性PAL - 轻(I) - MJ/d”；pdfplumber 压平表头；MinerU 保留 rowspan/colspan |
| GB 28050—2025 p6（28×4，多行单元格） | **Docling** 抽检正确；pdfplumber 单元格乱序；MinerU 7 处字符交错 |
| DRIs 2023 p65（2 张符号表） | **MinerU** 中文名正确，●/○ 变“空/O”；Docling 需 OCR，符号同样不保真 |
| GB 2760—2024 p13（26×4） | **Docling** 抽检正确；pdfplumber 行数对；MinerU 4 处字符交错 |
| 中国食物成分表 第6版第一册 p246（65 条双栏） | **Docling OCR** 大部分行对，页首/页尾仍错位；MinerU 也错位；必须抽检 |

路由：简单有框线网格/坐标 → `--goal table`（pdfplumber，单页 <0.5s）；合并表头/多行单元格/书表 → `--goal table-structure`（Docling，3–5s/页；OCR 10–12s/页）；扫描/坏文字层 → MinerU（约 2.5s/页）。**路由只看文件前 3 页；书/标准要先定位目标页再做页级探针。没有“所有表格都准”的工具；检测到表 ≠ 单元格正确。** 明细与复现见 [`docs/policy.md`](docs/policy.md) 的 P2 和 [`docs/benchmarks.md`](docs/benchmarks.md) 的五之八。

## 仓库结构

```
docarbiter/
├── README.md                        # 中文
├── README.en.md                     # English
├── LICENSE                          # MIT
├── THIRD_PARTY_NOTICES.md           # 逐个工具的许可与版权声明
├── registry.json                    # 机器可读工具注册表（18 个工具）
├── requirements-core.lock           # 核心层固定版本
├── requirements-extra.lock          # 扩展层版本（待逐项实测）
├── requirements-dev.lock            # 仅 benchmark/fixture 生成使用
├── skills/
│   ├── docarbiter/SKILL.md          # 唯一默认入口：分类与路由，不自己提取
│   └── _tools/                      # 薄壳工具说明（默认不作为独立技能注册）
│       ├── mineru.md
│       ├── docling.md
│       ├── liteparse.md
│       ├── markitdown.md
│       ├── rapidocr.md
│       ├── ocrmypdf.md
│       ├── pdfplumber.md
│       ├── pdftotext.md
│       ├── paddleocr.md
│       ├── marker.md
│       ├── unstructured.md
│       └── olmocr.md
├── scripts/
│   ├── install.sh                   # 按 profile 安装；默认固定版本
│   ├── doctor.sh                    # 体检 + 版本 + 重名/双路由检测
│   ├── bench.py                     # 在用户自己的文件上跑中文 CER 对比
│   ├── bench_tables.py              # 表格单元格级准确率（default / text）
│   ├── bench_abstract.py            # 真实双栏论文 abstract CER（部分对齐）
│   ├── bench_policy.py              # 固定工具 vs 路由 vs oracle
│   ├── survey_pdfs.py               # 工作区真实 PDF 只读抽样（hash + 探针）
│   ├── sample_real.py               # 真实中文/英文 PDF 2 页 smoke
│   ├── route.py                     # 可执行路由 + --selftest
│   ├── validate.py                  # frontmatter / 许可清单 / 禁用目录检查
│   └── wrappers/
│       ├── mineru-doc.sh            # 固定 CWD + 引擎冷启动重试
│       └── liteparse-doc.sh         # 默认关 OCR + 安全参数解析
├── docs/
│   ├── tool-registry.md             # 完整工具注册表（人读）
│   ├── architecture.md              # 调度器 / 注册表 / 薄壳三层架构
│   ├── harness-routing.md           # harness 原生调度 vs docarbiter
│   ├── migration.md                 # 旧 doc-extract / 单工具技能迁移
│   ├── gotchas.md                   # 实测坑（差异化核心）
│   ├── benchmarks.md                # 语料、指标、参考数据、复现方法
│   ├── decisions.md                 # 已定/待定决策与证据
│   ├── licensing-faq.md             # MinerU / AGPL / GPL 通俗说明
│   ├── reliability.md               # 可靠性验收记录（干净 HOME / 路由 / 冲突）
│   ├── policy.md                    # P0 策略对比 + P1/P2/P3 结论
│   ├── p4-claude-code.md            # Claude Code 真实触发验收
│   ├── p4-other-harnesses.md        # Codex / ZCode / DSH / MiniMax 验收
│   ├── harness-integration.md       # 各 harness 技能目录接入与切换
│   ├── release-plan.md              # v0.1.0 发布计划
│   ├── release-notes-v0.1.0.md      # v0.1.0 Release notes 草稿
│   ├── release-checklist.md         # 发布前检查清单
│   └── assets/                      # overview-zh.svg / overview-en.svg
├── benchmarks/
│   ├── fixtures/                    # 11 篇中英合成样本 + 答案 + 生成脚本
│   │   ├── real/                    # 4 篇 CC BY-SA 维基样本 + SOURCES.md
│   │   ├── edge/                    # CID / 繁体 / 交错双栏 / 真竖排
│   │   └── tables/                  # 有框线 / 合并 / 无框线表格 + cell truth
│   └── private/                     # gitignore；用户自有文件
└── .github/workflows/
    └── validate.yml                 # 校验 frontmatter、链接、许可清单
```

## 安装

```bash
git clone <repo>
cd docarbiter

# 核心层：8 个工具 + 唯一入口 docarbiter（推荐大多数用户）
./scripts/install.sh --profile core

# 扩展层：PaddleOCR / Marker / Unstructured / olmOCR 等
./scripts/install.sh --profile extra

# 全部：核心 + 扩展 + 独立工具技能注册
./scripts/install.sh --profile full

# 不装包：只装 wrapper + 注册 docarbiter（快速试用）
./scripts/install.sh --skills-only

# 体检：缺什么、版本对不对、有没有重名技能或两个路由器同时生效
./scripts/doctor.sh --check-conflicts
```

其他 harness 用 `--skills-dir` 指向它的技能目录；目录表、切换、回滚见 [`docs/harness-integration.md`](docs/harness-integration.md)：

```bash
./scripts/install.sh --skills-only --skills-dir ~/.dsh/skills
./scripts/install.sh --skills-only --skills-dir ~/.zcode/skills
./scripts/install.sh --skills-only --skills-dir ~/.codex/skills
./scripts/install.sh --skills-only --skills-dir ~/.minimax/skills
```

安装前须知：默认 `--profile core` 只注册 `docarbiter`，不会替换你已有的单工具技能；`--profile full` 才会注册独立工具技能。若已有同名技能（`liteparse` / `markitdown` / `docling` 等），先卸载旧的，或安装后用 `doctor.sh --check-conflicts` 确认只有一份生效。**一个 harness 只保留一个文档提取路由器。**

## MinerU 许可：我们能用吗？

**能用。** MinerU 是 **Apache-2.0 + 附加条款**。附加条款只在这两种情况下触发：

1. 你及关联方合并口径 **MAU > 1 亿**，或 **月收入 > 2000 万美元** → 需要单独商业许可；
2. 你基于 MinerU 向第三方提供**在线服务** → 必须在界面或公开文档显著位置标明「使用了 MinerU」。

本项目不盈利、不提供在线服务、不重新分发 MinerU 代码或模型，只在用户本机通过 `mineru-doc` 调用 CLI，因此当前用法不触发附加条款。**如果未来做成在线服务**，需要加 MinerU 标识；达到门槛则需要商业许可。

原文（英文 + 中文）见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)；更多问题见 [`docs/licensing-faq.md`](docs/licensing-faq.md)。

## Harness 本身不能调度吗？

能发现和调用技能，但通常没有确定性的领域路由：模型读 `description` 做语义选择，不探针、不理解 CID/ToUnicode、不维护降级链。同类技能一多就会竞争。`docarbiter` 补的就是这一层。详见 [`docs/harness-routing.md`](docs/harness-routing.md)。

## 已有 doc-extract 怎么办？

**先共存，验证后再替换；不自动删除旧路由。** 2026-11-10 在 Claude Code 实测：旧 `doc-extract` 与 `docarbiter` 共存时，中英文隐式提示都选中旧路由；把旧 symlink 移到 `~/.claude/skill-backups/` 后，`docarbiter` 被正确触发。其他 harness 未动。检测、替换、回滚见 [`docs/migration.md`](docs/migration.md)，P4 记录见 [`docs/p4-claude-code.md`](docs/p4-claude-code.md)。

## 许可与上游

- 本仓库：**MIT**。仅含自撰说明与调用脚本，**不含上游代码**。
- 上游工具由用户通过 `install.sh` 自行安装，各自适用其原始许可证。
- 逐个工具的许可证、版权方、上游 URL 与「只调用未修改」声明见 `THIRD_PARTY_NOTICES.md`（已起草）。

已知许可要点：

| 工具 | 许可证 | 处置 |
|---|---|---|
| Anthropic `pdf` 技能 | Proprietary | 不收录，README 给链接 |
| PyMuPDF / PDF-Extract-Kit | AGPL-3.0 | 不收录、不推荐，只给链接 |
| MinerU | Apache-2.0 + 附加条款 | 收录；附条款原文 + 显著署名 |
| Poppler / `pdftotext` | GPL-2.0/3.0 | 只调用系统命令，不修改、不再分发 |
| docling / markitdown / pdfplumber / camelot / pdfminer.six | MIT | 收录 |
| liteparse / rapidocr / marker / surya / paddleocr / unstructured / olmocr / tesseract / qpdf | Apache-2.0 | 收录 |
| ocrmypdf | MPL-2.0 | 收录；只调用不修改 |
| pypdf | BSD-3-Clause | 收录 |

> MinerU 的附加条款不是「署名即可」：含 MAU > 1 亿 / 月收入 > 2000 万美元的商业门槛，以及**在线服务标识义务**。原文见 `THIRD_PARTY_NOTICES.md`。

## 发布前

**已发布 v0.1.0**：[GitHub Release](https://github.com/ChemistryBus/docarbiter/releases/tag/v0.1.0)。`validate` CI 已通过；干净 venv、中英文语料、许可审计、核心路由和双语文档已完成。`extra/full`、Windows、ZCode / Codex / MiniMax 触发等仍按 [`docs/release-checklist.md`](docs/release-checklist.md) 的 Known Limitations 处理。

## 状态与路线图

- [x] 盘点本机工具与版本（2026-11-09）
- [x] 查名：`docarbiter` 在 GitHub / PyPI / npm 无占用
- [x] 确定分发方式、许可边界、默认单入口、10+ 工具范围
- [x] 编写 `docarbiter` 调度器
- [x] 编写 12 个薄壳（`skills/_tools/`）
- [x] `install.sh` / `doctor.sh` / `bench.py` / 两个 wrapper / `validate.py`
- [x] `registry.json`（18 个工具）+ `docs/architecture.md`
- [x] 中文 + 英文 README + 两张总览图 + licensing FAQ
- [x] 11 篇双语合成 smoke corpus + 5 工具 CER + RapidOCR/OCRmyPDF OCR 对比
- [x] 4 篇真实 CC BY-SA 维基文章 + core 8 工具跑通（文字层 6 + OCR 2 路径）
- [x] CID/无 ToUnicode、繁体、交错双栏、竖排模拟边缘样本
- [x] 真竖排（Chrome `vertical-rl`）+ 真实双栏论文定性检查（ResNet 3 页）
- [x] 表格单元格级准确率：有框线 / 合并 1.000；无框线默认 0 表
- [x] 无框线表格 default vs text 策略：text 能救无框线，但伤合并；无通吃设置
- [x] `route.py` 可执行路由 + `--selftest`（CI 可跑）
- [x] 真实 CC BY 双栏论文 abstract CER（BERT, ACL N19-1423）
- [x] 干净 venv 完整 core 安装 + `install.sh` 不升级已装 brew formula
- [x] 工作区真实 PDF 只读抽样（8,444 去重；48+24 样本）与 4 文件 smoke
- [x] P0 policy benchmark：固定工具 vs 路由 vs oracle（`docs/policy.md`）
- [x] 5 份真实高频表分流测试：复杂表 Docling、坏文字层 MinerU、简单网格 pdfplumber；composition 不做
- [x] P1 verify 试点为负结果，暂不发布；P2 真实表格分流完成；P3 默认策略已定（含 `table-structure`）
- [x] P4 Claude Code 真实触发：发现 + 中英文隐式触发通过；旧 `doc-extract` 已备份停用
- [x] P4 DSH headless：永久切换完成；中英文只触发 `docarbiter`（旧路由备份可回滚）
- [ ] P4 ZCode：技能被发现，但 CLI `--prompt` 需先设默认模型
- [ ] P4 Codex：未找到 CLI 可执行文件
- [ ] P4 MiniMax：有 `~/.minimax/skills`，未找到无头入口
- [ ] 真实双栏论文全文 CER（不只 abstract）
- [ ] 扩展层工具（按 A 决定：不装）
- [ ] 逐条复现 `gotchas.md`（已有 8 条本机实测）
- [ ] 按 `docs/release-checklist.md` 完成发布前验证

---

**English summary:** `docarbiter` is a Chinese-first arbitration skill plus a curated collection of thin-shell skills for open-source PDF/image/document extraction tools. It tells you which tools to install, when to switch, and where each tool breaks on Chinese documents. The repo contains only original documentation and install scripts — no upstream code.
