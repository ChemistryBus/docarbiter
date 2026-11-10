#!/usr/bin/env python3
"""Cell-level table accuracy for pdfplumber on the table fixtures.

Truth format: <fixture>.json with {"rows": [[...], ...]}. A covered merged
cell is represented by "" in the truth. Extracted cells are normalised by
removing whitespace; empty and None both become "".

Run: python3 -I scripts/bench_tables.py
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from pathlib import Path

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "benchmarks" / "fixtures" / "tables"


def norm(cell) -> str:
    if cell is None:
        return ""
    return re.sub(r"\s+", "", str(cell))


TEXT_SETTINGS = {
    "vertical_strategy": "text",
    "horizontal_strategy": "text",
    "text_x_tolerance": 3,
    "text_y_tolerance": 3,
    "snap_tolerance": 3,
    "join_tolerance": 3,
    "intersection_tolerance": 5,
}


def _drop_empty_rows(table: list[list[str | None]]) -> list[list[str | None]]:
    return [row for row in table if any(norm(cell) for cell in row)]


def extract(pdf: Path, strategy: str) -> list[list[list[str]]]:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber is not installed")
    tables: list[list[list[str]]] = []
    with pdfplumber.open(str(pdf)) as doc:
        for page in doc.pages:
            if strategy == "text":
                found = page.extract_tables(table_settings=TEXT_SETTINGS)
                found = [_drop_empty_rows(t) for t in found]
                found = [t for t in found if t]
            else:
                found = page.extract_tables()
            tables.extend(found)
    return tables


def compare(truth: list[list[str]], extracted: list[list[str]]) -> dict:
    rows = max(len(truth), len(extracted))
    cols = max(
        max((len(r) for r in truth), default=0),
        max((len(r) for r in extracted), default=0),
    )
    matches = 0
    total = len(truth) * max(len(r) for r in truth) if truth else 0
    row_hits = 0
    for r in range(len(truth)):
        row_ok = True
        for c in range(len(truth[r])):
            e = extracted[r][c] if r < len(extracted) and c < len(extracted[r]) else ""
            if norm(truth[r][c]) == norm(e):
                matches += 1
            else:
                row_ok = False
        row_hits += 1 if row_ok else 0
    return {
        "rows": rows,
        "cols": cols,
        "cell_matches": matches,
        "cell_total": total,
        "cell_accuracy": matches / total if total else 0.0,
        "row_accuracy": row_hits / len(truth) if truth else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixtures", default=str(DEFAULT_DIR))
    ap.add_argument("--out", default=str(ROOT / "benchmarks" / "results" / "tables"))
    ap.add_argument("--strategy", choices=["default", "text", "both"], default="both")
    args = ap.parse_args()
    fixtures = Path(args.fixtures)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    strategies = ["default", "text"] if args.strategy == "both" else [args.strategy]
    rows: list[dict] = []
    for pdf in sorted(fixtures.glob("*.pdf")):
        truth_path = pdf.with_suffix(".json")
        if not truth_path.exists():
            print(f"skip {pdf.name}: no truth JSON")
            continue
        truth = json.loads(truth_path.read_text(encoding="utf-8"))["rows"]
        for strategy in strategies:
            tables = extract(pdf, strategy)
            table = tables[0] if tables else []
            result = compare(truth, table)
            row = {
                "fixture": pdf.name,
                "strategy": strategy,
                "tables_found": len(tables),
                "truth_rows": len(truth),
                "truth_cols": max(len(r) for r in truth) if truth else 0,
                "extracted_rows": len(table),
                "extracted_cols": max((len(r) for r in table), default=0),
                **result,
            }
            rows.append(row)
            print(
                f"[{pdf.name}] {strategy:7} tables={len(tables)} "
                f"cell_acc={row['cell_accuracy']:.3f} row_acc={row['row_accuracy']:.3f}"
            )

    with (out / "per_table.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["fixture"])
        writer.writeheader()
        writer.writerows(rows)

    accs = [r["cell_accuracy"] for r in rows]
    lines = [
        "# Table cell accuracy (pdfplumber)",
        "",
        f"Fixtures: {fixtures}",
        "",
        "| fixture | strategy | tables | truth rows×cols | extracted rows×cols | cell acc | row acc |",
        "|---|---|---:|---|---|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['fixture']} | {r['strategy']} | {r['tables_found']} | {r['truth_rows']}×{r['truth_cols']} | "
            f"{r['extracted_rows']}×{r['extracted_cols']} | {r['cell_accuracy']:.3f} | {r['row_accuracy']:.3f} |"
        )
    if accs:
        lines += ["", f"Mean cell accuracy: {statistics.mean(accs):.3f}"]
    lines += [
        "",
        "Notes:",
        "- Covered merged cells are represented by an empty string in the truth; empty and None both normalise to \"\".",
        "- This measures pdfplumber only; Camelot is not installed on the reference machine.",
        "- A high cell accuracy does not prove merged-cell semantics; check the row/column dimensions too.",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
