---
name: olmocr
description: AllenAI 的 VLM 扫描件 OCR 工具包，面向高精度长文档。需要 GPU。
  无 GPU 用 ocrmypdf/rapidocr；中文 CER 待实测。适合低质量扫描、复杂版式。
license: Apache-2.0
---

# olmocr

## 定位

基于视觉语言模型的 OCR 工具包，面向扫描件、低质量 PDF、复杂版式。输出 Markdown/JSON，保留阅读顺序。适合「OCR 引擎搞不定」的硬样本。

不适合：无 GPU；要快速/轻量；有可用文字层的 PDF（先走文字层工具）。

## 装

```bash
pip install olmocr==0.4.27
# 需要 CUDA/GPU 与模型下载；按官方 README 配置
```

> 版本号以 `pip show olmocr` 为准；GPU 驱动、PyTorch/CUDA 版本要匹配。

## 用

```bash
olmocr ./localworkspace --markdown --pdfs file.pdf
```

**待验证**：`olmocr` CLI 的 workspace 结构、`--markdown` / `--pdfs` 参数、批量模式。调用前跑：

```bash
olmocr --help
```

## 坑（已知 / 待实测）

- **GPU 必需**：CPU 上不可用或不现实；显存要求按模型大小确认。
- **首次下载模型**：体积大、耗时长；离线环境要预下载。
- **中文表现未验证**：VLM 多语种能力不等于中文 CER；不要对外承诺。
- **成本高**：比传统 OCR 慢很多；只对硬样本用，不要全量默认。
- **输出可能包含模型幻觉**：关键数字/表格必须人工核对。

## 上游

https://github.com/allenai/olmocr

许可证：Apache-2.0（模型权重另见上游）。
