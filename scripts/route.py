#!/usr/bin/env python3
"""Executable version of docarbiter's routing table.

This is the testable engineering core: given a file, probe it and print the
route, reason, command, and fallbacks. Stdlib only; uses the system pdftotext
for PDF probing.

Usage:
    python3 -I scripts/route.py FILE [--goal speed|manuscript|text|table|table-structure|rag|ocr] [--json]
    python3 -I scripts/route.py --selftest
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

PDF = {".pdf"}
OFFICE = {".docx", ".xlsx", ".pptx", ".odt", ".ods", ".odp", ".doc", ".xls", ".ppt"}
WEB = {".html", ".htm", ".epub", ".xml", ".md", ".latex", ".tex"}
IMAGE = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".heic"}
AV = {".mp3", ".wav", ".m4a", ".flac", ".mp4", ".mov", ".mkv", ".webm"}


def _cmd(name: str) -> bool:
    return shutil.which(name) is not None


def _py(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def _available(tool: str) -> bool:
    return {
        "mineru": _cmd("mineru-doc") or _cmd("mineru"),
        "liteparse": _cmd("liteparse-doc"),
        "pdftotext": _cmd("pdftotext"),
        "pdfplumber": _py("pdfplumber"),
        "docling": _cmd("docling"),
        "markitdown": _cmd("markitdown"),
        "rapidocr": _py("rapidocr"),
        "ocrmypdf+mineru": _cmd("ocrmypdf") and (_cmd("mineru-doc") or _cmd("mineru")),
        "olmocr": _cmd("olmocr"),
        "qpdf": _cmd("qpdf"),
    }.get(tool, False)


def probe_pdf(path: Path) -> dict:
    if not _cmd("pdftotext"):
        return {"status": "no-pdftotext", "chars": 0, "bad": 0, "ctrl": 0, "cjk": 0,
                "latin": 0, "bad_ratio": 0.0, "language": "unknown"}
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", "1", "-l", "3", str(path), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        if proc.returncode != 0:
            return {
                "status": "probe-error", "error": (proc.stderr or "").strip()[:200],
                "chars": 0, "bad": 0, "ctrl": 0, "cjk": 0, "latin": 0,
                "bad_ratio": 0.0, "language": "unknown",
            }
        text = proc.stdout
    except Exception as exc:  # noqa: BLE001
        return {"status": "probe-error", "error": str(exc), "chars": 0, "bad": 0,
                "ctrl": 0, "cjk": 0, "latin": 0, "bad_ratio": 0.0, "language": "unknown"}

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
    return {
        "status": status, "chars": chars, "bad": bad, "ctrl": ctrl, "cjk": cjk,
        "latin": latin, "bad_ratio": round(ratio, 4), "language": language,
    }


def _route_pdf(path: Path, goal: str) -> dict:
    probe = probe_pdf(path)
    status = probe["status"]
    if status == "scan":
        intended = "mineru"
        reason = "no usable text layer; MinerU handles scans directly (OCRmyPDF+Tesseract is weaker for Chinese)"
        fallback = ["ocrmypdf+mineru", "rapidocr"]
    elif status == "garbled":
        intended = "mineru"
        reason = "CID / no ToUnicode; text layer is garbled; MinerU OCR is the reliable path"
        fallback = ["rapidocr", "olmocr"]
    elif status == "usable":
        routes = {
            "speed": ("liteparse", "fastest usable text-layer extraction"),
            "manuscript": ("mineru", "clean paragraphs, headings, and page anchors"),
            "text": ("pdftotext", "plain-text baseline; no structure"),
            "table": ("pdfplumber", "fast cell/table extraction for simple text-layer grids; if 0 tables, retry text strategy or --goal table-structure"),
            "table-structure": ("docling", "merged headers and multi-line cells survive; use for real book/standard tables"),
            "rag": ("docling", "RAG chunks / LaTeX / structured output"),
            "ocr": ("mineru", "text layer exists; MinerU if you need structure or page anchors"),
        }
        intended, reason = routes.get(goal, ("liteparse", "fast default for a usable text layer"))
        fallback = {
            "liteparse": ["pdftotext", "mineru", "docling"],
            "mineru": ["docling", "liteparse"],
            "pdftotext": ["liteparse", "mineru"],
            "pdfplumber": ["docling", "mineru"],
            "docling": ["liteparse", "mineru"],
        }.get(intended, ["mineru", "liteparse"])
        if goal == "table-structure" and intended == "docling":
            fallback = ["pdfplumber", "mineru"]
    else:
        intended = "mineru"
        reason = "probe could not classify the PDF; MinerU is the safest structural fallback"
        fallback = ["ocrmypdf+mineru", "docling"]

    chain = [intended] + fallback
    selected = next((t for t in chain if _available(t)), "install-needed")
    return {"kind": "pdf", "probe": probe, "goal": goal, "intended": intended,
            "selected": selected, "reason": reason, "fallback": fallback, "chain": chain}


def route(path: Path, goal: str) -> dict:
    suffix = path.suffix.lower()
    if suffix in PDF:
        return _route_pdf(path, goal)
    if suffix in IMAGE:
        return {"kind": "image", "intended": "rapidocr", "selected": "rapidocr" if _available("rapidocr") else "install-needed",
                "reason": "single image OCR; RapidOCR is the lightweight Chinese-first default",
                "fallback": ["paddleocr", "tesseract"], "chain": ["rapidocr", "paddleocr", "tesseract"]}
    if suffix in OFFICE or suffix in WEB:
        return {"kind": "office/web", "intended": "docling", "selected": "docling" if _available("docling") else "install-needed",
                "reason": "multi-format structure, tables, chunks, LaTeX; markitdown is single-column only",
                "fallback": ["markitdown"], "chain": ["docling", "markitdown"]}
    if suffix in AV:
        return {"kind": "audio/video", "intended": "docling", "selected": "docling" if _available("docling") else "install-needed",
                "reason": "audio/video transcription is a Docling capability", "fallback": [], "chain": ["docling"]}
    return {"kind": "unknown", "intended": "inspect", "selected": "inspect",
            "reason": f"unknown extension {suffix or '(none)'}", "fallback": [], "chain": []}


def command_for(path: Path, result: dict) -> str:
    tool = result["selected"]
    q = shlex.quote(str(path))
    if tool == "mineru":
        return f"mineru-doc {q} --pages all -o out.md"
    if tool == "liteparse":
        return f"liteparse-doc {q} --pages all"
    if tool == "pdftotext":
        return f"pdftotext {q} -"
    if tool == "docling":
        if result.get("goal") == "table-structure":
            return (f"mkdir -p out && docling convert {q} --from pdf --to md "
                    f"--page-range 1-5 --output out/ --image-export-mode placeholder  "
                    f"# 复杂表；干净文字层加 --no-ocr，按目标页改 --page-range")
        return f"docling convert {q} --to md --output out/ --image-export-mode placeholder"
    if tool == "markitdown":
        return f"markitdown {q}"
    if tool == "ocrmypdf+mineru":
        stem = path.with_suffix("")
        return f"ocrmypdf --language chi_sim+eng {q} {shlex.quote(str(stem))}-ocr.pdf && mineru-doc {shlex.quote(str(stem))}-ocr.pdf --pages all -o out.md"
    if tool == "pdfplumber":
        quoted = json.dumps(str(path), ensure_ascii=False)
        return f"python3 -c \"import pdfplumber; print(pdfplumber.open({quoted}).pages[0].extract_tables())\""
    if tool == "rapidocr":
        return "python3 -c \"from rapidocr import RapidOCR; print(RapidOCR()(image_path).txts)\""
    return "# install the intended tool first; see docs/tool-registry.md"


def print_human(path: Path, result: dict) -> None:
    print(f"file={path}")
    probe = result.get("probe")
    if probe:
        print(
            f"probe: status={probe['status']} language={probe['language']} "
            f"chars={probe['chars']} cjk={probe['cjk']} bad={probe['bad']} ctrl={probe['ctrl']} "
            f"bad_ratio={probe['bad_ratio']:.2%}"
        )
    print(f"route: intended={result['intended']} selected={result['selected']} goal={result.get('goal', '-')}")
    print(f"reason: {result['reason']}")
    print(f"command: {command_for(path, result)}")
    if result.get("fallback"):
        print(f"fallback: {', '.join(result['fallback'])}")
    if result["selected"] == "install-needed":
        print("warning: intended tool is not installed; run ./scripts/install.sh --profile core")


def selftest() -> int:
    root = Path(__file__).resolve().parent.parent
    cases = [
        ("benchmarks/fixtures/zh-text-layer.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/zh-scan.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/edge/zh-cid-no-tounicode.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/edge/zh-traditional.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/edge/en-two-column-interleaved.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/real/zh-ocr.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/real/bert-abstract-2p.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/en-hyphenation.pdf", "text", "pdftotext"),
        ("benchmarks/fixtures/zh-table.pdf", "table", "pdfplumber"),
        ("benchmarks/fixtures/zh-table.pdf", "table-structure", "docling"),
        ("benchmarks/fixtures/tables/zh-table-borderless.pdf", "table", "pdfplumber"),
        ("benchmarks/fixtures/edge/zh-empty.pdf", "manuscript", "mineru"),
        ("benchmarks/fixtures/edge/corrupt.pdf", "manuscript", "mineru"),
    ]
    failed = 0
    for rel, goal, expected in cases:
        path = root / rel
        if not path.exists():
            print(f"SKIP {rel}: missing")
            continue
        result = route(path, goal)
        ok = result["intended"] == expected
        print(f"{'OK  ' if ok else 'FAIL'} {rel} goal={goal} intended={result['intended']} expected={expected}")
        failed += 0 if ok else 1

    # Path with spaces + CJK; should not crash and should still classify as PDF.
    src = root / "benchmarks" / "fixtures" / "zh-text-layer.pdf"
    if src.exists():
        with tempfile.TemporaryDirectory(prefix="docarbiter-space-") as tmp:
            spaced = Path(tmp) / "space name 中文.pdf"
            shutil.copyfile(src, spaced)
            result = route(spaced, "speed")
            ok = result["intended"] == "liteparse"
            print(f"{'OK  ' if ok else 'FAIL'} path with spaces+CJK intended={result['intended']}")
            failed += 0 if ok else 1
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Executable docarbiter routing table.")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--goal", choices=["speed", "manuscript", "text", "table", "table-structure", "rag", "ocr"], default="speed")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.file:
        ap.error("file is required unless --selftest is used")
    path = Path(args.file)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2
    result = route(path, args.goal)
    if args.json:
        print(json.dumps({"file": str(path), **result}, ensure_ascii=False, indent=2))
    else:
        print_human(path, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
