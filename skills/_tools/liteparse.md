---
name: liteparse
description: 最快的 PDF 文字层提取（实测 0.04–0.09 秒/页），可选词级坐标和字体信息。
  当 PDF 有文字层、只要快速读正文时使用。要干净段落和页码锚点改用 mineru；扫描件不适用。
license: Apache-2.0
---

# liteparse

## 定位

本合集里**最快**的选项。适合「先快速看看里面写了什么」、批量检索、取词级坐标。上游只提供 Python 包，没有 CLI；本合集提供封装 `liteparse-doc`。

不适合：扫描件（没有文字层）；要成稿（段落会被页眉打断，标题层级会判错）。

## 装

```bash
pip install liteparse==2.18.0
# 本合集提供封装 liteparse-doc（见 scripts/wrappers/liteparse-doc.sh）
```

## 用

```bash
liteparse-doc file.pdf --pages 99-110
liteparse-doc file.pdf              # 全部页
liteparse-doc file.pdf --json       # 词级坐标 + 字体名/字号
```

`--json` 输出每页的 `text_items`：每个词的 `x/y/w/h`、字体名、字号。这是本工具相对其他工具的独有能力。

## 坑（本机实测）

- **默认开 OCR 会卡约 123 秒**：上游默认 `ocr_enabled=True`，会尝试从 GitHub 下载 tessdata，失败后长时间阻塞。封装已强制 `ocr_enabled=False`；要 OCR 用 `--ocr`，但先配好 tessdata。
- **段落被页眉打断**：页眉文字（如 `D. Ylli et al.`）会插进段落中间。
- **标题层级判错**：同级标题可能给成 `###` 和 `####`。
- **封装不支持 `--help`**：它会把 `--help` 当文件名，抛 `FileNotFoundError`；无参数运行才会打印用法。
- **中文文字层待 CER 复测**：英文样本快且准，不代表无 ToUnicode 的中文 PDF 可用。

## 上游

https://github.com/run-llama/liteparse

许可证：Apache-2.0。
