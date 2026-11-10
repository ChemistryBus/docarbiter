#!/usr/bin/env python3
"""Read-only survey of real PDFs in the workspace.

It hashes files for deduplication, samples a fixed number per top-level folder,
probes the first few pages with pdftotext, and writes only aggregate statistics
and paths. It never stores or prints document text, and never uploads anything.

Run:
    python3 -I scripts/survey_pdfs.py --root ~/Documents --dirs "ProjectA,ProjectB"
    python3 -I scripts/survey_pdfs.py --root ~/Documents --dirs "ProjectA" --per-dir 12
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT_DEFAULT = Path(os.environ.get("DOCARBITER_WORKSPACE", Path.cwd()))
DIRS_DEFAULT = os.environ.get("DOCARBITER_SURVEY_DIRS", "")
SOURCE_SUFFIXES = (".md", ".markdown", ".docx", ".txt")
CJK_RE = re.compile(r"[㐀-䶿一-鿿]")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pdf_pages(path: Path) -> int | None:
    if not shutil.which("pdfinfo"):
        return None
    try:
        proc = subprocess.run(
            ["pdfinfo", str(path)], capture_output=True, text=True, timeout=20,
        )
        m = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.M)
        return int(m.group(1)) if m else None
    except Exception:
        return None


def probe(path: Path, max_pages: int, timeout: int) -> dict:
    if not shutil.which("pdftotext"):
        return {"status": "no-pdftotext", "chars": 0, "cjk": 0, "bad": 0,
                "ctrl": 0, "bad_ratio": 0.0, "language": "unknown"}
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", "1", "-l", str(max_pages), str(path), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
        if proc.returncode != 0:
            return {"status": "probe-error", "chars": 0, "cjk": 0, "bad": 0,
                    "ctrl": 0, "bad_ratio": 0.0, "language": "unknown"}
        text = proc.stdout
    except Exception:
        return {"status": "probe-error", "chars": 0, "cjk": 0, "bad": 0,
                "ctrl": 0, "bad_ratio": 0.0, "language": "unknown"}

    chars = len("".join(text.split()))
    bad = sum(1 for c in text if c == "�" or 0xE000 <= ord(c) <= 0xF8FF)
    ctrl = sum(1 for c in text if unicodedata.category(c) == "Cc" and c not in "\n\r\t\f\v")
    cjk = sum(1 for c in text if 0x3400 <= ord(c) <= 0x4DBF or 0x4E00 <= ord(c) <= 0x9FFF
              or 0x20000 <= ord(c) <= 0x2FA1F)
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    ratio = (bad + ctrl) / max(chars, 1)
    if chars < 50 and ratio <= 0.05:
        status = "scan"
    elif ratio > 0.10:
        status = "garbled"
    elif chars >= 50:
        status = "usable"
    else:
        status = "unknown"
    language = "zh" if cjk > latin else ("en" if latin > cjk else "mixed")
    return {"status": status, "chars": chars, "cjk": cjk, "bad": bad,
            "ctrl": ctrl, "bad_ratio": round(ratio, 4), "language": language}


def source_pair(path: Path) -> str | None:
    for suffix in SOURCE_SUFFIXES:
        candidate = path.with_suffix(suffix)
        if candidate.exists():
            return candidate.name
    return None


def discover(root: Path, dirs: list[str], cjk_names: bool = False) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for d in dirs:
        base = root / d
        if not base.is_dir():
            out[d] = []
            continue
        files = [p for p in base.rglob("*") if p.is_file() and p.suffix.lower() == ".pdf"]
        if cjk_names:
            files = [p for p in files if CJK_RE.search(p.name)]
        out[d] = sorted(files)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT_DEFAULT))
    ap.add_argument("--dirs", default=DIRS_DEFAULT)
    ap.add_argument("--per-dir", type=int, default=12)
    ap.add_argument("--seed", type=int, default=20261110)
    ap.add_argument("--max-pages", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--out", default="benchmarks/private/survey.md")
    ap.add_argument("--json-out", default="benchmarks/private/survey.json")
    ap.add_argument("--no-probe", action="store_true")
    ap.add_argument("--cjk-names", action="store_true",
                    help="only include PDFs whose filename contains CJK characters")
    args = ap.parse_args()

    root = Path(args.root)
    dirs = [d.strip() for d in args.dirs.split(",") if d.strip()]
    if not dirs:
        ap.error("--dirs (or DOCARBITER_SURVEY_DIRS) is required; no personal defaults are built in")
    if not root.is_dir():
        ap.error(f"--root is not a directory: {root}")
    discovered = discover(root, dirs, cjk_names=args.cjk_names)
    rng = random.Random(args.seed)

    seen: set[str] = set()
    duplicates: Counter = Counter()
    unique: dict[str, list[Path]] = defaultdict(list)
    for d in dirs:
        for p in discovered[d]:
            try:
                h = sha256(p)
            except Exception:
                continue
            if h in seen:
                duplicates[d] += 1
                continue
            seen.add(h)
            unique[d].append(p)

    sampled: dict[str, list[Path]] = {}
    for d in dirs:
        pool = unique[d]
        n = min(args.per_dir, len(pool))
        sampled[d] = rng.sample(pool, n)

    rows = []
    for d in dirs:
        for p in sampled[d]:
            rel = p.relative_to(root)
            pages = pdf_pages(p)
            probe_data = (
                {"status": "not-probed", "chars": 0, "cjk": 0, "bad": 0, "ctrl": 0,
                 "bad_ratio": 0.0, "language": "unknown"}
                if args.no_probe else probe(p, args.max_pages, args.timeout)
            )
            rows.append({
                "dir": d,
                "path": str(rel),
                "size_kb": round(p.stat().st_size / 1024, 1),
                "pages": pages,
                "source_pair": source_pair(p),
                **probe_data,
            })

    status_counts = Counter(r["status"] for r in rows)
    lang_counts = Counter(r["language"] for r in rows)
    pair_count = sum(1 for r in rows if r["source_pair"])
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    out = Path(args.out)
    json_out = Path(args.json_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json_out.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "generated": now,
        "root": str(root),
        "dirs": dirs,
        "per_dir": args.per_dir,
        "seed": args.seed,
        "cjk_names": args.cjk_names,
        "discovered": {d: len(discovered[d]) for d in dirs},
        "duplicates_removed": dict(duplicates),
        "unique": {d: len(unique[d]) for d in dirs},
        "sampled": {d: len(sampled[d]) for d in dirs},
        "status_counts": dict(status_counts),
        "language_counts": dict(lang_counts),
        "rows": rows,
    }
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Workspace PDF survey (read-only)",
        "",
        f"> Generated: {now}  ",
        f"> Root: `{root}`  ",
        f"> Seed: {args.seed}; per-dir: {args.per_dir}; probe pages: {args.max_pages}  ",
        "> Only aggregate statistics and paths are stored. **No document text is written or uploaded.**",
        "",
        "## Inventory",
        "",
        "| folder | discovered | unique after hash | sampled | duplicates skipped |",
        "|---|---:|---:|---:|---:|",
    ]
    for d in dirs:
        lines.append(
            f"| {d} | {len(discovered[d])} | {len(unique[d])} | {len(sampled[d])} | {duplicates[d]} |"
        )
    lines += [
        "",
        f"**Sampled total:** {len(rows)}  ",
        f"**Probe status:** {dict(status_counts)}  ",
        f"**Language:** {dict(lang_counts)}  ",
        f"**Same-stem source pairs:** {pair_count}",
        "",
        "## Sampled files",
        "",
        "| folder | file | pages | status | lang | chars | cjk | bad_ratio | source pair |",
        "|---|---|---:|---|---|---:|---:|---:|---|",
    ]
    for r in rows:
        name = r["path"].replace("|", "\\|")
        pair = r["source_pair"] or ""
        lines.append(
            f"| {r['dir']} | {name} | {r['pages'] if r['pages'] is not None else ''} | "
            f"{r['status']} | {r['language']} | {r['chars']} | {r['cjk']} | "
            f"{r['bad_ratio']:.2%} | {pair} |"
        )
    lines += [
        "",
        "## Next",
        "",
        "- `scan` / `garbled` rows are the first candidates for OCR/robustness tests.",
        "- Rows with a `source pair` can be used for local CER (source text as answer).",
        "- This survey does not copy or upload any document content.",
    ]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"survey: {out}")
    print(f"json:   {json_out}")
    print(f"sampled {len(rows)} / unique {sum(len(v) for v in unique.values())}, status={dict(status_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
