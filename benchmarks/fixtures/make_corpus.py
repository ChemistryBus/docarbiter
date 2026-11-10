#!/usr/bin/env python3
"""Generate the bilingual smoke corpus and its answer texts.

This is a development corpus, not the final benchmark suite. It covers:
  zh: text layer, two columns, table, footnote, scan
  en: text layer, two columns, table, footnote, scan, line-break hyphen

Run: python3 -I benchmarks/fixtures/make_corpus.py
"""
from __future__ import annotations

import glob
import shutil
import subprocess
import tempfile
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

ZH_TEXT = [
    "中文文档提取测试：文字层",
    "第一段：这是一段用于测试中文文字层提取的文本，包含全角标点：，。！？；：“”‘’。"
    "这一页还要验证段落合并、行尾换行和常见汉字覆盖率。",
    "第二段：混排 English words、数字 12345、百分比 98.7%，以及括号（测试）和破折号——结束。",
    "第三段：常见汉字覆盖测试——的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可"
    "也对生能而子那得于着下自之年过发后作里用道行所然家种事成方多经去法学如都同现当没动面起看"
    "定天分还进好小部其些主样理心她本前开但因只从想实日军者意无力它与长把机十民第公此已工使情"
    "明性知全三又关点正业外将两高间由问很最重并物手应战向头文体政美相见被利什二等产或新己制身"
    "果加西斯月话合回特代内信表化老给世位次度门任常先海通教儿原东声提立及比员解水名真论处走义"
    "各入几口认条平系气题活尔更别打女变四神总何电数安少报才结反受目太量再感建务做接必场件计管"
    "期市直德资命山金指克许统区保至队形社便空决治展马科司五基眼书非则听白却界达光放强即像难且"
    "权思王象完设式色路记南品住告类求据程北边死张该交规万取拉格望觉术领共确传师观清今切院让识"
    "候带导争运笑飞风步改收根干造言联持组每济车亲极林服快办议往元英士证近失转夫令准布始怎呢存",
    "第四段：这一段的长度用于填满第二栏，让双栏阅读顺序可以被观察。如果提取器把两栏交错输出，"
    "这一段和上一段就会混在一起。中文没有空格，所以词级指标会掩盖这种错误；必须用字符级 CER。",
]
ZH_TABLE = [
    ["项目", "数值", "备注"],
    ["样本量", "24", "中英文各半"],
    ["中文正确率", "98.7%", "demo"],
    ["英文正确率", "97.2%", "demo"],
]
ZH_FOOT = "注：这是脚注测试。脚注应当出现在正文之后，不应插进正文段落中间。"

EN_TEXT = [
    "English Document Extraction Test: Text Layer",
    "Paragraph one: this page tests an English text layer, curly quotes (“ ” ‘ ’), an em dash — "
    "and a range 10–20. It also checks paragraph merging and line wrapping.",
    "Paragraph two: mixed content with numbers 12345, a percentage 98.7%, parentheses (test), "
    "and tokens such as foo_bar.",
    "Paragraph three: a document extractor has to preserve reading order, paragraph boundaries, "
    "and table structure while ignoring page headers and footers. A fast text-layer parser is "
    "usually enough for born-digital files, but scanned pages need an OCR layer first. The same "
    "page can produce very different output depending on the tool, so the choice of extractor "
    "should be made from the input and the desired output, not from a star count.",
    "Paragraph four: this paragraph is long enough to fill the second column, so a two-column "
    "extractor that interleaves left and right text will be visible in the output. The answer "
    "key is the source text, not another tool's output.",
]
EN_TABLE = [
    ["Item", "Value", "Note"],
    ["Sample size", "24", "half zh, half en"],
    ["Chinese accuracy", "98.7%", "demo"],
    ["English accuracy", "97.2%", "demo"],
]
EN_FOOT = "Note: this is a footnote test. It should appear after the body, not inside a paragraph."


def _styles(font: str) -> tuple[ParagraphStyle, ParagraphStyle, ParagraphStyle]:
    title = ParagraphStyle("title", fontName=font, fontSize=17, leading=22, spaceAfter=8)
    body = ParagraphStyle("body", fontName=font, fontSize=10.5, leading=16, spaceAfter=6)
    small = ParagraphStyle("small", fontName=font, fontSize=8.5, leading=12, textColor=colors.grey)
    return title, body, small


