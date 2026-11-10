# Harness-Native Routing vs. docarbiter

> Bottom line first: **a harness can usually discover and invoke skills, but generally lacks deterministic routing by "document type + language + text layer + target output."**
> It relies on the model reading `description` to make a semantic choice; once several similar skills exist, this becomes a competition. `docarbiter` fills in this layer of domain routing policy.

## 1. What Native Capabilities Roughly Are

| Capability | Typical implementation | Deterministic? | Notes |
|---|---|---|---|
| Skill discovery | Scan the skills directory, read `SKILL.md` / frontmatter | Yes | Discovery is deterministic; who gets chosen is not |
| Skill selection | Model reads `description` and decides | **No** | When several descriptions match, it may pick wrong or ask the user |
| Explicit invocation | `/skill-name`, commands, tool names | Yes | Deterministic only when specified by the user or a script |
| Subagent | Independent context + tool set | No | The subagent also chooses tools itself |
| Plugin namespace | `plugin:skill` | Yes (naming) | Reduces name collisions, but does not solve "which one to pick" |
| MCP tool | tool description / tool search | No | With many tools, the same competition occurs |
| Hook | Inject/intercept before and after tool calls | Yes (programmable) | Tightly coupled to the harness, not portable |

Take Claude Code as an example: skills are discovered via the `description` in `SKILL.md`, and the model chooses based on the description and the current task; there is no built-in rule such as "PDF has a text layer → use A, no text layer → use B." The specific implementations of Codex, zcode, and DSH may differ by version, but all four on this machine follow the "skills directory + model selection" model, not a domain router.

## 2. Why Native Selection Is Not Enough

- **It does not understand the document domain.** The model does not know about CID subset fonts, ToUnicode, Chinese OCR models, two-column reading order, or merged table cells; these require probes and rules.
- **There is no fallback chain.** Native selection is one-shot; when the result is unsatisfactory, the model may switch to another tool, or may repeat the same one.
- **Similar skills compete.** When three "PDF extraction" skills all match the description, which one is chosen is not reproducible.
- **Not auditable.** It is hard to answer "why was Marker chosen this time instead of MinerU?"

## 3. What docarbiter Adds

```
Input → classify (format/language) → probe (is the text layer usable?) → route (target output) → spot-check → fallback
```

- **Explicit rules**: the decision table is written in the skill; it can be reviewed and tested.
- **Domain knowledge**: text-layer probes, CID/garbled-text detection, Chinese/English differences, table/scan branches.
- **Fallback chain**: switch in order after a failure, and explain why the switch was made.
- **Cross-harness**: one skill, symlinked into four directories; does not depend on any harness's hooks.
- **Auditable**: the output states "who it routed to, why, and who to switch to after failure."

## 4. Can a Harness Invoke docarbiter Deterministically?

Yes, but the method varies by harness:

- **Explicit invocation**: the user says "use docarbiter", or you create a `/docarbiter` slash command wrapper.
- **Hook**: if the harness supports it, use `PreToolUse` to inject routing hints; the downside is harness coupling and poor portability.
- **Default semantic triggers**: rely on phrases in `description` such as "提取 PDF" / "不确定用哪个" / "结果乱码" (Chinese trigger phrases); this is the current approach and the most stable across harnesses.

This project's choice: **default semantic triggers + optional explicit invocation**. Core logic is not bound to any harness's hook.

### Claude Code Real-World Test (2026-11-10)

- When the old `doc-extract` and `docarbiter` coexisted, both Chinese and English implicit prompts selected `doc-extract`; **no amount of description optimization can beat a similar router.**
- After moving the old `doc-extract` symlink out of `~/.claude/skills`, both Chinese and English triggered `docarbiter` from a neutral `/tmp` directory.
- Tests must run in a neutral directory: in the repository root, the model may directly `Read SKILL.md`, which looks like "not triggered" but is actually being drawn to the file in the cwd.
- Conclusion: **keep only one document-extraction router per harness**; back up first, then disable the old router, then validate. Full log: [`docs/p4-claude-code.md`](p4-claude-code.md).

### Other Harnesses (2026-11-10)

| Harness | Discovery | Implicit trigger | Notes |
|---|---|---|---|
| DSH | Yes | Chinese/English pass (old router temporarily disabled) | With the old router present, both skills were loaded at once; the old state was restored after testing |
| ZCode | Yes (`skills list`) | Not completed | `--prompt` reports `Select a model`; a default model must be set in the TUI/desktop app |
| Codex | Not tested | Not completed | No `codex` CLI executable found |

The DSH result shows again: **coexistence is not "may pick wrong" but may load two decision tables at once**, which is even less auditable than a single choice. Full log: [`docs/p4-other-harnesses.md`](p4-other-harnesses.md).

## 5. What It Does Not Do

- Does not replace the harness's tool invocation, permissions, or sandbox.
- Does not guarantee the model will invoke it first; it only makes "how to choose after invocation" explicit.
- Does not solve all skill-discovery problems; similar tool skills should still be managed in ways other than `--profile full` (see `docs/migration.md`).

## 6. Advice for Other Harness Maintainers

If you build native routing in your own harness, you minimally need:

1. File type / language detection;
2. PDF text-layer probe (character count + replacement characters + CJK coverage);
3. Target-output classification (speed / manuscript / tables / complex tables / RAG / OCR);
4. Tool availability and version checks;
5. Fallback chain and explainable output.

These five steps are the core of `docarbiter`; you can directly reuse the structure of `registry.json` and `docs/architecture.md`.
