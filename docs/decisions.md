# 设计决策与证据

> 状态：2026-11-09。本文记录已拍板事项、核实过的外部事实、以及仍待验证的项。

## 一、已拍板

| # | 决策 | 结论 |
|---:|---|---|
| 1 | 分发方式 | 薄壳拉取。仓库只含自撰说明与安装脚本，不含上游代码 |
| 2 | Anthropic `pdf` 技能 | 只给链接，不收录（Proprietary） |
| 3 | PyMuPDF | 排除（AGPL-3.0），只给链接 |
| 4 | 仓库许可证 | MIT |
| 5 | 仓库名 | `ChemistryBus/docarbiter`（GitHub 无精确同名仓库） |
| 6 | 调度器技能名 | **`docarbiter`**（GitHub 用户/仓库、PyPI、npm 均无占用） |
| 7 | 打包拓扑 | 默认只注册 `docarbiter` 一个技能；工具薄壳放 `skills/_tools/`；`install.sh --profile full` 才注册独立技能 |
| 8 | 首版范围 | 12 个主选工具 + 6 个可选补充；AGPL 与商业 API 只进「未纳入」表 |
| 9 | 中文语料 | 合成 PDF + CC BY-SA 中文维基 + 公版 Wikisource；用户自有文件只做本地 smoke test |
| 10 | 语言覆盖 | **中文 + 英文都保证**；语料、CER、路由、工具说明均覆盖两种语言 |
| 11 | 集合规模 | 工具集可以继续扩大；`registry.json` 是事实来源，默认只注册一个调度器；新增已有类别的工具不改调度器 |
| 12 | 发布节奏 | **暂不发布**；先按 `docs/release-checklist.md` 验证；README 中英文 + 配图 |
| 13 | MinerU 使用 | 本项目非盈利、不提供在线服务、不重新分发代码/模型；当前用法不触发附加条款，原文保留在 notices |

## 二、命名证据（2026-11-09）

`docarbiter` 检索结果：

| 位置 | 结果 |
|---|---|
| GitHub 用户/组织 `github.com/docarbiter` | 404 |
| GitHub 仓库 `github.com/docarbiter/docarbiter` | 404 |
| GitHub 仓库搜索 `docarbiter in:name` | 0 条 |
| PyPI `docarbiter` | 404 |
| npm `docarbiter` | 404 |
| Web 搜索 | 无同名项目 |

含义：`docarbiter` = document + arbiter（仲裁者）。它不自己提取，只在互相竞争的工具之间裁决，和调度器的职责一致。

> 注意：GitHub 上已有 `misbahsy/doc-router`（文档 OCR 路由）、`MeZyV/doc_extraction_router`（OpenWebUI 文档解析路由）、`horizon123104/PdfRouter`、`yidingwanglnsy-boop/PDFROUTER`。概念相近，但名字都不同；`doc-router` / `docrouter` / `pdfrouter` **不要用**。

## 三、本机已验证事实

| 工具 | 本机版本 | 许可证（包元数据） | CLI |
|---|---|---|---|
| liteparse | 2.18.0 | Apache-2.0 | `liteparse-doc` |
| markitdown | 0.1.9 | MIT | `markitdown` |
| mineru | 4.1.7 | `LicenseRef-MinerU-Open-Source-License` | `mineru-doc` / `mineru` |
| docling | 2.149.0 | MIT | `docling` |
| rapidocr | 3.10.0 | Apache-2.0 | Python API |
| ocrmypdf | 17.12.1 | MPL-2.0 | `ocrmypdf` |
| pdfplumber | 0.11.10 | MIT | Python API |
| pdftotext (Poppler) | 26.11.0（测量时 26.08.0；干净安装时 Homebrew 升级） | GPL-2.0-only OR GPL-3.0-only | `pdftotext` |
| pymupdf | 1.28.2 | AGPL-3.0 / 商业双许可 | Python API（不收录） |

## 四、GitHub 快照（star / 许可证，2026-11-09）

