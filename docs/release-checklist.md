# 发布前检查清单

> 状态：**已发布 v0.1.0**（2026-11-10）。`main` 初始提交 `5e1f9fd`；GitHub Actions `validate` 已通过；Release 已创建。
> 发布计划与执行记录见 [`docs/release-plan.md`](release-plan.md)。
> 当前进度（2026-11-10）：11 篇双语合成样本 + 4 篇真实 CC BY-SA 维基样本 + CID/繁体/交错双栏/真竖排边缘样本 + 6 个文字层工具 + 2 条 OCR 路径 + 干净 venv 安装 + 工作区 8,444 个真实 PDF 只读抽样（48+24 样本、4 文件 smoke）+ P0 policy benchmark（22 个有答案文档）+ 5 份真实高频表（WS/T 578.1、GB 28050、DRIs 2023、GB 2760、中国食物成分表）已完成；P1 verify 负结果不发布、P2 真实表分流完成（Docling/MinerU/pdfplumber）、P3 默认策略已定、Claude Code P4 真实触发完成（旧 doc-extract 已备份停用）、DSH headless 触发通过并永久切换（全局 .agents 旧路由已备份）、ZCode 技能发现通过但 CLI 需先设默认模型、Codex 未找到 CLI、MiniMax 未测试；真竖排全量、真实双栏全文 CER、真实表逐单元格 CER、扩展层工具尚未完成。
> 本清单的目标：把「能跑」变成「可复现、可解释、可维护」。

## 0. 发布门槛（先定）

- [x] 版本号：`v0.1.0`（首个公开预览，已确认）
- [ ] 支持范围写清楚：macOS arm64 实测；Linux x86_64 待验证；Windows 未验证
- [ ] Python 版本：3.10 / 3.11 / 3.12；3.11.11 实测
- [ ] 默认安装 profile：`core`；`extra` / `full` 标注「未逐项实测」
- [ ] 不发布任何 AGPL / Proprietary 工具代码或模型
- [ ] `README.md`（中文）与 `README.en.md`（英文）内容一致
- [ ] 所有「待测」项在发布说明里可见，不藏

## 1. 干净环境安装

- [x] macOS arm64 干净 venv：`/tmp/docarbiter-release-venv`，Python 3.11（2026-11-10 重跑）
- [x] `./scripts/install.sh --profile core --no-skills` 成功（core 7 包对版：MinerU 4.1.7 / Docling 2.149.0 / liteparse 2.18.0 / MarkItDown 0.1.9 / RapidOCR 3.10.0 / OCRmyPDF 17.12.1 / pdfplumber 0.11.10）
- [x] `install.sh` 不升级已装 Homebrew formula（poppler 等 `skip (no upgrade)`）
- [x] 隔离 HOME + `install.sh --skills-only`：wrapper + symlink 创建成功
- [x] `doctor.sh` 在隔离 HOME 退出码 0，core 无 MISSING（MinerU 模型未下载属预期）
- [x] `install.sh --force` 备份 + symlink；无 `--force` 时跳过并警告
- [ ] `./scripts/install.sh --profile extra` 的失败项逐条记录（不要求全绿）
- [ ] Linux x86_64（Docker/VM）跑同一套；记录差异
- [ ] Windows / WSL 至少记录「未验证」或已知问题
- [ ] 路径含空格、中文、括号时，wrapper 与 `bench.py` 仍可用
- [ ] 无网络环境：给出预下载模型/离线安装说明（至少 MinerU / Docling）

> 2026-11-10 干净安装时 PyPI 直连很慢，使用清华镜像完成；版本仍由 `requirements-core.lock` 固定，镜像只影响下载速度。发布流程不依赖镜像。

## 2. 中英文语料

### 中文

- [ ] 正常文字层 PDF
- [ ] CID 子集字体 / 无 ToUnicode
- [ ] 扫描件（300dpi / 150dpi 各一）
- [x] 双栏交错（合成，内容流逐行交错；markitdown 未复现失败，pdfplumber 失败）
- [x] 真实 CC BY 双栏论文 abstract CER（BERT, ACL N19-1423；markitdown/pdfplumber 73%）
- [ ] 真实双栏论文全文 CER（不只 abstract）
- [x] 有框线 / 合并单元格 cell accuracy（pdfplumber 1.000；合并语义仍需人工抽检）
- [x] 无框线表格：default 0 表；text 策略 1.000/0.917，但合并掉到 0.667/0.583；需按页选策略并抽检
- [x] 真实高频表结构与抽检（WS/T 578.1、GB 28050、DRIs 2023、GB 2760、中国食物成分表；Docling/MinerU/pdfplumber 分流）
- [ ] 真实表逐单元格 CER（当前只有结构与抽检，不能对外叫 accuracy）
- [ ] 符号表（●/○）保真：当前 MinerU/Docling 都只保留二元状态，不保留原字形
- [x] 繁体（`zh-traditional`）
- [ ] 繁简混排
- [ ] 真竖排（vertical writing mode、从右到左换列；当前只有一字一行模拟）
- [x] 脚注 / 图注（合成）

