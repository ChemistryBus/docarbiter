# 可靠性验收记录

> 环境：macOS 26 / Apple M2 Pro / 16GB / Python 3.11.11
> 原则：所有安装/覆盖测试都在 `/tmp` 隔离 HOME 或独立 venv 里做；不碰真实 `~/.claude`。

## 1. 隔离 HOME + `--skills-only`

```bash
rm -rf /tmp/docarbiter-clean-home
mkdir -p /tmp/docarbiter-clean-home/.claude/skills
HOME=/tmp/docarbiter-clean-home ./scripts/install.sh \
  --skills-only --skills-dir /tmp/docarbiter-clean-home/.claude/skills
```

结果：

- wrapper 写入 `/tmp/docarbiter-clean-home/.local/bin/`；
- `docarbiter/SKILL.md` symlink 指向仓库；
- 没有安装 Python 包，没有改真实 HOME。

`HOME=/tmp/docarbiter-clean-home ./scripts/doctor.sh`：core 14 项全 OK；`~/.mineru/models` 缺失是预期（临时 HOME）。

## 2. 抓到的真 bug（已修）

在隔离 HOME 下 `install.sh` 曾报：

```
./scripts/install.sh: line 136: resolved�: unbound variable
```

原因：`set -u` 下，`$resolved，` 和 `$target（` 里的全角标点被 Bash 当作变量名的一部分；变量未定义就直接退出。已改成 `${resolved}` / `${target}`。

这个 bug 用 `bash -n` 测不出来，只有真实执行到那一行才暴露。

## 3. 冲突与回滚

### 双路由检测

在隔离 HOME 里同时放：

- `docarbiter`（本仓库）
- 假 `doc-extract/SKILL.md`
- 假 `mineru/SKILL.md`

`HOME=... ./scripts/doctor.sh --check-conflicts` 输出：

```
router      docarbiter doc-extract
conflict:mineru  WARN  ... 同时有工具技能与 docarbiter
dual-router      WARN  docarbiter 与旧 doc-extract 同时存在；建议只保留一个
```

### `--force` 备份

```bash
HOME=... ./scripts/install.sh --skills-only --skills-dir ... --force
```

结果：原 `SKILL.md` 备份为 `SKILL.md.bak.<timestamp>`，再建 symlink；不加 `--force` 时跳过并警告。

## 4. 路由自测

```bash
python3 -I scripts/route.py --selftest
```

当前 **13/13 通过**，覆盖：

- 中文文字层、扫描件、CID / 无 ToUnicode、繁体
- 交错双栏、真实 CC BY 论文
- 英文连字符、表格、无框线表格
- 空 PDF、损坏 PDF
- 含空格 + 中文的文件路径

损坏 PDF 现在返回 `probe-error` 并走 MinerU 兜底，不会假装成可读文字层。

## 5. 真实 CC BY 双栏 abstract CER

BERT（ACL Anthology N19-1423，CC BY 4.0）2 页 excerpt，abstract 从 ACL HTML 取，rapidfuzz 部分对齐后只算 abstract：

| 工具 | CER | no-punct CER |
|---|---:|---:|
| MinerU | 0.0044 | 0.0000 |
| pdftotext | 0.0066 | 0.0012 |
| liteparse | 0.0066 | 0.0000 |
| Docling | 0.0066 | 0.0012 |
| markitdown | 0.7303 | 0.7344 |
| pdfplumber | 0.7303 | 0.7344 |

结论：真实双栏 abstract 上，MinerU 最好；markitdown / pdfplumber 是阅读顺序问题，不是标点。

## 6. 完整干净 venv 安装

在 `/tmp/docarbiter-clean-venv`（Python 3.11）里执行：

```bash
HOME=/tmp/docarbiter-clean-home2 PATH="/tmp/docarbiter-clean-venv/bin:$PATH" \
  ./scripts/install.sh --profile core --no-skills
```

结果：**exit 0**。venv 约 2.0GB，core 版本全部对版（benchmark 的 `rapidfuzz` 不在 core 里；跑 `bench_abstract.py` 会自动用 stdlib `difflib` fallback，想要稳定的 high-fidelity 对齐就 `pip install -r requirements-dev.lock`）：

```
mineru 4.1.7
docling 2.149.0
liteparse 2.18.0
markitdown 0.1.9
rapidocr 3.10.0
ocrmypdf 17.12.1
pdfplumber 0.11.10
```

`HOME=/tmp/docarbiter-clean-home2 PATH="/tmp/docarbiter-clean-venv/bin:/tmp/docarbiter-clean-home2/.local/bin:$PATH" ./scripts/doctor.sh`：core 14 项全 OK；`~/.mineru/models` 缺失是预期（临时 HOME，首次运行才下载）。

### 发现并修复的第二个真问题

第一次干净安装时，`install.sh` 执行 `brew install poppler tesseract tesseract-lang qpdf`，把 **poppler 从 26.08.0 升到 26.11.0**，并升级了 pcre2/glib/cairo 等依赖。这不是我们想要的副作用。

修复：已安装的 formula 直接跳过，缺失才装；macOS 加 `HOMEBREW_NO_AUTO_UPDATE=1`；Linux apt 加 `--no-upgrade`。

修复后在同一个 venv 重跑：日志显示

```
brew poppler already installed; skip (no upgrade)
brew tesseract already installed; skip (no upgrade)
brew tesseract-lang already installed; skip (no upgrade)
brew qpdf already installed; skip (no upgrade)
```

exit 0。

## 7. 工作区真实 PDF 抽样（只读）

- 工作区共 **8,466** 个 PDF，按 SHA-256 去重后 **8,444** 个（114MB）。
- 随机 48 个：全部可用文字层；47 英文 / 1 中文；0 个同名源文件。
- 中文文件名样本 24 个：全部可用文字层；18 英文 / 6 中文内容。
- 真实 4 文件 smoke（2 页）：三个工具都成功；顺序 CER 0.05–0.65，但**字符袋差异只有 0.1%–2.6%**，多数是阅读顺序/分段差异。
- **发现 MinerU 真实风险**：某中文文章第 1 页 MinerU 比 pdftotext 少约 35%（2,299→1,480），拉丁字符 1,257→675，第 2 页几乎一致；疑似丢英文摘要/作者信息。已写入 `docs/gotchas.md` 第 18 条。
- 明细：`benchmarks/private/survey*.md`、`survey*.json`、`real-smoke.md`（gitignored；不保存正文、不上传）。

## 8. 仍未完成

- **真实双栏全文 CER**：目前只有 abstract；全文需要更完整的答案对齐。
- **harness 真实触发**：`route.py` 已自测，但 `docarbiter` 还没在 Claude Code / Codex / zCode / DSH 里实际触发；需要重启 harness 或装进真实技能目录。
- **真竖排 / 任意无框线表格**：前者所有工具都差；后者有 default/text 策略取舍，Camelot 未装。

## 9. CI 覆盖

`.github/workflows/validate.yml` 现在会在 Ubuntu 上跑：

- `install.sh --skills-only` 隔离 HOME 冒烟测试（能抓住 `set -u` + 非 ASCII 变量名这类 bug）；
- `validate.py`；
- `route.py --selftest`（先装 poppler）；
- 所有 shell `bash -n`、Python `py_compile`、SVG XML。

## 10. 复现清单

```bash
python3 -I scripts/route.py --selftest
python3 -I scripts/validate.py
python3 -I scripts/bench_abstract.py --out /tmp/docarbiter-abstract
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

> 这些测试依赖本机已装的 core 工具和 `pdftotext`；干净 venv 安装完成后再跑一次 `doctor.sh`。