| 仓库 | ★ | SPDX |
|---|---:|---|
| microsoft/markitdown | 194,491 | MIT |
| PaddlePaddle/PaddleOCR | 92,460 | Apache-2.0 |
| opendatalab/MinerU | 83,343 | NOASSERTION（自定义：Apache-2.0 + 附加条款） |
| tesseract-ocr/tesseract | 77,417 | Apache-2.0 |
| docling-project/docling | 70,315 | MIT |
| datalab-to/marker | 40,822 | Apache-2.0 |
| ocrmypdf/OCRmyPDF | 35,272 | MPL-2.0 |
| datalab-to/surya | 21,587 | Apache-2.0 |
| allenai/olmocr | 19,818 | Apache-2.0 |
| Unstructured-IO/unstructured | 15,701 | Apache-2.0 |
| run-llama/liteparse | 13,020 | Apache-2.0 |
| jsvine/pdfplumber | 10,884 | MIT |
| py-pdf/pypdf | 10,291 | BSD-3-Clause（GitHub 标 NOASSERTION） |
| opendatalab/PDF-Extract-Kit | 10,075 | AGPL-3.0 |
| RapidAI/RapidOCR | 8,486 | Apache-2.0 |
| pdfminer/pdfminer.six | 7,048 | MIT |
| qpdf/qpdf | 5,563 | Apache-2.0 |
| camelot-dev/camelot | 3,849 | MIT |

## 五、许可要点

### MinerU

包元数据为 `LicenseRef-MinerU-Open-Source-License`，正文是 Apache-2.0 + 附加条款。附加条款实际内容：

- 商业使用默认允许；但合并口径 MAU > 1 亿或月收入 > 2000 万美元时，须另行取得商业许可。
- 基于 MinerU 向第三方提供**在线服务**时，须在界面或公开文档显著位置标明使用了 MinerU。
- 违反上述两条，许可自动终止。

`THIRD_PARTY_NOTICES.md` 必须附原文（英文 + 中文），不能只写「Apache-2.0 + 附加条款」。

### RapidOCR

Apache-2.0，但模型权重来自 PaddleOCR / 百度，包内另有 `MODEL_LICENSES.md`。分发或再发布时需保留模型来源与版权说明。本仓库只调用，不再分发模型。

### Poppler / pdftotext

GPL-2.0-only OR GPL-3.0-only。本仓库只通过系统包调用命令行，不修改、不再分发；仓库自身 MIT 不受影响。若把 `pdftotext` 二进制打包进发行物，则需另行评估。

### pypdf

GitHub 的许可证识别为 NOASSERTION，实际 `LICENSE` 是 BSD-3-Clause 风格（版权头 + 三条款）。以 `THIRD_PARTY_NOTICES.md` 的原文为准。

## 六、对交接文档的修正

### 修正 1：中文评测不能用「顺序相似度 vs pdftotext」

- 中文没有空格，词级相似度不可用；改用 **CER（字符错误率）**。
- `pdftotext` 是另一个工具，不是 ground truth；和它一致 ≠ 准确。

### 修正 2：文字层检测阈值不够

「> 200 字符 = 有文字层」会被损坏的 CID 字体骗过：字符数达标但内容是乱码。检测需同时报告：

- 字符数；
- `U+FFFD` 与私用区字符占比；
- 中文常用字覆盖率（前 3 页）；
- 结论：可用 / 疑似乱码 / 扫描件。

### 修正 3：8 个顶层技能会重新制造「一锅粥」

已改为默认单入口 `docarbiter` + `--profile full` 可选注册。7+ 个工具说明放 `skills/_tools/`，不参与 harness 的技能发现。

### 修正 4：`install.sh` 必须固定版本

薄壳命令按本机版本实测；不固定版本，上游一改参数就会漂移。`requirements.lock` + `doctor.sh` 版本校验。

### 修正 5：markitdown 双栏——合成纯文字未复现，真实论文含图会坏

- **合成纯文字、内容流逐行交错**：0.1.9 上 markitdown CER **0**；pdftotext / liteparse / MinerU 0；**pdfplumber 60%–68%**。所以「markitdown 一定不处理双栏」在干净样本上没有复现。
- **真实论文（ResNet, arXiv:1512.03385, 3 页，本地 private）**：markitdown 输出大量 Markdown 表格/坐标轴标签，abstract 被打散；pdfplumber 丢空格、混入坐标轴；MinerU / Docling / liteparse 的 abstract 可读。没有答案 key，不做 CER。
- 结论：不要两边都过度概括。干净双栏它能过；真实含图双栏会坏。真实双栏优先 MinerU / Docling / liteparse。

