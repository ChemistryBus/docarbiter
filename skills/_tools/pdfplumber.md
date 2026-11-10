---
name: pdfplumber
description: 从有文字层的 PDF 提取有框线表格、单元格和字符级坐标。适合简单网格、DataFrame、精确位置。
  合并表头/多行单元格/书表优先 docling；扫描件不适用；整本成稿用 mineru；RAG 分块用 docling。
license: MIT
---

# pdfplumber

## 定位

PDF 表格和字符级信息提取的精细工具：能拿到每个字符的坐标、字体、大小，以及表格的单元格结构。适合简单有框线网格、财务报表、实验数据表、需要转 DataFrame 的场合。

不适合：扫描件（没有文字层）；合并表头/多行单元格/书表（实测单元格文字顺序会乱，优先 `docling`）；整本论文成稿（用 `mineru`）；只要纯文字（`pdftotext` 更快）。

## 装

```bash
pip install pdfplumber==0.11.10
```

## 用

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    page = pdf.pages[98]                 # 第 99 页（0 起）
    print(page.extract_text())           # 纯文字
    for table in page.extract_tables():  # 表格 → 二维列表
        print(table)
```

需要更细的单元格/坐标时，读上游文档的 `table_settings` 和 `chars` / `rects` API；不要凭记忆猜参数。

## 坑（本机实测 / 已知）

- **不做 OCR**：扫描件输出为空；先用 `ocrmypdf` 或 `rapidocr`。
- **依赖文字层质量**：CID / 无 ToUnicode 的 PDF 同样乱码；先跑文字层探针。
- **合并单元格会丢结构**：跨行/跨列的表头容易错位；需要人工校验。复杂表优先 `docling`。
- **多行单元格文字会乱序**：GB 28050 的“单不饱和脂肪（或单不饱和脂肪酸）”会被拆成多行并交错；不是 PDF 坏了，是单元格 bbox 不按阅读顺序。
- **无框线表格靠启发式**：`extract_tables()` 默认策略对无框线表格不稳；调 `table_settings`（`vertical_strategy="text"`）或改用 `camelot`。text 策略会伤合并单元格。
- **速度快**：单页通常 <0.5s；比 `docling` / `mineru` 快一个数量级。只对需要的页调用。

## 上游

https://github.com/jsvine/pdfplumber

许可证：MIT。
