#!/usr/bin/env python3
"""Abstract-only CER on a real CC BY two-column paper (BERT, ACL Anthology).

The truth is the abstract text from the ACL Anthology HTML page. Each tool is
aligned to it with rapidfuzz's partial alignment, then CER is computed on the
aligned segment. This avoids penalising a tool for extracting title, authors,
or the introduction as well.

Run:
    python3 -I scripts/bench_abstract.py \
      --pdf benchmarks/fixtures/real/bert-abstract-2p.pdf \
      --truth benchmarks/fixtures/real/bert-abstract.txt
"""
from __future__ import annotations

import argparse
import csv
import difflib
import statistics
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import bench  # noqa: E402

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", default=str(ROOT / "benchmarks" / "fixtures" / "real" / "bert-abstract-2p.pdf"))
    ap.add_argument("--truth", default=str(ROOT / "benchmarks" / "fixtures" / "real" / "bert-abstract-2p.txt"))
    ap.add_argument("--tools", default="pdftotext,liteparse,markitdown,pdfplumber,mineru,docling")
    ap.add_argument("--out", default=str(ROOT / "benchmarks" / "results" / "abstract"))
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-chars", type=int, default=20000)
    args = ap.parse_args()

    if fuzz is None:
        print("rapidfuzz not installed; using stdlib difflib fallback", file=sys.stderr)

    pdf = Path(args.pdf)
    truth_raw = Path(args.truth).read_text(encoding="utf-8", errors="replace")
    truth = bench.normalize(truth_raw, strip_md=True)
    truth_np = bench.normalize(truth_raw, strip_md=True, strip_punct=True)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    for tool in [t.strip() for t in args.tools.split(",") if t.strip()]:
        with tempfile.TemporaryDirectory(prefix="docarbiter-abstract-") as tmp:
            text, stderr, rc, secs = bench.extract(tool, pdf, Path(tmp), args.timeout)
        pred = bench.normalize(text, strip_md=True)
        pred_np = bench.normalize(text, strip_md=True, strip_punct=True)
        status = "ok" if rc == 0 and pred else "error"
        row = {
            "tool": tool, "status": status, "seconds": f"{secs:.3f}",
            "truth_chars": len(truth), "pred_chars": len(pred),
            "alignment_score": "", "aligned_chars": "", "cer": "", "cer_nopunct": "",
            "error": "" if status == "ok" else (stderr.strip().splitlines()[-1] if stderr.strip() else f"exit {rc}"),
        }
        if status == "ok":
            segment = None
            score = None
            if fuzz is not None:
                align = fuzz.partial_ratio_alignment(truth, pred)
                if align and align.dest_end > align.dest_start:
                    segment = pred[align.dest_start:align.dest_end]
                    score = align.score
            else:
                # stdlib fallback: locate the longest common block, then take a
                # window of the truth length around it.
                sm = difflib.SequenceMatcher(None, truth, pred, autojunk=False)
                match = sm.find_longest_match(0, len(truth), 0, len(pred))
                if match.size:
                    start = max(0, match.b - match.a)
                    segment = pred[start:start + len(truth)]
                    score = sm.ratio() * 100
            if segment is not None and score is not None:
                segment_np = bench.normalize(segment, strip_md=True, strip_punct=True)
                c = bench.cer(truth, segment, args.max_chars)
                c_np = bench.cer(truth_np, segment_np, args.max_chars)
                row.update(
                    alignment_score=f"{score:.1f}",
                    aligned_chars=len(segment),
                    cer=f"{c['cer']:.6f}",
                    cer_nopunct=f"{c_np['cer']:.6f}",
                )
            else:
                row["status"] = "no-align"
        rows.append(row)
        print(f"[{tool:12}] {row['status']:8} CER={row['cer'] or '-'} align={row['alignment_score'] or '-'} {row['seconds']}s")

    with (out / "per_tool.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["tool"])
        writer.writeheader()
        writer.writerows(rows)

    cers = [float(r["cer"]) for r in rows if r["cer"]]
    lines = [
        "# Abstract CER — BERT (ACL Anthology, CC BY 4.0)",
        "",
        f"PDF: `{pdf}`",
        f"Truth: `{args.truth}` (abstract from the ACL Anthology HTML page)",
        "",
        "| tool | status | CER | no-punct CER | aligned chars | seconds |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['tool']} | {r['status']} | {r['cer'] or '—'} | {r['cer_nopunct'] or '—'} | "
            f"{r['aligned_chars'] or '—'} | {r['seconds']} |"
        )
    if cers:
        lines += ["", f"Median CER: {statistics.median(cers):.6f}"]
    align_note = (
        "`rapidfuzz.fuzz.partial_ratio_alignment`"
        if fuzz is not None
        else "stdlib `difflib` fallback (alignment score is not comparable to rapidfuzz)"
    )
    lines += [
        "",
        "Notes:",
        f"- Alignment uses {align_note}; CER is computed on the aligned segment only.",
        "- This is the abstract, not the full two-column body; figures/tables/references are not scored.",
        "- The PDF is a 2-page excerpt; source and license are in `benchmarks/fixtures/real/SOURCES.md`.",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"results: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