### 修正 6：调度器也要纳入重名/双路由检测

本机已有 `doc-extract` 在四个 harness 生效。`docarbiter` 与它功能重叠，不是同名冲突；`doctor.sh --check-conflicts` 要同时检测：

- 同名工具技能；
- 两个文档提取路由器同时生效。

## 七、MinerU 使用结论（2026-11-09）

问题：MinerU 是 Apache-2.0 + 附加条款，我们能不能用？

结论：**能用。** 附加条款只在两种情况下触发：

1. 合并口径 MAU > 1 亿，或月收入 > 2000 万美元 → 需要商业许可；
2. 基于 MinerU 向第三方提供在线服务 → 需要显著标识。

本项目不盈利、不提供在线服务、不再分发 MinerU 代码或模型，只在用户本机调用 CLI。因此当前用法不触发附加条款。如果未来做在线服务，必须在界面/文档标注 MinerU；达到门槛则联系 MinerU 团队。

原文已附在 `THIRD_PARTY_NOTICES.md`；通俗说明见 `docs/licensing-faq.md`。

## 八、语言与规模（2026-11-09 增补）

- **语言**：中文和英文都是第一等公民。中文的 CID/ToUnicode、扫描件、繁简、竖排要测；英文的双栏、连字符、引号/破折号、页眉页脚也要测。只测一种语言的分数不能外推。
- **规模**：工具可以继续加，但默认只注册 `docarbiter` 一个技能。新增工具 = `registry.json` 一条记录 + 可选薄壳；只有新类别才改调度器。这样 N 个工具不会产生 N² 条交叉引用，也不会出现 N 个顶层技能抢活。
- **发布**：当前是骨架，不是发布版。发布前必须过 `docs/release-checklist.md`；README 必须有中文和英文两个版本，并配图说明问题与适用人群。

## 九、仍待验证

- [ ] 12 个主选工具的中英文 CER（文字层 / 扫描 / 双栏 / 表格 / 繁简混排）
- [ ] Marker / Surya / Unstructured / olmOCR 的 CLI 入口与中英文表现
- [ ] MinerU / Marker / Surya 模型权重的独立许可
- [ ] `liteparse` 对无 ToUnicode 中文 PDF 的行为
- [ ] `docling` 默认 OCR 后端与中文模型
- [ ] MinerU 附加条款的官方英文原文 URL（用于 notices 引用）
- [ ] 真实 CC BY-SA 文章、CID/无 ToUnicode、繁简/竖排样本

## 十、本轮新增结论（2026-11-09，v0.3）

### 语料与指标

- 11 篇双语合成 smoke corpus：文字层 / 双栏 / 表格 / 脚注 / 扫描件 / 英文行末连字符。
- 所有工具的 **no-punct CER = 0.0000**；`cer_text` 的残差全部来自标点归一化（MinerU 全角冒号/分号→ASCII，liteparse/markitdown 引号/破折号→ASCII）。因此 `bench.py` 同时输出 `cer_text` 与 `cer_nopunct`。
- 空输出/扫描件：`pdftotext`、`markitdown` 在两份扫描件上 error，`liteparse` empty；MinerU/Docling 能直接 OCR。`bench.py` 增加 coverage < 5% → `empty`，不计入 CER 汇总。

### 边缘样本（CID / 繁体 / 交错双栏 / 竖排模拟）

- **CID/无 ToUnicode**：pdftotext / liteparse / markitdown / pdfplumber / Docling 全部 garbled；MinerU 能 OCR，CER 4.95%。探针必须加控制字符比例，不能只看字符数。
- **繁体**：所有工具基本正确；MinerU 1.72% 是标点归一化。
- **交错双栏**：pdftotext / liteparse / markitdown / MinerU 0；pdfplumber 60%–68%；Docling 2%–3%。修正了「markitdown 双栏失败」的旧说法。
- **竖排模拟**：pdftotext / markitdown / pdfplumber / Docling 0；liteparse 34.78%、MinerU 13.04%。这是模拟，不是真竖排。
- 生成脚本：`benchmarks/fixtures/edge/make_edge.py`；CID 依赖 LibreOffice + pypdf，仅用于生成 fixture。

