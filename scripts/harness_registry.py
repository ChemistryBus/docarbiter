#!/usr/bin/env python3
"""Read the harness table from registry.json.

This is the single source of truth consumed by install.sh and doctor.sh:
harness label, skills directory, expected shape, and status.

Usage:
    python3 -I scripts/harness_registry.py --format tsv [--scanned]
    python3 -I scripts/harness_registry.py --lookup ~/.codex/skills
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "registry.json"


def load() -> list[dict]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return data.get("harnesses", [])


def expanded(skills_dir: str) -> str:
    home = os.environ.get("HOME", "")
    return os.path.normpath(os.path.abspath(os.path.expanduser(os.path.join(home, skills_dir))))


def main() -> int:
    ap = argparse.ArgumentParser(description="Read registry.json harness entries.")
    ap.add_argument("--format", choices=["tsv", "json"], default="tsv")
    ap.add_argument("--lookup", metavar="DIR", help="print shape<TAB>status<TAB>note for DIR")
    ap.add_argument("--scanned", action="store_true", help="exclude directories harnesses do not scan")
    args = ap.parse_args()

    harnesses = load()
    if args.lookup:
        target = os.path.normpath(os.path.abspath(os.path.expanduser(args.lookup)))
        for harness in harnesses:
            if expanded(harness["skills_dir"]) == target:
                print(
                    f"{harness.get('shape', 'file')}\t"
                    f"{harness.get('status', 'unknown')}\t"
                    f"{harness.get('note', '')}"
                )
                return 0
        return 1

    if args.scanned:
        harnesses = [h for h in harnesses if h.get("status") != "not-scanned"]
    if args.format == "json":
        print(json.dumps(harnesses, ensure_ascii=False, indent=2))
        return 0
    for harness in harnesses:
        print("\t".join([
            harness.get("id", ""),
            harness.get("label", harness.get("id", "")),
            harness["skills_dir"],
            harness.get("shape", "file"),
            harness.get("status", "unknown"),
        ]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