### 英文

- [ ] 正常文字层 PDF
- [ ] 双栏论文
- [ ] 表格页
- [ ] 连字符换行 / 引号 / em dash
- [ ] 扫描件
- [ ] 页眉页脚干扰

### 答案与指标

- [ ] 每份样本有独立答案（源文本 / 人工校对 / CC BY-SA 源文本）
- [ ] **没有**用 `pdftotext` 输出当答案
- [ ] CER 归一化规则固定（NFC、去空白、保留标点）
- [ ] 报告每页 CER、median、IQR、**最差页**
- [ ] 冷启动与热启动分开
- [ ] 记录工具版本、语料 commit、机器

## 3. 工具覆盖

### core（默认 8 个）

- [ ] MinerU：中英文各 ≥ 2 份样本
- [ ] Docling：Office / HTML / PDF / chunks / LaTeX
- [ ] liteparse：文字层 PDF；标点归一化行为已记录
- [ ] MarkItDown：单栏；双栏失败未复现（合成），真实双栏待测；扫描件不支持
- [ ] RapidOCR：中文图片 / 截图
- [ ] OCRmyPDF：扫描件 → 可搜索 PDF → MinerU
- [ ] pdfplumber：表格 / 坐标；交错双栏 60%–68%（已记录）
- [ ] pdftotext：基线 / 文字层探针

### extra / optional

- [ ] PaddleOCR：中文 OCR / PP-Structure
- [ ] Marker：GPU / CPU 各一次；中文 CER
- [ ] Unstructured：多格式分区；中文语言码
- [ ] olmOCR：GPU；中文 CER
- [ ] Surya / Camelot / Tesseract / qpdf / pypdf / pdfminer.six：至少 smoke test
- [ ] 未装/失败的工具在 `doctor.sh` 里标 optional，不阻塞 core

## 4. 调度器测试

- [ ] 中文文字层 PDF → 期望 `liteparse` / `mineru`
- [ ] 中文扫描件 → 期望 `ocrmypdf` → `mineru`
- [ ] 英文双栏 PDF → 期望 `mineru` / `docling`，不是 `markitdown`
- [ ] 简单网格表格 → 期望 `pdfplumber`（`--goal table`）
- [ ] 复杂合并表头/多行单元格 → 期望 `docling`（`--goal table-structure`）
- [ ] 扫描/坏文字层表格 → 期望 `mineru`
- [ ] Office → 期望 `docling`
- [ ] 图片 → 期望 `rapidocr`
- [ ] 用户明确指定工具 → 不经过调度器
- [ ] 工具缺失 → 给安装命令 + 降级方案，不静默失败
- [ ] 结果不满意 → 降级链可解释
- [ ] 不把敏感文档默认发到云 API

## 5. Harness 兼容

本机四个 harness：Claude Code / Codex / zcode / DSH。

- [x] `docarbiter` 在 Claude Code 被正确发现（2026-11-10，`docs/p4-claude-code.md`）
- [x] Claude Code 上 description 能触发中文/英文「提取 PDF」「转 Markdown」「该用哪个工具」（Haiku，中立目录）
- [x] Claude Code 不同时激活旧的 `doc-extract`（已备份停用；其他 harness 未动）
- [x] DSH 已永久切换：旧 `doc-extract` 备份停用，中文/英文 headless 只触发 `docarbiter`（2026-11-10）
- [x] DSH 同时处理了全局 `~/.agents/skills/doc-extract`；Codex / ZCode 的旧路由副本保留，未被破坏
- [ ] ZCode 能发现 `docarbiter`，但 `--prompt` 被 “Select a model” 卡住；需 TUI/桌面端设默认模型
- [ ] Codex 未找到 CLI 可执行文件，无法做非交互触发
- [ ] MiniMax 有 `~/.minimax/skills`，未找到无头入口；发布后按 `docs/harness-integration.md` 接
- [ ] `--profile full` 注册 12 个工具技能后，无重名冲突
- [x] `doctor.sh --check-conflicts` 能检测同名技能与双路由（隔离 HOME + 本机已跑）
- [x] 旧 `doc-extract` 的共存 / 替换 / 回滚步骤已在 Claude Code / DSH 验证（`docs/migration.md`）
- [x] README 已说明「harness 原生调度 vs docarbiter」（见 `docs/harness-routing.md`）
- [x] 不自动删除用户旧路由器；替换必须用户确认（本次已确认，只移动 symlink）
- [x] 卸载/回滚步骤写进文档（`docs/p4-claude-code.md`、`docs/migration.md`）

