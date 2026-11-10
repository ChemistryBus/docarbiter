#!/usr/bin/env python3
"""Validate skill frontmatter and compliance invariants. Stdlib only.

Run: python3 -I scripts/validate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

REQUIRED_TOOLS = [
    "MinerU",
    "Docling",
    "liteparse",
    "MarkItDown",
    "RapidOCR",
    "OCRmyPDF",
    "pdfplumber",
    "Poppler",
    "qpdf",
    "pypdf",
    "pdfminer.six",
    "Camelot",
    "Tesseract",
    "PaddleOCR",
    "Marker",
    "Surya",
    "Unstructured",
    "olmOCR",
]

errors: list[str] = []


def parse_frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def check_skill(path: Path, expected_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return
    for key in ("name", "description"):
        if not fm.get(key):
            errors.append(f"{path.relative_to(ROOT)}: missing frontmatter key '{key}'")
    if fm.get("name") and fm["name"] != expected_name:
        errors.append(
            f"{path.relative_to(ROOT)}: name '{fm['name']}' != expected '{expected_name}'"
        )
    if len(fm.get("description", "")) < 20:
        errors.append(f"{path.relative_to(ROOT)}: description is too short for routing")


def main() -> int:
    if not SKILLS.is_dir():
        errors.append("skills/ directory is missing")
        print("\n".join(errors))
        return 1

    orchestrator = SKILLS / "docarbiter" / "SKILL.md"
    if not orchestrator.exists():
        errors.append("skills/docarbiter/SKILL.md is missing")
    else:
        check_skill(orchestrator, "docarbiter")

    shells = sorted((SKILLS / "_tools").glob("*.md"))
    if len(shells) < 12:
        errors.append(f"skills/_tools/: expected >= 12 tool shells, found {len(shells)}")
    for path in shells:
        check_skill(path, path.stem)
        if "## 上游" not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)}: missing '## 上游' section")

    forbidden = [p for p in SKILLS.rglob("*") if p.name.lower() in {"pymupdf", "pdf"}]
    if forbidden:
        errors.append(f"skills/: forbidden AGPL/proprietary directories: {forbidden}")

    registry_path = ROOT / "registry.json"
    registry_tools = 0
    if not registry_path.exists():
        errors.append("registry.json is missing")
    else:
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"registry.json: invalid JSON: {exc}")
            registry = {}
        registry_entries = registry.get("tools", [])
        registry_tools = len(registry_entries)
        ids = [t.get("id") for t in registry_entries]
        if len(ids) != len(set(ids)):
            errors.append("registry.json: duplicate tool ids")
        required_keys = {
            "id", "name", "tier", "license", "languages", "roles",
            "input_types", "output_types", "best_for", "avoid_when",
            "install", "upstream",
        }
        for tool in registry_entries:
            missing = sorted(required_keys - set(tool))
            if missing:
                errors.append(f"registry.json[{tool.get('id', '?')}]: missing {missing}")
            if tool.get("tier") in {"core", "extra"}:
                shell = SKILLS / "_tools" / f"{tool.get('id')}.md"
                if not shell.exists():
                    errors.append(f"registry.json[{tool.get('id')}]: missing {shell.relative_to(ROOT)}")

    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for tool in REQUIRED_TOOLS:
        if tool not in notices:
            errors.append(f"THIRD_PARTY_NOTICES.md: missing '{tool}'")

    readme_checks = {
        "README.md": ("docarbiter", "English", "CER", "MinerU"),
        "README.zh-CN.md": ("docarbiter", "中文", "CER", "MinerU"),
    }
    for name, needles in readme_checks.items():
        path = ROOT / name
        if not path.exists():
            errors.append(f"{name} is missing")
            continue
        readme = path.read_text(encoding="utf-8")
        for needle in needles:
            if needle not in readme:
                errors.append(f"{name}: missing '{needle}'")

    for name in ("bootstrap.sh", "scripts/update.sh"):
        if not (ROOT / name).exists():
            errors.append(f"{name} is missing")

    for rel in (
        "docs/architecture.md",
        "docs/harness-routing.md",
        "docs/migration.md",
        "docs/licensing-faq.md",
        "docs/reliability.md",
        "docs/policy.md",
        "docs/p4-claude-code.md",
        "docs/p4-other-harnesses.md",
        "docs/harness-integration.md",
        "docs/install-routed-tools.md",
        "docs/updating.md",
        "docs/release-notes-v0.1.0.md",
        "docs/release-notes-v0.1.1.md",
        "docs/release-checklist.md",
        "docs/assets/overview-zh.svg",
        "docs/assets/overview-en.svg",
    ):
        if not (ROOT / rel).exists():
            errors.append(f"{rel} is missing")

    fixtures = ROOT / "benchmarks" / "fixtures"
    pdfs = sorted(fixtures.glob("*.pdf")) if fixtures.is_dir() else []
    for pdf in pdfs:
        if not (pdf.with_suffix(".txt").exists() or pdf.with_suffix(".truth.txt").exists()):
            errors.append(f"{pdf.relative_to(ROOT)}: missing answer text")
    if len(pdfs) < 10:
        errors.append(f"benchmarks/fixtures/: expected >= 10 PDFs, found {len(pdfs)}")

    real = fixtures / "real"
    if not real.is_dir():
        errors.append("benchmarks/fixtures/real/ is missing")
    else:
        if not (real / "SOURCES.md").exists():
            errors.append("benchmarks/fixtures/real/SOURCES.md is missing (CC BY-SA attribution)")
        for pdf in sorted(real.glob("*.pdf")):
            if not pdf.with_suffix(".txt").exists():
                errors.append(f"{pdf.relative_to(ROOT)}: missing answer text")

    edge = fixtures / "edge"
    if not edge.is_dir():
        errors.append("benchmarks/fixtures/edge/ is missing")
    else:
        if not (edge / "make_edge.py").exists():
            errors.append("benchmarks/fixtures/edge/make_edge.py is missing")
        for pdf in sorted(edge.glob("*.pdf")):
            if not pdf.with_suffix(".txt").exists():
                errors.append(f"{pdf.relative_to(ROOT)}: missing answer text")

    tables = fixtures / "tables"
    if not tables.is_dir():
        errors.append("benchmarks/fixtures/tables/ is missing")
    else:
        if not (tables / "make_tables.py").exists():
            errors.append("benchmarks/fixtures/tables/make_tables.py is missing")
        for pdf in sorted(tables.glob("*.pdf")):
            if not pdf.with_suffix(".json").exists():
                errors.append(f"{pdf.relative_to(ROOT)}: missing cell truth JSON")
    if not (ROOT / "scripts" / "bench_tables.py").exists():
        errors.append("scripts/bench_tables.py is missing")
    if not (ROOT / "scripts" / "route.py").exists():
        errors.append("scripts/route.py is missing")
    if not (ROOT / "scripts" / "bench_abstract.py").exists():
        errors.append("scripts/bench_abstract.py is missing")
    if not (ROOT / "scripts" / "bench_policy.py").exists():
        errors.append("scripts/bench_policy.py is missing")
    for name in ("survey_pdfs.py", "sample_real.py"):
        if not (ROOT / "scripts" / name).exists():
            errors.append(f"scripts/{name} is missing")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(
        f"OK: 1 orchestrator, {len(shells)} tool shells, "
        f"registry {registry_tools} tools, notices cover {len(REQUIRED_TOOLS)} tools"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
