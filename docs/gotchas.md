# 实测坑

> 每条都附复现方式。环境：macOS 26 / M2 Pro / Python 3.11.11（2026-11-09）。
> 其他平台标「未验证」。不要把这些结论当成上游的普遍行为——它们是在本机、本版本上测到的。

---

## 1. liteparse 默认开 OCR，失败时卡约 123 秒

**症状**：直接 `LiteParse().parse("file.pdf")` 长时间无输出，最后报 tessdata 下载失败。

**原因**：上游默认 `ocr_enabled=True`，会尝试从 GitHub 下载 tessdata；网络不通时阻塞。

**修复**：用本仓库的 `liteparse-doc`（强制 `ocr_enabled=False`）；确实要 OCR 时加 `--ocr`，并先配好 tessdata。

**复现**：

```bash
python3 -c "from liteparse import LiteParse; LiteParse().parse('benchmarks/fixtures/demo-zh.pdf')"
time liteparse-doc benchmarks/fixtures/demo-zh.pdf >/dev/null
```

---

## 2. docling 默认把图片 base64 内联，Markdown 爆炸

**症状**：一页 Markdown 从约 2.6k 字符膨胀到约 69k。

**原因**：`--image-export-mode` 默认把图片嵌入文档。

**修复**：始终加 `--image-export-mode placeholder`。

```bash
docling convert file.pdf --to md --output out/ --image-export-mode placeholder
```

---

## 3. MinerU 用当前工作目录解析缓存，留下 blobs/ 和锁文件

**症状**：在项目目录执行 `mineru server start` 后，目录里出现 `blobs/` 和 `.mineru-service.lock`。2026-11-10 在 `~/Documents/Claude` 又出现一次，实测 **200MB**；内容是按 SHA 分桶的解析缓存，不是项目文件。

**原因**：MinerU 用 CWD 解析缓存目录；`mineru-doc` 封装固定了 `cd "$HOME/.mineru"`，但手动裸跑 `mineru server start` 不会。

**修复**：用 `mineru-doc`；手动起服务时必须先 `cd ~/.mineru`。已经生成的 `blobs/` 可以直接删（缓存可重建）；删之前确认没有 `mineru` 进程在跑。

```bash
# 错误
mineru server start
# 正确
(cd "$HOME/.mineru" && mineru server start)

# 清理误生成的缓存
rm -rf blobs .mineru-service.lock
```

> 本仓库 `.gitignore` 已加入 `blobs/` 和 `.mineru-service.lock`；但它们仍不该出现在工作目录里。测试/脚本里不要裸跑 `mineru server start`。

---

## 4. 双栏：合成纯文字未复现，真实论文（含图）会打散

**合成纯文字、内容流逐行交错**：markitdown / pdftotext / liteparse / MinerU 的 CER 都是 **0**；pdfplumber **60%–68%**。所以「markitdown 一定不处理双栏」在干净合成样本上**没有复现**。

**真实论文（ResNet, arXiv:1512.03385, 3 页，本地 `benchmarks/private/`）**：markitdown 输出大量 Markdown 表格/坐标轴标签，abstract 被打散；pdfplumber 丢空格、混入坐标轴；MinerU / Docling / liteparse 的 abstract 可读。这份没有答案 key，所以不做 CER，只做定性阅读顺序检查。

**真实 CC BY 双栏论文（BERT, ACL Anthology N19-1423, abstract CER）**：MinerU **0.44%**；pdftotext / liteparse / Docling **0.65%**；markitdown / pdfplumber **73%**。no-punct 仍是 73%，是阅读顺序/混排，不是标点。这条把「合成双栏通过」和「真实双栏通过」彻底分开了。

**结论**：不要说「markitdown 一定/一定不处理双栏」。干净的文字栏它能过；真实论文有图、坐标轴、文本框时会坏。真实双栏优先 `mineru` / `docling` / `liteparse`；`pdfplumber` 不要直接抽全文。

