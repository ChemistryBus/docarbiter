# 中文文档提取基准：方法与语料

> 本文件定义「怎么测」，不发布未经复测的分数。
> 所有分数必须附：机器、系统、工具版本、语料版本、归一化规则。

## 一、三条原则

1. **答案必须是独立来源，不能是另一个工具的输出。**
   用 `pdftotext` 当标准答案，只是在测「谁更像 pdftotext」。
2. **中文用 CER，不用词级相似度。**
   中文没有空格，token/word 级指标会掩盖漏字、错字、乱序。
3. **报告最差页，不只报平均分。**
   一个平均 97% 的工具可能在某类表格页只有 40%；平均值会让用户踩坑。

## 二、语料设计

### A. 合成样本（答案精确、可公开、可复现）

用 `reportlab` + Source Han Sans/Serif 生成；源文本写入 `.txt` 作为答案。

| 样本 | 构造 | 要暴露的失败模式 |
|---|---|---|
| `zh-text-layer.pdf` | 正常中文正文 + 中英混排 + 数字 + 全角标点 | 基础正确性、标点、混排 |
| `zh-cid-no-tounicode.pdf` | 嵌入子集字体并移除 ToUnicode 映射 | 乱码、空白、替换符 |
| `zh-two-column.pdf` | 双栏学术版式 + 页眉页脚 | 栏间交错、阅读顺序 |
| `zh-table.pdf` | 合并单元格、无框线、表头跨列 | 表格结构、单元格错位 |
| `zh-scan.pdf` | 文本渲染为图片后包成 PDF | OCR 模型、分辨率、置信度 |
| `zh-traditional.pdf` | 繁体字 + 异体字 | 字符集覆盖 |
| `zh-vertical.pdf` | 竖排 + 从右到左 | 阅读顺序（可选，v0.2） |
| `zh-footnote.pdf` | 脚注、边注、图注 | 阅读顺序、段落合并 |

English counterparts (same categories, different failure modes):

| 样本 | 构造 | 要暴露的失败模式 |
|---|---|---|
| `en-text-layer.pdf` | 正常英文正文 + 数字 + 引号/破折号 | 基础正确性、标点归一化 |
| `en-two-column.pdf` | 双栏 + 页眉页脚 | 栏间交错、阅读顺序 |
| `en-table.pdf` | 有框线 / 无框线表格 | 表格结构、单元格错位 |
| `en-scan.pdf` | 文本渲染为图片后包成 PDF | OCR 模型、分辨率 |
| `en-hyphenation.pdf` | 行末连字符换行（`docu-\nment`） | dehyphenation、CER 虚高 |
| `en-footnote.pdf` | 脚注、边注、图注 | 阅读顺序、段落合并 |

> 当前 demo 只生成了 `demo-zh.pdf` / `demo-en.pdf` 各 1 页；上表是发布前要补齐的完整集。

### B. 真实样本（许可干净、答案可得）

| 来源 | 许可 | 答案 | 用途 |
|---|---|---|---|
| 中文维基百科文章 → 渲染 PDF | CC BY-SA 4.0 | 条目纯文本 | 真实长文、双栏/单栏、内链与表格 |
| 英文维基百科文章 → 渲染 PDF | CC BY-SA 4.0 | 条目纯文本 | 英文双栏/表格、连字符、引号 |
| Wikisource 公版中文古籍 → 渲染 PDF | 公版 | 校对本 | 繁体、竖排、异体字 |
| 开放获取中文论文（CC BY） | 按原文 | 出版社 HTML/XML 全文 | 真实学术版式、公式、表格 |

> 渲染管线本身要固定版本并记录，否则「PDF 变了」会让分数不可复现。

### C. 私有样本（只本地跑）

用户自己的 PDF 放 `benchmarks/private/`，`.gitignore` 排除。`bench.py` 只在本地输出报告，不上传、不写入公开分数。

## 三、指标

### 1. CER（字符错误率）

```
CER = (S + D + I) / N
```

