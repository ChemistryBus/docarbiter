---
name: marker
description: PDF 转 Markdown/JSON/HTML，基于 Surya 的多语种 OCR 与版面模型。适合有 GPU、要高质量 PDF→MD 的场合。
  无 GPU 先用 mineru/liteparse；只要中文 OCR 用 paddleocr/rapidocr。中文 CER 待实测。
license: Apache-2.0
---

# marker

## 定位

Datalab 的 PDF → Markdown 工具：版面检测、阅读顺序、OCR、表格、公式、图片。底层是 `surya`，支持多语种。输出 Markdown / JSON / HTML，适合批量转换和 RAG 预处理。

不适合：无 GPU 的大文档（慢）；只要快速读文字层（`liteparse`）；中文成稿未实测（先用 `mineru`）。

## 装

```bash
pip install marker-pdf==2.1.0
# 首次运行下载 Surya / Marker 模型
```

> 版本号以 `pip show marker-pdf` 为准；`marker-pdf` 是包名，不是 `marker`。

## 用

```bash
marker_single file.pdf --output_dir out/
```

**待验证**：`marker_single` 的实际参数（输出格式、页码范围、batch 模式）。调用前跑：

```bash
marker_single --help
```

批量模式可能是 `marker` 命令；以本机安装版本为准。

## 坑（已知 / 待实测）

- **GPU 推荐**：CPU 上很慢；首次运行要下载模型。
- **模型权重许可另算**：代码 Apache-2.0；Surya / Marker 模型权重的许可要单独确认，再分发前读上游。
- **中文表现未验证**：Surya 声称多语种，但没有本机中文 CER 数据；不要对外承诺。
- **输出结构因版本而变**：Markdown 的标题层级、表格格式可能和 `mineru` 不同，做 diff 前先固定版本。
- **公式/表格是模型推断**：关键页要人工抽检。

## 上游

https://github.com/datalab-to/marker

许可证：Apache-2.0（模型权重另见上游）。