### 真竖排 / 真实双栏 / 表格（2026-11-09）

- **真竖排**（Chrome `writing-mode: vertical-rl`）：所有工具都差。Docling 26.7%、MinerU 29.5%、markitdown 41.9%、pdftotext 78.1%、liteparse 90.5%、pdfplumber 97.1%。结论：真竖排不要默认任何工具可用，必须人工检查。
- **真实双栏论文**（ResNet, arXiv:1512.03385, 3 页，本地 `benchmarks/private/`）：MinerU / Docling / liteparse 的 abstract 可读；markitdown 被图表/坐标轴标签打散；pdfplumber 丢单词间空格。没有答案 key，不做 CER。
- **表格单元格级**（pdfplumber，6 个 fixture）：默认策略下有框线 / 合并 **1.000**；无框线 **0 个表 / 0.000**。`text` 策略能救无框线（**1.000/0.917**），但合并掉到 **0.667/0.583**，英文还会截断（`half z`）。没有通吃设置；实际对同一页跑两种策略并抽检。合并的 1.000 只证明行列对齐，不证明合并语义。
- 机器约束：仍然是 16GB / 无 GPU；没有安装扩展层。Chrome 只用于生成真竖排 fixture，跑完即退。

### 真实 CC BY 双栏论文 abstract CER（BERT，2026-11-09）

- 来源：BERT, NAACL 2019, ACL Anthology N19-1423，CC BY 4.0；PDF 前 2 页 + HTML abstract 作答案。
- 结果：MinerU 0.44%；pdftotext / liteparse / Docling 0.65%；**markitdown / pdfplumber 73%**（no-punct 仍 73%，是阅读顺序/混排，不是标点）。
- 只评 abstract；全文、图、表、参考文献未计分。

### 真实 CC BY-SA 样本（4 篇）

- 中文/英文维基各 2 篇，截取约 2,200 / 3,200 字符，渲染为 1–2 页文字层 PDF。
- `no-punct CER` 全部 **0.0000**；`cer_text` 0.02%–2.5%，残差同样是标点（MinerU 最差 2.51%，no-punct 0）。
- 这四份 fixture 是 **CC BY-SA 4.0**，不是 MIT；署名与来源见 `benchmarks/fixtures/real/SOURCES.md`。

### 机器约束

- 本机：Apple M2 Pro / 16GB RAM / 10 核 / 119GB 可用磁盘。
- 没有安装 PaddleOCR、Marker、Unstructured、olmOCR；它们会带来重依赖或 GPU 需求，先用已装 core 8 + RapidOCR/OCRmyPDF 把流程跑通。
- 所有重工具（MinerU / Docling）单进程顺序跑，`nice -n 10`，不并发。

### OCR 路径

| 路径 | 中文扫描 CER | 英文扫描 CER |
|---|---:|---:|
| RapidOCR | 1.16% | 0.10% |
| MinerU | 1.59% | 0.20% |
| Docling | 1.01% | 7.12% |
| OCRmyPDF（Tesseract chi_sim+eng） | **10.1%** | 0.20% |

结论：中文扫描不要默认 Tesseract `chi_sim`；优先 RapidOCR / MinerU / Docling。英文扫描 OCRmyPDF 可用。

### 路由与迁移

- 新增 `docs/harness-routing.md`：harness 能发现/调用技能，但通常是模型按 description 语义选择，不是确定性领域路由；`docarbiter` 补探针、决策表、降级链。
- 新增 `docs/migration.md`：旧 `doc-extract` **本轮不动**；默认先共存、验证、再替换；对其他用户给同一套建议（检测 → 单 harness 试用 → 替换 → 回滚）。
- 用户确认：`docarbiter` 名字可用；本机研发继续；发布前必须验证；README 中英文 + 配图。

### 工程验收（2026-11-09，v0.9）

- 新增 `scripts/route.py`：可执行路由，输出 probe / intended / selected / reason / command / fallback。
- `--selftest` 覆盖：文字层、扫描件、CID、繁体、交错双栏、真实 CC BY、表格；CI 可跑。
- 用户选择 **A：core-only**，不安装 PaddleOCR / Marker / Unstructured / olmOCR；Camelot 也不装。表格用 core 内分流：简单网格 pdfplumber；复杂合并表 Docling；扫描/坏文字层 MinerU。

