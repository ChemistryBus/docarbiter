#!/usr/bin/env python3
"""Page-structure regression for MinerU output.

This checks page markers, page order, blank-page preservation, and selected-page
numbering. It is deliberately separate from scripts/bench.py: page structure and
OCR character error rate are different measurements.

The sample is built from repository fixtures only (no user documents):
  page 1: zh-scan.pdf   (scanned image)
  page 2: zh-empty.pdf  (blank page)
  page 3: zh-scan.pdf   (scanned image)
  page 4: zh-scan.pdf   (scanned image)

Run:
    python3 -I scripts/check_pagemarkers.py
    python3 -I scripts/check_pagemarkers.py --pdf my-sample.pdf --keep

Exit codes: 0 = pass or skipped (MinerU not installed); 1 = regression.
"""
from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES = REPO_ROOT / "benchmarks" / "fixtures"
MARKER = re.compile(r"<!--\s*page\s+(\d+)\s+of\s+(\d+)\s*-->", re.IGNORECASE)


def run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )


def build_sample(workdir: Path) -> Path:
    parts = [
        FIXTURES / "zh-scan.pdf",
        FIXTURES / "edge" / "zh-empty.pdf",
        FIXTURES / "zh-scan.pdf",
        FIXTURES / "zh-scan.pdf",
    ]
    for part in parts:
        if not part.exists():
            raise SystemExit(f"missing fixture: {part}")
    out = workdir / "page-marker-sample.pdf"

    if shutil.which("pdfunite"):
        proc = run([shutil.which("pdfunite"), *map(str, parts), str(out)], 60)
    elif shutil.which("qpdf"):
        proc = run(
            [shutil.which("qpdf"), "--empty", "--pages", *map(str, parts), "--", str(out)],
            60,
        )
    else:
        raise SystemExit("need pdfunite or qpdf to build the 4-page sample")
    if proc.returncode != 0 or not out.exists():
        raise SystemExit(f"could not build sample: {proc.stderr.strip()}")

    if shutil.which("pdfinfo"):
        info = run([shutil.which("pdfinfo"), str(out)], 20)
        match = re.search(r"^Pages:\s+(\d+)", info.stdout, re.MULTILINE)
        if match and int(match.group(1)) != 4:
            raise SystemExit(f"sample has {match.group(1)} pages, expected 4")
    return out


def mineru_cmd() -> list[str] | None:
    if shutil.which("mineru-doc"):
        return ["mineru-doc"]
    if shutil.which("mineru"):
        return ["mineru", "parse"]
    return None


def find_markdown(workdir: Path, expected: Path) -> Path | None:
    if expected.exists():
        return expected
    files = sorted(workdir.rglob("*.md"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def extract(cmd: list[str], pdf: Path, pages: str, out: Path, workdir: Path, timeout: int) -> str:
    proc = run([*cmd, str(pdf), "--pages", pages, "-o", str(out)], timeout)
    md = find_markdown(workdir, out)
    if proc.returncode != 0 or md is None:
        raise SystemExit(
            f"MinerU failed for --pages {pages} (rc={proc.returncode})\n"
            f"stderr:\n{proc.stderr[-2000:]}"
        )
    return md.read_text(encoding="utf-8", errors="replace")


def split_pages(markdown: str) -> list[tuple[int, int, str]]:
    matches = list(MARKER.finditer(markdown))
    pages: list[tuple[int, int, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        pages.append((int(match.group(1)), int(match.group(2)), markdown[start:end]))
    return pages


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text)


def main() -> int:
    ap = argparse.ArgumentParser(description="Check MinerU page markers and selected-page numbering.")
    ap.add_argument("--pdf", help="use this PDF instead of the built-in 4-page sample")
    ap.add_argument("--keep", action="store_true", help="keep the temp work directory")
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per MinerU run")
    args = ap.parse_args()

    cmd = mineru_cmd()
    if cmd is None:
        print("SKIP: mineru-doc / mineru is not installed")
        return 0

    tmp = Path(tempfile.mkdtemp(prefix="docarbiter-pagemarkers-"))
    try:
        pdf = Path(args.pdf) if args.pdf else build_sample(tmp)
        if not pdf.exists():
            raise SystemExit(f"missing PDF: {pdf}")

        full_md = extract(cmd, pdf, "all", tmp / "full.md", tmp, args.timeout)
        full = split_pages(full_md)
        numbers = [page for page, _, _ in full]
        totals = {total for _, total, _ in full}
        failures: list[str] = []

        if numbers != [1, 2, 3, 4]:
            failures.append(f"full export markers are {numbers}, expected [1, 2, 3, 4]")
        if totals != {4}:
            failures.append(f"full export totals are {sorted(totals)}, expected [4]")
        if len(full) == 4 and len(norm(full[1][2])) >= 50:
            failures.append("blank page 2 is not preserved as blank")
        for page, _, body in full:
            if page in (1, 3, 4) and len(norm(body)) < 50:
                failures.append(f"scanned page {page} produced no body text")

        selected_md = extract(cmd, pdf, "3-4", tmp / "selected.md", tmp, args.timeout)
        selected = split_pages(selected_md)
        selected_numbers = [page for page, _, _ in selected]
        selected_totals = {total for _, total, _ in selected}
        if selected_numbers != [3, 4]:
            failures.append(f"selected export markers are {selected_numbers}, expected [3, 4]")
        if selected_totals != {4}:
            failures.append(f"selected export totals are {sorted(selected_totals)}, expected [4]")

        full_by_page = {page: body for page, _, body in full}
        for page, _, body in selected:
            if page not in full_by_page:
                failures.append(f"selected page {page} has no counterpart in the full export")
                continue
            left, right = norm(body), norm(full_by_page[page])
            if not left or not right:
                failures.append(f"page {page} body is empty in one export")
                continue
            ratio = difflib.SequenceMatcher(None, left, right, autojunk=False).ratio()
            if ratio < 0.90:
                failures.append(f"page {page} differs between full and selected export (ratio={ratio:.2f})")

        if failures:
            print("FAIL")
            for failure in failures:
                print(f"  - {failure}")
            print(f"workdir: {tmp}")
            return 1
        print(f"PASS: full markers {numbers}, selected markers {selected_numbers}, blank page preserved")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(tmp, ignore_errors=True)
        else:
            print(f"kept: {tmp}")


if __name__ == "__main__":
    raise SystemExit(main())
