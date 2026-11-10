#!/usr/bin/env python3
"""Executable version of docarbiter's routing table.

This is the testable engineering core: given a file, probe it and print the
route, reason, command, and fallbacks. Stdlib only; uses the system pdftotext
for PDF probing.

Usage:
    python3 -I scripts/route.py FILE [--goal speed|manuscript|text|table|table-structure|rag|ocr]
                                     [--page N] [--json]
    python3 -I scripts/route.py --selftest
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
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

# Keep probing cheap: short documents are checked page by page; long documents
# sample the first, middle, and last pages. This is the page budget.
SHORT_DOC_PAGES = 20
SAMPLE_HEAD = 3
SAMPLE_MIDDLE = 2
SAMPLE_TAIL = 2


def _cmd(name: str) -> bool:
    return shutil.which(name) is not None


def _py(mod: str) -> bool:
    return importlib.util.find_spec(mod) is not None


def _mineru_entry() -> str | None:
    """The actual MinerU executable, so availability and commands agree."""
    if _cmd("mineru-doc"):
        return "mineru-doc"
    if _cmd("mineru"):
        return "mineru parse"
    return None


def _entry(tool: str) -> str | None:
    """Return the executable entry point for a routed tool, or None.

    Every tool that `_available` accepts must also be handled by
    `command_for`; this table is the single place that decides both.
    """
    return {
        "mineru": _mineru_entry(),
        "liteparse": "liteparse-doc" if _cmd("liteparse-doc") else None,
        "pdftotext": "pdftotext" if _cmd("pdftotext") else None,
        "pdfplumber": "python3" if _py("pdfplumber") else None,
        "docling": "docling" if _cmd("docling") else None,
        "markitdown": "markitdown" if _cmd("markitdown") else None,
        "rapidocr": "python3" if _py("rapidocr") else None,
        "paddleocr": "python3" if _py("paddleocr") else None,
        "tesseract": "tesseract" if _cmd("tesseract") else None,
        "ocrmypdf+mineru": (
            "ocrmypdf" if _cmd("ocrmypdf") and _mineru_entry() else None
        ),
        "olmocr": "olmocr" if _cmd("olmocr") else None,
        "qpdf": "qpdf" if _cmd("qpdf") else None,
    }.get(tool)


def _available(tool: str) -> bool:
    return _entry(tool) is not None


def _page_count(path: Path) -> int | None:
    if _cmd("pdfinfo"):
        try:
            proc = subprocess.run(
                ["pdfinfo", str(path)], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=20,
            )
        except Exception:  # noqa: BLE001 - a bad PDF must not crash the router
            proc = None
        if proc is not None and proc.returncode == 0:
            match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
            if match:
                return int(match.group(1))
    if _cmd("qpdf"):
        try:
            proc = subprocess.run(
                ["qpdf", "--show-npages", str(path)], capture_output=True, text=True,
                encoding="utf-8", errors="replace", timeout=20,
            )
        except Exception:  # noqa: BLE001
            return None
        if proc.returncode == 0 and proc.stdout.strip().isdigit():
            return int(proc.stdout.strip())
    return None


def _image_pages(path: Path) -> set[int] | None:
    """Pages that contain raster images, from `pdfimages -list`.

    Returns None when pdfimages is unavailable or cannot read the file.
    """
    if not _cmd("pdfimages"):
        return None
    try:
        proc = subprocess.run(
            ["pdfimages", "-list", str(path)], capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=30,
        )
    except Exception:  # noqa: BLE001
        return None
    if proc.returncode != 0:
        return None
    pages: set[int] = set()
    for line in proc.stdout.splitlines():
        if line.lstrip().lower().startswith("page"):
            continue
        match = re.match(r"\s*(\d+)\s", line)
        if match:
            pages.add(int(match.group(1)))
    return pages


def _pdf_has_image(path: Path) -> bool:
    """Cheap fallback when pdfimages is not available: look for /Image."""
    try:
        with path.open("rb") as fh:
            if b"/Image" in fh.read(4 * 1024 * 1024):
                return True
            try:
                fh.seek(-4 * 1024 * 1024, 2)
            except OSError:
                return False
            return b"/Image" in fh.read()
    except OSError:
        return False


def _classify_text(text: str) -> dict:
    chars = len("".join(text.split()))
    bad = sum(1 for c in text if c == "�" or 0xE000 <= ord(c) <= 0xF8FF)
    ctrl = sum(1 for c in text if unicodedata.category(c) == "Cc" and c not in "\n\r\t\f\v")
    cjk = sum(
        1 for c in text
        if 0x3400 <= ord(c) <= 0x4DBF or 0x4E00 <= ord(c) <= 0x9FFF
        or 0x20000 <= ord(c) <= 0x2FA1F
    )
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    ratio = (bad + ctrl) / max(chars, 1)
    if chars == 0:
        status = "empty"
    elif ratio > 0.10:
        status = "garbled"
    elif chars < 50:
        status = "scan"
    else:
        status = "usable"
    return {
        "status": status, "chars": chars, "bad": bad, "ctrl": ctrl,
        "cjk": cjk, "latin": latin, "bad_ratio": round(ratio, 4),
    }


def _pdftotext_range(path: Path, first: int, last: int) -> tuple[str | None, str | None]:
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", str(first), "-l", str(last), str(path), "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
    if proc.returncode != 0:
        return None, (proc.stderr or "pdftotext failed").strip()[:200]
    return proc.stdout, None


def _sample_pages(page_count: int) -> list[int]:
    if page_count <= SHORT_DOC_PAGES:
        return list(range(1, page_count + 1))
    picks = set(range(1, min(SAMPLE_HEAD, page_count) + 1))
    middle = page_count // 2
    last_middle = min(middle + SAMPLE_MIDDLE - 1, page_count)
    picks.update(range(middle, last_middle + 1))
    picks.update(range(max(1, page_count - SAMPLE_TAIL + 1), page_count + 1))
    return sorted(p for p in picks if 1 <= p <= page_count)


def _aggregate_status(pages: list[dict]) -> str:
    statuses = [p["status"] for p in pages]
    if not statuses or all(s == "error" for s in statuses):
        return "probe-error"
    if all(s == "usable" for s in statuses):
        return "usable"
    if "usable" in statuses:
        return "mixed"
    if "garbled" in statuses:
        return "garbled"
    if "scan" in statuses:
        return "scan"
    if all(s == "empty" for s in statuses):
        return "empty"
    if "error" in statuses:
        return "probe-error"
    return "unknown"


def probe_pdf(path: Path) -> dict:
    if not _cmd("pdftotext"):
        return {
            "status": "no-pdftotext", "chars": 0, "bad": 0, "ctrl": 0, "cjk": 0,
            "latin": 0, "bad_ratio": 0.0, "language": "unknown",
            "page_count": None, "sampled": "none", "coverage": "pdftotext missing",
            "pages": [],
        }

    page_count = _page_count(path)
    image_pages = _image_pages(path)
    image_fallback: bool | None = None
    pages: list[dict] = []
    error: str | None = None

    def _has_image(page: int | str) -> bool:
        nonlocal image_fallback
        if image_pages is not None:
            return bool(image_pages) if not isinstance(page, int) else page in image_pages
        if image_fallback is None:
            image_fallback = _pdf_has_image(path)
        return image_fallback

    if page_count is None:
        text, error = _pdftotext_range(path, 1, 3)
        if text is not None:
            info = _classify_text(text)
            if info["status"] == "empty" and _has_image("1-3"):
                info["status"] = "scan"
            pages.append({"page": "1-3", **info})
        else:
            pages.append({"page": "1-3", "status": "error", "chars": 0,
                          "bad": 0, "ctrl": 0, "cjk": 0, "latin": 0,
                          "bad_ratio": 0.0, "error": error})
        sampled = "1-3"
        coverage = "pages 1-3 (page count unknown)"
    else:
        sample = _sample_pages(page_count)
        for page in sample:
            text, err = _pdftotext_range(path, page, page)
            if text is None:
                pages.append({"page": page, "status": "error", "chars": 0,
                              "bad": 0, "ctrl": 0, "cjk": 0, "latin": 0,
                              "bad_ratio": 0.0, "error": err})
            else:
                info = _classify_text(text)
                if info["status"] == "empty" and _has_image(page):
                    info["status"] = "scan"
                pages.append({"page": page, **info})
        sampled = ",".join(str(p) for p in sample)
        coverage = f"{len(sample)}/{page_count} pages sampled ({sampled})"
        if pages and all(p["status"] == "error" for p in pages):
            error = pages[0].get("error")

    totals = {
        key: sum(int(p.get(key, 0)) for p in pages)
        for key in ("chars", "bad", "ctrl", "cjk", "latin")
    }
    ratio = (totals["bad"] + totals["ctrl"]) / max(totals["chars"], 1)
    if totals["cjk"] > totals["latin"]:
        language = "zh"
    elif totals["latin"] > totals["cjk"]:
        language = "en"
    elif totals["cjk"] == totals["latin"] == 0:
        language = "unknown"
    else:
        language = "mixed"

    result = {
        "status": _aggregate_status(pages),
        "chars": totals["chars"], "bad": totals["bad"], "ctrl": totals["ctrl"],
        "cjk": totals["cjk"], "latin": totals["latin"],
        "bad_ratio": round(ratio, 4), "language": language,
        "page_count": page_count, "sampled": sampled,
        "coverage": coverage,
        "pages": [
            {"page": p["page"], "status": p["status"], "chars": p["chars"],
             "bad_ratio": p["bad_ratio"]}
            for p in pages
        ],
    }
    if error:
        result["error"] = error
    return result


def _select(chain: list[str]) -> str:
    for tool in chain:
        if tool == "inspect" or _available(tool):
            return tool
    return "install-needed"


def _route_pdf(path: Path, goal: str, page: int = 1) -> dict:
    probe = probe_pdf(path)
    status = probe["status"]
    intended: str
    reason: str
    fallback: list[str]

    if status == "no-pdftotext":
        intended = "mineru"
        reason = "pdftotext is unavailable, so the text layer cannot be probed; MinerU is the OCR-capable fallback"
        fallback = ["rapidocr", "docling"]
    elif status == "probe-error":
        intended = "inspect"
        reason = "the PDF probe failed (damaged, encrypted, or unreadable pages); verify the file before extraction"
        fallback = ["qpdf"]
    elif status == "empty":
        if goal == "ocr":
            intended = "mineru"
            reason = "the sampled pages are blank to pdftotext; OCR was requested explicitly, so MinerU will re-check visually"
            fallback = ["rapidocr"]
        else:
            intended = "inspect"
            reason = "no extractable text on the sampled pages; the file may be blank, encrypted, or image-only — confirm before OCR"
            fallback = ["mineru"]
    elif status == "scan":
        if goal in ("table", "table-structure"):
            intended = "docling" if goal == "table-structure" else "pdfplumber"
            reason = "sparse text layer but a table goal takes precedence; verify cells, and switch to MinerU if the table is image-only"
            fallback = ["mineru", "rapidocr"] if goal == "table-structure" else ["docling", "mineru"]
        else:
            intended = "mineru"
            reason = "no usable text layer; MinerU handles scans directly (OCRmyPDF+Tesseract is weaker for Chinese)"
            fallback = ["rapidocr", "ocrmypdf+mineru"]
    elif status == "garbled":
        intended = "mineru"
        reason = "CID / missing ToUnicode; the text layer is garbled, so MinerU OCR is the reliable path"
        fallback = ["rapidocr", "olmocr"]
    elif status == "mixed":
        if goal in ("table", "table-structure"):
            intended = "docling"
            reason = "mixed text layer (some sampled pages are scans or blank); Docling preserves table structure and can OCR the scanned pages"
            fallback = ["mineru", "pdfplumber"]
        else:
            intended = "mineru"
            reason = "mixed text layer: sampled pages include scans, blank pages, or garbled text; MinerU covers both text and scans"
            fallback = ["docling", "rapidocr"]
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
        intended = "inspect"
        reason = "the probe could not classify the PDF; inspect it before choosing an extractor"
        fallback = ["mineru", "qpdf"]

    if intended == "inspect":
        chain = ["inspect"] + ([t for t in fallback if _available(t)] if status == "probe-error" else [])
        selected = "qpdf" if status == "probe-error" and _available("qpdf") else "inspect"
    else:
        chain = [intended] + fallback
        selected = _select(chain)

    return {
        "kind": "pdf", "probe": probe, "goal": goal, "page": page,
        "intended": intended, "selected": selected, "reason": reason,
        "fallback": fallback, "chain": chain,
    }


def route(path: Path, goal: str, page: int = 1) -> dict:
    suffix = path.suffix.lower()
    if suffix in PDF:
        return _route_pdf(path, goal, page)
    if suffix in IMAGE:
        chain = ["rapidocr", "paddleocr", "tesseract"]
        return {"kind": "image", "intended": "rapidocr", "selected": _select(chain),
                "reason": "single image OCR; RapidOCR is the lightweight Chinese-first default",
                "fallback": ["paddleocr", "tesseract"], "chain": chain}
    if suffix in OFFICE or suffix in WEB:
        chain = ["docling", "markitdown"]
        return {"kind": "office/web", "intended": "docling", "selected": _select(chain),
                "reason": "multi-format structure, tables, chunks, LaTeX; markitdown is single-column only",
                "fallback": ["markitdown"], "chain": chain}
    if suffix in AV:
        chain = ["docling"]
        return {"kind": "audio/video", "intended": "docling", "selected": _select(chain),
                "reason": "audio/video transcription is a Docling capability",
                "fallback": [], "chain": chain}
    return {"kind": "unknown", "intended": "inspect", "selected": "inspect",
            "reason": f"unknown extension {suffix or '(none)'}", "fallback": [], "chain": []}


def command_for(path: Path, result: dict) -> str:
    tool = result["selected"]
    q = shlex.quote(str(path))
    probe = result.get("probe") or {}
    page = int(result.get("page") or 1)

    if tool == "mineru":
        entry = _mineru_entry() or "mineru-doc"
        return f"{entry} {q} --pages all -o out.md"
    if tool == "liteparse":
        return f"liteparse-doc {q} --pages all"
    if tool == "pdftotext":
        return f"pdftotext {q} -"
    if tool == "docling":
        if result.get("goal") == "table-structure":
            page_range = f" --page-range {page}-{page}" if path.suffix.lower() == ".pdf" else ""
            return (
                f"mkdir -p out && docling convert {q} --from pdf --to md"
                f"{page_range} --output out/ --image-export-mode placeholder"
                f"  # complex table; adjust --page-range; add --no-ocr only for a clean text layer"
            )
        return f"docling convert {q} --to md --output out/ --image-export-mode placeholder"
    if tool == "markitdown":
        return f"markitdown {q} > out.md"
    if tool == "ocrmypdf+mineru":
        lang = "eng" if probe.get("language") == "en" else "chi_sim+eng"
        stem = shlex.quote(str(path.with_suffix("")))
        mineru = _mineru_entry() or "mineru-doc"
        return (
            f"ocrmypdf --language {lang} {q} {stem}-ocr.pdf && "
            f"{mineru} {stem}-ocr.pdf --pages all -o out.md"
        )
    if tool == "pdfplumber":
        code = (
            "import sys,pdfplumber;"
            "pdf=pdfplumber.open(sys.argv[1]);"
            "print(pdf.pages[int(sys.argv[2])-1].extract_tables())"
        )
        return f"python3 -c {shlex.quote(code)} {q} {page}"
    if tool == "rapidocr":
        if path.suffix.lower() == ".pdf":
            # RapidOCR takes images, not PDFs. Render pages first so a fallback
            # selected for a scanned PDF is still an executable command.
            code = (
                "import glob,sys;"
                "from rapidocr import RapidOCR;"
                "engine=RapidOCR();"
                "[print(t) for f in sorted(glob.glob(sys.argv[1])) "
                "for t in (engine(f).txts or [])]"
            )
            return (
                f"mkdir -p rapidocr-pages && pdftoppm -png -r 150 {q} rapidocr-pages/page && "
                f"python3 -c {shlex.quote(code)} 'rapidocr-pages/page*.png'"
            )
        code = (
            "import sys;"
            "from rapidocr import RapidOCR;"
            "print(RapidOCR()(sys.argv[1]).txts)"
        )
        return f"python3 -c {shlex.quote(code)} {q}"
    if tool == "paddleocr":
        code = (
            "import sys;"
            "from paddleocr import PaddleOCR;"
            'print(PaddleOCR(lang="ch").predict(sys.argv[1]))'
        )
        return f"python3 -c {shlex.quote(code)} {q}  # verify the API with: paddleocr --help"
    if tool == "tesseract":
        return f"tesseract {q} stdout -l chi_sim+eng"
    if tool == "qpdf":
        return f"qpdf --check {q}"
    if tool == "inspect":
        return f"# inspect {q} first (open it or run qpdf --check); no extraction until the probe result is explained"
    return "# install the intended tool first; see docs/tool-registry.md"


def print_human(path: Path, result: dict) -> None:
    print(f"file={path}")
    probe = result.get("probe")
    if probe:
        print(
            f"probe: status={probe['status']} language={probe['language']} "
            f"pages={probe.get('sampled', '-')} chars={probe['chars']} "
            f"cjk={probe['cjk']} bad={probe['bad']} ctrl={probe['ctrl']} "
            f"bad_ratio={probe['bad_ratio']:.2%}"
        )
        if probe.get("pages"):
            detail = ", ".join(f"{p['page']}:{p['status']}" for p in probe["pages"])
            print(f"sample: {detail} ({probe.get('coverage', '-')})")
        if probe.get("error"):
            print(f"probe-error: {probe['error']}")
    print(f"route: intended={result['intended']} selected={result['selected']} goal={result.get('goal', '-')}")
    if result["selected"] not in (result["intended"], "inspect", "install-needed"):
        print(f"note: {result['intended']} is not installed; selected {result['selected']}")
    print(f"reason: {result['reason']}")
    print(f"command: {command_for(path, result)}")
    if result.get("fallback"):
        print(f"fallback: {', '.join(result['fallback'])}")
    if result["selected"] == "install-needed":
        print("warning: intended tool is not installed; run ./scripts/install.sh --profile core")


def _assert_command_is_complete(cmd: str) -> str | None:
    """Reject commands that still contain a literal placeholder identifier."""
    for marker in ("image_path", "<file>", "{path}", "{file}", "FILE.pdf"):
        if marker in cmd:
            return f"unsubstituted placeholder {marker!r}"
    return None


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
        ("benchmarks/fixtures/tables/zh-table-merged.pdf", "table-structure", "docling"),
        ("benchmarks/fixtures/edge/zh-empty.pdf", "manuscript", "inspect"),
        ("benchmarks/fixtures/edge/corrupt.pdf", "manuscript", "inspect"),
    ]
    failed = 0
    for rel, goal, expected in cases:
        path = root / rel
        if not path.exists():
            print(f"SKIP {rel}: missing")
            continue
        result = route(path, goal)
        ok = result["intended"] == expected
        cmd = command_for(path, result)
        problem = _assert_command_is_complete(cmd)
        if problem:
            ok = False
        print(
            f"{'OK  ' if ok else 'FAIL'} {rel} goal={goal} "
            f"intended={result['intended']} selected={result['selected']} expected={expected}"
            + (f" ({problem})" if problem else "")
        )
        failed += 0 if ok else 1

    # Path with spaces + CJK; should not crash and should still classify as PDF.
    src = root / "benchmarks" / "fixtures" / "zh-text-layer.pdf"
    if src.exists():
        with tempfile.TemporaryDirectory(prefix="docarbiter-space-") as tmp:
            spaced = Path(tmp) / "space name 中文.pdf"
            shutil.copyfile(src, spaced)
            result = route(spaced, "speed")
            cmd = command_for(spaced, result)
            ok = result["intended"] == "liteparse" and _assert_command_is_complete(cmd) is None
            print(f"{'OK  ' if ok else 'FAIL'} path with spaces+CJK intended={result['intended']}")
            failed += 0 if ok else 1

    # Image and Office branches: routing must not depend on a real file body.
    with tempfile.TemporaryDirectory(prefix="docarbiter-suffix-") as tmp:
        for suffix, goal, expected in ((".png", "speed", "rapidocr"), (".docx", "speed", "docling")):
            path = Path(tmp) / f"sample{suffix}"
            path.write_bytes(b"")
            result = route(path, goal)
            cmd = command_for(path, result)
            ok = result["intended"] == expected and _assert_command_is_complete(cmd) is None
            print(f"{'OK  ' if ok else 'FAIL'} suffix {suffix} intended={result['intended']} expected={expected}")
            failed += 0 if ok else 1

    # A file that is not a PDF at all must not be sent to MinerU.
    with tempfile.TemporaryDirectory(prefix="docarbiter-broken-") as tmp:
        broken = Path(tmp) / "broken.pdf"
        broken.write_bytes(b"this is not a pdf\n")
        result = route(broken, "manuscript")
        ok = result["intended"] == "inspect" and result["probe"]["status"] == "probe-error"
        print(f"{'OK  ' if ok else 'FAIL'} broken PDF status={result['probe']['status']} intended={result['intended']}")
        failed += 0 if ok else 1

    # The pdfplumber command must survive spaces, quotes, $, and CJK in the path.
    if _available("pdfplumber"):
        with tempfile.TemporaryDirectory(prefix="docarbiter-quote-") as tmp:
            tricky = Path(tmp) / 'quote" $dollar 中文.pdf'
            shutil.copyfile(root / "benchmarks" / "fixtures" / "zh-table.pdf", tricky)
            result = route(tricky, "table")
            if result["selected"] == "pdfplumber":
                cmd = command_for(tricky, result)
                proc = subprocess.run(
                    ["bash", "-c", cmd], capture_output=True, text=True, timeout=60,
                )
                ok = proc.returncode == 0 and "NameError" not in proc.stderr
                print(f"{'OK  ' if ok else 'FAIL'} pdfplumber command with quotes/$/CJK rc={proc.returncode}")
                failed += 0 if ok else 1
            else:
                print(f"SKIP pdfplumber command: selected={result['selected']}")

    # MinerU availability must match the command entry point.
    entry = _mineru_entry()
    if entry:
        result = route(root / "benchmarks" / "fixtures" / "zh-scan.pdf", "manuscript")
        if result["selected"] == "mineru":
            cmd = command_for(root / "benchmarks" / "fixtures" / "zh-scan.pdf", result)
            ok = cmd.startswith(entry + " ")
            print(f"{'OK  ' if ok else 'FAIL'} mineru entry={entry!r} command starts with it")
            failed += 0 if ok else 1

    # Only `mineru` (no wrapper) must still produce a runnable command.
    original_cmd = globals()["_cmd"]
    try:
        globals()["_cmd"] = lambda name: name == "mineru"
        only_mineru = _mineru_entry()
        cmd = command_for(Path("plain.pdf"), {"selected": "mineru", "goal": "manuscript"})
        ok = only_mineru == "mineru parse" and cmd.startswith("mineru parse ")
        print(f"{'OK  ' if ok else 'FAIL'} mineru without wrapper entry={only_mineru!r}")
        failed += 0 if ok else 1
    finally:
        globals()["_cmd"] = original_cmd

    # Fallback selection must consider every tool in the chain, not just the first.
    original_available = globals()["_available"]
    try:
        globals()["_available"] = lambda tool: tool == "markitdown"
        office = _select(["docling", "markitdown"])
        globals()["_available"] = lambda tool: tool == "tesseract"
        image = _select(["rapidocr", "paddleocr", "tesseract"])
        ok = office == "markitdown" and image == "tesseract"
        print(f"{'OK  ' if ok else 'FAIL'} fallback selection office={office} image={image}")
        failed += 0 if ok else 1
    finally:
        globals()["_available"] = original_available

    # RapidOCR must receive the actual path, never the literal `image_path`.
    rapid_cmd = command_for(Path("/tmp/a b.png"), {"selected": "rapidocr"})
    ok = "image_path" not in rapid_cmd and "/tmp/a b.png" in rapid_cmd
    print(f"{'OK  ' if ok else 'FAIL'} rapidocr command interpolates the path")
    failed += 0 if ok else 1

    # A RapidOCR fallback selected for a PDF must render pages first.
    rapid_pdf = command_for(Path("/tmp/scan.pdf"), {"selected": "rapidocr"})
    ok = "pdftoppm" in rapid_pdf and "image_path" not in rapid_pdf
    print(f"{'OK  ' if ok else 'FAIL'} rapidocr PDF command renders pages first")
    failed += 0 if ok else 1

    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Executable docarbiter routing table.")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--goal", choices=["speed", "manuscript", "text", "table", "table-structure", "rag", "ocr"], default="speed")
    ap.add_argument("--page", type=int, default=1, help="target page for page-specific commands (1-based)")
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
    if args.page < 1:
        ap.error("--page must be >= 1")
    result = route(path, args.goal, args.page)
    if args.json:
        print(json.dumps({"file": str(path), **result}, ensure_ascii=False, indent=2))
    else:
        print_human(path, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