### 可靠性验收（2026-11-10）

- **干净 HOME + `install.sh --skills-only`**：通过；wrapper 落盘、`docarbiter` symlink 创建成功。
- **发现并修复 `install.sh` 真 bug**：`set -u` 下 `$resolved，` / `$target（` 被 Bash 当作变量名的一部分（全角标点），触发 `unbound variable`；已改为 `${resolved}` / `${target}`。
- **`doctor.sh --check-conflicts`**：在临时 HOME 里同时放 `docarbiter` + 假 `doc-extract` + 假 `mineru` 技能，能报 `dual-router` 和 `conflict:mineru`。
- **`install.sh --force`**：能先备份为 `SKILL.md.bak.<timestamp>` 再建 symlink；不加 `--force` 时跳过并警告。
- **`route.py --selftest` 13/13**：新增空 PDF、损坏 PDF、含空格/中文路径；全部不崩溃，路由符合预期。
- 这些测试都在 `/tmp` 隔离 HOME 里做，没有改真实 `~/.claude` / `~/.local` 之外的配置。
- **完整干净 venv 安装**：`/tmp/docarbiter-clean-venv`，exit 0，core 7 个包全部对版（mineru 4.1.7 / docling 2.149.0 / liteparse 2.18.0 / markitdown 0.1.9 / rapidocr 3.10.0 / ocrmypdf 17.12.1 / pdfplumber 0.11.10）；`doctor.sh` core 14 项 OK。
- **开发依赖分离**：`rapidfuzz` 不在 core；`bench_abstract.py` 在干净 venv 里自动用 stdlib `difflib` fallback，结果可跑但 alignment score 不可与 rapidfuzz 直接比较。需要稳定对齐时 `pip install -r requirements-dev.lock`。
- **修复 `install.sh` 升级 Homebrew 依赖的副作用**：已装 formula 现在跳过，`HOMEBREW_NO_AUTO_UPDATE=1`；apt 用 `--no-upgrade`。修复后重跑日志确认 `skip (no upgrade)`，exit 0。

### P0–P3 策略评估（2026-11-10）

- **P0 policy benchmark**（22 个有答案文档）：
  - 固定 MinerU：100% 成功 / 中位 CER 0.0115 / 61.98s；
  - `router:text`：100% / 0.0000 / 4.73s（比 MinerU 快约 13 倍，中位 CER 更低；最差真竖排 0.781）；
  - `router:speed`：100% / 0.0063 / 7.06s；
  - `router:quality`：100% / 0.0079 / 60.04s；
  - oracle：中位 0 / 最差 0.2667 / 47.17s。
  - 结论：混合语料上路由能提高成功率/速度/中位 CER；不能超过 oracle，不能保证每篇都超过最强单工具。
- **P1 verify**：当前启发式负结果（中位 0.0079 无改善，最差 0.3478 比 quality 0.2952 更差，在 zh-vertical-sim 上错误切换）。**不发布**；需要输出级 bag/bigram 比较。
- **P2 真实高频表格（2026-11-10 补测，替代原“composition 暂缓”）**：用 WS/T 578.1 p8、GB 28050 p6、DRIs 2023 p65、GB 2760 p13、中国食物成分表 p246 五份本机真实表验证。
  - **复杂合并表头/多行单元格 → Docling**：WS/T 三层表头、GB 28050 多行单元格、GB 2760 大表结构与阅读顺序最好；新增 `--goal table-structure`。
  - **坏文字层/符号表 → MinerU**：DRIs 2023 的 ●/○ 文字层已坏；MinerU 能恢复中文名并区分“空/O”，但不保留原符号。
  - **pdfplumber 只做简单网格/坐标**：单页 <0.5s，但真实书表多行单元格会乱序；`text` 策略会把 29×4 吹成 76×6。
  - **composition 不做**：没有出现“MinerU 丢结构 + pdfplumber 单元格好”的同一份真实表；Docling 已同时给出结构和可读单元格。密集双栏食物成分表仍有页首/页尾行错位，必须抽检。
