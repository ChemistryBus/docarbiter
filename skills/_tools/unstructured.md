---
name: unstructured
description: 企业级多格式文档 ingestion：分区、元素分类、表格、OCR，输出结构化元素列表。
  适合批量多格式管道；单文件小任务用 docling/markitdown。依赖重，中文待实测。
license: Apache-2.0
---

# unstructured

## 定位

面向 RAG / 数据管道的文档 ingestion 库：把 PDF、DOCX、PPTX、HTML、EML 等切成带类型的元素（Title / NarrativeText / Table / ListItem），可选 OCR、表格结构、坐标。适合批量、多格式、需要元素级元数据的场景。

不适合：单文件快速转换（`docling` / `markitdown` 更轻）；只要 Markdown 成稿（`mineru`）；依赖敏感的环境。

## 装

```bash
pip install unstructured
# 按需装 extras，例如 PDF：pip install 'unstructured[pdf]'
```

> 依赖重，且不同 extras 会拉入不同 OCR/版面模型；先确认 Python 版本和磁盘。

## 用

```python
from unstructured.partition.pdf import partition_pdf

elements = partition_pdf(
    "file.pdf",
    strategy="hi_res",          # fast / hi_res / ocr_only
    languages=["chi_sim"],      # 待验证：按本机 OCR 后端确认语言码
)
for el in elements:
    print(el.category, el.text)
```

**待验证**：`languages` 的语言码、`hi_res` 的模型下载、CLI 入口（`unstructured-ingest` 可能来自独立包）。调用前读本机安装版本的文档。

## 坑（已知 / 待实测）

- **依赖重、首次运行下载模型**：不适合一次性小任务。
- **`hi_res` 慢**：比 `fast` 慢一个数量级；先用 `fast` 试，再决定。
- **中文取决于 OCR 后端**：Tesseract `chi_sim` 与 PaddleOCR 效果差异大；`languages` 配置要实测。
- **输出是元素列表，不是 Markdown**：要 Markdown 还得自己拼，或改用 `docling`。
- **版本/API 漂移**：`partition_pdf` 的参数随版本变化；不要跨版本套用。

## 上游

https://github.com/Unstructured-IO/unstructured

许可证：Apache-2.0。
