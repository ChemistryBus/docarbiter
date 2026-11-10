# v0.1.0 — 首个公开预览

`docarbiter` 是一个中英文优先的**文档提取仲裁器**：它不自己造提取器，而是在 MinerU、Docling、liteparse、MarkItDown、RapidOCR、OCRmyPDF、pdfplumber、pdftotext 等工具之间，按“输入类型 / 文字层 / 语言 / 目标产出”做路由，并给出失败后的降级链。

## 包含

- 单一入口技能 `docarbiter`，12 个工具薄壳，18 个工具的 `registry.json`；
- 可执行路由 `scripts/route.py` + `--selftest`（14/14）；
- `install.sh` / `doctor.sh` / `bench.py` / `bench_abstract.py` / `bench_policy.py`；
- 中文 + 英文 README、架构图、许可 FAQ、迁移与 harness 接入文档；
- 合成双语 fixture、真实 CC BY-SA 样本、CID/繁体/双栏/竖排边缘样本；
- 真实高频表分流：复杂表 Docling、坏文字层/符号表 MinerU、简单网格 pdfplumber；
- P0 策略对比、P1 verify 负结果、P2 真实表结论、P3 默认策略、P4 Claude Code/DSH 触发记录。

## 安装

```bash
git clone https://github.com/ChemistryBus/docarbiter.git
cd docarbiter
./scripts/install.sh --profile core
./scripts/doctor.sh --check-conflicts
```

只注册技能、不装工具：

```bash
./scripts/install.sh --skills-only --skills-dir ~/.claude/skills
```

## 验证范围

- macOS arm64 + Python 3.11 实测；
- core 7 包版本按 `requirements-core.lock` 固定；
- 干净 venv + `doctor.sh` 通过；
- Claude Code / DSH 的中英文隐式触发通过；
- Linux 由 CI 验证；Windows 未验证。

## 已知限制

- 不是“所有 PDF 都准”：路由提升来自“不选错工具 + 失败换工具”，不是算法更强；
- 真竖排、真实双栏全文、真实表逐单元格 CER、符号表原字形保真仍未完成；
- 中国食物成分表这类密集双栏书表的页首/页尾仍可能错行，必须抽检；
- `extra` / `full` 未逐项实测；Windows 未验证；
- ZCode / Codex / MiniMax 的触发测试未完成，发布后按 `docs/harness-integration.md` 配置；
- 真实工作区无独立答案 key 的 PDF 只报告一致率/覆盖率，不叫 accuracy。

## 许可

本仓库 MIT，仅含自撰文档、wrapper 与安装脚本，不含上游代码或模型权重。上游工具由用户自行安装，各自保留原许可证。MinerU 的附加条款与 AGPL 工具说明见 `THIRD_PARTY_NOTICES.md`。
