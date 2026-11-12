#!/usr/bin/env python3
"""Probe docarbiter and the routed upstream tools for updates.

This is the fixed dependency probe:
  - docarbiter: local HEAD vs origin/main vs latest GitHub release;
  - routed Python tools: installed vs registry pin vs latest PyPI;
  - upstream GitHub releases for the same repos.

It does not install or upgrade anything. A weekly GitHub Actions workflow runs
it and opens/updates an issue labelled `upstream-probe` when it exits non-zero.

Run:
    python3 -I scripts/check_updates.py
    python3 -I scripts/check_updates.py --format json --exit-code --no-github
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"
REPO = "ChemistryBus/docarbiter"

# registry tool id -> PyPI distribution name
PYPI = {
    "mineru": "mineru",
    "docling": "docling",
    "liteparse": "liteparse",
    "markitdown": "markitdown",
    "rapidocr": "rapidocr",
    "ocrmypdf": "ocrmypdf",
    "pdfplumber": "pdfplumber",
    "paddleocr": "paddleocr",
    "marker": "marker-pdf",
    "unstructured": "unstructured",
    "olmocr": "olmocr",
    "surya": "surya-ocr",
    "camelot": "camelot-py",
    "pypdf": "pypdf",
    "pdfminer": "pdfminer.six",
}
CORE = {"mineru", "docling", "liteparse", "markitdown", "rapidocr", "ocrmypdf", "pdfplumber"}


def get_json(url: str, timeout: int = 15, token: str | None = None) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "docarbiter-upstream-probe"})
    if token:
        request.add_header("Authorization", f"token {token}")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def parse_pin(install: str) -> str | None:
    match = re.search(r"pip install\s+[A-Za-z0-9_.-]+==([0-9][^\s#]*)", install or "")
    return match.group(1) if match else None


def installed(pkg: str) -> str | None:
    try:
        return metadata.version(pkg)
    except metadata.PackageNotFoundError:
        return None


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", value)[:4])


def compare(a: str, b: str) -> int:
    left = version_tuple(a)
    right = version_tuple(b)
    return (left > right) - (left < right)


def pypi_latest(pkg: str, token: str | None) -> tuple[str | None, str | None, str | None]:
    try:
        data = get_json(f"https://pypi.org/pypi/{pkg}/json", token=token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, None, "not on PyPI"
        return None, None, f"PyPI HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, None, f"PyPI probe failed: {type(exc).__name__}"
    version = data.get("info", {}).get("version")
    files = data.get("releases", {}).get(version, []) if version else []
    date = files[0].get("upload_time_iso_8601") if files else None
    return version, date, None


def github_latest(url: str, token: str | None) -> tuple[str | None, str | None, str | None]:
    match = re.search(r"github\.com/([^/]+)/([^/#?]+)", url or "")
    if not match:
        return None, None, "no GitHub URL"
    owner, repo = match.group(1), match.group(2)
    try:
        data = get_json(f"https://api.github.com/repos/{owner}/{repo}/releases/latest", token=token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, None, "no GitHub release"
        return None, None, f"GitHub HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        return None, None, f"GitHub probe failed: {type(exc).__name__}"
    return data.get("tag_name"), data.get("published_at"), None


def git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(ROOT), *args], text=True, stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def load_tools() -> list[dict]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tools = []
    for entry in data.get("tools", []):
        tool = entry.get("id")
        pkg = PYPI.get(tool)
        if not pkg:
            continue
        tools.append({
            "id": tool,
            "name": entry.get("name", tool),
            "tier": entry.get("tier", "optional"),
            "pypi": pkg,
            "pin": parse_pin(entry.get("install", "")),
            "upstream": entry.get("upstream", ""),
        })
    return tools


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe docarbiter and routed upstream tools.")
    ap.add_argument("--format", choices=["text", "markdown", "json"], default="text")
    ap.add_argument("--exit-code", action="store_true", help="exit 1 when any update or drift is found")
    ap.add_argument("--no-github", action="store_true", help="skip GitHub release API calls")
    ap.add_argument("--timeout", type=int, default=15)
    args = ap.parse_args()

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    issues: list[str] = []
    docarbiter = {
        "local": git("rev-parse", "HEAD"),
        "remote": None,
        "release": None,
        "release_date": None,
        "error": None,
    }
    local = docarbiter["local"]
    remote = git("ls-remote", "origin", "refs/heads/main")
    if remote:
        docarbiter["remote"] = remote.split()[0]
    if not docarbiter["remote"]:
        docarbiter["error"] = "origin/main not reachable"
    elif local and local != docarbiter["remote"]:
        issues.append("docarbiter local HEAD differs from origin/main")
    if not args.no_github:
        tag, date, error = github_latest(f"https://github.com/{REPO}", token)
        docarbiter["release"] = tag
        docarbiter["release_date"] = date
        if error and error != "no GitHub release":
            docarbiter["error"] = error

    rows = []
    for tool in load_tools():
        row = dict(tool)
        row["installed"] = installed(tool["pypi"])
        row["latest"], row["latest_date"], row["pypi_error"] = pypi_latest(tool["pypi"], token)
        row["github_release"], row["github_date"], row["github_error"] = (None, None, "skipped")
        if not args.no_github:
            row["github_release"], row["github_date"], row["github_error"] = github_latest(tool["upstream"], token)

        status = "ok"
        if row["pypi_error"] and row["pypi_error"] != "not on PyPI":
            status = "probe-error"
        elif not row["pin"]:
            status = "unpinned"
        elif not row["latest"]:
            status = "probe-error"
        elif compare(row["latest"], row["pin"]) > 0:
            status = "pinned-behind"
        if row["installed"] and row["pin"] and row["installed"] != row["pin"]:
            status = "env-drift" if status == "ok" else status + "+env-drift"
        if not row["installed"]:
            status = "not-installed" if status == "ok" else status + "+not-installed"
        row["status"] = status

        if tool["tier"] in ("core", "extra") and "pinned-behind" in status:
            issues.append(f"{tool['id']}: upstream {row['latest']} > pinned {row['pin']}")
        if tool["tier"] == "core" and "env-drift" in status:
            issues.append(f"{tool['id']}: installed {row['installed']} != pinned {row['pin']}")
        if tool["tier"] == "core" and "not-installed" in status:
            issues.append(f"{tool['id']}: core tool is not installed")
        row["impact"] = (
            "rerun route selftest, page-marker regression, and real-table/full-text benchmarks; "
            "check the CLI before updating thin shells"
            if tool["tier"] == "core"
            else "benchmark before routing; extra tools are not in the default core"
        )
        rows.append(row)

    if args.format == "json":
        print(json.dumps({"generated": datetime.now(timezone.utc).isoformat(),
                          "docarbiter": docarbiter, "tools": rows, "issues": issues},
                         ensure_ascii=False, indent=2))
    elif args.format == "markdown":
        print(f"# Upstream probe — {datetime.now(timezone.utc).date().isoformat()}")
        print()
        print("## docarbiter")
        print()
        print(f"- local HEAD: `{docarbiter['local'] or '?'}`")
        print(f"- origin/main: `{docarbiter['remote'] or '?'}`")
        print(f"- latest release: `{docarbiter['release'] or '?'}`")
        if docarbiter["error"]:
            print(f"- error: {docarbiter['error']}")
        print()
        print("## Routed tools")
        print()
        print("| tool | tier | installed | pinned | latest | latest release | status |")
        print("|---|---|---|---|---|---|---|")
        for row in rows:
            print(
                f"| {row['id']} | {row['tier']} | {row['installed'] or '—'} | "
                f"{row['pin'] or '—'} | {row['latest'] or '—'} | "
                f"{row['github_release'] or '—'} | {row['status']} |"
            )
        print()
        print("## Recommended checks")
        print()
        print("- Any `pinned-behind`, `env-drift`, or `not-installed` on a core tool means: "
              "re-run `validate.py`, `route.py --selftest`, `check_pagemarkers.py`, and the "
              "real-table/full-text benchmarks before changing a pin.")
        print("- Check upstream release notes for CLI/API changes before updating a thin shell.")
        print("- `extra`/`optional` updates are informational; they are not in the default core.")
        if issues:
            print()
            print("## Issues")
            print()
            for issue in issues:
                print(f"- {issue}")
    else:
        print(f"docarbiter: local={docarbiter['local'] or '?'} remote={docarbiter['remote'] or '?'} "
              f"release={docarbiter['release'] or '?'}")
        for row in rows:
            print(f"{row['id']:14} tier={row['tier']:9} installed={row['installed'] or '—':12} "
                  f"pinned={row['pin'] or '—':12} latest={row['latest'] or '—':12} {row['status']}")
        if issues:
            print("\nissues:")
            for issue in issues:
                print(f"  - {issue}")

    return 1 if (args.exit_code and issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
