#!/usr/bin/env python3
"""bench.py — character-level CER benchmark for document extraction tools.

The answer key must be independent of the tools under test. Pass a human-checked
.txt next to each PDF (same stem), or --truth for a single file. Do NOT use
pdftotext output as the answer key: that only measures agreement with pdftotext.

Run with -I to avoid importing modules from the current directory:
    python3 -I scripts/bench.py benchmarks/fixtures/zh-text-layer.pdf
"""
from __future__ import annotations

import argparse
import csv
import difflib
import importlib.metadata as md
import json
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

try:
    from rapidfuzz.distance import Levenshtein as _RFLev
except ImportError:  # optional; fall back to pure Python
    _RFLev = None

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TOOLS = "pdftotext,liteparse,mineru,docling,markitdown"


# ---------------------------------------------------------------- extraction
def _run(cmd: list[str], timeout: int) -> tuple[str, str, int, float]:
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return proc.stdout, proc.stderr, proc.returncode, time.time() - t0
    except FileNotFoundError:
        return "", f"command not found: {cmd[0]}", 127, time.time() - t0
    except subprocess.TimeoutExpired:
        return "", f"timeout after {timeout}s", 124, time.time() - t0
    except Exception as exc:  # noqa: BLE001 - report and continue
        return "", f"{type(exc).__name__}: {exc}", 1, time.time() - t0


