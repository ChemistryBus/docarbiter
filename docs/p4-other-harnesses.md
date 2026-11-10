# P4: Codex / ZCode / DSH Trigger Acceptance (2026-11-10)

> Scope: DSH is permanently switched; ZCode / Codex / MiniMax get skill-discovery/entry checks.
> Bottom line first (evening of 2026-11-10): **DSH fully passed; MiniMax top-level fully passed (Chinese and English); ZCode top-level fully passed (Chinese and English); Codex conditionally passed (explicit/minimal-set usable, full skill set limited by capacity).**
> See [`docs/p4-claude-code.md`](p4-claude-code.md) for the Claude Code test.

## Results matrix

| Harness | Skill directory | Old doc-extract | docarbiter discovered | Implicit trigger | Conclusion |
|---|---|---|---|---|---|
| Claude Code | `~/.claude/skills` | Backed up and disabled | Yes | Chinese/English pass | Complete (see p4-claude-code) |
| DSH | `~/.dsh/skills` + `~/.agents/skills` | Backed up and disabled | Yes | Chinese/English pass | **Permanently switched** (old route can be rolled back) |
| ZCode | `~/.zcode/skills` + `~/.agents/skills` | Moved away → `~/.local/share/docarbiter-migration-backup/` | Yes | **Fully passed** | Top-level new session; both Chinese and English route docarbiter → MinerU |
| Codex | `~/.codex/skills` | Moved away | Yes (recognizes both symlinks and regular files) | **Conditionally passed** | Implicit fails with all 620 skills; implicit passes with a 17-skill minimal set; explicit invocation passes |
| MiniMax | `~/.agents/skills` + `~/.codex/skills` (observed) | Moved away | Yes | **Fully passed** | Top-level new session; both Chinese and English route docarbiter → MinerU; whole-directory symlink works |

## Evening retest (ZCode / MiniMax / Codex)

- **ZCode (fully passed)**: In a top-level new session after restarting the app, both Chinese and English call `docarbiter`, routing to MinerU; old `doc-extract` moved away.
- **MiniMax (fully passed)**: In a top-level new session after restart, both Chinese and English implicit prompts call `docarbiter`, routing to MinerU; the old router moved away. Key finding: MiniMax scans `~/.agents/skills` and also watches `~/.codex/skills`; it skips "directory + SKILL.md file symlinks" and recognizes only real files or **whole-directory symlinks**.
- **Codex (conditionally passed)**: `~/.codex/skills/docarbiter/SKILL.md` installed, old `doc-extract` moved away. Diagnosis: symlinks are recognized; in the full environment with 619–620 skills, 371–380 do not enter the model-visible list and their descriptions are removed, so implicit prompts bypass `docarbiter`; with a minimal skill set (17 skills, keeping only `docarbiter` + `mineru`) implicit prompts actually read `docarbiter` and route to MinerU; explicitly saying "use docarbiter" also passes in the full environment. **Conclusion: the install is correct; implicit triggering is affected by Codex skill capacity.**
- **Installer fix**: `install.sh` now automatically uses whole-directory symlinks for `~/.agents/skills`, `~/.codex/skills`, and `~/.minimax/skills`; Claude/DSH/ZCode keep file symlinks. Use `--skill-mode dir|file` to force. Existing `~/.local/bin` wrappers are first backed up as `.bak.<timestamp>`.

## DSH: tested and passing

### 1) Old route present

After installing `~/.dsh/skills/docarbiter/SKILL.md`, use this Chinese sample prompt:

```bash
cd /tmp/p4-dsh
dsh --profile headless "我有个中文扫描版 PDF，想提取成带页码的 Markdown。应该用哪个工具？只路由，不提取。"
```

The DSH session log shows it **called two skills at the same time**:

```
skill {"name":"docarbiter"}
skill {"name":"doc-extract"}
```

The final route is still correct (MinerU), but this is dual-route coexistence: the context is occupied by two decision tables at once, and the behavior is not auditable.

### 2) Old route temporarily disabled

After moving `~/.dsh/skills/doc-extract` to `~/.dsh/skill-backups/`, the same prompt calls only:

```
skill {"name":"docarbiter"}
bash  {"command":"for t in mineru-doc ...; do command -v $t; done"}
```

Both Chinese and English route correctly to **MinerU**, and local tool availability was checked.

### 3) Permanent switch (done)

DSH reads not only `~/.dsh/skills` but also `~/.agents/skills`. Moving only `~/.dsh/skills/doc-extract` is not enough; English prompts still load the old route from the global directory. The permanent switch did three things:

1. `~/.dsh/skills/doc-extract` → `~/.dsh/skill-backups/doc-extract.20261110-125933`;
2. Global `~/.agents/skills/doc-extract` → `~/.agents/skill-backups/doc-extract.20261110-130247`;
3. The Codex / ZCode old-route symlinks were repointed to that global backup so as not to break them.