**复现**：合成样本见 `benchmarks/fixtures/edge/`；真实论文用 `benchmarks/private/resnet-3p.pdf`（本地保留，不随仓库分发）。

---

## 5. 对有文字层的 PDF 做 OCR 是负优化

**症状**：本来顺序正确的文本，OCR 后双栏被打乱；实测字符顺序相似度从 97% 掉到 40%。

**原因**：OCR 重新检测文本框，按图像位置而不是原始阅读顺序输出。

**修复**：先跑 `docarbiter` 的文字层探针；`bad_ratio` 低且 `chars` 足够时不要 OCR。

---

## 6. liteparse 的段落会被页眉打断

**症状**：

```
...whereas 80% is derived from the
D. Ylli et al.                      ← 页眉混进段落中间
monodeiodination of T4 by 5'-deiodinase...
```

**原因**：liteparse 不做页眉/页脚过滤，按页面文本流输出。

**修复**：要成稿用 `mineru`；用 liteparse 时按页眉字符串清洗，或只取正文页。

---

## 7. liteparse 的标题层级会判错

**症状**：同级标题有的输出 `###`，有的输出 `####`。

**原因**：标题层级靠字体/字号启发式判断，跨页或样式不一致时漂移。

**修复**：成稿用 `mineru`；用 liteparse 时按字号/字体后处理，不要直接信 Markdown 层级。

---

## 8. liteparse 会把全角标点归一化成 ASCII

**症状**：源文本的 `“”‘’` 变成 `""''`，`——` 变成 `--`。在 1 页中文 demo 上，CER 从 0 升到 0.61%（8 处替换）。

**原因**：liteparse 的文本归一化/输出层把部分全角标点映射成 ASCII。

**修复**：做标点敏感校对时，先对比原始 PDF；`bench.py` 同时报告 `cer_text` 与 `cer_raw`，后者不剥离 Markdown，但仍会看到这个差异。

**复现**：

```bash
liteparse-doc benchmarks/fixtures/demo-zh.pdf | grep -n '第一段'
pdftotext benchmarks/fixtures/demo-zh.pdf - | grep -n '第一段'
```

---

## 9. MinerU `--tier flash` 没有结构

**症状**：输出只有纯文字，没有 `## Heading`、图注、页码锚点。

**原因**：flash 层是免服务的快速纯文字模式。

**修复**：成稿用默认 tier（basic/standard）或 `mineru-doc`；flash 只用于快速预览。

---

## 10. `liteparse-doc --help` 曾被当成文件名

**症状**：`liteparse-doc --help` 抛 `FileNotFoundError: --help`。

**原因**：旧封装把第一个参数无条件当路径。

**修复**：本仓库的封装已加 `-h/--help` 分支；如果你用的是旧版封装，直接无参数运行看用法。

---

## 11. 拿 `pdftotext` 当答案会让基准失去意义

**症状**：`pdftotext` 的 CER 永远是 0，其他工具看起来都「不准」。

**原因**：答案就是 `pdftotext` 的输出，测的是「谁更像 pdftotext」，不是准确率。

**修复**：答案必须来自独立来源（我们自己写的文本 / CC BY-SA 文章源文本 / 公版校对文本）。本仓库的 demo 用源文本作答案，所以 `pdftotext` 的 0 是真实的，而不是循环论证。

---

## 12. 英文行末连字符会让 CER 虚高

**症状**：`docu-\nment` 被工具保留成 `docu-ment`，和答案 `document` 对比时算成 1 个替换 + 1 个插入。

**原因**：PDF 行末断词；`pdftotext` / `liteparse` 保留连字符，不做 dehyphenation。

**修复**：`bench.py` 在归一化时合并 `[A-Za-z]-\n[A-Za-z]`。但 `well-known` 这类**真连字符**不能被合并（它们没有换行），所以要人工抽检。

