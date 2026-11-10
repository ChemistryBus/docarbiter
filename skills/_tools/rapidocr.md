---
name: rapidocr
description: 轻量中文图片 OCR。适合单张图片、截图、扫描页的识别。
  整本扫描 PDF 先用 ocrmypdf 加文字层；要版面/表格结构用 paddleocr。
license: Apache-2.0
---

# rapidocr

## 定位

基于 PaddleOCR PP-OCR 模型的轻量 OCR，中文识别强、安装比 PaddleOCR 小得多。适合单张图片、截图、扫描页。本机实测中文置信度 0.999（模型自报，不等于 CER）。

不适合：整本扫描 PDF（要逐页转图再调用）；需要版面分析、阅读顺序、表格结构（用 `paddleocr` 的 PP-Structure 或 `docling`）。

## 装

```bash
pip install rapidocr==3.10.0
# 首次运行会下载/加载 ONNX 模型
```

## 用

```python
from rapidocr import RapidOCR

engine = RapidOCR()
result = engine("image.png")
print(result.txts)     # 识别文本列表
print(result.scores)   # 每行置信度
```

批量：先把你自己的图片列表循环传入；不要一次塞整本 PDF。

## 坑（本机实测 / 已知）

- **只做 OCR，不做版面**：输出是按检测框排的文本行，不是阅读顺序完整的 Markdown。
- **PDF 要先转图**：`pdftoppm -png -r 300 file.pdf page`，再逐页 OCR；否则没有输入。
- **置信度不是准确率**：0.999 是模型自报分数，中文 CER 要另测。
- **模型许可另算**：代码 Apache-2.0，模型来自 PaddleOCR / 百度，见上游 `MODEL_LICENSES.md`。
- **复杂版式会乱序**：多栏、表格、竖排不要直接信输出顺序。

## 上游

https://github.com/RapidAI/RapidOCR

许可证：Apache-2.0（模型权重另有来源说明）。