- `S` 替换、`D` 删除、`I` 插入；`N` 为答案字符数。
- 编辑距离按 Unicode 码点计算；中文标点算独立字符。
- 同时报告 **raw CER** 与 **normalized CER**。

### 2. 归一化（固定写进 `bench.py`）

- Unicode **NFC**（不做 NFKC，保留全角/半角差异）。
- 英文行末连字符（`docu-\nment`）合并为 `document`；中文不受影响。
- 去除所有空白字符（空格、换行、制表）。
- 保留标点；另设「忽略标点」变体，单独报告。
- 不做繁简转换；繁简混排样本单独报告。

### 3. 分项指标

| 指标 | 说明 |
|---|---|
| 汉字 CER | 仅统计 CJK 统一表意文字 |
| 标点 CER | 全角/半角标点分别统计 |
| 数字/英文 CER | 混排场景 |
| 阅读顺序 | 双栏样本的块顺序准确率（人工标注块 ID） |
| 表格单元格准确率 | 单元格文本 + 行列位置；合并单元格单列 |
| 速度 | 秒/页；含冷启动单独一行 |
| OCR 置信度 | 工具自报均值；仅作参考，不作为准确率 |

### 4. 汇总方式

每个工具输出：

- 每页一行：`page, chars, cer, substitutions, deletions, insertions, seconds`
- 每文档汇总：`median CER`, `IQR`, `worst_page`, `worst_page_cer`
- 跨文档汇总：按样本类型分组，不混成一个总分

## 四、报告格式

`bench.py` 输出：

```
benchmarks/results/<timestamp>/
├── environment.json      # OS、CPU、内存、Python、工具版本
├── per_page.csv          # 每页指标
├── summary.md            # 人读：分组 median/IQR/worst
└── raw/                  # 各工具原始输出（可选，--keep-raw）
```

`summary.md` 顶部必须写：

> 本结果来自 `<machine>` / `<os>` / `<tool versions>` / `<corpus commit>`。
> 换机器、换版本、换文件都会变。请在你的文件上跑 `bench.py`。

## 五、参考值（英文样本，仅量级参考）

来源：本机 macOS / M2 Pro / Hackney 第 3 版 3 页。**不可外推到中文。**

| 页型 | liteparse | MinerU | Docling |
|---|---|---|---|
| 正文 | 0.24 s / 98.3% | 1.58 s / 96.6% | — |
| 表格页 | 0.09 s / 92.0% | 1.40 s / 91.4% | — |
| 冷启动 | 无 | +16 s | — |

注意：上表是**历史英文参考**，指标是「与 pdftotext 的顺序相似度」，不是 CER。已有中英双语 demo（见下），但样本量不足以替换本表，保留作历史参考。

## 五之二、首轮中英双语 demo（合成各 1 页，2026-11-09）

语料：`benchmarks/fixtures/demo-zh.pdf` 与 `demo-en.pdf`（`make_demo.py` 生成，答案均为源文本，不是 pdftotext 输出）。
机器：macOS 26 / M2 Pro / Python 3.11.11。

| 工具 | 版本 | 中文耗时（3 次范围） | 中文 CER | 英文耗时（3 次范围） | 英文 CER | 备注 |
|---|---|---:|---:|---:|---:|---|
| pdftotext | Poppler 26.08.0（测量时） | 0.03 s | 0.0000 | 0.04 s | 0.0000 | 基线；与源文本一致 |
| liteparse | 2.18.0 | 0.13–0.42 s | 0.0061 | 0.14 s | 0.0079 | 最快；引号/破折号被归一化为 ASCII |
| markitdown | 0.1.9 | 0.98–1.19 s | 0.0061 | 0.90–0.98 s | 0.0185 | 单栏可用；英文标点归一化最明显 |
| mineru | 4.1.7 | 1.0–9.6 s | **0.0046** | 1.0–3.9 s | **0.0013** | 中英两轮最低 CER；范围含冷/热启动 |
| docling | 2.149.0 | 9.5–19.3 s | 0.0061 | 9.5–12.2 s | 0.0093 | 最慢；中英均可用 |

