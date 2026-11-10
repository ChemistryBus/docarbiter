# 工具注册表

> 核实日期：2026-11-09。star 数为 GitHub 当日快照；许可证以仓库 `LICENSE` / 包元数据为准。
> 机器可读版本：`registry.json`。本文件是人读说明。
> 逐工具安装命令与上游链接：`docs/install-routed-tools.md`。
> 中英状态的「待测」一律指**尚未用中英文 CER 语料验证**，不是「不支持」。

## 一、主选工具（12 个）

### 核心层：默认安装，CPU 可跑，许可证宽松

| # | 工具 | ★ | 许可证 | 角色 | 安装 | 中英状态 |
|---:|---|---:|---|---|---|---|
| 1 | **MinerU** | 83.3k | Apache-2.0 + 附加条款 | PDF → 结构化 Markdown、标题层级、页码锚点 | `pip install mineru==4.1.7`；`mineru-doc` | 中英 demo 0.0046 / 0.0013；扫描 1.59% / 0.20% |
| 2 | **Docling** | 70.3k | MIT | Office / HTML / EPUB / 音视频 / RAG chunks / LaTeX / 复杂合并表格 | `pip install docling==2.149.0`；`docling convert` | 中英 demo 0.0061 / 0.0093；扫描 1.01% / 7.12%；真实合并表结构与阅读顺序最好 |
| 3 | **liteparse** | 13.0k | Apache-2.0 | 最快的有文字层 PDF；词级坐标、字体信息 | `pip install liteparse==2.18.0`；封装 `liteparse-doc` | 中英 demo 0.0061 / 0.0079；文字层可用；扫描件不适用 |
| 4 | **MarkItDown** | 194.5k | MIT | 单栏 / Office 快速转 Markdown | `pip install markitdown==0.1.9`；`markitdown` | 中英 demo 0.0061 / 0.0185；双栏失败未复现（合成）；扫描件不适用 |
| 5 | **RapidOCR** | 8.5k | Apache-2.0 | 图片 / 截图 OCR | `pip install rapidocr==3.10.0`；Python API | 中文扫描 1.16%；英文扫描 0.10% |
| 6 | **OCRmyPDF** | 35.3k | MPL-2.0 | 扫描 PDF 加文字层 | `pip install ocrmypdf==17.12.1`；`ocrmypdf` | 中文扫描 10.1%；英文扫描 0.20% |
| 7 | **pdfplumber** | 10.9k | MIT | 简单有框线表格 / 字符坐标 / DataFrame | `pip install pdfplumber==0.11.10`；Python API | 合成有框线/合并 cell 1.000；真实多行单元格乱序；无框线 0 表；交错双栏 60%–68%；扫描件不适用 |
| 8 | **pdftotext**（Poppler） | — | GPL-2.0/3.0 | 纯文字基线、文字层探测 | 系统包（Homebrew `poppler`）；`pdftotext` | 中英文字层；CID/无 ToUnicode 会乱码 |

### 扩展层：按需安装，重依赖 / GPU / 特殊场景

| # | 工具 | ★ | 许可证 | 角色 | 安装 | 中英状态 |
|---:|---|---:|---|---|---|---|
| 9 | **PaddleOCR** | 92.5k | Apache-2.0 | 中文 OCR / PP-Structure 版面与表格 | `pip install paddleocr paddlepaddle`；`paddleocr` | 中文原生，英文可用；CER 待测；依赖体积大 |
| 10 | **Marker** | 40.8k | Apache-2.0 | PDF → Markdown，多语种 | `pip install marker-pdf==2.1.0`；CLI `marker_single`（待验证） | Surya 多语种 OCR；中英待测；GPU 推荐 |
| 11 | **Unstructured** | 15.7k | Apache-2.0 | 企业级多格式 ingestion / 分区 | `pip install unstructured`；Python API（CLI 待验证） | 取决于 OCR 后端；中英待测；依赖重 |
| 12 | **olmOCR** | 19.8k | Apache-2.0 | VLM 扫描件 OCR / 长文档 | `pip install olmocr==0.4.27`；CLI `olmocr`（待验证） | 多语种；中英待测；GPU 必需 |

### 可选补充（注册表里保留，默认不装）