- **P3 默认策略**：正文准确 → `text`；成稿结构 → `quality`；快速浏览 → `speed`；复杂表格 → `table-structure`（Docling）；简单网格 → `table`（pdfplumber）；真竖排人工；verify 关闭。
- 完整报告：`docs/policy.md`；明细 `benchmarks/private/policy.md`。

### P4 Claude Code 真实触发（2026-11-10）

- 安装：`~/.claude/skills/docarbiter/SKILL.md` 软链到本仓库；新会话能发现 `docarbiter`。
- **共存冲突**：旧 `doc-extract` 还在 `~/.claude/skills` 时，中英文隐式提示都调用 `Skill: doc-extract`，docarbiter 未被选中。这不是描述问题，是“两个路由器只能留一个”。
- **停用旧路由后**：中文 / 英文在 `/tmp` 中立目录都能触发 `Skill: docarbiter`，正确路由扫描件 → `mineru`，并给出 `mineru-doc` 命令。
- **测试偏差**：在仓库根目录跑 `claude -p`，英文那次模型直接 `Read SKILL.md` 而没调用 Skill；路由仍正确，但不算干净触发。P4 验收要从中立目录跑。
- **处理**：经用户确认，只把 Claude Code 的 `doc-extract` symlink 移到 `~/.claude/skill-backups/doc-extract.20261110-121227`；源目录 `~/.agents/skills/doc-extract` 和其他 harness 未动，可恢复。
- **未完成**：Sonnet / Opus 复测、真实文件端到端提取。
- **DSH（2026-11-10，已永久切换）**：`dsh --profile headless` 可测；旧 `doc-extract` 在场时会**同时调用 docarbiter 和 doc-extract**。把 `~/.dsh/skills/doc-extract` 移到 `~/.dsh/skill-backups/doc-extract.20261110-125933`，并把全局 `~/.agents/skills/doc-extract` 移到 `~/.agents/skill-backups/doc-extract.20261110-130247` 后，中英文都只调 docarbiter，路由 MinerU。Codex / ZCode 的旧路由 symlink 已改指全局备份，仍可用。
- **ZCode（2026-11-10）**：`skills list` 能发现 docarbiter；`--prompt` 报 `Select a model before sending a message`，CLI 无 `--model`，需 TUI/桌面端选模型。DSH 切换后 `.agents` 已无旧路由，ZCode 只剩 `~/.zcode/skills/doc-extract` 一份，将来只需备份这一处。
- **Codex（2026-11-10）**：`command -v codex` 为空，未找到 CLI 可执行文件；`~/.codex/skills/doc-extract` 仍指向全局备份，无法非交互触发。
- **MiniMax（2026-11-10）**：有 `~/.minimax/skills` 和 `.builtin-skills`，但未找到 CLI/无头入口；本轮未测试，未改动。
- 完整记录：`docs/p4-claude-code.md`、`docs/p4-other-harnesses.md`、`docs/harness-integration.md`。

### 工作区真实 PDF 抽样（2026-11-10）

- 工作区 8,466 个 PDF，去重后 8,444 个（114MB）；随机 48 个全部可用文字层（47 en / 1 zh），中文文件名样本 24 个（18 en / 6 zh）。
- 真实 4 文件 2 页 smoke：三工具都成功；顺序 CER 0.05–0.65，但字符袋差异仅 0.1%–2.6%，多数是阅读顺序/分段差异。
- **MinerU 真实风险**：某中文文章第 1 页 MinerU 2,299→1,480（少 35%），拉丁 1,257→675，第 2 页几乎一致；疑似丢英文摘要/作者信息。已写入 gotchas 第 18 条。
- 工作区没有自然覆盖扫描件/CID/竖排；这些仍由合成/边缘 fixture 覆盖。
- 明细只写 `benchmarks/private/`（gitignored），不保存正文、不上传。

### 发布状态

- 仍未 `git init` / push / tag。
- 下一步：P4 在单个 harness 做真实触发测试（需要用户确认安装/重启）；真实双栏全文 CER；真实表逐单元格 CER；扩展层（PaddleOCR / Marker / Unstructured / olmOCR）按可行性安装与测试；发布前逐项过 `docs/release-checklist.md`。
