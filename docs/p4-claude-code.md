# P4: Claude Code Real Trigger Acceptance (2026-11-10)

> Scope: **Claude Code** only. Codex / zcode / DSH untouched, still keeping the old `doc-extract`.
> Model: `claude -p --model haiku`, non-interactive `stream-json`; this is a low-cost trigger test and should be retested on Sonnet / Opus before release.
> Install: `~/.claude/skills/docarbiter/SKILL.md` symlinked to this repository; the old `doc-extract` symlink has been moved to `~/.claude/skill-backups/doc-extract.20261110-121227`, and the source directory `~/.agents/skills/doc-extract` is untouched.

## Results

| Test | Old doc-extract | Actual call | Conclusion |
|---|---|---|---|
| Skill discovery | Present | — | New session can list `docarbiter` and returns YES |
| Chinese implicit trigger | Present | `Skill: doc-extract` | **Old router wins**, docarbiter not called |
| English implicit trigger | Present | `Skill: doc-extract` | **Old router wins**, regardless of language |
| Chinese implicit trigger | Disabled | `Skill: docarbiter` | Correctly routes to `mineru`, gives the `mineru-doc` command |
| English implicit trigger (`/tmp` neutral directory) | Disabled | `Skill: docarbiter` | Correctly routes to `mineru`; both Chinese and English descriptions trigger |
| Chinese + real file path (`zh-scan.pdf`) | Disabled | `Skill: docarbiter` + Bash probe | Probe `chars=0 cjk=0` → correctly routes to `mineru`, and checked `mineru-doc` / `ocrmypdf` availability |
| English implicit trigger (repository root) | Disabled | Did not call Skill; directly Read `SKILL.md` | Routing is still correct, but **not a clean skill trigger**; a cwd inside the repository makes the model switch to reading the file |

## Conclusions

1. **Coexistence is unacceptable.** As long as the old `doc-extract` is still in `~/.claude/skills`, implicit prompts in either language choose the old router; no amount of description on docarbiter can win.
2. **After disabling the old route, docarbiter takes over.** Chinese and English both trigger in the `/tmp` neutral directory; given a real file path, it runs the text-layer probe first (`chars=0`), then correctly routes the scan → MinerU, and checks whether `mineru-doc` / `ocrmypdf` are available.
3. **Tests must run in a neutral directory.** Running `claude -p` at the repository root makes the model `ls` / `Read SKILL.md` first; it looks like "no trigger" but is actually attraction to files in the cwd. Real user projects will not behave this way, but acceptance testing must avoid this bias.
4. **Old skills are not deleted automatically.** This time only the symlink was moved to `~/.claude/skill-backups/`; the source directory and other harnesses are preserved and can be restored at any time.
5. **Triggering is model-dependent behavior.** Passing on `haiku` does not mean passing on Sonnet / Opus; retest before release, and do not treat "one successful trigger" as a stability guarantee.

## Reproduction

```bash
# 0) Confirm docarbiter is discovered (Chinese sample prompt)
claude -p "当前可用技能里有没有 docarbiter？有就 YES。" \
  --model haiku --output-format json

# 1) Chinese implicit trigger (should run in a neutral directory)
cd /tmp
claude -p "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由，不提取。" \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill,Read"

# 2) English implicit trigger
claude -p "I have a scanned Chinese PDF and need page-anchored Markdown. Which tool? Use your routing skill; route only." \
  --model haiku --output-format stream-json --verbose --allowedTools "Skill"

# 3) Check whether Skill was called
#    Look for "name":"Skill" and "skill":"docarbiter" in the stream-json
```

## Restoring the old route (Claude Code)

```bash
mv ~/.claude/skill-backups/doc-extract.20261110-121227 ~/.claude/skills/doc-extract
```

After restoring, Claude Code will compete with `docarbiter` for triggering again; this is a **rollback**, not a recommended state.

## Outstanding

- [ ] Retest Chinese/English triggering on Sonnet / Opus
- [x] Real-file routing (`benchmarks/fixtures/zh-scan.pdf`, routing only, no extraction)
- [ ] Actual end-to-end extraction test with a real file (this round only routed)
- [ ] Equivalent tests for Codex / zcode / DSH (untouched this round)
- [ ] Final disposition of the old `doc-extract` in Claude Code (currently backed up and disabled, not deleted)
