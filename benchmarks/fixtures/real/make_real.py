#!/usr/bin/env python3
"""Render the fetched CC BY-SA Wikipedia articles to small PDF fixtures.

Source texts live in benchmarks/fixtures/real/source/*.md, fetched on
2026-11-09 via the local seekport bridge (DeepSeek Fetch) from Wikipedia.
They are CC BY-SA 4.0; see SOURCES.md. The repo's MIT license does not apply
to these fixture texts.

The script cleans Markdown noise (infobox tables, edit markers, references),
takes a bounded prefix, and renders headings + paragraphs with reportlab.
The cleaned text written next to each PDF is the answer key.

Run: python3 -I benchmarks/fixtures/real/make_real.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

ARTICLES = [
    ("wiki-zh-ocr.md", "zh-ocr", "光学字符识别（维基百科）", "STSong-Light", 2200),
    ("wiki-zh-pdf.md", "zh-pdf", "PDF（维基百科）", "STSong-Light", 2200),
    ("wiki-en-ocr.md", "en-ocr", "Optical character recognition (Wikipedia)", "Helvetica", 3200),
    ("wiki-en-pdf.md", "en-pdf", "PDF (Wikipedia)", "Helvetica", 3200),
]

NOISE = (
    "此条目需要补充更多来源",
    "此条目序言章节可能需要重写",
    "本条目需要补充更多来源",
    "Checked",
)


def clean(md: str, limit: int) -> list[tuple[str, str]]:
    """Return [(kind, text)] with kind in {title, h2, body}."""
    lines = md.replace("\r\n", "\n").split("\n")
    blocks: list[tuple[str, str]] = []
    in_table = False
    for raw in lines:
        line = raw.strip()
        if not line:
            in_table = False
            continue
        if line.startswith("<https://") or line.startswith("<http://"):
            continue
        if line.startswith("|") or re.match(r"^[-: ]+\|[-: |]+$", line):
            in_table = True
            continue
        if in_table:
            # Table rows can be followed by non-table prose; the next blank line
            # resets in_table, so keep processing here.
            in_table = False
        if line.startswith("![") or line.startswith("{{") or line.startswith("}}"):
            continue
        if any(noise in line for noise in NOISE):
            continue
        line = re.sub(r"\[编辑\]|\[edit\]", "", line)
        line = re.sub(r"\[\d+\]|\[citation needed\]|\[需要引用\]|\[來源請求\]", "", line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[*_`]", "", line)
        line = html.unescape(line).strip()
        if not line:
            continue
        if line.startswith("# "):
            continue  # article title; we supply our own
        if line.startswith("## "):
            blocks.append(("h2", line[3:].strip()))
        elif line.startswith("### "):
            blocks.append(("h2", line[4:].strip()))
        else:
            blocks.append(("body", line))
        total = sum(len(text) for _, text in blocks)
        if total >= limit:
            break
    return blocks


def render(md_path: Path, stem: str, title: str, font: str, limit: int) -> None:
    blocks = clean(md_path.read_text(encoding="utf-8", errors="replace"), limit)
    pdf = HERE / f"{stem}.pdf"
    truth = HERE / f"{stem}.txt"

    title_style = ParagraphStyle("title", fontName=font, fontSize=16, leading=22, spaceAfter=8)
    h2_style = ParagraphStyle("h2", fontName=font, fontSize=12.5, leading=18, spaceBefore=8,
                              spaceAfter=4, textColor=colors.HexColor("#1F2937"))
    body_style = ParagraphStyle("body", fontName=font, fontSize=10.2, leading=15.5, spaceAfter=5)

    doc = SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm)
    story = [Paragraph(title, title_style)]
    truth_lines = [title]
    for kind, text in blocks:
        if kind == "h2":
            story.append(Paragraph(text, h2_style))
        else:
            story.append(Paragraph(text, body_style))
        truth_lines.append(text)
    story.append(Spacer(1, 4))
    doc.build(story)
    truth.write_text("\n".join(truth_lines) + "\n", encoding="utf-8")
    print(f"wrote {pdf.name} ({len(blocks)} blocks, {sum(len(t) for _, t in blocks)} chars)")


if __name__ == "__main__":
    for md_name, stem, title, font, limit in ARTICLES:
        render(SOURCE / md_name, stem, title, font, limit)
