#!/usr/bin/env python3
"""Real-workspace smoke test on a few PDFs selected from the private survey.

It runs 2-page extraction with pdftotext, liteparse, and MinerU, then reports
character counts, times, and pairwise agreement (CER between tool outputs).
Agreement is NOT accuracy: there is no independent answer key here.

No document text is written or printed; only aggregate stats and paths go to
the private report.

Run:
    python3 -I scripts/sample_real.py --root ~/Documents
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT_DEFAULT = Path(os.environ.get("DOCARBITER_WORKSPACE", Path.cwd()))
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import bench  # noqa: E402


def run(cmd: list[str], timeout: int) -> tuple[str, str, int, float]:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout)
        return p.stdout, p.stderr, p.returncode, time.time() - t0
    except FileNotFoundError:
        return "", f"missing {cmd[0]}", 127, time.time() - t0
    except subprocess.TimeoutExpired:
        return "", "timeout", 124, time.time() - t0
    except Exception as exc:  # noqa: BLE001
        return "", str(exc), 1, time.time() - t0


def extract(tool: str, path: Path, pages: str, timeout: int) -> tuple[str, int, float, str]:
    if tool == "pdftotext":
        text, err, rc, secs = run(["pdftotext", "-f", "1", "-l", "2", str(path), "-"], timeout)
    elif tool == "liteparse":
        text, err, rc, secs = run(["liteparse-doc", str(path), "--pages", pages], timeout)
    elif tool == "mineru":
        text, err, rc, secs = run(["mineru-doc", str(path), "--pages", pages], timeout)
    else:
        raise ValueError(tool)
    return text, rc, secs, err


def agreement(a: str, b: str) -> float:
    if not a or not b:
        return 1.0
    dist = bench.levenshtein(a, b, 50000)
    return dist / max(len(a), len(b), 1)


def bag_distance(a: str, b: str) -> float:
    """Character-multiset difference: low means same content, order may differ."""
    if not a or not b:
        return 1.0
    ca, cb = Counter(a), Counter(b)
    diff = sum((ca - cb).values()) + sum((cb - ca).values())
    return diff / max(len(a), len(b), 1)


def bigram_distance(a: str, b: str) -> float:
    """1 - Jaccard of adjacent character bigrams: low means similar order."""
    if len(a) < 2 or len(b) < 2:
        return 1.0
    sa = {a[i:i + 2] for i in range(len(a) - 1)}
    sb = {b[i:i + 2] for i in range(len(b) - 1)}
    if not sa or not sb:
        return 1.0
    return 1.0 - len(sa & sb) / len(sa | sb)


def load_candidates(root: Path) -> list[dict]:
    rows = []
    for name in ("survey.json", "survey-cjk.json"):
        path = REPO / "benchmarks" / "private" / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for r in data.get("rows", []):
            if r.get("status") != "usable":
                continue
            if (r.get("pages") or 999) > 30:
                continue
            path_obj = root / r["path"]
            if path_obj.exists():
                rows.append(r)
    return rows


def pick(candidates: list[dict], lang: str, n: int) -> list[dict]:
    seen = set()
    out = []
    for r in candidates:
        if r.get("language") != lang or r["path"] in seen:
            continue
        seen.add(r["path"])
        out.append(r)
        if len(out) >= n:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="workspace root used when survey.json stores relative paths")
    ap.add_argument("--pages", default="1-2")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--out", default=str(REPO / "benchmarks" / "private" / "real-smoke.md"))
    args = ap.parse_args()

    root = Path(args.root)
    if not root.is_dir():
        ap.error(f"--root is not a directory: {root}")

    candidates = load_candidates(root)
    picks = pick(candidates, "zh", 2) + pick(candidates, "en", 2)
    if not picks:
        print("no usable candidates; run scripts/survey_pdfs.py first", file=sys.stderr)
        return 2

    rows = []
    for r in picks:
        path = root / r["path"]
        outputs = {}
        outputs_np = {}
        for tool in ("pdftotext", "liteparse", "mineru"):
            text, rc, secs, err = extract(tool, path, args.pages, args.timeout)
            norm = bench.normalize(text, strip_md=True)
            norm_np = bench.normalize(text, strip_md=True, strip_punct=True)
            outputs[tool] = norm
            outputs_np[tool] = norm_np
            rows.append({
                "path": r["path"], "lang": r["language"], "pages": r.get("pages"),
                "tool": tool, "chars": len(norm), "seconds": round(secs, 3),
                "status": "ok" if rc == 0 and norm else "error",
            })
        pairs = []
        tools = list(outputs)
        for i in range(len(tools)):
            for j in range(i + 1, len(tools)):
                pairs.append((
                    tools[i], tools[j],
                    agreement(outputs[tools[i]], outputs[tools[j]]),
                    agreement(outputs_np[tools[i]], outputs_np[tools[j]]),
                    bag_distance(outputs[tools[i]], outputs[tools[j]]),
                    bigram_distance(outputs[tools[i]], outputs[tools[j]]),
                ))
        for a, b, cer, cer_np, bag, bigram in pairs:
            order_flag = "order?" if bag < 0.05 and bigram > 0.25 else ""
            rows.append({"path": r["path"], "lang": r["language"], "pages": r.get("pages"),
                         "tool": f"{a} vs {b}", "chars": "", "seconds": "", "status": "agree",
                         "agreement": round(cer, 6), "agreement_nopunct": round(cer_np, 6),
                         "bag": round(bag, 6), "bigram": round(bigram, 6), "flag": order_flag})

    lines = [
        "# Real workspace smoke test (private)",
        "",
        "> Selected from `benchmarks/private/survey*.json`; 2-page extraction.",
        "> **Agreement = CER between tool outputs, not accuracy.** No answer key is used.",
        "> No document text is stored or printed.",
        "",
        "| file | lang | pages | tool | chars | seconds | status | agreement | no-punct | bag | bigram | flag |",
        "|---|---|---:|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for r in rows:
        name = r["path"].replace("|", "\\|")
        lines.append(
            f"| {name} | {r['lang']} | {r['pages']} | {r['tool']} | {r['chars']} | "
            f"{r['seconds']} | {r['status']} | {r.get('agreement', '')} | {r.get('agreement_nopunct', '')} | "
            f"{r.get('bag', '')} | {r.get('bigram', '')} | {r.get('flag', '')} |"
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"report: {out}")
    print(f"selected {len(picks)} files: {[p['path'] for p in picks]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