解读：

- 这是**两个合成页**，不是中英文基准的全貌；不能据此给工具排序。
- 0.6%–1.9% 的差距主要来自标点归一化（`“”` → `""`，`——` → `--`），不是错字；见 `gotchas.md` 第 8 条。
- MinerU 的 `raw CER` 高是因为 Markdown 标记（`#`、`|`、表格分隔行）被计入；`cer_text` 已剥离。**不同输出格式的 raw CER 不可直接比较。**
- 耗时受冷/热启动影响大：MinerU 三次运行 1.0–9.6 s，Docling 9.5–19.3 s。发布前要分别报冷启动和热启动，不要用一个数字代表全部。
- 下一轮要加入真实 CC BY-SA 文章、CID/无 ToUnicode、繁简混排、竖排，并做冷/热启动分离。

复现：

```bash
python3 -I benchmarks/fixtures/make_demo.py
python3 -I scripts/bench.py \
  benchmarks/fixtures/demo-zh.pdf benchmarks/fixtures/demo-en.pdf \
  --tools pdftotext,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-demo --keep-raw
```

## 五之三、11 篇双语 smoke corpus（5 个工具，2026-11-09）

语料：`benchmarks/fixtures/zh-*.pdf` 与 `en-*.pdf`，由 `make_corpus.py` 生成，答案均为源文本。覆盖：文字层、双栏、表格、脚注、扫描件、英文行末连字符。

| 工具 | ok | empty/error | median CER | median no-punct CER | worst file | worst CER | median s |
|---|---:|---:|---:|---:|---|---:|---:|
| pdftotext | 9 | 2 | 0.0000 | 0.0000 | zh-footnote.pdf | 0.0000 | 0.04 |
| markitdown | 9 | 2 | 0.0000 | 0.0000 | en-hyphenation.pdf | 0.0066 | 0.89 |
| liteparse | 9 | 2 | 0.0130 | 0.0000 | zh-footnote.pdf | 0.0385 | 0.15 |
| mineru | 11 | 0 | **0.0030** | 0.0000 | zh-footnote.pdf | 0.0385 | 1.00 |
| docling | 11 | 0 | 0.0130 | 0.0000 | en-scan.pdf | 0.0712 | 10.06 |

解读：

- **empty/error = 2 的都是两份扫描件**：`pdftotext` / `markitdown` 没有文字层，`liteparse` 只输出约 0 字符。MinerU / Docling 能直接 OCR 扫描件，所以 ok=11。
- **所有工具的 no-punct CER 都是 0.0000**：剩下的 CER 全部来自标点归一化（MinerU 把全角 `：`/`；` 变成 ASCII，liteparse/markitdown 把引号/破折号变成 ASCII），不是错字。这是为什么必须同时报 `cer_text` 和 `cer_nopunct`。
- **MinerU 在本轮 11 篇上 median CER 最低（0.0030），但最差页仍是 zh-footnote（0.0385，标点）**；Docling 最差是 en-scan（0.0712，OCR 错误）。
- 耗时是模型已加载后的热启动；首次冷启动会明显更长（见上一节）。
- `pdfplumber` 在两份简单表格 fixture 上文本 CER 0.0000；真实合并表的结构/抽检见五之八，但**逐单元格 CER 仍未测**，不要把它当成表格结构已验证。
- **双栏 fixture 太温和**：reportlab 的两栏是按「左栏→右栏」顺序写入内容流，`markitdown` 也能读对。它没有强制「左一行、右一行」交错，不能证明真实双栏 PDF 已通过。下一轮要构造内容流逐行交错的 PDF。
- 这仍是合成语料，不能替代真实 PDF；下一轮加 CC BY-SA 真实文章和 CID/无 ToUnicode 样本。

复现：

```bash
python3 -I benchmarks/fixtures/make_corpus.py
python3 -I scripts/bench.py benchmarks/fixtures/zh-*.pdf benchmarks/fixtures/en-*.pdf \
  --tools pdftotext,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-corpus --keep-raw
```

