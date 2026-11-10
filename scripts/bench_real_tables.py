#!/usr/bin/env python3
"""Per-cell CER for real private tables.

This is separate from scripts/bench_tables.py (synthetic fixtures, pdfplumber
only). It compares pdfplumber, Docling, and MinerU against a hand-checked
truth JSON and reports per-cell CER plus exact-match accuracy.

Truth format: {"rows": [[...], ...]}, with "" for cells covered by a merged
cell. Keep the PDFs and truth under benchmarks/private/ (gitignored); do not
commit real document content.

Run:
    python3 -I scripts/bench_real_tables.py
    python3 -I scripts/bench_real_tables.py --dir benchmarks/private/tables \
        --tools pdfplumber,docling,mineru
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import shutil
import statistics
import subprocess
import sys
import unicodedata
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

try:
    from rapidfuzz.distance import Levenshtein as _RFLev
except ImportError:  # optional; falls back to pure Python
    _RFLev = None

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "benchmarks" / "private" / "tables"
DEFAULT_CACHE = DEFAULT_DIR / "cache"
DEFAULT_OUT = ROOT / "benchmarks" / "results" / "real-tables"

TEXT_SETTINGS = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "intersection_tolerance": 5,
}


# ---------------------------------------------------------------- normalise / CER
def norm(text: str, strip_punct: bool = False) -> str:
    text = unicodedata.normalize("NFC", text or "")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"-{2,}", "-", text)
    text = text.translate(str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"}))
    text = re.sub(r"\s+", "", text)
    if strip_punct:
        text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return text


def levenshtein(a: str, b: str) -> int:
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


def cell_cer(truth_cell: str, pred_cell: str, strip_punct: bool) -> float:
    truth = norm(truth_cell, strip_punct)
    pred = norm(pred_cell, strip_punct)
    if not truth:
        return 1.0 if pred else 0.0
    return levenshtein(truth, pred) / len(truth)


def _pad(grid: list[list[str]], rows: int, cols: int) -> list[list[str]]:
    out = []
    for r in range(rows):
        row = list(grid[r]) if r < len(grid) else []
        row = (row + [""] * cols)[:cols]
        out.append(row)
    return out


def compare(truth: list[list[str]], pred: list[list[str]], strip_punct: bool) -> dict:
    rows = len(truth)
    cols = max((len(r) for r in truth), default=0)
    t = _pad(truth, rows, cols)
    p = _pad(pred, rows, cols)

    exact = 0
    nonempty_exact = 0
    nonempty_total = 0
    missing = 0
    spurious = 0
    micro_dist = 0
    micro_den = 0
    macro: list[float] = []
    row_hits = 0

    for r in range(rows):
        row_ok = True
        for c in range(cols):
            tv = norm(t[r][c], strip_punct)
            pv = norm(p[r][c], strip_punct)
            if tv == pv:
                exact += 1
                if tv:
                    nonempty_exact += 1
            else:
                row_ok = False
            if tv:
                nonempty_total += 1
                dist = levenshtein(tv, pv)
                micro_dist += dist
                micro_den += len(tv)
                macro.append(dist / len(tv))
                if not pv:
                    missing += 1
            elif pv:
                spurious += 1
                micro_dist += len(pv)
        row_hits += 1 if row_ok else 0

    total_cells = rows * cols
    return {
        "truth_rows": rows,
        "truth_cols": cols,
        "cell_total": total_cells,
        "cell_exact": exact,
        "cell_accuracy": exact / total_cells if total_cells else 0.0,
        "nonempty_truth_cells": nonempty_total,
        "nonempty_exact": nonempty_exact,
        "nonempty_accuracy": nonempty_exact / nonempty_total if nonempty_total else 0.0,
        "micro_cer": micro_dist / micro_den if micro_den else 0.0,
        "macro_cer": statistics.mean(macro) if macro else 0.0,
        "median_cell_cer": statistics.median(macro) if macro else 0.0,
        "max_cell_cer": max(macro) if macro else 0.0,
        "missing_cells": missing,
        "spurious_cells": spurious,
        "row_accuracy": row_hits / rows if rows else 0.0,
    }


# ---------------------------------------------------------------- extractors
def pdfplumber_tables(pdf: Path, strategy: str) -> list[list[list[str]]]:
    import pdfplumber  # imported lazily so --help works without it

    tables: list[list[list[str]]] = []
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            if strategy == "text":
                found = page.extract_tables(table_settings=TEXT_SETTINGS)
                found = [[row for row in table if any(cell not in (None, "") for cell in row)]
                         for table in found]
                found = [table for table in found if table]
            else:
                found = page.extract_tables()
            tables.extend([[list(row) for row in table] for table in found])
    return tables


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )


def _choose(tables: list[list[list[str]]], rows: int, cols: int) -> list[list[str]]:
    if not tables:
        return []
    return min(
        tables,
        key=lambda t: abs(len(t) - rows) + abs(max((len(r) for r in t), default=0) - cols),
    )


def docling_grid(pdf: Path, truth: list[list[str]], cache: Path, timeout: int) -> list[list[str]]:
    outdir = cache / pdf.stem / "docling"
    outdir.mkdir(parents=True, exist_ok=True)
    json_path = outdir / f"{pdf.stem}.json"
    if not json_path.exists():
        proc = _run(
            ["docling", "convert", str(pdf), "--to", "json", "--output", str(outdir),
             "--image-export-mode", "placeholder"],
            timeout,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "docling failed")
    if not json_path.exists():
        raise RuntimeError("docling produced no JSON")

    data = json.loads(json_path.read_text(encoding="utf-8"))
    truth_rows = len(truth)
    truth_cols = max((len(r) for r in truth), default=0)
    candidates: list[list[list[str]]] = []
    for table in data.get("tables", []):
        body = table.get("data", {})
        rows = int(body.get("num_rows") or 0)
        cols = int(body.get("num_cols") or 0)
        if rows <= 0 or cols <= 0:
            continue
        grid = [["" for _ in range(cols)] for _ in range(rows)]
        for cell in body.get("table_cells", []):
            r = int(cell.get("start_row_offset_idx") or 0)
            c = int(cell.get("start_col_offset_idx") or 0)
            if 0 <= r < rows and 0 <= c < cols:
                # Covered merged positions stay ""; the top-left carries the text.
                grid[r][c] = cell.get("text") or ""
        candidates.append(grid)
    return _choose(candidates, truth_rows, truth_cols)


class _HTMLTableParser(HTMLParser):
    """Collect <table> rows/cells, preserving rowspan/colspan and <sup> text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[dict]] = []
        self._rows: list[list[dict]] | None = None
        self._cell: dict | None = None
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "table":
            self._depth += 1
            if self._depth == 1:
                self._rows = []
        elif self._depth == 1 and tag == "tr":
            self._rows.append([])
        elif self._depth == 1 and tag in ("td", "th"):
            attrs = dict(attrs)
            self._cell = {
                "text": "",
                "rowspan": int(attrs.get("rowspan") or 1),
                "colspan": int(attrs.get("colspan") or 1),
            }
        elif self._cell is not None and tag == "br":
            self._cell["text"] += "\n"

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell["text"] += data

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in ("td", "th") and self._cell is not None and self._rows is not None:
            self._rows[-1].append(self._cell)
            self._cell = None
        elif tag == "tr" and self._rows is not None:
            pass
        elif tag == "table":
            if self._depth == 1 and self._rows is not None:
                self.tables.append(self._rows)
                self._rows = None
            self._depth = max(0, self._depth - 1)