| 工具 | ★ | 许可证 | 角色 | 备注 |
|---|---:|---|---|---|
| **Surya** | 21.6k | Apache-2.0 | OCR / 版面 / 阅读顺序 | Marker 的底层；GPU 推荐 |
| **Camelot** | 3.8k | MIT | 表格提取（lattice / stream） | 与 pdfplumber 互补；文字层表格 |
| **Tesseract** | 77.4k | Apache-2.0 | OCR 兜底 | `chi_sim` 中文弱于 PaddleOCR；系统依赖多 |
| **qpdf** | 5.6k | Apache-2.0 | 拆分 / 合并 / 解密 / 修复 | PDF 操作，不做内容提取 |
| **pypdf** | 10.3k | BSD-3-Clause | 纯 Python PDF 操作 | 不依赖外部二进制；适合脚本化 |
| **pdfminer.six** | 7.0k | MIT | 底层文字/坐标提取 | 兜底；比 pdfplumber 更底层 |

## 二、考虑过但未纳入默认路径

| 工具 | ★ | 许可证 | 未纳入原因 |
|---|---:|---|---|
| **PDF-Extract-Kit** | 10.1k | AGPL-3.0 | 传染性许可；版式/表格/公式能力强。只给链接，用户自行决定是否安装 |
| **PyMuPDF** | — | AGPL-3.0 / 商业双许可 | 同上；底层控制强，但会把项目拖入 AGPL |
| **Ghostscript** | — | AGPL-3.0 | 同上；PDF 渲染/转换用 |
| **Anthropic `pdf` 技能** | — | Proprietary | 不可再分发；负责合并/拆分/加密/表单，不做结构化提取。README 只给链接 |
| **LlamaParse** | — | 商业 API | 云端解析，数据离机、按页计费 |
| **Azure Document Intelligence** | — | 商业 API | 同上；中文 layout 能力强，但不本地 |
| **Google Document AI** | — | 商业 API | 同上 |
| **Adobe PDF Extract** | — | 商业 API | 同上 |
| **Mathpix** | — | 商业 API | 公式/表格强，但云端 |
| **EasyOCR** | — | Apache-2.0 | 可跑，但中文场景 RapidOCR/PaddleOCR 更轻、更专 |
| **MMOCR** | — | Apache-2.0 | 研究框架，依赖重，部署成本高于 PaddleOCR |
| **docTR** | — | Apache-2.0 | OCR 为主，缺完整 PDF 版面/阅读顺序 |

## 三、许可证分组（用于 `install.sh`）

**默认 `--profile core`（宽松、CPU、轻量）：**
MinerU、Docling、liteparse、MarkItDown、RapidOCR、OCRmyPDF、pdfplumber、Poppler/pdftotext。

**`--profile extra`（重依赖 / GPU / 特殊）：**
PaddleOCR、Marker、Unstructured、olmOCR、Surya、Camelot、Tesseract、qpdf、pypdf、pdfminer.six。

**永不进入安装脚本：**
PDF-Extract-Kit（AGPL）、PyMuPDF（AGPL）、Ghostscript（AGPL）、Anthropic `pdf`（Proprietary）、商业云 API。

> **GPL/MPL 工具的处理**：`pdftotext`（Poppler，GPL）与 OCRmyPDF（MPL）通过系统包/独立进程调用，不修改、不再分发；仓库 MIT 不受影响。`install.sh` 只执行包管理器命令，不把上游代码复制进仓库。

## 四、版本固定策略

薄壳里的命令与坑是按本机版本实测的。`install.sh` 默认读取 `requirements.lock` 中的精确版本；`--latest` 才装最新版并标注「未验证」。当前实测版本：

```
mineru==4.1.7
docling==2.149.0
liteparse==2.18.0
markitdown==0.1.9
rapidocr==3.10.0
ocrmypdf==17.12.1
pdfplumber==0.11.10
pymupdf==1.28.2      # 仅记录，不安装
```

> 扩展层版本待安装后补入；`marker-pdf` / `surya-ocr` / `unstructured` / `olmocr` / `paddleocr` 以第一次实测版本为准。

## 五、待核实项

- [ ] Marker / Surya / Unstructured / olmOCR 的实际 CLI 入口与参数
- [x] 各工具对中文扫描件、合成交错双栏、繁体、CID/无 ToUnicode 的 CER
- [ ] 真实双栏、真竖排、合并单元格表格的单元格级 CER
- [ ] 各工具对英文真实双栏、英文表格、连字符换行、引号/破折号的 CER（合成交错双栏已测）
- [ ] PaddleOCR 的 PP-Structure 在中文表格上的单元格准确率
- [ ] MinerU 模型权重的独立许可（安装时下载的模型是否另有条款）
- [ ] Marker / Surya 模型权重的独立许可
- [ ] `liteparse` 对无 ToUnicode 中文 PDF 的行为
- [ ] `docling` 默认 OCR 后端与中文模型选择
- [x] `registry.json` 与 `skills/_tools/` 的 id 一致（`validate.py` 已检查）
- [ ] 12 个主选工具的中英文全量 CER