## 五之四、OCR 路径对比（2 份扫描件，2026-11-09）

语料：`zh-scan.pdf` / `en-scan.pdf`（150 dpi，无文字层）。OCRmyPDF 行是「Tesseract chi_sim+eng 加文字层 → pdftotext」。

| 路径 | 中文 CER | 英文 CER | 中位耗时 | 备注 |
|---|---:|---:|---:|---|
| **RapidOCR** | **0.0116** | **0.0010** | 2.41 s | 直接 OCR；中英文都强 |
| MinerU | 0.0159 | 0.0020 | 1.44 s | 直接解析/OCR |
| Docling | 0.0101 | 0.0712 | 16.82 s | 中文好，英文扫描明显差 |
| OCRmyPDF（Tesseract） | 0.1012 | 0.0020 | 3.81 s | 中文差一个数量级；英文好 |
| pdfplumber | error | error | — | 无文字层，预期失败 |

解读：

- **中文扫描件**：RapidOCR / Docling / MinerU 都在 1%–1.6%；Tesseract `chi_sim` 约 10%，明显更差。中文扫描不要默认走 OCRmyPDF。
- **英文扫描件**：RapidOCR / MinerU / OCRmyPDF 都在 0.1%–0.2%；Docling 这次 7.1%，英文扫描要抽检。
- **pdfplumber 需要文字层**：扫描件上失败是正确行为，不是 bug。
- 这是 150 dpi 合成扫描件；低分辨率、倾斜、手写会改变排序。

复现：

```bash
python3 -I scripts/bench.py benchmarks/fixtures/zh-scan.pdf benchmarks/fixtures/en-scan.pdf \
  --tools rapidocr,ocrmypdf,pdfplumber,mineru,docling \
  --out /tmp/docarbiter-ocr --keep-raw
```

## 五之五、真实 CC BY-SA 样本（4 篇，2026-11-09）

语料：中文/英文维基百科各 2 篇，截取约 2,200 / 3,200 字符，渲染为 1–2 页文字层 PDF。来源、修改和 CC BY-SA 4.0 署名见 `benchmarks/fixtures/real/SOURCES.md`。

| 工具 | ok | median CER | median no-punct CER | worst file | worst CER | median s |
|---|---:|---:|---:|---|---:|---:|
| pdftotext | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0017 | 0.04 |
| pdfplumber | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0017 | 0.05 |
| markitdown | 4 | 0.0002 | 0.0000 | en-pdf.pdf | 0.0021 | 0.98 |
| liteparse | 4 | 0.0014 | 0.0000 | zh-ocr.pdf | 0.0082 | 0.25 |
| docling | 4 | 0.0020 | 0.0000 | zh-ocr.pdf | 0.0046 | 10.27 |
| mineru | 4 | 0.0074 | 0.0000 | zh-ocr.pdf | 0.0251 | 4.99 |

解读：

- **no-punct CER 仍然全部是 0.0000**：真实文章上的残差也主要是标点归一化（尤其 MinerU 的全角标点→ASCII）。这说明「内容正确性」在这些干净文字层样本上已经很高。
- MinerU 的 `cer_text` 最高（zh-ocr 2.51%），但 no-punct 为 0；不要只用 text CER 断言它「提取错了」。
- 速度排序与合成样本一致：`pdftotext`/`pdfplumber` < `liteparse` < `markitdown` < MinerU < Docling。
- 这些是**文字层** PDF，不是扫描件；也没有 CID/无 ToUnicode、双栏、竖排。真实世界的硬样本还要补。
- CC BY-SA 4.0：这四份 fixture 不是 MIT；再分发时保留 `SOURCES.md` 的署名与许可。

复现：

```bash
python3 -I benchmarks/fixtures/real/make_real.py
python3 -I scripts/bench.py benchmarks/fixtures/real/*.pdf \
  --tools pdftotext,pdfplumber,liteparse,markitdown,mineru,docling \
  --out /tmp/docarbiter-real --keep-raw
```

## 五之六、边缘样本（CID / 繁体 / 交错双栏 / 竖排模拟，2026-11-09）

