---
name: paddleocr
description: 中文原生 OCR 与 PP-Structure 版面/表格分析。适合中文扫描件、复杂版式、表格单元格。
  轻量单图 OCR 用 rapidocr；整本成稿用 mineru。依赖 paddlepaddle，体积大。
license: Apache-2.0
---

# paddleocr

## 定位

中文 OCR 的事实标准之一：PP-OCR 系列模型 + PP-Structure 版面/表格分析。RapidOCR 复用了它的模型，但 PaddleOCR 本体提供更完整的版面、表格、方向分类能力。

不适合：只想装一个轻量 OCR（用 `rapidocr`）；没有 GPU/内存受限；只要整本 PDF 成稿（先试 `mineru`）。

## 装

```bash
pip install paddleocr paddlepaddle          # CPU
# GPU：按 PaddlePaddle 官方文档安装对应 CUDA 版本
```

> 安装体积大、依赖多；先确认磁盘和 Python 版本。版本号以第一次实测为准，不在此处硬编码。

## 用

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang="ch")
result = ocr.predict("image.png")     # v3 API；旧版可能是 ocr.ocr(...)
```

CLI 与 PP-Structure 的参数因版本而异：

```bash
paddleocr --help
```

**待验证**：`paddleocr ocr -i image.png`、PP-Structure 的 CLI/API 入口。调用前先跑 `--help` 或读官方 quickstart，不要凭记忆猜。

## 坑（已知 / 待实测）

- **依赖重**：paddlepaddle + 模型，安装和首次加载都慢；不适合临时小任务。
- **版本 API 漂移**：2.x 的 `ocr.ocr()` 与 3.x 的 `ocr.predict()` 不同；按安装版本确认。
- **中文置信度不是 CER**：模型自报分数不能当准确率。
- **表格/版面要 PP-Structure**：只跑 OCR 不会给你阅读顺序和单元格。
- **模型许可**：代码 Apache-2.0；模型权重来自 PaddleOCR/百度，再分发时保留来源说明。

## 上游

https://github.com/PaddlePaddle/PaddleOCR

许可证：Apache-2.0。
