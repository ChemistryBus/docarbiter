#!/usr/bin/env python3
"""Full-text CER on real two-column papers.

Truth comes from an independent source, not from any tool under test:
  - PMC JATS XML (`.truth.xml`) for journal articles;
  - ar5iv HTML (`.truth.html`) for arXiv papers.

Scope is the abstract plus the main body, with section headings and paragraphs.
References, figure/table content and captions, and appendices are excluded. Tool
output is stripped of Markdown/HTML and aligned to the truth by its first/last
anchors before CER is computed.

Run:
    python3 -I scripts/bench_fulltext.py \
        --dir benchmarks/private/incoming/two-column \
        --tools pdftotext,liteparse,docling,mineru
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
import time
import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

try:
    from rapidfuzz.distance import Levenshtein as _RFLev
except ImportError:  # pragma: no cover
    _RFLev = None

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "benchmarks" / "private" / "incoming" / "two-column"
DEFAULT_CACHE = DEFAULT_DIR / "cache"
DEFAULT_OUT = ROOT / "benchmarks" / "results" / "fulltext"

JATS_SKIP = {
    "table-wrap", "fig", "supplementary-material", "ref-list", "fn-group",
    "ack", "notes", "license", "author-notes", "funding-group", "permissions",
}
CAPTION_RE = re.compile(r"^\s*(?:Figure|Fig\.|Table)\s+\d+[.:]|^\s*(?:图|表)\s*\d+", re.I)
REFERENCES_RE = re.compile(r"(?:^|\n)\s*(?:References|REFERENCES|Bibliography|参考文献)\s*(?:\n|$)")
END_RE = re.compile(
    r"(?im)^\s*(?:Supplementary Material|Acknowledg(?:e)?ments?|Author Contributions|"
    r"Data and Code Availability|Funding|References|Bibliography|参考文献)\s*$"
)


def cut_end(text: str) -> str:
    """Drop acknowledgments, funding, supplementary material, and references."""
    match = END_RE.search(text)
    return text[:match.start()] if match else text


# ---------------------------------------------------------------- normalise
def nfc(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.replace("­", "")
    # PDF line-break hyphenation: "docu-\nment" -> "document".
    text = re.sub(r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])", "", text)
    return text


def norm(text: str, strip_punct: bool = False) -> str:
    text = nfc(text)
    text = re.sub(r"\s+", "", text)
    if strip_punct:
        text = "".join(c for c in text if not unicodedata.category(c).startswith("P"))
    return text


def cer(truth: str, pred: str) -> float:
    if not truth:
        return 0.0 if not pred else 1.0
    if _RFLev is not None:
        return _RFLev.distance(truth, pred) / len(truth)
    # Pure Python is impractical for full papers; refuse loudly rather than hang.
    raise RuntimeError("rapidfuzz is required for full-text CER; install it with pip install rapidfuzz")


# ---------------------------------------------------------------- truth
def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(el: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _jats_walk(el: ET.Element, parts: list[str]) -> None:
    for child in el:
        tag = _local(child.tag)
        if tag in JATS_SKIP:
            continue
        if tag == "title":
            text = _text(child)
            if text:
                parts.append(text)
        elif tag == "p":
            text = _text(child)
            if text:
                parts.append(text)
        elif tag in ("sec", "abstract", "body", "article", "trans-abstract", "list", "list-item"):
            _jats_walk(child, parts)
        else:
            _jats_walk(child, parts)


def truth_from_jats(path: Path) -> str:
    root = ET.parse(path).getroot()
    parts: list[str] = []
    abstract = root.find(".//abstract")
    if abstract is not None:
        _jats_walk(abstract, parts)
    body = root.find(".//body")
    if body is not None:
        _jats_walk(body, parts)
    return cut_end("\n\n".join(parts))


class Ar5ivParser(HTMLParser):
    """Collect headings and paragraphs before References; skip figures/tables."""

    SKIP = {"figure", "table", "script", "style", "math", "nav", "svg"}
    BLOCK = {"h1", "h2", "h3", "h4", "h5", "h6", "p"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.stop = False
        self.current: str | None = None
        self.buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.SKIP:
            self.skip_depth += 1
        if tag in self.BLOCK:
            self.current = tag
            self.buf = []
        elif tag == "br" and self.current:
            self.buf.append(" ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.SKIP:
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag == self.current:
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if text and not self.stop:
                if tag.startswith("h") and re.match(r"^(References|Bibliography)$", text, re.I):
                    self.stop = True
                else:
                    self.parts.append(text)
            self.current = None
            self.buf = []

    def handle_data(self, data: str) -> None:
        if not self.stop and not self.skip_depth and self.current:
            self.buf.append(data)


def truth_from_ar5iv(path: Path) -> str:
    parser = Ar5ivParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = "\n\n".join(parser.parts)
    # Drop the title/authors before the abstract heading.
    match = re.search(r"\bAbstract\b", text)
    if match:
        text = text[match.start():]
    return cut_end(text)


def load_truth(pdf: Path, cache: Path) -> tuple[str, Path]:
    cached = pdf.with_suffix(".truth.txt")
    if cached.exists():
        text = cut_end(cached.read_text(encoding="utf-8"))
        cached.write_text(text, encoding="utf-8")
        return text, cached
    source = None
    for suffix in (".truth.xml", ".truth.html"):
        candidate = pdf.with_suffix(suffix)
        if candidate.exists():
            source = candidate
            break
    if source is None:
        raise RuntimeError(f"missing truth source for {pdf.name}")
    if source.suffix == ".xml":
        text = truth_from_jats(source)
    else:
        text = truth_from_ar5iv(source)
    if not text.strip():
        raise RuntimeError(f"truth extraction produced no text: {source}")
    cached.write_text(text, encoding="utf-8")
    return text, cached


# ---------------------------------------------------------------- tool text
def strip_markup(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"<table\b.*?</table>", "", text, flags=re.S | re.I)
    text = re.sub(r"<script\b.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style\b.*?</style>", "", text, flags=re.S | re.I)
    # Require a tag name after "<": mathematical "<0.1%" is not HTML and must
    # not swallow text up to the next ">".
    text = re.sub(r"</?[A-Za-z][^>]*>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[>*+-]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\|.*\|\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*[-:|\s]+\s*$", "", text, flags=re.M)
    text = re.sub(r"[*_~`]", "", text)
    return text


def drop_captions_and_references(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    in_caption = False
    for line in lines:
        if CAPTION_RE.match(line):
            in_caption = True
            continue
        if in_caption:
            if not line.strip():
                in_caption = False
            continue
        if REFERENCES_RE.search("\n" + line):
            break
        kept.append(line)
    text = "\n".join(kept)
    # Drop running headers/footers: short lines repeated three or more times.
    counts: dict[str, int] = {}
    for line in text.splitlines():
        key = re.sub(r"\s+", " ", line).strip()
        if key:
            counts[key] = counts.get(key, 0) + 1
    out = []
    for line in text.splitlines():
        key = re.sub(r"\s+", " ", line).strip()
        if key and len(key) < 100 and counts.get(key, 0) >= 3:
            continue
        if re.fullmatch(r"\s*\d+\s*", line):
            continue
        out.append(line)
    return "\n".join(out)


def _run(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )


def tool_text(tool: str, pdf: Path, cache: Path, timeout: int) -> tuple[str, float]:
    outdir = cache / pdf.stem
    outdir.mkdir(parents=True, exist_ok=True)
    cached = outdir / f"{tool}.txt"
    if cached.exists():
        text = cut_end(cached.read_text(encoding="utf-8", errors="replace"))
        cached.write_text(text, encoding="utf-8")
        return text, 0.0

    t0 = time.time()
    if tool == "pdftotext":
        proc = _run(["pdftotext", str(pdf), "-"], timeout)
        raw = proc.stdout
    elif tool == "pdftotext-layout":
        proc = _run(["pdftotext", "-layout", str(pdf), "-"], timeout)
        raw = proc.stdout
    elif tool == "liteparse":
        proc = _run(["liteparse-doc", str(pdf), "--pages", "all"], timeout)
        raw = proc.stdout
    elif tool == "mineru":
        out_md = outdir / "mineru.md"
        if shutil.which("mineru-doc"):
            cmd = ["mineru-doc"]
        elif shutil.which("mineru"):
            cmd = ["mineru", "parse"]
        else:
            raise RuntimeError("mineru-doc / mineru is not installed")
        proc = _run([*cmd, str(pdf), "--pages", "all", "-o", str(out_md)], timeout)
        raw = out_md.read_text(encoding="utf-8", errors="replace") if out_md.exists() else proc.stdout
    elif tool == "docling":
        outdir_docling = outdir / "docling"
        outdir_docling.mkdir(exist_ok=True)
        proc = _run(
            ["docling", "convert", str(pdf), "--to", "md", "--output", str(outdir_docling),
             "--image-export-mode", "placeholder", "--no-ocr"],
            timeout,
        )
        files = sorted(outdir_docling.rglob("*.md"))
        raw = files[0].read_text(encoding="utf-8", errors="replace") if files else proc.stdout
    elif tool == "markitdown":
        proc = _run(["markitdown", str(pdf)], timeout)
        raw = proc.stdout
    else:
        raise RuntimeError(f"unknown tool {tool}")

    if proc.returncode != 0 and not raw.strip():
        raise RuntimeError(proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else f"exit {proc.returncode}")
    cleaned = cut_end(drop_captions_and_references(strip_markup(raw)))
    cached.write_text(cleaned, encoding="utf-8")
    return cleaned, time.time() - t0


# ---------------------------------------------------------------- alignment
def align_span(truth: str, pred: str, last_paragraph: str = "") -> tuple[int, int, str]:
    """Find the body span in pred using anchors from the truth.

    Matching is case-insensitive because HTML/LaTeX truth and PDF extraction
    often differ only in sentence-initial capitalisation.
    """
    if not truth or not pred:
        return 0, len(pred), "empty"
    haystack = pred.lower()
    start = -1
    for offset in (0, 120, 300):
        for length in (80, 60, 40):
            anchor = truth[offset:offset + length].lower()
            if len(anchor) >= 20:
                start = haystack.find(anchor)
                if start >= 0:
                    break
        if start >= 0:
            break
    end = -1
    for length in (80, 120, 160):
        anchor = truth[-length:].lower()
        if len(anchor) >= 20:
            end = haystack.rfind(anchor)
            if end >= 0:
                end += len(anchor)
                break
    if start >= 0 and end > start:
        return start, end, "start+end"
    # Fallback: find the start of the last truth paragraph and cut at its end.
    if start >= 0 and last_paragraph:
        last = last_paragraph.lower()
        if len(last) >= 20:
            idx = haystack.find(last[:80])
            if idx < 0:
                idx = haystack.find(last[:60])
            if idx >= 0:
                return start, min(len(pred), idx + len(last)), "last-paragraph"
    if start >= 0:
        return start, len(pred), "start only"
    return 0, len(pred), "whole"


def measure(truth: str, pred: str, strip_punct: bool) -> dict:
    t = norm(truth, strip_punct)
    p = norm(pred, strip_punct)
    paragraphs = [x for x in re.split(r"\n\s*\n", truth) if x.strip()]
    last_para = norm(paragraphs[-1], strip_punct) if len(paragraphs) > 1 else ""
    start, end, mode = align_span(t, p, last_para)
    aligned = p[start:end]
    return {
        "truth_chars": len(t),
        "pred_chars": len(p),
        "aligned_chars": len(aligned),
        "coverage": len(aligned) / len(t) if t else 0.0,
        "cer": cer(t, aligned),
        "alignment": mode,
        "aligned": aligned,
    }


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="Full-text CER on real two-column papers.")
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--cache", default=str(DEFAULT_CACHE))
    ap.add_argument("--out", default=None)
    ap.add_argument("--tools", default="pdftotext,pdftotext-layout,liteparse,docling,mineru")
    ap.add_argument("--timeout", type=int, default=1200, help="seconds per tool per paper")
    ap.add_argument("--papers", help="comma-separated PDF stems to include")
    args = ap.parse_args()

    src = Path(args.dir)
    cache = Path(args.cache)
    out = Path(args.out) if args.out else DEFAULT_OUT / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True, exist_ok=True)
    tools = [t.strip() for t in args.tools.split(",") if t.strip()]

    pdfs = sorted(p for p in src.glob("*.pdf")
                  if any(p.with_suffix(s).exists() for s in (".truth.xml", ".truth.html", ".truth.txt")))
    if args.papers:
        wanted = {p.strip() for p in args.papers.split(",") if p.strip()}
        pdfs = [p for p in pdfs if p.stem in wanted]
    if not pdfs:
        print(f"no PDF with a truth source in {src}", file=sys.stderr)
        return 2

    rows: list[dict] = []
    for pdf in pdfs:
        truth, truth_path = load_truth(pdf, cache)
        print(f"=== {pdf.name}: truth {len(norm(truth))} chars ({truth_path.name}) ===")
        for tool in tools:
            try:
                text, secs = tool_text(tool, pdf, cache, args.timeout)
            except Exception as exc:  # noqa: BLE001
                print(f"  SKIP {tool}: {exc}")
                continue
            for strip_punct, label in ((False, "text"), (True, "nopunct")):
                result = measure(truth, text, strip_punct)
                valid = (
                    result["alignment"] in ("start+end", "last-paragraph")
                    and 0.5 <= result["coverage"] <= 1.5
                )
                row = {
                    "paper": pdf.stem,
                    "tool": tool,
                    "metric": label,
                    "truth_chars": result["truth_chars"],
                    "pred_chars": result["pred_chars"],
                    "aligned_chars": result["aligned_chars"],
                    "coverage": result["coverage"],
                    "cer": result["cer"],
                    "valid": valid,
                    "alignment": result["alignment"],
                    "seconds": secs,
                }
                # Keep the aligned text in private results for audit; never publish it.
                audit = out / f"aligned_{pdf.stem}_{tool}_{label}.txt"
                audit.write_text(result["aligned"], encoding="utf-8", errors="replace")
                rows.append(row)
                print(
                    f"  {tool:16} {label:7} cer={row['cer']:.4f} "
                    f"coverage={row['coverage']:.3f} align={row['alignment']} "
                    f"{'valid' if valid else 'ALIGNMENT-INVALID'} "
                    f"chars={row['truth_chars']}->{row['aligned_chars']}"
                )

    if not rows:
        print("no results", file=sys.stderr)
        return 1

    with (out / "fulltext.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        "# Full-text CER on real two-column papers",
        "",
        "> Truth: independent PMC JATS or ar5iv HTML; abstract + main body, excluding",
        "> references, figure/table content and captions, and appendices. Tool output",
        "> is aligned to the truth's first/last anchors before CER.",
        "",
        "| paper | tool | metric | truth chars | aligned chars | coverage | CER | valid | alignment |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for r in rows:
        cer_value = f"{r['cer']:.4f}" if r["valid"] else "—"
        lines.append(
            f"| {r['paper']} | {r['tool']} | {r['metric']} | {r['truth_chars']} | "
            f"{r['aligned_chars']} | {r['coverage']:.3f} | {cer_value} | "
            f"{'yes' if r['valid'] else 'no'} | {r['alignment']} |"
        )
    lines += [
        "",
        "Notes:",
        "- This is CER on the aligned main-body span, not a claim about figures, tables, or references.",
        "- `coverage` = aligned prediction characters / truth characters; low coverage means the anchor was weak.",
        "- Do not generalise to another edition, layout, or tool version.",
    ]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nresults: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