语料：`benchmarks/fixtures/edge/`，由 `make_edge.py` 生成。CID 样本用 LibreOffice 生成正常中文 PDF，再用 pypdf 删除 `/ToUnicode`；竖排是**模拟**（一字一行），不是真正的 vertical writing mode。

| 样本 | pdftotext | liteparse | markitdown | pdfplumber | MinerU | Docling |
|---|---:|---:|---:|---:|---:|---:|
| `zh-cid-no-tounicode` | garbled | garbled | garbled | garbled | **4.95%** | garbled |
| `zh-traditional` | 0 | 0 | 0 | 0 | 1.72% | 0 |
| `zh-two-column-interleaved` | 0 | 0 | 0 | **67.94%** | 1.53% | 2.29% |
| `en-two-column-interleaved` | 0 | 0 | 0 | **60.36%** | 0 | 3.18% |
| `zh-vertical-sim` | 0 | **34.78%** | 0 | 0 | **13.04%** | 0 |

解读：

- **CID / 无 ToUnicode**：文字层工具（pdftotext / liteparse / markitdown / pdfplumber / Docling）全部 garbled；**MinerU 能 OCR 并拿到 4.95%**。这是「有字形、无字符映射」的典型场景：不要信文字层，走 MinerU / RapidOCR / olmOCR。
- **繁体**：所有工具基本正确；MinerU 的 1.72% 仍是标点归一化（no-punct 为 0）。
- **交错双栏**：`pdftotext` / `liteparse` / `markitdown` / MinerU 都能读对；**`pdfplumber` 60%–68%**，它按内容流/位置读，交错后阅读顺序不可用；Docling 2%–3% 有轻微问题。
  - 这**推翻**了交接文档里「markitdown 不处理双栏」的说法（至少在 0.1.9 + 本合成样本上没有复现）。不要在 README/gotchas 里继续断言；真实双栏仍要测。
- **竖排模拟**：pdftotext / markitdown / pdfplumber / Docling 正确；liteparse 34.78%、MinerU 13.04% 会打乱一字一行的顺序。**注意：这只是模拟，不是真正的竖排排版**；真竖排（vertical writing mode、从右到左换列）还没测。

复现：

```bash
python3 -I benchmarks/fixtures/edge/make_edge.py
python3 -I scripts/bench.py benchmarks/fixtures/edge/*.pdf \
  --tools pdftotext,liteparse,markitdown,pdfplumber,mineru,docling \
  --out /tmp/docarbiter-edge --keep-raw
```

> `make_edge.py` 的 CID 样本需要 LibreOffice `soffice`；`pypdf` 用于删除 `/ToUnicode`。两者都不是运行时依赖，只用于生成 fixture。

## 五之七、真实双栏论文（定性，2026-11-09）

来源：ResNet, arXiv:1512.03385，取前 3 页，保存在 `benchmarks/private/resnet-3p.pdf`（本地测试，不随仓库分发；没有答案 key，所以不做 CER）。

观察（同一份 3 页）：

| 工具 | 观察 |
|---|---|
| MinerU | abstract / 标题干净，正文可读；最佳 |
| Docling | abstract 可读；图注位置略前，整体可用 |
| liteparse | abstract 可读；段落合并较好 |
| pdftotext | abstract 可读；正文需检查栏序 |
| markitdown | **大量 Markdown 表格/坐标轴标签，abstract 被打散**；真实双栏含图时不可靠 |
| pdfplumber | 单词间空格丢失（`presentaresiduallearning...`），混入坐标轴标签 |

结论：

- 干净的文字双栏（合成）markitdown 能过；**真实论文含图/坐标轴时 markitdown 会坏**。不要把「合成双栏通过」当成「真实双栏通过」。
- 真实双栏优先 MinerU / Docling / liteparse；pdfplumber 只用于表格，不要直接抽全文。
- 尝试过 PLOS ONE `10.1371/journal.pone.0296319`（CC BY 4.0）：第 2 页是左侧 sidebar + 右侧正文，不是经典学术双栏；不作为双栏 CER fixture。
- 下一轮找一份 CC BY 的经典双栏论文（CVPR/IEEE 风格），用 HTML 全文作答案，做真正的 CER。

