---
name: pdftotext
description: Poppler 的纯文字提取命令行，速度最快、无依赖。适合文字层探测、纯文字检索、作为其他工具的基线。
  要结构/表格/成稿用 mineru 或 docling；扫描件不适用。
license: GPL-2.0/3.0 (upstream) / MIT (this shell)
---

# pdftotext

## 定位

Poppler 自带的命令行工具，把 PDF 文字层抽成纯文本。它**不做 OCR、不做版面、不做表格**，但速度极快（约 0.01 秒），是文字层探测和纯文字检索的基线。

不适合：要标题层级、段落、表格、页码锚点；扫描件；CID / 无 ToUnicode 的 PDF（会乱码）。

## 装

```bash
brew install poppler
# Debian/Ubuntu: sudo apt install poppler-utils
```

## 用

```bash
pdftotext file.pdf -                         # 默认：能按栏排序
pdftotext -layout file.pdf -                 # 保留物理并排布局
pdftotext -f 99 -l 101 file.pdf out.txt      # 指定页范围
pdftotext -f 1 -l 3 file.pdf - | wc -c       # 文字层探测（粗）
```

文字层探针不要只看字符数；用 `docarbiter` 里的 `bad_ratio` / `cjk` 版本。

## 坑（本机实测 / 已知）

- **对文字层 PDF 做 OCR 是负优化**；反过来，`pdftotext` 对扫描件输出为空，不要误判为「文件损坏」。
- **CID / 无 ToUnicode 会输出乱码或替换符**：字符数可能很多，但内容不可用。
- **`-layout` 与默认行为不同**：默认按阅读顺序/栏排序；`-layout` 保留物理位置，需要自己分栏读。
- **不做表格结构**：表格会变成空格分隔的文本行；简单网格/坐标用 `pdfplumber`，复杂合并表用 `docling`，扫描表用 `mineru`。
- **许可证是 GPL**：本仓库只调用系统命令，不修改、不再分发；不要把二进制打包进 MIT 发行物。

## 上游

https://poppler.freedesktop.org/

许可证：GPL-2.0-only OR GPL-3.0-only（系统工具，只调用）。
