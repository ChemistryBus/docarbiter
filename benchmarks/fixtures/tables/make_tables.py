#!/usr/bin/env python3
"""Generate table fixtures and their cell-level truth JSON.

Run: python3 -I benchmarks/fixtures/tables/make_tables.py
"""
from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

ZH_GRID = [
    ["项目", "数值", "备注"],
    ["样本量", "24", "中英文各半"],
    ["中文正确率", "98.7%", "demo"],
    ["英文正确率", "97.2%", "demo"],
]
ZH_MERGED = [
    ["合并表头", "", "备注"],
    ["样本量", "24", "中英文各半"],
    ["中文正确率", "98.7%", "跨行合并"],
    ["英文正确率", "97.2%", ""],
]
EN_GRID = [
    ["Item", "Value", "Note"],
    ["Sample size", "24", "half zh, half en"],
    ["Chinese accuracy", "98.7%", "demo"],
    ["English accuracy", "97.2%", "demo"],
]
EN_MERGED = [
    ["Merged header", "", "Note"],
    ["Sample size", "24", "half zh, half en"],
    ["Chinese accuracy", "98.7%", "merged row"],
    ["English accuracy", "97.2%", ""],
]


def build(stem: str, data: list[list[str]], font: str, spans: list[tuple[int, int, int, int]] | None = None, borderless: bool = False) -> None:
    pdf = HERE / f"{stem}.pdf"
    truth = HERE / f"{stem}.json"
    c = canvas.Canvas(str(pdf), pagesize=A4)
    c.setFont(font, 14)
    c.drawString(20 * mm, 270 * mm, "表格单元格测试" if font == "STSong-Light" else "Table cell test")

    table = Table(data, colWidths=[42 * mm, 32 * mm, 42 * mm], rowHeights=[10 * mm] * len(data))
    style = [
        ("FONT", (0, 0), (-1, -1), font, 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    if not borderless:
        style += [
            ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]
    if spans:
        style.extend(("SPAN", (r1, c1), (r2, c2)) for r1, c1, r2, c2 in spans)
    table.setStyle(TableStyle(style))
    table.wrapOn(c, A4[0] - 40 * mm, A4[1] - 60 * mm)
    table.drawOn(c, 20 * mm, 230 * mm)
    c.save()

    truth.write_text(json.dumps({"rows": data}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {pdf.name} + {truth.name}")


if __name__ == "__main__":
    HERE.mkdir(parents=True, exist_ok=True)
    build("zh-table-grid", ZH_GRID, "STSong-Light")
    build("zh-table-merged", ZH_MERGED, "STSong-Light", spans=[(0, 0, 1, 0), (2, 2, 2, 3)])
    build("zh-table-borderless", ZH_GRID, "STSong-Light", borderless=True)
    build("en-table-grid", EN_GRID, "Helvetica")
    build("en-table-merged", EN_MERGED, "Helvetica", spans=[(0, 0, 1, 0), (2, 2, 2, 3)])
    build("en-table-borderless", EN_GRID, "Helvetica", borderless=True)