## 五之八、表格单元格级准确率（pdfplumber，2026-11-09）

语料：`benchmarks/fixtures/tables/`，由 `make_tables.py` 生成；truth 是 `<fixture>.json`。覆盖有框线、合并单元格、无框线三类。

| fixture | 找到表 | truth 行×列 | 提取行×列 | 单元格准确率 | 行准确率 |
|---|---:|---|---|---:|---:|
| zh/en-table-grid | 1 | 4×3 | 4×3 | **1.000** | 1.000 |
| zh/en-table-merged | 1 | 4×3 | 4×3 | **1.000** | 1.000 |
| zh/en-table-borderless | **0** | 4×3 | 0×0 | **0.000** | 0.000 |

解读：

- **有框线表格**：pdfplumber 默认 `extract_tables()` 单元格和行都 100%。
- **合并单元格**：测试里被覆盖的单元格 truth 为空、提取也为空，所以 1.000；这证明行列对齐和文本位置，**不证明它理解合并语义**。真实合并表头仍要人工检查。
- **无框线表格**：pdfplumber 默认找到 **0 个表**；需要 `table_settings` 的 text 策略，或改用 Camelot。默认路径不要承诺无框线表格可用。
- 只测了 pdfplumber；Camelot 未安装。

### text 策略的代价（同一批 fixture）

`text` 策略 = `vertical_strategy=text` + `horizontal_strategy=text` + 删除全空行：

| fixture | default 单元格准确率 | text 单元格准确率 |
|---|---:|---:|
| zh-table-grid | 1.000 | 1.000 |
| en-table-grid | 1.000 | 0.917 |
| zh-table-merged | 1.000 | 0.667 |
| en-table-merged | 1.000 | 0.583 |
| zh-table-borderless | 0.000 | **1.000** |
| en-table-borderless | 0.000 | **0.917** |

结论：**没有一种设置通吃**。默认适合有框线/合并；text 策略能救无框线，但会把合并单元格拆开、丢掉部分英文（`half z`）。实际使用时对同一页跑两种策略，选行列结构更合理的那份，或人工抽检。

### 真实高频表格（2026-11-10，本机私有文件，只读）

上面是合成 fixture。为了回答“真实书表/标准表能不能用”，另测了 5 份本机高频 PDF。**这些文件不在仓库、不上传、不保存正文；下面是结构与抽检结果，不是 CER 分数。**

| 真实文档（页） | 期望结构 | pdfplumber `lines` | pdfplumber `text` | MinerU | Docling |
|---|---|---|---|---|---|
| WS/T 578.1—2017 p8 | 21 数据行 × 13 列，3 层表头 | 27×13；表头压平 | 50×13；破 | 27×13；rowspan/colspan 正确 | 21×13；表头展开正确 |
| GB 28050—2025 p6 | 28 数据行 × 4 列，多行单元格 | 29×4；单元格乱序 | 76×6；破 | 29×4；7 处单元格交错 | 29×4；抽检正确 |
| DRIs 2023 p65 | 2 张符号表 15×6、14×6 | 0 表 | 69×9；不可用 | 15×6 + 14×6；中文名对，●/○ → 空/O | 名称需 OCR；●→`.`、○→`O` |
| GB 2760—2024 p13 | 26 数据行 × 4 列 | 27×4；抽检正确 | 84×3；破 | 27×4；4 处单元格交错 | 27×4；抽检正确 |
| 中国食物成分表 第6版第一册 p246 | 65 条目，双栏书表 | 0 表 | 45×4；不可用 | 6 列；65 条；前 3 行错位 | OCR 后 7 列；底部 3 行错位 |

解读：