After the switch, rerun Chinese and English:

```
skill {"name":"docarbiter"}
bash  {"command":"command -v mineru-doc ..."}
```

Both runs call only `docarbiter`, never `doc-extract`, and route to MinerU. **DSH is currently single-entry docarbiter.**

Rollback:

```bash
mv ~/.dsh/skill-backups/doc-extract.20261110-125933 ~/.dsh/skills/doc-extract
mv ~/.agents/skill-backups/doc-extract.20261110-130247 ~/.agents/skills/doc-extract
# Then point the Codex / ZCode doc-extract symlinks back to ~/.agents/skills/doc-extract
```

## ZCode: discovery passes, triggering blocked by model selection

The ZCode app's CLI is inside the bundle, not on PATH:

```bash
node /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs --help
```

`skills list` discovers the skill installed at `~/.zcode/skills/docarbiter`:

```
- docarbiter (user/zcode)
  ~/.zcode/skills/docarbiter/SKILL.md
```

But `--prompt` reports:

```
Error: Select a model before sending a message
```

The CLI help has no `--model`; model selection lives in the TUI / desktop configuration. Trying `/model GLM-5.2` as a prompt prefix still reports the same error. **ZCode implicit triggering was not completed this round and is not counted as passing.**

ZCode scans both `~/.zcode/skills` and `~/.agents/skills`. During the DSH switch, the global `~/.agents/skills/doc-extract` was moved away and `~/.zcode/skills/doc-extract` was pointed at the backup; so ZCode now has only the `user/zcode` old route. Switching ZCode in future only requires backing up `~/.zcode/skills/doc-extract` and installing docarbiter.

## Codex: conditionally passed (skill capacity limit)

On the evening of 2026-11-10, retested with Codex CLI `0.167.0-alpha.3.2` / `gpt-6-astra` in two environments:

| Environment | Visible skills | docarbiter visible | Implicit trigger | Explicit trigger |
|---|---:|---|---|---|
| Full | 619–620 | Yes | **Failed** (371–380 skills do not enter the model-visible list, descriptions removed) | **Passed** |
| Minimal set | 17 | Yes | **Passed** (actually reads `docarbiter/SKILL.md`) | Passed |

Conclusion:

- **Installation and symlinks are fine**; Codex recognizes file symlinks and regular files.
- The problem in the full environment is **skill capacity/indexing**: many skills do not enter the model-visible list, `docarbiter`'s description is trimmed off, and implicit prompts naturally bypass it.
- **Explicit invocation works**: saying "use the docarbiter skill" reads it and routes.
- To make implicit triggering reliable: trim the Codex skill directory, or use a minimal skill set; do not mix 600+ skills with docarbiter and expect it to be selected reliably.

On this machine, `~/.codex/skills/docarbiter/SKILL.md` is currently a regular file; the old `doc-extract` has been moved away.

## Conclusions

1. **A harness should keep only one document-extraction router.** Claude Code already proved the old route wins; DSH proved the old route makes the model load two skills at once. ZCode also discovers the old route twice from two directories.
2. **DSH is permanently switched.** With the old route disabled and the global `.agents` old route moved out, both Chinese and English trigger only docarbiter; the old-route copies for Codex / ZCode are preserved and unbroken.
3. **ZCode fully passed.** In a top-level new session, both Chinese and English call docarbiter and route to MinerU; the CLI's `--prompt` still needs a default model, but the app top level does not depend on it.
4. **Codex conditionally passed.** Installation and symlinks are correct; implicit triggering is squeezed out by capacity with all 620 skills, passes with a 17-skill minimal set, and explicit invocation passes. Usage recommendation: trim the skill directory, or explicitly say "use docarbiter".
5. **MiniMax fully passed.** At the top level both Chinese and English hit docarbiter; it skips file symlinks and requires a whole-directory symlink.

## Reproduction commands

```bash
# DSH (Chinese sample prompt)
dsh --profile headless "我有个中文扫描版 PDF，想提取成带页码的 Markdown。该用哪个工具？只路由。"

# ZCode skill discovery
node /Applications/ZCode.app/Contents/Resources/glm/zcode.cjs skills list | grep -A2 docarbiter

# Inspect the actual tool calls in the DSH session
# ~/.dsh/sessions/--private-tmp-p4-dsh-final-zh--/*/session.jsonl.zstd
# zstd -dc ... | grep '"name":"skill"'
```

## Outstanding

- [x] DSH permanent switch (2026-11-10, old-route backup can roll back)
- [x] ZCode top-level new-session triggering (Chinese/English docarbiter → MinerU)
- [x] Codex symlink/capacity diagnosis (explicit passes; minimal-set implicit passes; full-set implicit affected by capacity)
- [x] MiniMax top-level new-session triggering (Chinese/English docarbiter → MinerU)
- [ ] Real-file routing / actual end-to-end extraction for the three harnesses