**复现**：找一份英文双栏 PDF，检索 `-` 后紧跟换行的词；对比原文。

---

## 13. 全角标点被归一化成 ASCII，CER 会虚高

**症状**：MinerU 把全角 `：` / `；` 输出成 `:` / `;`；liteparse 把 `“”‘’` 输出成 `""''`；markitdown 对英文引号/破折号也会变。

**后果**：在 11 篇双语 smoke corpus 上，所有工具的 **no-punct CER = 0.0000**，但 `cer_text` 最高 3.85%。这不是错字，是标点归一化。

**修复**：

- 同时报 `cer_text` 与 `cer_nopunct`（`bench.py` 已输出两列）；
- 做标点敏感校对时，与原始 PDF 对比；
- 不要用单一 CER 断言「工具提取错了」。

**复现**：

```bash
mineru-doc benchmarks/fixtures/zh-footnote.pdf | grep '第一段'
pdftotext benchmarks/fixtures/zh-footnote.pdf - | grep '第一段'
```

---

## 14. 中文扫描件不要默认用 Tesseract chi_sim

**症状**：`ocrmypdf --language chi_sim+eng` 加文字层后再 `pdftotext`，中文 CER **10.1%**；同一份扫描件：

| 路径 | 中文 CER |
|---|---:|
| RapidOCR | 1.16% |
| Docling | 1.01% |
| MinerU | 1.59% |
| OCRmyPDF（Tesseract chi_sim） | **10.1%** |

英文扫描件上 Tesseract 正常（0.20%），所以问题不是 OCRmyPDF 本身，而是 `chi_sim` 中文模型。

**修复**：中文扫描优先 `rapidocr` / `mineru` / `docling`；OCRmyPDF 用于英文或兜底。

**复现**：

```bash
ocrmypdf --language chi_sim+eng --output-type pdf --quiet zh-scan.pdf /tmp/zh-scan-ocr.pdf
python3 -I scripts/bench.py /tmp/zh-scan-ocr.pdf --truth benchmarks/fixtures/zh-scan.txt \
  --tools pdftotext --out /tmp/ocr-check
```

---

## 15. CID / 无 ToUnicode 会输出控制字符，不是「扫描件」

**症状**：`pdftotext` 输出 `\x01\x02\x03...` 一类控制字符；`markitdown` / `pdfplumber` 输出更长乱码（CER > 1）；Docling 也 garbled。MinerU 反而能 OCR，CER 4.95%。

**原因**：字体有字形，但没有 `/ToUnicode` 映射；文字层「有字符」但不可用。只看字符数会把 68 个控制字符误判成「有文字层」。

**修复**：

- 探针加 `ctrl_ratio`（控制字符占非空白字符的比例）；`> 10%` 判乱码；
- 不要用 `pdftotext` / `liteparse` / `markitdown` / `pdfplumber` 硬抽；
- 走 MinerU / RapidOCR / olmOCR；这类 PDF 需要 OCR，不是「有文字层就不要 OCR」。

**复现**：

```bash
python3 -I benchmarks/fixtures/edge/make_edge.py
pdftotext benchmarks/fixtures/edge/zh-cid-no-tounicode.pdf - | head -3
python3 -I scripts/bench.py benchmarks/fixtures/edge/zh-cid-no-tounicode.pdf \
  --tools pdftotext,markitdown,mineru,docling --out /tmp/cid-check
```

---

## 16. 竖排模拟：liteparse / MinerU 会打乱一字一行的顺序

**实测**：`zh-vertical-sim.pdf`（一字一行，从上到下）上，pdftotext / markitdown / pdfplumber / Docling CER 0；liteparse 34.78%，MinerU 13.04%。

**注意**：这只是**模拟**，不是真正的 vertical writing mode；真竖排（从右到左换列、标点旋转）还没测。不要把这条当成真竖排结论。

**修复**：真竖排先用 MinerU/Docling 抽，人工检查列顺序；不要默认任何工具能处理竖排。