- **复杂合并表头/多行单元格 → Docling。** WS/T 578.1、GB 28050、GB 2760 的结构与阅读顺序最好；这是 `--goal table-structure` 的依据。
- **坏文字层/符号表 → MinerU。** DRIs 2023 的文字层把 ● 变成 `.`、○ 变成 `。`；MinerU 能恢复中文名并把 ●/○ 区分为“空/O”，但**不保留原符号**。
- **pdfplumber 只做简单网格/坐标。** 单页 <0.5s；真实书表的多行单元格会乱序，`text` 策略会把 29×4 吹成 76×6。
- **密集双栏书表仍不保证。** 食物成分表 p246 的 65 条双栏表，Docling OCR 和 MinerU 都在页首/页尾行错位；必须人工抽检。**不要把“检测到表”当成“单元格正确”。**

耗时（M2 Pro，模型已热）：pdfplumber <0.5s/页；MinerU ≈2.5s/页；Docling no-OCR 3–5s/页，OCR 10–12s/页。

复现（把 `FILE` / `PAGE` 换成你的文件；真实文件不要放进仓库）：

```bash
# pdfplumber：两种策略都跑，比较行列
python3 -I -c 'import pdfplumber,sys; p=pdfplumber.open(sys.argv[1]).pages[int(sys.argv[2])-1]; print(p.extract_tables()); print(p.extract_tables(table_settings={"vertical_strategy":"text","horizontal_strategy":"text"}))' FILE PAGE

# Docling：干净文字层用 --no-ocr；坏文字层/扫描用默认 OCR；书要加 --page-range
mkdir -p /tmp/table-out
docling convert FILE --from pdf --to md --page-range PAGE --no-ocr --output /tmp/table-out --image-export-mode placeholder

# MinerU：必须在 ~/.mineru 里启动服务，否则会在当前目录生成 blobs/
(cd "$HOME/.mineru" && mineru server start)
mineru parse FILE --pages PAGE --force --output /tmp/table-out/page.md --json
```

合成 fixture 的复现：

