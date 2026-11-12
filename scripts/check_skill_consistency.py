#!/usr/bin/env python3
"""Check that SKILL.md and route.py describe the same router.

The skill text and the executable router are two implementations of the same
routing table. This check catches the common drift: a goal or tool added to one
side only, a stale version, or camelot creeping back into the default chain.

Run:
    python3 -I scripts/check_skill_consistency.py
    python3 -I scripts/check_skill_consistency.py --check-git
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "docarbiter" / "SKILL.md"
ROUTE = ROOT / "scripts" / "route.py"
README = ROOT / "README.md"
README_ZH = ROOT / "README.zh-CN.md"

TOOL_ALIASES = {
    "ocrmypdf+mineru": ("ocrmypdf", "mineru"),
}


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data


def route_shape() -> tuple[list[str], list[str]]:
    tree = ast.parse(ROUTE.read_text(encoding="utf-8"))
    goals: list[str] = []
    tools: list[str] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_argument"
            and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value == "--goal"
        ):
            for keyword in node.keywords:
                if keyword.arg == "choices" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                    goals = [
                        item.value for item in keyword.value.elts
                        if isinstance(item, ast.Constant) and isinstance(item.value, str)
                    ]
        if isinstance(node, ast.FunctionDef) and node.name == "_entry":
            for inner in ast.walk(node):
                if not isinstance(inner, ast.Return):
                    continue
                value = inner.value
                # _entry returns {...}.get(tool), so unwrap the call.
                if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
                    value = value.func.value
                if isinstance(value, ast.Dict):
                    tools = [
                        key.value for key in value.keys
                        if isinstance(key, ast.Constant) and isinstance(key.value, str)
                    ]
    return goals, tools


def readme_version(text: str) -> str | None:
    match = re.search(r"releases/tag/v(\d+\.\d+\.\d+)", text)
    if match:
        return match.group(1)
    match = re.search(r"<strong>v(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else None


def git_version(ref: str) -> str | None:
    try:
        text = subprocess.check_output(
            ["git", "-C", str(ROOT), "show", f"{ref}:skills/docarbiter/SKILL.md"],
            text=True, stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return frontmatter(text).get("version")


def main() -> int:
    ap = argparse.ArgumentParser(description="Check SKILL.md / route.py consistency.")
    ap.add_argument("--check-git", action="store_true",
                    help="fail if SKILL.md changed against origin/main without a version bump")
    args = ap.parse_args()

    text = SKILL.read_text(encoding="utf-8")
    fm = frontmatter(text)
    goals, tools = route_shape()
    errors: list[str] = []

    if fm.get("name") != "docarbiter":
        errors.append(f"SKILL.md name is {fm.get('name')!r}, expected 'docarbiter'")
    version = fm.get("version")
    if not version:
        errors.append("SKILL.md is missing frontmatter version")

    for goal in goals:
        if f"`{goal}`" not in text:
            errors.append(f"goal '{goal}' is in route.py but not written as `{goal}` in SKILL.md")

    lower = text.lower()
    for tool in tools:
        terms = TOOL_ALIASES.get(tool, (tool,))
        missing = [term for term in terms if term.lower() not in lower]
        if missing:
            errors.append(f"tool '{tool}' (terms {terms}) is missing from SKILL.md")

    if re.search(r"pdfplumber\s*(?:→|->)\s*camelot", text):
        errors.append("camelot is still in the default simple-table chain in SKILL.md")

    for name, path in (("README.md", README), ("README.zh-CN.md", README_ZH)):
        if not path.exists():
            errors.append(f"{name} is missing")
            continue
        readme_v = readme_version(path.read_text(encoding="utf-8"))
        if readme_v != version:
            errors.append(f"{name} version {readme_v!r} != SKILL.md version {version!r}")

    if args.check_git and version:
        base_version = git_version("origin/main")
        if base_version is not None and base_version == version:
            diff = subprocess.run(
                ["git", "-C", str(ROOT), "diff", "--quiet", "origin/main", "--", "skills/docarbiter/SKILL.md"],
                capture_output=True,
            )
            if diff.returncode != 0:
                errors.append(
                    "SKILL.md differs from origin/main but version was not bumped "
                    f"(still {version}); bump version and the README badges"
                )

    # Registry pins should not silently disappear for core tools.
    if version and not re.search(r"^\s*version:\s*" + re.escape(version) + r"\s*$", text, re.M):
        errors.append("version line is not a plain frontmatter scalar")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(
        f"OK: SKILL.md version {version}; {len(goals)} goals; "
        f"{len(tools)} routed tools; README versions match"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
