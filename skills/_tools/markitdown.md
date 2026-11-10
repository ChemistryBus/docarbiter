---
name: markitdown
description: 微软的轻量文档转 Markdown 工具。适合单栏 Office / PDF 快速转换。
  不处理双栏，不处理扫描件；双栏 PDF 用 mineru，扫描件用 ocrmypdf/rapidocr。
license: MIT
---

# markitdown

## 定位

微软官方的轻量转换器：DOCX / XLSX / PPTX / PDF / HTML 等 → Markdown。安装小、速度快（实测约 1.5 秒/5 页），适合单栏、结构简单的文档。

不适合：双栏（两栏文字会交错混排）；扫描件（不做 OCR）；要保留复杂表格/标题层级。

## 装

```bash
pip install markitdown==0.1.9
# 需要更多格式支持时：pip install 'markitdown[all]'
```

## 用

```bash
markitdown report.docx > out.md
markitdown report.pdf  > out.md
markitdown report.docx -o out.md
cat report.pdf | markitdown
```

## 坑（本机实测）

- **不处理双栏**：两栏文字交错混排，阅读顺序不可用。只适合单栏。
- **不做 OCR**：扫描件输出为空或只有页眉页脚。
- **中文文字层依赖 ToUnicode**：字体映射损坏时同样乱码；先跑文字层探针。
- **结构保留有限**：标题层级、合并单元格、脚注不如 `mineru` / `docling`。

## 上游

https://github.com/microsoft/markitdown

许可证：MIT。
