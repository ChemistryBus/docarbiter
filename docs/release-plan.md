# GitHub 发布计划（已执行）

> 目标：把当前仓库作为 **首个公开预览版** 发布到 GitHub。
> 2026-11-10：已发布 **v0.1.0**（`main` 初始提交 `5e1f9fd`，CI `validate` 绿，Release 已创建）。
> 本地验证、隐私修复、干净 venv 和提交预演均已完成。

## 0. 发布范围（建议）

| 项 | 建议 | 理由 |
|---|---|---|
| 仓库 | `ChemistryBus/docarbiter` | 已定；短、无重名、和技能同名 |
| 版本 | `v0.1.0` | 已定；首个公开预览，README 状态已同步 |
| 默认 profile | `core` | 8 个工具，已实测；`extra/full` 未逐项验证 |
| 许可 | MIT（本仓库） | 不含上游代码；上游工具由用户自行安装 |
| 不收录 | PyMuPDF / PDF-Extract-Kit / Anthropic `pdf` 技能 | AGPL 或 Proprietary；已在 notices 说明 |
| 平台声明 | macOS arm64 实测；Linux CI 待跑；Windows 未验证 | 发布说明必须写清楚 |
| Harness 声明 | Claude Code / DSH 已测；ZCode / Codex / MiniMax 未完成 | 不把“技能被发现”写成“触发通过” |

## 1. 阻塞项（必须先做）

### 1.1 隐私与可移植性

- [x] `scripts/survey_pdfs.py`：`ROOT_DEFAULT` 改为 `Path.cwd()` / `DOCARBITER_WORKSPACE`，`--dirs` 显式传入
- [x] `scripts/sample_real.py`：新增 `--root`（默认 `Path.cwd()` / `DOCARBITER_WORKSPACE`）
- [x] `docs/p4-other-harnesses.md`：个人绝对路径改成 `~/.zcode/...`
- [x] 全仓 `grep -R '/Users/<username>'` 必须为空（文档示例除外也要改）
- [ ] 确认 `benchmarks/private/` 不会进 Git；检查 `git status` 里没有私有 PDF / survey JSON / policy cache
- [x] 清理 `scripts/__pycache__/`、`.DS_Store`、`blobs/`、`.mineru-service.lock`

### 1.2 许可与声明

- [x] `LICENSE`（MIT）存在且年份/作者正确
- [x] `THIRD_PARTY_NOTICES.md` 覆盖 18 个 registry 工具
- [x] MinerU 附加条款中英文原文 + 在线服务标识义务写清楚
- [x] README 顶部有“不含上游代码”声明
- [x] `skills/` 下没有 `pdf` / `pymupdf` / `pdf-extract-kit`
- [x] 真实 CC BY-SA fixture 的 `SOURCES.md` 署名完整

### 1.3 可复现验证

- [x] `python3 -I scripts/validate.py` 通过
- [x] `python3 -I scripts/route.py --selftest` 通过（14/14）
- [x] 所有 shell `bash -n` 通过
- [x] 所有 Python `py_compile` 通过
- [x] SVG XML 可解析
- [x] 干净 venv 跑 `./scripts/install.sh --profile core --no-skills`，再跑 `doctor.sh`（2026-11-10，core 完整；临时 HOME 无 MinerU 模型属预期）
- [x] 隔离 HOME 跑 `install.sh --skills-only`，确认技能注册与 wrapper
- [ ] Linux CI（GitHub Actions）实际跑绿；当前 workflow 只是写好了，还没在远端跑过

### 1.4 Git / GitHub 机制

- [x] 用户确认 GitHub owner / repo 名 / public 可见性（`ChemistryBus/docarbiter`）
- [x] 设置仓库本地 git 身份：`ChemistryBus <306856809+ChemistryBus@users.noreply.github.com>`
- [x] `git init -b main`
- [x] 在 `/tmp/docarbiter-release-preview` 做提交预演：128 个文件、1.6MB、`benchmarks/private` / `__pycache__` / `blobs` 均 0
- [x] 真实 `git add` 前审查 `git status`：128 文件，私有/缓存 0
- [x] 首次 commit（conventional commit，f40b18c）
- [x] 创建远端仓库并 `git push -u origin main`
- [x] GitHub Actions `validate` 跑绿（25s）
- [x] 打 tag `v0.1.0`
- [x] 创建 Release notes
- [x] 发布后 fresh clone + validate + route selftest 再验一次

## 2. 发布说明必须写的边界

- 中文/英文都覆盖，但不是“所有 PDF 都准”；真实工作区无答案 key 的文档只做一致性/覆盖率，不叫 accuracy。
- 固定工具不是万能的；路由提升来自“不选错工具 + 失败换工具”，不是算法更强。
- 表格：复杂合并表 Docling、坏文字层/符号表 MinerU、简单网格 pdfplumber；密集双栏书表仍可能行错位。
- 真竖排、真实双栏全文、真实表逐单元格 CER、符号表字形保真仍未完成。
- `extra/full` 未逐项实测；Windows 未验证；Linux 只以 CI 为准。
- Harness：Claude Code / DSH 已测；ZCode / Codex / MiniMax 未完成，发布后按 `docs/harness-integration.md` 配。

## 3. 不阻塞发布、但要写进 Known Limitations

- Linux x86_64 / Windows 的真实安装体验（CI 只覆盖最小验证）
- `--profile extra` 的 12 工具逐项 CER
- Marker / Surya / olmOCR / Camelot 等扩展层
- 真实双栏论文全文 CER（目前只有 BERT abstract）
- 真竖排全量、繁简混排
- 真实表逐单元格 CER；中国食物成分表这类密集双栏表的页首/页尾错位
- ZCode / Codex / MiniMax 的触发测试

## 4. 建议执行顺序

1. **先做 1.1 + 1.2**（隐私/许可），这是公开仓库的硬门槛。
2. **再做 1.3**（本地验证 + 干净 venv）；失败就修，不带病发布。
3. **确认 owner/repo/版本**，再 `git init` / commit / push。
4. **看 GitHub Actions**；绿了再打 tag / Release。
5. **fresh clone 复验**；最后再对外说“已发布”。

## 5. 需要用户确认的事

1. ✅ GitHub owner / repo：**ChemistryBus/docarbiter**（已确认）
2. ✅ 版本：**v0.1.0**（已确认）
3. P4 内部测试文档是否公开：`docs/p4-claude-code.md` / `docs/p4-other-harnesses.md` 含本机备份路径与 harness 状态。建议**保留但改成 `~` 相对路径**，让用户知道哪些没测；也可以发布前移除。
4. 发布说明是否明确写“ZCode / Codex / MiniMax 未完成，发布后按文档配置”？建议写，避免过度承诺。

## 6. 发布门禁

只有同时满足以下条件才执行 `git push` / tag：

- [ ] 全仓无个人绝对路径、无私有文件、无密钥
- [ ] `validate.py` / `route.py --selftest` / shell / py_compile / SVG 全绿
- [ ] 干净 venv core 安装 + doctor 通过
- [ ] GitHub Actions 在默认分支跑绿
- [ ] README 中英文、LICENSE、THIRD_PARTY_NOTICES 一致
- [ ] Release notes 含 Known Limitations
- [ ] 用户明确确认发布