---

## 17. pdfplumber 默认对无框线表格返回 0 个表

**实测**：有框线 / 合并单元格 fixture 上 `extract_tables()` 单元格准确率 1.000；**无框线 fixture 上 `tables=0`，单元格准确率 0.000**。

**原因**：pdfplumber 默认的表格检测依赖 ruling lines（框线）；没有线时，默认策略找不到表格。

**修复**：

- 调 `table_settings`（`vertical_strategy=text` + `horizontal_strategy=text`），或改用 Camelot；
- 但 text 策略不是免费午餐：同批 fixture 上，无框线从 0 升到 **1.000/0.917**，合并单元格却从 1.000 掉到 **0.667/0.583**，英文还会被截断（`half z`）；
- 实际使用时对同一页跑 default + text 两种策略，选行列结构更合理的那份，或人工抽检；
- 不要把「pdfplumber 支持表格」理解成「任何表格都能抽」；合并单元格的 1.000 也不证明语义正确。

**复现**：

```bash
python3 -I benchmarks/fixtures/tables/make_tables.py
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

---

## 18. MinerU 在中文期刊第 1 页可能丢英文摘要/作者信息

**实测（工作区真实中文文章，2 页 smoke）**：

| 页 | pdftotext 字符 | MinerU 字符 | 拉丁字符 pdftotext→MinerU | 中文 pdftotext→MinerU |
|---|---:|---:|---|---|
| 第 1 页 | 2,299 | **1,480** | 1,257 → **675** | 664 → 531 |
| 第 2 页 | 2,012 | 2,009 | 521 → 518 | 1,016 → 1,016 |

第 1 页 MinerU 少了约 **35%** 内容，主要是拉丁字符；第 2 页几乎完全一致。很像中文期刊的**英文摘要/作者信息/参考文献**被丢掉。

**修复**：

- 中文期刊不要只看中文正文；检查第一页的拉丁字符覆盖率。
- 对第一页用 pdftotext/liteparse 交叉核对；如果英文摘要重要，不要只用 MinerU。
- 没有独立答案 key 时，报告 `bag`（字符袋）差异，不要只报顺序 CER。

**复现**：`python3 -I scripts/survey_pdfs.py --root <workspace> --dirs "<dir1,dir2>"` 抽中文样本，再用 `scripts/sample_real.py --root <workspace>` 做 2 页 smoke；明细在 `benchmarks/private/real-smoke.md`（gitignored）。

---

## 19. pdfplumber 检测到表 ≠ 单元格文字正确

**实测（真实标准表）**：

- WS/T 578.1—2017 p8：`lines` 策略找到 27×13，但三层合并表头被压平；`text` 策略变成 50×13，`重(III)` 被拆成两列。
- GB 28050—2025 p6：`lines` 策略 29×4 行数对，但多行单元格阅读顺序乱（“单不饱和脂肪（或单不饱和脂肪酸）”被拆开交错）；`text` 策略变成 76×6。
- 中国食物成分表 第6版第一册 p246：`lines` 找到 0 表；`text` 找到 45×4，仍不可用。

**修复**：复杂合并表头/多行单元格优先 `docling`；pdfplumber 只用于简单网格/坐标。无框线中文表可试 `vertical_strategy="text"`，但要接受合并单元格被拆。

**复现**：见 `docs/benchmarks.md` 五之八“真实高频表格”。

---

## 20. Docling 表格：干净文字层用 `--no-ocr`，坏文字层才开 OCR

**实测**：

- GB 28050 p6、GB 2760 p13、WS/T 578.1 p8：`--no-ocr` 的结构和阅读顺序最好（3–5s/页）。
- DRIs 2023 p65：文字层本身把 ● 变成 `.`、○ 变成 `。`；`--no-ocr` 会把错字原样复制。开 OCR 后中文名恢复，但符号仍不保留原字形。
- 中国食物成分表 p246：`--no-ocr` 输出大量错字（“宣物丢”“十酸”）；开 OCR 后才可用，但页首/页尾仍有行错位。
- 中文无框线表格（`zh-table-borderless.pdf`）：Docling 输出 0 个表；`pdfplumber` 的 text 策略反而 1.000。

**修复**：先跑文字层探针；干净文字层用 `--no-ocr`，坏文字层/扫描用默认 OCR。书只跑 `--page-range`；`--output` 目录要先 `mkdir -p`，否则会写到当前目录。

**复现**：见 `docs/benchmarks.md` 五之八。

---

## 21. 符号表（●/○）没有工具能完全保真

**实测（DRIs 2023 p65“矿物质概览/维生素概览”）**：

| 工具 | 中文名 | ●/○ 区分 | 原符号 |
|---|---|---|---|
| MinerU | 正确 | 空 / O | 否 |
| Docling no-OCR | 错 5 个矿物种名 | `.` / `O` | 否 |
| Docling OCR | 正确 | `.` / `O` | 否 |
| pdfplumber | — | 0 表 / 69×9 不可用 | 否 |

**修复**：符号表只把“已制定/未制定/未涉及”当二元/三元状态用，不要声称保留了 ●/○ 字形；交付前人工对照原页抽检。需要精确符号时，用页面截图或人工转录。

**复现**：`docling convert FILE --page-range 65 --no-ocr ...` 与 `mineru parse FILE --pages 65 ...`。

---

## 22. 只有一张小表的页可能被文字层探针判成扫描件

**实测**：`zh-table-merged.pdf` 只有 4×3 表，文字层 47 字符；`route.py` 的阈值是 `chars < 50` → `status=scan` → 路由到 MinerU。它其实是文字层表格。

**修复**：探针是启发式，不是判决。确认 PDF 有文字层（`pdftotext` 能出字、`bad_ratio` 低）时，直接按表格目标调用 `pdfplumber` / `docling`，不要因为 `status=scan` 就强制 OCR。反过来，真正的扫描件即使 OCR 出几个字也不要信文字层。

**复现**：`python3 -I scripts/route.py benchmarks/fixtures/tables/zh-table-merged.pdf --goal table-structure`。

---

## 23. 整本书的路由只看前 3 页，不能代表后面的表格页

**实测**：DRIs 2023 前 3 页文字层可用，`route.py --goal table-structure` 会选 Docling；但第 65 页的 ●/○ 符号表文字层是坏的，Docling `--no-ocr` 会把错字原样复制，必须对**目标页**开 OCR 或改用 MinerU。

**修复**：书/标准不要用整本路由结果直接跑；先定位目标页，用 `pdftotext -f PAGE -l PAGE` 或 `pdfplumber` 对该页做小探针，再决定 `--no-ocr` / OCR / MinerU。路由是文件级启发式，不是页级判决。

**复现**：`pdftotext -f 65 -l 65 FILE -` 与 `mineru parse FILE --pages 65 ...` 对比。

---

## 未验证 / 待补

- [ ] Linux / Windows 上的行为（尤其 MinerU 服务、PaddleOCR 安装）
- [x] 中文扫描件上 Tesseract `chi_sim` vs RapidOCR 的 CER（RapidOCR 1.16% / Tesseract 10.1%）
- [x] 合成交错双栏、繁体、CID/无 ToUnicode、竖排模拟
- [x] 5 份真实高频表的结构与抽检（WS/T 578.1、GB 28050、DRIs 2023、GB 2760、中国食物成分表）
- [ ] 真实表逐单元格 CER（当前只有结构/抽检，不能叫 accuracy）
- [ ] 英文真实双栏、页眉页脚的 CER（合成交错双栏已测）
- [ ] Marker / Surya / olmOCR 的中英文表现
- [x] `liteparse` 对无 ToUnicode 中文 PDF 的行为（garbled）