def _write_truth(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _table(rows: list[list[str]], font: str) -> Table:
    t = Table(rows, colWidths=[38 * mm, 32 * mm, 42 * mm])
    t.setStyle(
        TableStyle(
            [
                ("FONT", (0, 0), (-1, -1), font, 9.5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("SPAN", (0, 0), (0, 0)),
            ]
        )
    )
    return t


def build_single(pdf: Path, truth: Path, title: str, paragraphs: list[str], rows: list[list[str]], foot: str | None, font: str) -> None:
    title_style, body, small = _styles(font)
    doc = SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm)
    story = [Paragraph(title, title_style)]
    story.extend(Paragraph(p, body) for p in paragraphs)
    if rows:
        story.extend([Spacer(1, 6), _table(rows, font)])
    if foot:
        story.extend([Spacer(1, 8), Paragraph(foot, small)])
    doc.build(story)
    lines = [title, *paragraphs]
    for row in rows:
        lines.extend(row)
    if foot:
        lines.append(foot)
    _write_truth(truth, lines)


def build_two_column(pdf: Path, truth: Path, title: str, paragraphs: list[str], font: str) -> None:
    title_style, body, _ = _styles(font)
    doc = BaseDocTemplate(str(pdf), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=18 * mm, bottomMargin=18 * mm)
    gap = 8 * mm
    frame_w = (A4[0] - 36 * mm - gap) / 2
    frame_h = A4[1] - 36 * mm
    left = Frame(18 * mm, 18 * mm, frame_w, frame_h, id="left")
    right = Frame(18 * mm + frame_w + gap, 18 * mm, frame_w, frame_h, id="right")
    doc.addPageTemplates([PageTemplate(id="two-col", frames=[left, right])])
    story = [Paragraph(title, title_style)]
    story.extend(Paragraph(p, body) for p in paragraphs)
    doc.build(story)
    _write_truth(truth, [title, *paragraphs])


def build_hyphenation(pdf: Path, truth: Path) -> None:
    c = canvas.Canvas(str(pdf), pagesize=A4)
    c.setFont("Helvetica", 11)
    lines = [
        "English line-break hyphenation test",
        "",
        "This paragraph tests a line-break hyphen: docu-",
        "ment should be joined to document in the answer.",
        "",
        "A real compound such as well-known should stay.",
    ]
    y = 780
    for line in lines:
        c.drawString(50, y, line)
        y -= 18
    c.save()
    _write_truth(
        truth,
        [
            "English line-break hyphenation test",
            "This paragraph tests a line-break hyphen: document should be joined to document in the answer.",
            "A real compound such as well-known should stay.",
        ],
    )


def build_scan(source_pdf: Path, pdf: Path, truth: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="docarbiter-scan-") as tmp:
        prefix = str(Path(tmp) / "page")
        subprocess.run(
            ["pdftoppm", "-png", "-r", "150", str(source_pdf), prefix],
            check=True,
            capture_output=True,
        )
        images = sorted(glob.glob(prefix + "*.png"))
        if not images:
            raise RuntimeError(f"pdftoppm produced no images for {source_pdf}")
        c = canvas.Canvas(str(pdf), pagesize=A4)
        for image in images:
            img = ImageReader(image)
            iw, ih = img.getSize()
            scale = min((A4[0] - 24 * mm) / iw, (A4[1] - 24 * mm) / ih)
            c.drawImage(img, 12 * mm, (A4[1] - ih * scale) / 2, iw * scale, ih * scale)
            c.showPage()
        c.save()
    shutil.copyfile(source_pdf.with_suffix(".txt"), truth)


def main() -> None:
    zh_title, zh_paras = ZH_TEXT[0], ZH_TEXT[1:]
    en_title, en_paras = EN_TEXT[0], EN_TEXT[1:]

    build_single(HERE / "zh-text-layer.pdf", HERE / "zh-text-layer.txt", zh_title, zh_paras, ZH_TABLE, ZH_FOOT, "STSong-Light")
    build_two_column(HERE / "zh-two-column.pdf", HERE / "zh-two-column.txt", zh_title, zh_paras, "STSong-Light")
    build_single(HERE / "zh-table.pdf", HERE / "zh-table.txt", "中文表格测试", [zh_paras[0], zh_paras[1]], ZH_TABLE, None, "STSong-Light")
    build_single(HERE / "zh-footnote.pdf", HERE / "zh-footnote.txt", "中文脚注测试", [zh_paras[0]], [], ZH_FOOT, "STSong-Light")
    build_scan(HERE / "zh-text-layer.pdf", HERE / "zh-scan.pdf", HERE / "zh-scan.txt")

    build_single(HERE / "en-text-layer.pdf", HERE / "en-text-layer.txt", en_title, en_paras, EN_TABLE, EN_FOOT, "Helvetica")
    build_two_column(HERE / "en-two-column.pdf", HERE / "en-two-column.txt", en_title, en_paras, "Helvetica")
    build_single(HERE / "en-table.pdf", HERE / "en-table.txt", "English Table Test", [en_paras[0], en_paras[1]], EN_TABLE, None, "Helvetica")
    build_single(HERE / "en-footnote.pdf", HERE / "en-footnote.txt", "English Footnote Test", [en_paras[0]], [], EN_FOOT, "Helvetica")
    build_scan(HERE / "en-text-layer.pdf", HERE / "en-scan.pdf", HERE / "en-scan.txt")
    build_hyphenation(HERE / "en-hyphenation.pdf", HERE / "en-hyphenation.txt")

    print("wrote 11 bilingual fixtures to", HERE)


if __name__ == "__main__":
    main()