def _expand_html_rows(rows: list[list[dict]]) -> list[list[str]]:
    occupied: set[tuple[int, int]] = set()
    placed: dict[tuple[int, int], str] = {}
    max_col = 0
    for r, row in enumerate(rows):
        col = 0
        for cell in row:
            while (r, col) in occupied:
                col += 1
            text = html.unescape(cell["text"]).strip()
            placed[(r, col)] = text
            for dr in range(cell["rowspan"]):
                for dc in range(cell["colspan"]):
                    occupied.add((r + dr, col + dc))
            max_col = max(max_col, col + cell["colspan"])
            col += cell["colspan"]
    max_row = max((r for r, _ in occupied), default=-1) + 1
    return [[placed.get((r, c), "") for c in range(max_col)] for r in range(max_row)]


def _pipe_tables(markdown: str) -> list[list[list[str]]]:
    tables: list[list[list[str]]] = []
    current: list[list[str]] = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if re.fullmatch(r"\|[\s:|-]+\|", stripped):
                continue
            cells = [
                html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                for c in stripped.strip("|").split("|")
            ]
            current.append(cells)
        elif current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    return tables


def mineru_grid(pdf: Path, truth: list[list[str]], cache: Path, timeout: int) -> list[list[str]]:
    outdir = cache / pdf.stem / "mineru"
    outdir.mkdir(parents=True, exist_ok=True)
    out_md = outdir / "out.md"
    if not out_md.exists():
        if shutil.which("mineru-doc"):
            cmd = ["mineru-doc"]
        elif shutil.which("mineru"):
            cmd = ["mineru", "parse"]
        else:
            raise RuntimeError("mineru-doc / mineru is not installed")
        proc = _run([*cmd, str(pdf), "--pages", "all", "-o", str(out_md)], timeout)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "mineru failed")
    if not out_md.exists():
        raise RuntimeError("mineru produced no Markdown")

    markdown = out_md.read_text(encoding="utf-8", errors="replace")
    candidates: list[list[list[str]]] = []
    if "<table" in markdown.lower():
        parser = _HTMLTableParser()
        parser.feed(markdown)
        candidates.extend(_expand_html_rows(rows) for rows in parser.tables)
    if not candidates:
        candidates = _pipe_tables(markdown)
    truth_rows = len(truth)
    truth_cols = max((len(r) for r in truth), default=0)
    return _choose(candidates, truth_rows, truth_cols)


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Per-cell CER for real private tables.")
    ap.add_argument("--dir", default=str(DEFAULT_DIR), help="directory with PDFs and .truth.json")
    ap.add_argument("--cache", default=str(DEFAULT_CACHE), help="tool output cache")
    ap.add_argument("--out", default=None, help="results directory")
    ap.add_argument("--tools", default="pdfplumber,docling,mineru")
    ap.add_argument("--timeout", type=int, default=900, help="seconds per tool per page")
    args = ap.parse_args()

    src = Path(args.dir)
    cache = Path(args.cache)
    out = Path(args.out) if args.out else DEFAULT_OUT / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    tools = [t.strip() for t in args.tools.split(",") if t.strip()]

    pdfs = sorted(p for p in src.glob("*.pdf") if p.with_suffix(".truth.json").exists())
    if not pdfs:
        print(f"no PDF with .truth.json in {src}", file=sys.stderr)
        return 2

    rows: list[dict] = []
    for pdf in pdfs:
        truth = json.loads(pdf.with_suffix(".truth.json").read_text(encoding="utf-8"))["rows"]
        print(f"=== {pdf.name}: truth {len(truth)}x{max(len(r) for r in truth)} ===")
        for tool in tools:
            strategies: list[tuple[str, list[list[str]]]] = []
            try:
                if tool == "pdfplumber":
                    if shutil.which("python3") is None:
                        raise RuntimeError("python3 missing")
                    try:
                        import pdfplumber  # noqa: F401
                    except ImportError as exc:
                        raise RuntimeError(f"pdfplumber not installed: {exc}") from exc
                    for strategy in ("default", "text"):
                        tables = pdfplumber_tables(pdf, strategy)
                        strategies.append((strategy, _choose(tables, len(truth), max(len(r) for r in truth))))
                elif tool == "docling":
                    if not shutil.which("docling"):
                        raise RuntimeError("docling not installed")
                    strategies.append(("json", docling_grid(pdf, truth, cache, args.timeout)))
                elif tool == "mineru":
                    strategies.append(("markdown", mineru_grid(pdf, truth, cache, args.timeout)))
                else:
                    raise RuntimeError(f"unknown tool {tool}")
            except Exception as exc:  # noqa: BLE001 - report and continue
                print(f"  SKIP {tool}: {exc}")
                continue

            for strategy, grid in strategies:
                for strip_punct, label in ((False, "text"), (True, "nopunct")):
                    result = compare(truth, grid, strip_punct)
                    row = {
                        "page": pdf.stem,
                        "tool": tool,
                        "strategy": strategy,
                        "metric": label,
                        "pred_rows": len(grid),
                        "pred_cols": max((len(r) for r in grid), default=0),
                        **result,
                    }
                    rows.append(row)
                    print(
                        f"  {tool:10} {strategy:7} {label:7} "
                        f"pred={row['pred_rows']}x{row['pred_cols']} "
                        f"microCER={row['micro_cer']:.4f} macroCER={row['macro_cer']:.4f} "
                        f"content_exact={row['nonempty_accuracy']:.3f} "
                        f"struct_exact={row['cell_accuracy']:.3f} row_exact={row['row_accuracy']:.3f}"
                    )
                # Keep a cell-level audit trail in the private results directory.
                audit = out / f"cells_{pdf.stem}_{tool}_{strategy}.csv"
                with audit.open("w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["row", "col", "truth", "pred", "cer_text", "cer_nopunct"])
                    for r in range(len(truth)):
                        for c in range(len(truth[r])):
                            pred_cell = grid[r][c] if r < len(grid) and c < len(grid[r]) else ""
                            writer.writerow([
                                r, c, truth[r][c], pred_cell,
                                f"{cell_cer(truth[r][c], pred_cell, False):.6f}",
                                f"{cell_cer(truth[r][c], pred_cell, True):.6f}",
                            ])

    if not rows:
        print("no results", file=sys.stderr)
        return 1

    with (out / "real_tables.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Real-table per-cell CER",
        "",
        "> Truth is hand-checked against the rendered page. `nopunct` removes Unicode",
        "> punctuation; `text` keeps it. A merged cell is `\"\"` in the truth, so covered",
        "> positions are structural, not content.",
        "",
        "| page | tool | strategy | metric | pred | micro CER | macro CER | exact content cells | row exact |",
        "|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['page']} | {r['tool']} | {r['strategy']} | {r['metric']} | "
            f"{r['pred_rows']}×{r['pred_cols']} | {r['micro_cer']:.4f} | {r['macro_cer']:.4f} | "
            f"{r['nonempty_accuracy']:.3f} | {r['row_accuracy']:.3f} |"
        )
    lines += [
        "",
        "Notes:",
        "- `micro CER` = total edit distance / total truth characters; `macro CER` = mean per-cell CER.",
        "- `exact content cells` ignores structural empty cells; `cell_accuracy` in the CSV includes them.",
        "- Do not call this accuracy for a different edition, page, or tool version.",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
