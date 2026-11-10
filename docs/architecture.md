# Architecture: Why "many tools" can still be routed

> Related files: `skills/docarbiter/SKILL.md` (router), `registry.json` (machine-readable registry), `skills/_tools/*.md` (thin shells).
> Diagrams: `docs/assets/overview-zh.svg` / `overview-en.svg`.

## 1. Three-layer separation

```
        ┌────────────────────────────────────────────────────┐
        │ 1. Router  skills/docarbiter/SKILL.md              │
        │ Classify → Probe → Route → Fallback                │
        │ Rules only, no per-tool details                    │
        └─────────────────────┬──────────────────────────────┘
                              │ reads
        ┌─────────────────────▼──────────────────────────────┐
        │ 2. Registry  registry.json                         │
        │ id / tier / languages / input_types /              │
        │ output_types / best_for / avoid_when /             │
        │ install / upstream / status                        │
        └─────────────────────┬──────────────────────────────┘
                              │ maps to
        ┌─────────────────────▼──────────────────────────────┐
        │ 3. Thin shell  skills/_tools/<id>.md               │
        │ Purpose / Install / Use / Pitfalls / Upstream      │
        │ 15–40 lines each, one tool per file                │
        └────────────────────────────────────────────────────┘
```

**Rules are written only once.** The router does not need to know the full commands of 18 tools; it only needs to know "what input, what goal, which class of tool" and "how to fall back when a tool is missing." Tool details live in the thin shells; the tool list lives in the registry.

## 2. Why not "one top-level skill per tool"

By default, installing registers only one skill: `docarbiter`. The reasons:

- If each of the 18 tools registered its own top-level skill, all 18 `description` fields would match "extract PDF" and the agent would pick at random; this is exactly the problem the project aims to solve.
- The more top-level skills there are, the higher the cost of name collisions/conflicts/maintenance (N tools → O(N²) cross-references).
- A default single entry point + optional registration via `--profile full` balances "no confusion for ordinary users" and "direct invocation for experts."

## 3. How to add a 19th tool

### Case A: Fits an existing category (recommended)

For example, adding a "Chinese table OCR" tool; it still belongs to the "table / scan" category.

1. Add a record under `tools` in `registry.json` (copy an existing entry and fill in `id`, `tier`, `languages`, `input_types`, `output_types`, `best_for`, `avoid_when`, `install`, `upstream`, `status`).
2. Add a thin shell at `skills/_tools/<id>.md` (Purpose / Install / Use / Pitfalls / Upstream).
3. **Do not change the router** unless its priority is higher than the current first choice. If priority is higher, change only the corresponding row in the decision table + the fallback chain.
4. Run `python3 -I scripts/validate.py` and `./scripts/doctor.sh --check-conflicts`.

### Case B: Introduce a new category

For example, adding a "subtitles / audio transcription" category.

1. Add an input-type branch line to `docarbiter`'s classification logic.
2. Add a "goal → first choice → alternatives" row to the decision table.
3. Add an entry to the fallback chain.
4. The rest is the same as Case A.

### Case C: The license does not allow default installation

For example, AGPL tools.

- Add only to `excluded` in `registry.json`, or add to `tools` but with `tier: "excluded"` + `install` saying "do not install automatically."
- Provide links and reasons in `THIRD_PARTY_NOTICES.md`.
- The router may "suggest the user install it themselves," but must not install it automatically.

## 4. The router's decision order

```
1. Did the user explicitly name a tool?
   Yes → call it directly (at most one sentence about risk), done.
2. Input format?
   PDF / Office / image / audio-video / HTML / EPUB...
3. Language? (Chinese / English / mixed)
   For Chinese, also check CJK coverage; for English, check replacement characters and garbled ratio.
4. Is the PDF text layer usable?
   Usable → route by goal
   Scanned / garbled → OCR or MinerU, then return to 4
5. Target output?
   Speed / finished manuscript / plain text / tables (simple grid / complex merges) / RAG / LaTeX / OCR
6. Is the tool installed?
   Not installed → give the install command + a fallback using installed tools
7. Select the tool; on failure or unsatisfactory result → fallback chain
```

## 5. Availability checks

The router cannot route to a tool that is not installed. How to check:

```bash
command -v mineru-doc
command -v liteparse-doc
command -v docling
python3 -c "import rapidocr"
python3 -c "import pdfplumber"
```

When a tool is missing:

1. Give the exact install command (pinned version);
2. Give an alternative path using an installed tool;
3. Do not fail silently.

## 6. Anti-patterns

- ❌ Copying the full routing table into every thin shell → rule drift.
- ❌ Registering every tool as a top-level skill by default → back to "a bowl of porridge."
- ❌ Hardcoding the full commands of 18 tools in the router → every upstream parameter change requires editing the router.
- ❌ Sorting only by star count → Chinese scanned documents get routed to unsuitable tools.
- ❌ Treating `pdftotext` as the answer → the benchmark becomes circular.
- ❌ Auto-installing AGPL / auto-calling cloud APIs → licensing and privacy risk.

## 7. Executable mirror

`scripts/route.py` is an executable version of the same decision table:

```bash
python3 -I scripts/route.py file.pdf --goal manuscript
python3 -I scripts/route.py --selftest
```

It runs the same PDF probe (character count / CJK / control characters / garbled ratio) and outputs `intended` / `selected` / `reason` / `command` / `fallback`. Differences:

- `docarbiter` is for agents; it can ask clarifying questions, read thin shells, and explain fallbacks;
- `route.py` is for scripts / CI / non-agent users; its output is deterministic and assertable.

`--selftest` is engineering acceptance: text layer / scan / CID / traditional Chinese / interleaved two-column / real CC BY / tables / complex tables; routing must match expectations. CI runs it.

## 8. Extension checklist

- [ ] `registry.json` parses and `id` values are unique
- [ ] core / extra tools each have a corresponding thin shell
- [ ] Each thin shell has "Purpose / Install / Use / Pitfalls / Upstream"
- [ ] A new tool's Chinese/English status is marked "tested" or "pending," with no overclaiming
- [ ] The fallback chain for a new category is written
- [ ] `THIRD_PARTY_NOTICES.md` is updated
- [ ] `validate.py` passes
- [ ] `doctor.sh --check-conflicts` passes
