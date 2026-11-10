---
name: ocrmypdf
description: 给扫描版 PDF 加可搜索文字层，输出新的 PDF。适合扫描件先 OCR 再交给 mineru/docling 做结构解析。
  已有可用文字层的 PDF 不要用（OCR 是负优化）；图片 OCR 用 rapidocr。
license: MPL-2.0
---

# ocrmypdf

## 定位

把**扫描版 PDF** 变成带文字层的可搜索 PDF。它不是结构提取器；正确用法是「先加文字层，再交给 `mineru` / `docling` 做版面与 Markdown」。

不适合：已有可用文字层的 PDF（会把顺序搞乱）；单张图片（用 `rapidocr`）。

## 装

```bash
brew install ocrmypdf tesseract-lang
# 或：pip install ocrmypdf==17.12.1
# 中文需要 tesseract 的 chi_sim 语言包
```

检查语言包：

```bash
tesseract --list-langs | grep -E 'chi_sim|chi_tra|eng'
```

## 用

```bash
ocrmypdf --language chi_sim+eng scan.pdf searchable.pdf
ocrmypdf --language chi_sim+eng --skip-text scan.pdf searchable.pdf
ocrmypdf --language chi_sim+eng --redo-ocr scan.pdf searchable.pdf
```

然后：

```bash
mineru-doc searchable.pdf --pages all -o out.md
```

## 坑（本机实测 / 已知）

- **不要对文字层 PDF 做 OCR**：实测顺序相似度会从 97% 掉到 40%。先跑 `docarbiter` 的文字层探针。
- **输入输出不能同名**：`ocrmypdf in.pdf in.pdf` 会拒绝；用新文件名。
- **`chi_sim` 中文效果弱于 PaddleOCR**：古籍、繁体、竖排、低分辨率扫描件尤其明显；必要时改用 `paddleocr` / `olmocr`。
- **大文件很慢**：按页数线性增长；先 `--pages` 试一小段。
- **`--skip-text` 只处理无文字页**：混合型 PDF（部分页有文字层）用它；整本重做用 `--redo-ocr`。
- **输出是 PDF，不是 Markdown**：不要把它当最终提取结果。

## 上游

https://github.com/ocrmypdf/OCRmyPDF

许可证：MPL-2.0（文件级 copyleft；本仓库只调用，不修改）。
