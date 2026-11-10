# Reliability acceptance record

> Environment: macOS 26 / Apple M2 Pro / 16GB / Python 3.11.11
> Principle: all install/override tests run in an isolated HOME under `/tmp` or a separate venv; the real `~/.claude` is never touched.

## 1. Isolated HOME + `--skills-only`

```bash
rm -rf /tmp/docarbiter-clean-home
mkdir -p /tmp/docarbiter-clean-home/.claude/skills
HOME=/tmp/docarbiter-clean-home ./scripts/install.sh \
  --skills-only --skills-dir /tmp/docarbiter-clean-home/.claude/skills
```

Results:

- the wrapper is written to `/tmp/docarbiter-clean-home/.local/bin/`;
- `docarbiter/SKILL.md` is a symlink to the repository;
- no Python packages were installed, and the real HOME was not modified.

`HOME=/tmp/docarbiter-clean-home ./scripts/doctor.sh`: all 14 core checks OK; the missing `~/.mineru/models` is expected (temporary HOME).

## 2. A real bug caught (fixed)

Under the isolated HOME, `install.sh` once reported:

```
./scripts/install.sh: line 136: resolved�: unbound variable
```

Cause: under `set -u`, the full-width punctuation in `$resolved，` and `$target（` was treated by Bash as part of the variable name; since the variable was undefined, it exited immediately. Changed to `${resolved}` / `${target}`.

This bug cannot be caught with `bash -n`; it only appears when that line actually executes.

## 3. Conflicts and rollback

### Dual-router detection

In the isolated HOME, place all of:

- `docarbiter` (this repository)
- a fake `doc-extract/SKILL.md`
- a fake `mineru/SKILL.md`

`HOME=... ./scripts/doctor.sh --check-conflicts` outputs:

```
router      docarbiter doc-extract
conflict:mineru  WARN  ... 同时有工具技能与 docarbiter
dual-router      WARN  docarbiter 与旧 doc-extract 同时存在；建议只保留一个
```

### `--force` backup

```bash
HOME=... ./scripts/install.sh --skills-only --skills-dir ... --force
```

Result: the original `SKILL.md` is backed up as `SKILL.md.bak.<timestamp>`, then the symlink is created; without `--force` it skips with a warning.

## 4. Routing self-test

```bash
python3 -I scripts/route.py --selftest
```

Currently **13/13 pass**, covering:

- Chinese text layer, scans, CID / no ToUnicode, traditional Chinese
- interleaved two-column, real CC BY papers
- English hyphenation, tables, borderless tables
- empty PDFs, corrupt PDFs
- file paths containing spaces + Chinese

Corrupt PDFs now return `probe-error` and fall back to MinerU instead of pretending to be a readable text layer.

## 5. Real CC BY two-column abstract CER

BERT (ACL Anthology N19-1423, CC BY 4.0) 2-page excerpt, abstract taken from ACL HTML, partially aligned with rapidfuzz, then CER computed only on the abstract:

| Tool | CER | no-punct CER |
|---|---:|---:|
| MinerU | 0.0044 | 0.0000 |
| pdftotext | 0.0066 | 0.0012 |
| liteparse | 0.0066 | 0.0000 |
| Docling | 0.0066 | 0.0012 |
| markitdown | 0.7303 | 0.7344 |
| pdfplumber | 0.7303 | 0.7344 |

Conclusion: on a real two-column abstract, MinerU is best; markitdown / pdfplumber suffer from reading-order problems, not punctuation.

## 6. Full clean venv install

In `/tmp/docarbiter-clean-venv` (Python 3.11):

```bash
HOME=/tmp/docarbiter-clean-home2 PATH="/tmp/docarbiter-clean-venv/bin:$PATH" \
  ./scripts/install.sh --profile core --no-skills
```

Result: **exit 0**. The venv is about 2.0GB, and all core versions match the lockfile (benchmark's `rapidfuzz` is not in core; running `bench_abstract.py` automatically falls back to the stdlib `difflib`, and for stable high-fidelity alignment run `pip install -r requirements-dev.lock`):

```
mineru 4.1.7
docling 2.149.0
liteparse 2.18.0
markitdown 0.1.9
rapidocr 3.10.0
ocrmypdf 17.12.1
pdfplumber 0.11.10
```

`HOME=/tmp/docarbiter-clean-home2 PATH="/tmp/docarbiter-clean-venv/bin:/tmp/docarbiter-clean-home2/.local/bin:$PATH" ./scripts/doctor.sh`: all 14 core checks OK; the missing `~/.mineru/models` is expected (temporary HOME; downloaded on first run).

### A second real problem found and fixed

On the first clean install, `install.sh` ran `brew install poppler tesseract tesseract-lang qpdf`, upgrading **poppler from 26.08.0 to 26.11.0** and upgrading dependencies such as pcre2/glib/cairo. That was an unwanted side effect.

Fix: skip formulas that are already installed and install only missing ones; add `HOMEBREW_NO_AUTO_UPDATE=1` on macOS; add `--no-upgrade` for Linux apt.

After the fix, rerunning in the same venv showed:

```
brew poppler already installed; skip (no upgrade)
brew tesseract already installed; skip (no upgrade)
brew tesseract-lang already installed; skip (no upgrade)
brew qpdf already installed; skip (no upgrade)
```

exit 0.

## 7. Real workspace PDF sampling (read-only)

- The workspace has **8,466** PDFs in total, **8,444** after SHA-256 deduplication (114MB).
- Random 48: all have a usable text layer; 47 English / 1 Chinese; 0 source files with the same name.
- 24 Chinese-filename samples: all have a usable text layer; 18 English / 6 Chinese content.
- Real 4-file smoke (2 pages per file): all three tools succeeded; order CER 0.05–0.65, but the **bag-of-characters difference is only 0.1%–2.6%**, mostly reading-order/paragraph differences.
- **Found a real MinerU risk**: on page 1 of a Chinese article, MinerU has about 35% less than pdftotext (2,299→1,480), Latin characters 1,257→675, while page 2 is almost identical; suspected loss of the English abstract/author information. Written up as item 18 in `docs/gotchas.md`.
- Details: `benchmarks/private/survey*.md`, `survey*.json`, `real-smoke.md` (gitignored; body text is not saved, nothing is uploaded).

## 8. Still not done

- **Real two-column full-text CER**: currently only the abstract; full text requires a more complete answer alignment.
- **Real harness trigger**: `route.py` is self-tested, but `docarbiter` has not actually been triggered in Claude Code / Codex / zCode / DSH; it requires restarting the harness or installing into the real skills directory.
- **True vertical writing / arbitrary borderless tables**: the former is poor with all tools; the latter has a default/text strategy trade-off, and Camelot is not installed.

## 9. CI coverage

`.github/workflows/validate.yml` now runs on Ubuntu:

- `install.sh --skills-only` isolated-HOME smoke test (catches bugs like `set -u` + non-ASCII variable names);
- `validate.py`;
- `route.py --selftest` (poppler installed first);
- `bash -n` on all shell scripts, Python `py_compile`, SVG XML.

## 10. Reproduction checklist

```bash
python3 -I scripts/route.py --selftest
python3 -I scripts/validate.py
python3 -I scripts/bench_abstract.py --out /tmp/docarbiter-abstract
python3 -I scripts/bench_tables.py --out /tmp/docarbiter-tables
```

> These tests depend on the core tools and `pdftotext` already installed on this machine; run `doctor.sh` once more after the clean venv install completes.