## 6. 合规审计

- [x] `THIRD_PARTY_NOTICES.md` 覆盖所有安装的工具（validate 检查 18 个）
- [x] MinerU 附加条款英文 + 中文原文都在
- [x] `skills/` 下没有 `pdf` / `pymupdf` / `pdf-extract-kit`
- [x] `install.sh` 不自动装 AGPL（只给链接/说明）
- [x] 商业云 API 不在默认路径
- [x] `README` 顶部有「不含上游代码」声明
- [x] 许可证分组与 `registry.json` 一致
- [x] 模型权重来源（RapidOCR / MinerU / Marker / Surya / olmOCR）有说明
- [x] 如果未来做在线服务，MinerU 标识义务已写进 README

## 7. 安全与隐私

- [x] 不硬编码密钥 / token（2026-11-10 扫描无命中）
- [ ] 默认不把文件上传到云
- [ ] `bench.py` 用 `python3 -I`，不被 cwd 的 `json.py` 之类劫持
- [ ] 不执行 PDF 里的脚本 / 不打开外部链接
- [x] 用户自有文件放 `benchmarks/private/`，`.gitignore` 生效
- [x] 日志不打印文档正文片段（或明确说明会打印）
- [x] 全仓无个人绝对路径 `/Users/<name>`；脚本用 `--root` / `DOCARBITER_WORKSPACE`
- [x] `.gitignore` 覆盖 `benchmarks/private/`、`blobs/`、`.mineru-service.lock`

## 8. 文档

- [ ] `README.md` 中文：问题、适用人群、图、安装、评测、许可、路线图
- [ ] `README.en.md` 英文：与中文内容一致
- [ ] 配图：`docs/assets/overview-zh.svg` / `overview-en.svg` 在 GitHub 正常渲染
- [ ] 快速开始 5 分钟内可跑通
- [ ] 常见失败（缺工具 / 没 GPU / 网络失败）有排查路径
- [ ] `docs/architecture.md` 解释「工具很多也能调度」
- [ ] `docs/gotchas.md` 每条可复现
- [ ] `docs/benchmarks.md` 有「不要信我的数字」声明
- [ ] `docs/licensing-faq.md` 回答 MinerU / AGPL / GPL
- [ ] 截图或图里不出现真实用户文档内容

## 9. CI 与仓库卫生

- [x] `python3 -I scripts/validate.py` 通过
- [x] `python3 -I scripts/route.py --selftest` 通过（14/14，含空 PDF / 损坏 PDF / 空格+中文路径）
- [x] 所有 shell `bash -n` 通过
- [x] 所有 Python `py_compile` 通过
- [ ] CI 在 push / PR 上跑 validate + route selftest（workflow 已写好，待远端）
- [x] CI 增加 `install.sh --skills-only` 隔离 HOME 冒烟测试（能抓 set -u 问题）
- [x] 没有 `__pycache__` / `.DS_Store` / 大文件（仓库 3.1MB）
- [ ] `registry.json` 与 `skills/_tools/` 一致
- [ ] `requirements-core.lock` 与实测版本一致
- [ ] `requirements-extra.lock` 标注「未逐项实测」

## 10. 发布机制

- [ ] 用户明确同意后才 `git init` / commit / push
- [ ] 远端仓库名确认（`ChemistryBus/docarbiter`）
- [ ] 默认分支 `main`
- [ ] tag `v0.1.0`；release notes 列已知限制
- [ ] 发布说明里写：macOS 实测、Linux/Windows 未验证、extra 未逐项实测
- [ ] 发布说明里写：不收录 Anthropic `pdf`、PyMuPDF、PDF-Extract-Kit
- [ ] 发布后跑一次 `doctor.sh` + 两页 demo，确认远端版本可复现

## 11. 签收

| 项目 | 负责人 | 日期 | 结果 |
|---|---|---|---|
| 中文语料 / CER | | | |
| 英文语料 / CER | | | |
| 许可审计 | | | |
| Harness 兼容 | | | |
| 文档 / 图 | | | |
| 发布确认 | | | |