def extract(tool: str, doc: Path, workdir: Path, timeout: int) -> tuple[str, str, int, float]:
    if tool == "pdftotext":
        return _run(["pdftotext", str(doc), "-"], timeout)
    if tool == "liteparse":
        return _run(["liteparse-doc", str(doc)], timeout)
    if tool == "mineru":
        return _run(["mineru-doc", str(doc), "--pages", "all"], timeout)
    if tool == "markitdown":
        return _run(["markitdown", str(doc)], timeout)
    if tool == "pdfplumber":
        t0 = time.time()
        try:
            import pdfplumber
        except ImportError as exc:
            return "", f"pdfplumber not installed: {exc}", 127, time.time() - t0
        try:
            with pdfplumber.open(str(doc)) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
            return text, "", 0, time.time() - t0
        except Exception as exc:  # noqa: BLE001
            return "", f"{type(exc).__name__}: {exc}", 1, time.time() - t0
    if tool == "rapidocr":
        t0 = time.time()
        prefix = workdir / "page"
        proc = subprocess.run(
            ["pdftoppm", "-png", "-r", "150", str(doc), str(prefix)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode != 0:
            return "", proc.stderr, proc.returncode, time.time() - t0
        try:
            from rapidocr import RapidOCR
        except ImportError as exc:
            return "", f"rapidocr not installed: {exc}", 127, time.time() - t0
        engine = RapidOCR()
        texts: list[str] = []
        for image in sorted(workdir.glob("page*.png")):
            result = engine(str(image))
            texts.extend(result.txts or [])
        return "\n".join(texts), "", 0, time.time() - t0
    if tool == "ocrmypdf":
        out = workdir / "ocr.pdf"
        _, stderr, rc, secs = _run(
            ["ocrmypdf", "--language", "chi_sim+eng", "--output-type", "pdf", "--quiet", str(doc), str(out)],
            timeout,
        )
        if rc != 0:
            return "", stderr, rc, secs
        text, stderr2, rc2, secs2 = _run(["pdftotext", str(out), "-"], timeout)
        return text, stderr + stderr2, rc2, secs + secs2
    if tool == "docling":
        outdir = workdir / f"docling-{doc.stem}"
        outdir.mkdir(parents=True, exist_ok=True)
        stdout, stderr, rc, secs = _run(
            [
                "docling",
                "convert",
                str(doc),
                "--to",
                "md",
                "--output",
                str(outdir),
                "--image-export-mode",
                "placeholder",
            ],
            timeout,
        )
        md_files = sorted(outdir.rglob("*.md"))
        text = md_files[0].read_text(encoding="utf-8", errors="replace") if md_files else stdout
        return text, stderr, rc, secs
    raise ValueError(f"unsupported tool: {tool}")


# ---------------------------------------------------------------- normalisation
def strip_markdown(text: str) -> str:
    """Approximate Markdown-to-text so structural markers do not count as errors."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\|?[\s:|-]+\|?\s*$", "", text, flags=re.M)
    text = text.replace("|", "")
    text = re.sub(r"[*_~`]", "", text)
    return text


def control_ratio(text: str) -> float:
    """Fraction of non-whitespace characters that are control characters."""
    n = len("".join(text.split()))
    ctrl = sum(
        1 for c in text
        if unicodedata.category(c) == "Cc" and c not in "\n\r\t\f\v"
    )
    return ctrl / max(n, 1)


def normalize(text: str, strip_md: bool, strip_punct: bool = False) -> str:
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if strip_md:
        text = strip_markdown(text)
    # English line-break hyphenation: "docu-\nment" -> "document".
    # Only joins a hyphen at end of line between Latin letters; real compounds
    # such as "well-known" are untouched because they have no newline.
    text = re.sub(r"(?<=[A-Za-z])-\n(?=[A-Za-z])", "", text)
    if strip_punct:
        text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return re.sub(r"\s+", "", text)


# ---------------------------------------------------------------- CER
def levenshtein(a: str, b: str, max_chars: int) -> int:
    if len(a) > max_chars or len(b) > max_chars:
        raise ValueError(f"text too long for CER (>{max_chars} chars); raise --max-chars")
    if _RFLev is not None:
        return int(_RFLev.distance(a, b))
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def opcode_counts(truth: str, pred: str) -> tuple[int, int, int]:
    """Approximate S/D/I from difflib opcodes (not minimal edit distance)."""
    sm = difflib.SequenceMatcher(None, truth, pred, autojunk=False)
    s = d = i = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace":
            s += min(i2 - i1, j2 - j1)
            d += max(0, (i2 - i1) - (j2 - j1))
            i += max(0, (j2 - j1) - (i2 - i1))
        elif tag == "delete":
            d += i2 - i1
        elif tag == "insert":
            i += j2 - j1
    return s, d, i


def cer(truth: str, pred: str, max_chars: int) -> dict:
    dist = levenshtein(truth, pred, max_chars)
    s, d, i = opcode_counts(truth, pred)
    return {
        "dist": dist,
        "cer": dist / max(len(truth), 1),
        "sub": s,
        "del": d,
        "ins": i,
    }


# ---------------------------------------------------------------- reporting
def pct(values: list[float], p: float) -> float:
    if not values:
        return float("nan")
    vals = sorted(values)
    k = (len(vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(vals) - 1)
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def tool_version(tool: str) -> str:
    pkg = {
        "mineru": "mineru",
        "docling": "docling",
        "liteparse": "liteparse",
        "markitdown": "markitdown",
        "pdfplumber": "pdfplumber",
        "rapidocr": "rapidocr",
        "ocrmypdf": "ocrmypdf",
    }
    if tool == "pdftotext":
        _, out, _, _ = _run(["pdftotext", "-v"], 10)
        return (out.splitlines() or [""])[0]
    if tool in pkg:
        try:
            return md.version(pkg[tool])
        except md.PackageNotFoundError:
            return "not installed"
    return "unknown"


def environment(args) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "cwd": os.getcwd(),
        "args": vars(args),
        "tool_versions": {t: tool_version(t) for t in args.tools},
        "rapidfuzz": _RFLev is not None,
    }


def write_summary(path: Path, rows: list[dict], env: dict) -> None:
    tools = sorted({r["tool"] for r in rows})
    lines = [
        "# docarbiter benchmark",
        "",
        "> 本结果来自 `{}` / `{}` / Python {} / 语料见下方文件列表。".format(
            env["platform"], env["machine"], env["python"]
        ),
        "> 换机器、换版本、换文件都会变。请在你的文件上跑 `python3 -I scripts/bench.py`。",
        "",
        "| tool | ok | empty/error/garbled | median CER | median no-punct CER | IQR | worst file | worst CER | median s |",
        "|---|---:|---:|---:|---:|---|---|---:|---:|",
    ]
    for tool in tools:
        all_rows = [r for r in rows if r["tool"] == tool]
        sub = [r for r in all_rows if r["status"] == "ok" and r["cer_text"] != ""]
        cers = [float(r["cer_text"]) for r in sub]
        cers_np = [float(r["cer_nopunct"]) for r in sub if r["cer_nopunct"] != ""]
        secs = [float(r["seconds"]) for r in sub]
        bad = len(all_rows) - len(sub)
        if not cers:
            lines.append(f"| {tool} | 0 | {bad} | — | — | — | — | — | — |")
            continue
        worst = max(sub, key=lambda r: float(r["cer_text"]))
        lines.append(
            f"| {tool} | {len(sub)} | {bad} | {statistics.median(cers):.4f} | "
            f"{statistics.median(cers_np):.4f} | "
            f"{pct(cers,0.25):.4f}–{pct(cers,0.75):.4f} | "
            f"{Path(worst['doc']).name} | {float(worst['cer_text']):.4f} | "
            f"{statistics.median(secs):.2f} |"
        )
    lines += ["", "## Files", ""]
    for doc in sorted({r["doc"] for r in rows}):
        lines.append(f"- `{doc}`")
    lines += [
        "",
        "## Notes",
        "",
        "- `cer_text` 先剥离 Markdown 标记再计算；`cer_raw` 不剥离。",
        "- `cer_nopunct` 去掉 Unicode 标点，用于区分标点归一化（如全角冒号→半角）和真错字。",
        "- `status=empty` 表示输出覆盖率 < 5%（常见于扫描件 + 无 OCR 的工具），不计入 CER 汇总。",
        "- `status=garbled` 表示控制字符 > 10% 或 CER > 1.0（常见于 CID/无 ToUnicode），不计入 CER 汇总。",
        "- `sub/del/ins` 来自 difflib opcodes，是近似值，不是最小编辑距离分解。",
        "- 未提供答案文本时只记录字符数和耗时，不计算 CER。",
        "- 不把 `pdftotext` 输出当答案；答案必须来自独立来源。",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Character-level CER benchmark for document extraction tools.")
    ap.add_argument("docs", nargs="*", help="PDF files; default: benchmarks/fixtures/*.pdf")
    ap.add_argument("--truth", help="answer text for a single document")
    ap.add_argument("--tools", default=DEFAULT_TOOLS, help=f"comma-separated; default: {DEFAULT_TOOLS}")
    ap.add_argument("--out", help="output directory; default: benchmarks/results/<timestamp>")
    ap.add_argument("--keep-raw", action="store_true", help="keep raw tool outputs")
    ap.add_argument("--smoke", action="store_true", help="no CER; chars/time only")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per tool per document")
    ap.add_argument("--max-chars", type=int, default=50000, help="refuse longer texts for CER")
    args = ap.parse_args()
    args.tools = [t.strip() for t in args.tools.split(",") if t.strip()]

    docs = [Path(p) for p in args.docs]
    if not docs:
        docs = sorted((REPO_ROOT / "benchmarks" / "fixtures").glob("*.pdf"))
    if not docs:
        print("没有输入文档。把 PDF 放到 benchmarks/fixtures/，或传入路径。", file=sys.stderr)
        return 2
    for doc in docs:
        if not doc.exists():
            print(f"文件不存在: {doc}", file=sys.stderr)
            return 2

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = Path(args.out) if args.out else REPO_ROOT / "benchmarks" / "results" / stamp
    outdir.mkdir(parents=True, exist_ok=True)
    rawdir = outdir / "raw"
    if args.keep_raw:
        rawdir.mkdir(parents=True, exist_ok=True)

    env = environment(args)
    (outdir / "environment.json").write_text(json.dumps(env, ensure_ascii=False, indent=2), encoding="utf-8")

    rows: list[dict] = []
    for doc in docs:
        if args.truth and len(docs) == 1:
            truth_path = Path(args.truth)
        else:
            truth_path = doc.with_suffix(".txt")
            if not truth_path.exists():
                truth_path = doc.with_suffix(".truth.txt")
        truth = None
        truth_nopunct = None
        if truth_path.exists() and not args.smoke:
            truth_text = truth_path.read_text(encoding="utf-8", errors="replace")
            truth = normalize(truth_text, strip_md=True)
            truth_nopunct = normalize(truth_text, strip_md=True, strip_punct=True)
        elif not args.smoke:
            print(f"[warn] 没有答案文本: {doc}（只记录 chars/time）", file=sys.stderr)

        for tool in args.tools:
            with tempfile.TemporaryDirectory(prefix="docarbiter-") as tmp:
                text, stderr, rc, secs = extract(tool, doc, Path(tmp), args.timeout)
            ok = rc == 0 and bool(text.strip())
            text_norm = normalize(text, strip_md=True)
            coverage = (len(text_norm) / len(truth)) if truth else 1.0
            ctrl = control_ratio(text)
            status = "ok" if ok else "error"
            if status == "ok" and truth is not None and coverage < 0.05:
                status = "empty"
            if status == "ok" and ctrl > 0.10:
                status = "garbled"
            row = {
                "doc": str(doc),
                "tool": tool,
                "status": status,
                "seconds": f"{secs:.3f}",
                "chars_pred": len(text_norm),
                "chars_truth": len(truth) if truth is not None else "",
                "coverage": f"{coverage:.4f}" if truth is not None else "",
                "ctrl_ratio": f"{ctrl:.4f}",
                "cer_text": "",
                "cer_nopunct": "",
                "cer_raw": "",
                "sub": "",
                "del": "",
                "ins": "",
                "error": "" if ok else stderr.strip().splitlines()[-1] if stderr.strip() else f"exit {rc}",
            }
            if truth is not None and ok and status == "ok":
                try:
                    raw_norm = normalize(text, strip_md=False)
                    text_nopunct = normalize(text, strip_md=True, strip_punct=True)
                    c_text = cer(truth, text_norm, args.max_chars)
                    c_nopunct = cer(truth_nopunct or "", text_nopunct, args.max_chars)
                    c_raw = cer(truth, raw_norm, args.max_chars)
                    row.update(
                        {
                            "cer_text": f"{c_text['cer']:.6f}",
                            "cer_nopunct": f"{c_nopunct['cer']:.6f}",
                            "cer_raw": f"{c_raw['cer']:.6f}",
                            "sub": c_text["sub"],
                            "del": c_text["del"],
                            "ins": c_text["ins"],
                        }
                    )
                    if c_text["cer"] > 1.0:
                        row["status"] = "garbled"
                except ValueError as exc:
                    row["error"] = str(exc)
            rows.append(row)
            if args.keep_raw:
                target = rawdir / tool / f"{doc.stem}.txt"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8", errors="replace")
            print(f"[{doc.name}] {tool:12} {row['status']:5} {row['seconds']}s "
                  f"{'CER=' + row['cer_text'] if row['cer_text'] else ''}")

    with (outdir / "per_page.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    write_summary(outdir / "summary.md", rows, env)
    print(f"\n结果: {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
