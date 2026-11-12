---
name: docling
description: 多格式文档转结构化 Markdown/JSON/HTML/chunks/LaTeX。适合 Office、HTML、EPUB、音视频、邮件、RAG 分块，以及合并表头/多行单元格的复杂表格。
  纯 PDF 正文成稿优先用 mineru；只要最快读文字层用 liteparse；简单网格表格用 pdfplumber。
license: MIT
---

# docling

## 定位

本合集里**格式覆盖最广**的选项：DOCX / XLSX / PPTX / HTML / EPUB / 图片 / 音频 / 视频 / LaTeX / 邮件等 30+ 种输入，输出 Markdown、JSON、HTML、doctags、chunks、LaTeX。基于 IBM Docling，纯本地。

不适合：只读 PDF 正文（比 `liteparse` 慢，成稿不如 `mineru`）；只要纯文字（`pdftotext` 更快）；中文无框线表格（实测可能 0 表，改用 `pdfplumber` 的 text 策略）。

## 装

```bash
pip install docling==2.150.0
# 首次运行会下载版面/表格模型
```

## 用

```bash
docling convert report.docx --to md --output out/ --image-export-mode placeholder
docling convert book.pdf --to chunks --output ./rag --image-export-mode placeholder
docling convert paper.pdf --to latex --output out/
docling convert page.png --to md --image-export-mode placeholder
```

## 坑（本机实测）

- **图片默认 base64 内联**：不加 `--image-export-mode placeholder`，一页 Markdown 可能从 2.6k 膨胀到 69k 字符。**永远加**。
- **PDF 解析慢**：实测 4–8 秒/页，明显慢于 `liteparse` / `mineru`。只读正文时不要默认用它。
- **复杂表格是本机实测最强项**：WS/T 578.1 的三层合并表头、GB 28050 的多行单元格、GB 2760 的大表都能保住结构和阅读顺序；`pdfplumber` 在这些表上会乱序，`mineru` 会把多行单元格字符交错。
- **中文无框线表格会漏**：`zh-table-borderless.pdf` 上 Docling 输出 0 个表；`pdfplumber` 的 `vertical_strategy="text"` 能救，但会伤合并单元格。不要承诺“所有表格”。
- **OCR 默认开**：有干净文字层的 PDF 用 `--no-ocr`；文字层本身是坏的（如 DRIs 2023 的 ●/○ 符号页）用默认 OCR，仍要抽检符号。
- **书只跑目标页**：`--page-range 65`；整本 655 页会非常慢。
- **输出目录要先存在**：`--output` 是目录，不是文件名；目录不存在时会写到当前目录。先 `mkdir -p out`。
- **表格结构模型可选**：`--tables` 默认开；表格差时试 `--table-structure` 的不同后端，或改用 `pdfplumber`。

## 上游

https://github.com/docling-project/docling

许可证：MIT。