```bash
python3 -I benchmarks/fixtures/tables/make_tables.py
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

## 五之九、真实 CC BY 双栏论文 abstract CER（BERT，2026-11-09）

来源：Devlin et al., "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", NAACL 2019, ACL Anthology `N19-1423`，**CC BY 4.0**。取 PDF 前 2 页作真实双栏 fixture；答案取 ACL Anthology HTML 的 abstract，用 rapidfuzz 部分对齐后只对 abstract 段算 CER。来源与署名见 `benchmarks/fixtures/real/SOURCES.md`。

| 工具 | CER | no-punct CER | 对齐分数 | 耗时 |
|---|---:|---:|---:|---:|
| MinerU | **0.0044** | 0.0000 | 99.8 | 18.40 s |
| pdftotext | 0.0066 | 0.0012 | 99.7 | 0.05 s |
| liteparse | 0.0066 | 0.0000 | 99.7 | 0.11 s |
| Docling | 0.0066 | 0.0012 | 99.7 | 11.23 s |
| markitdown | **0.7303** | 0.7344 | 56.6 | 1.13 s |
| pdfplumber | **0.7303** | 0.7344 | 56.8 | 0.16 s |

解读：

- **MinerU 在真实双栏 abstract 上最好（0.44%）**；pdftotext / liteparse / Docling 约 0.65%。
- **markitdown / pdfplumber 在真实双栏 abstract 上 CER 73%**：不是标点问题（no-punct 仍 73%），是 reading order / 文本混排问题。这和合成纯文字双栏的结果不同，说明「合成双栏通过」不能外推到真实论文。
- 只评了 abstract，不是全文；图、表、参考文献没有计分。全文 CER 仍待做。
- 这是一份 CC BY 4.0 的真实论文，可以随仓库分发 2 页 excerpt；完整 16 页只在 `benchmarks/private/`。

复现：

```bash
python3 -I scripts/bench_abstract.py --out /tmp/docarbiter-abstract
```

## 五之十、工作区真实 PDF 抽样（只读，2026-11-10）

只读扫描本机工作区，按 SHA-256 去重；不保存正文、不上传。明细在 `benchmarks/private/survey*.md` / `survey*.json` / `real-smoke.md`（gitignored）。

### 盘点与抽样

| 目录 | PDF 数 | 去重后 | 随机抽样 |
|---|---:|---:|---:|
| Doctoral Dissertation | 189 | 177 | 12 |
| CPET Data Analysis | 399 | 396 | 12 |
| Bioinformatics Data Analysis | 16 | 14 | 12 |
| Metabolomics Data Analysis | 7,862 | 7,857 | 12 |
| **合计** | **8,466** | **8,444** | **48** |

- 随机 48 个：**全部可用文字层**；47 英文 / 1 中文；0 个同名源文件；页数分布 25 个 1–3 页、10 个 4–20 页、13 个 21+ 页。
- 中文文件名样本 24 个（CPET 397 + Dissertation 35 个中文文件名中抽）：全部可用文字层；18 英文 / **6 中文**内容。
- 结论：工作区主体是**英文期刊库 + 干净文字层**；它适合验证路由、英文文字层提取和性能，但**天然不覆盖扫描件/CID/竖排**。

### 真实 4 文件 smoke（2 页/文件）

选 2 个中文 + 2 个英文，跑 pdftotext / liteparse / MinerU：

- 三个工具都成功；pdftotext/liteparse 约 0.03–0.13s，MinerU 冷启动后约 1–1.5s（首次 42s）。
- **顺序 CER 0.05–0.65，但字符袋差异只有 0.1%–2.6%**：多数情况下内容都在，差异是阅读顺序/分段，不是漏字。
- **一个真实风险**：某中文文章第 1 页，pdftotext 2,299 字符，MinerU 只有 1,480；拉丁字符 1,257→675，中文 664→531；第 2 页两者几乎一致（2,012 vs 2,009）。这像是 MinerU 丢了第一页的英文摘要/作者信息。**不要默认 MinerU 在中文期刊第一页一定完整。**

### 对项目的意义

- 工作区真实样本验证了：路由探针、文字层提取、性能。
- 它没有自然覆盖：扫描件、CID/无 ToUnicode、真竖排、复杂表格——这些仍由合成/边缘 fixture 负责。
- 真实 PDF 没有独立答案 key 时，只能报告 **agreement / coverage / bag 差异**，不能叫 accuracy。
- 下一步：对中文期刊样本按页检查拉丁内容覆盖；有同名源文件的再做本地 CER。

## 六、反模式（写进 CI 检查）

- ❌ 用 `pdftotext` 输出当 ground truth。
- ❌ 只报一个总分，不报最差页。
- ❌ 用英文样本的分数推断中文。
- ❌ 只测正文页，跳过表格/扫描/双栏。
- ❌ 不记录工具版本和语料版本。
- ❌ 把模型自报置信度当准确率。

## 七、待办

- [x] 生成 11 个双语合成样本 + 答案文本（`make_corpus.py`）
- [x] 写 `scripts/bench.py`（CER、no-punct CER、coverage、空输出识别）
- [x] 跑 5 个主选工具 + RapidOCR/OCRmyPDF 两条 OCR 路径
- [x] 把「最差页」样本加入 `gotchas.md`（标点、中文扫描 OCR）
- [x] 4 篇真实 CC BY-SA 维基文章（中文/英文各 2）
- [x] CID/无 ToUnicode、繁体、交错双栏、竖排模拟边缘样本
- [x] 真竖排（Chrome `vertical-rl`）+ 真实双栏定性（ResNet 3 页）
- [x] 真实 CC BY 双栏论文 abstract CER（BERT, ACL N19-1423）
- [x] 表格单元格级准确率（有框线/合并 1.000；无框线默认 0 表）
- [x] 5 份真实高频表的结构与抽检（Docling / MinerU / pdfplumber 分流）
- [ ] 真实表逐单元格 CER（当前只有结构与抽检）
- [ ] 无框线表格的 `table_settings` / Camelot 策略
- [ ] 繁简混排 + 公版古籍样本（可选）
- [ ] 跑完 12 个主选工具（含扩展层）
- [ ] 冷启动 / 热启动分离，写进 reporting
