---
name: mineru
description: 中文 PDF 成稿提取的首选。把 PDF 转成带标题层级、段落合并和页码锚点的结构化 Markdown。
  当要引用、要成稿、要追溯页码时使用。只要快速预览用 liteparse；Office/音视频用 docling。
license: Apache-2.0 (upstream) / MIT (this shell)
---

# mineru

## 定位

本合集里**中文 PDF 成稿**的默认选项。输出有章节标题（`## Heading`）、合并后的段落、图注和页码锚点，适合要引用、要校对、要落盘的场合。

不适合：只要快速看一眼（用 `liteparse`）；纯 Office / 音视频（用 `docling`）；干净文字层的复杂表格（`docling` 的单元格阅读顺序更稳）。

## 装

```bash
pip install mineru==4.1.7
# 首次运行下载模型（basic 层约 860MB）到 ~/.mineru/models
mineru config set parse_server.local.managed_tier basic
mineru config set parse_server.local.mode managed
```

本合集提供封装 `mineru-doc`（见 `scripts/wrappers/mineru-doc.sh`），自动拉起本地服务并处理引擎冷启动。

## 用

```bash
mineru-doc file.pdf --pages all -o out.md
mineru-doc file.pdf --pages 99-110 -o chapter.md
mineru-doc file.pdf --tier flash          # 免服务，纯文字快速预览
```

## 坑（本机实测）

- **CWD 污染**：`mineru server start` 会在调用目录生成 `blobs/`（实测约 13MB）和 `.mineru-service.lock`。封装已固定 `cd "$HOME/.mineru"`；不要绕过封装直接起服务。
- **引擎冷启动 8–15 秒**：首次直接 `mineru parse` 会报 `No basic/standard/advanced engine available`。封装会重试 10 次 × 8 秒。
- **`--tier flash` 只有纯文字**：没有标题层级、图注、页码锚点，不要用于成稿。
- **首次运行要下模型**：无网络或磁盘不足会失败；先跑 `mineru-kit models show` 检查。
- **`pipefail` + `grep -q` 会 SIGPIPE 误判**：封装已改用 `case` 匹配。
- **坏文字层/符号表优先 MinerU**：DRIs 2023 第 65 页的 ●/○ 概览表，文字层被坏字体破坏（●→`.`、○→`。`），MinerU 能恢复中文名，并把 ●/○ 区分为“空/O”；但**不保留原符号**，要人工抽检。
- **干净多行单元格会被交错**：GB 28050 第 6 页的“单不饱和脂肪（或单不饱和脂肪酸）”被读成“单单不不饱饱和…”；这类表用 `docling`。

## 上游

https://github.com/opendatalab/MinerU

许可证：Apache-2.0 + 附加条款（商业门槛、在线服务标识义务）。原文见仓库根目录 `THIRD_PARTY_NOTICES.md`。
