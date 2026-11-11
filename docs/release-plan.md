# GitHub Release Plan (executed)

> Goal: publish the current repository to GitHub as the **first public preview**.
> 2026-11-10: **v0.1.0 — First Public Preview** published (`main` initial commit `5e1f9fd`, CI `validate` green, Release created).
> 2026-11-11: Published **v0.1.1 — Harness Compatibility Patch** (install compatibility, wrapper backup, update mechanism, harness docs).
> Local verification, privacy fixes, clean venv, and commit rehearsal are all complete.

## 0. Release scope (recommended)

| Item | Recommendation | Rationale |
|---|---|---|
| Repository | `ChemistryBus/docarbiter` | Decided; short, unique, same name as the skill |
| Version | `v0.1.0` | Decided; first public preview, README status synced |
| Default profile | `core` | 8 tools, tested; `extra/full` not individually verified |
| License | MIT (this repository) | No upstream code included; upstream tools are installed by the user |
| Not included | PyMuPDF / PDF-Extract-Kit / Anthropic `pdf` skill | AGPL or Proprietary; explained in the notices |
| Platform statement | macOS arm64 tested; Linux CI pending; Windows not verified | Must be stated clearly in the release notes |
| Harness statement | Claude Code / DSH tested; ZCode / Codex / MiniMax not complete | Do not write "skill discovered" as "triggering passed" |

## 1. Blockers (must be done first)

### 1.1 Privacy and portability

- [x] `scripts/survey_pdfs.py`: `ROOT_DEFAULT` changed to `Path.cwd()` / `DOCARBITER_WORKSPACE`, `--dirs` passed explicitly
- [x] `scripts/sample_real.py`: new `--root` option (defaults to `Path.cwd()` / `DOCARBITER_WORKSPACE`)
- [x] `docs/p4-other-harnesses.md`: personal absolute paths changed to `~/.zcode/...`
- [x] Repo-wide `grep -R '/Users/<username>'` must return nothing (documentation examples must be changed too)
- [ ] Confirm `benchmarks/private/` never enters Git; check `git status` shows no private PDFs / survey JSON / policy cache
- [x] Clean up `scripts/__pycache__/`, `.DS_Store`, `blobs/`, `.mineru-service.lock`

### 1.2 Licensing and statements

- [x] `LICENSE` (MIT) exists with correct year/author
- [x] `THIRD_PARTY_NOTICES.md` covers the 18 registry tools
- [x] MinerU additional terms in both Chinese and English + online-service attribution obligation stated clearly
- [x] README has a "no upstream code included" statement at the top
- [x] No `pdf` / `pymupdf` / `pdf-extract-kit` under `skills/`
- [x] Real CC BY-SA fixture `SOURCES.md` attribution is complete

### 1.3 Reproducible verification

- [x] `python3 -I scripts/validate.py` passes
- [x] `python3 -I scripts/route.py --selftest` passes (all checks; 24 at the time of writing)
- [x] All shell scripts pass `bash -n`
- [x] All Python files pass `py_compile`
- [x] SVG XML is parseable
- [x] Clean venv runs `./scripts/install.sh --profile core --no-skills`, then `doctor.sh` (2026-11-10, core complete; temporary HOME without MinerU models is expected)
- [x] Isolated HOME runs `install.sh --skills-only`, confirming skill registration and wrapper
- [ ] Linux CI (GitHub Actions) actually passes; the workflow is only written, not yet run remotely

### 1.4 Git / GitHub mechanics

- [x] User confirmed GitHub owner / repo name / public visibility (`ChemistryBus/docarbiter`)
- [x] Local git identity set for the repository: `ChemistryBus <306856809+ChemistryBus@users.noreply.github.com>`
- [x] `git init -b main`
- [x] Commit rehearsal in `/tmp/docarbiter-release-preview`: 128 files, 1.6MB, `benchmarks/private` / `__pycache__` / `blobs` all 0
- [x] Reviewed `git status` before the real `git add`: 128 files, private/cache 0
- [x] First commit (conventional commit, f40b18c)
- [x] Created remote repository and `git push -u origin main`
- [x] GitHub Actions `validate` passes (25s)
- [x] Tag `v0.1.0`
- [x] Create release notes
- [x] After release, re-verify with fresh clone + validate + route selftest

## 2. Boundaries the release notes must state

- Both Chinese and English are covered, but not "all PDFs are accurate"; documents in real workspaces without answer keys are checked only for consistency/coverage, not called accuracy.
- A fixed tool is not a silver bullet; the routing gain comes from "not choosing the wrong tool + switching tools on failure", not from a stronger algorithm.
- Tables: complex merged tables → Docling, bad text layer/symbol tables → MinerU, simple grids → pdfplumber; dense two-column book tables may still have row misalignment.
- True vertical writing and symbol-table glyph fidelity are still incomplete. Real-table per-cell CER is done for WS/T 578.1 p8 and GB 28050 p6 only; full-text two-column CER is done for BERT full, the Cell Perspective, and ResNet only (Cell figure-text caveat; Nature flagship needs a full-article scope); the other real tables remain structure/spot checks.
- `extra/full` not individually tested; Windows not verified; Linux is only covered by CI.
- Harness: Claude Code / DSH / ZCode / MiniMax tested; Codex conditional (large catalog). See `docs/harness-integration.md`.

## 3. Not release blockers, but must go into Known Limitations

- Real install experience on Linux x86_64 / Windows (CI covers only minimal verification)
- Per-tool CER for the 12 tools in `--profile extra`
- Extension layer such as Marker / Surya / olmOCR / Camelot
- Full-text CER on more papers and layouts (BERT, Cell Perspective, and ResNet are done; Cell figure-text caveat; Nature flagship needs a full-article scope)
- Full true vertical writing, mixed traditional and simplified Chinese
- Per-cell CER on the remaining real tables and other editions (WS/T 578.1 p8 and GB 28050 p6 are done); first/last page misalignment in dense two-column tables such as the China Food Composition Tables
- Triggering tests for ZCode / Codex / MiniMax

## 4. Recommended execution order

1. **Do 1.1 + 1.2 first** (privacy/licensing); these are hard gates for a public repository.
2. **Then 1.3** (local verification + clean venv); fix failures — do not ship broken.
3. **Confirm owner/repo/version**, then `git init` / commit / push.
4. **Watch GitHub Actions**; tag / Release only after it is green.
5. **Re-verify with a fresh clone**; only then announce "released" publicly.

## 5. Items requiring user confirmation

1. ✅ GitHub owner / repo: **ChemistryBus/docarbiter** (confirmed)
2. ✅ Version: **v0.1.0** (confirmed)
3. Whether to publish the internal P4 test docs: `docs/p4-claude-code.md` / `docs/p4-other-harnesses.md` contain local backup paths and harness status. Recommendation: **keep them but change paths to `~`-relative**, so users know what is untested; they can also be removed before release.
4. Should the release notes explicitly state "ZCode / Codex / MiniMax incomplete, configure after release per the docs"? Recommended, to avoid over-promising.

## 6. Release gate

Only run `git push` / tag when all of the following hold:

- [ ] No personal absolute paths, no private files, no secrets anywhere in the repo
- [ ] All green: `validate.py` / `route.py --selftest` / shell / py_compile / SVG
- [ ] Clean venv core install + doctor passes
- [ ] GitHub Actions passes on the default branch
- [ ] README (both languages), LICENSE, and THIRD_PARTY_NOTICES are consistent
- [ ] Release notes include Known Limitations
- [ ] User explicitly confirms the release
