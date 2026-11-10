#!/usr/bin/env python3
"""Generate edge-case fixtures: CID/no-ToUnicode, traditional, interleaved
two-column, and a vertical-text simulation.

Dependencies:
  - reportlab, python-docx, pypdf (already used by the benchmark)
  - LibreOffice `soffice` for the CID fixture (DOCX -> PDF)

Run: python3 -I benchmarks/fixtures/edge/make_edge.py
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.shared import Pt
from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))

CID_TEXT = (
    "中文文档提取测试：CID 字体与无 ToUnicode 场景。"
    "这是一段用于验证文字层损坏时提取行为的文本，包含全角标点：，。！？；：“”‘’。"
    "正确行为是识别出乱码并拒绝直接使用文字层，而不是把它当成正常文本。"
)
TRAD_TEXT = (
    "繁體中文文件提取測試：這是一段用於測試繁體字、異體字與全形標點的文本。"
    "正確行為是保留繁體字形與標點；不要擅自轉成簡體，也不要把全形標點換成半形。"
    "常見繁體字：體、國、學、發、裡、著、麼、這、說、時、間、開、關、讀、寫。"
)
ZH_LEFT = (
    "左欄第一段：這是一段用於測試雙欄閱讀順序的文字。如果提取器按內容流逐行讀取，"
    "左右兩欄就會交錯，閱讀順序不可用。我們需要看到正確的左欄全篇、再右欄全篇。"
) * 2
ZH_RIGHT = (
    "右欄第二段：這是一段用於測試雙欄閱讀順序的文字。正確的閱讀順序是先讀完左欄，"
    "再讀右欄；不是左一行、右一行。"
) * 2
EN_LEFT = (
    "Left column, paragraph one: this fixture tests two-column reading order. If an extractor "
    "reads the content stream row by row, left and right text will interleave and the reading "
    "order becomes unusable. The correct order is the whole left column, then the whole right column. "
) * 2
EN_RIGHT = (
    "Right column, paragraph two: this fixture tests two-column reading order. The correct order "
    "is to finish the left column before starting the right column, not to alternate lines. "
) * 2
VERT_TEXT = "豎排測試：從上到下閱讀，從右到左換行。"
VERT_REAL_TEXT = (
    "豎排測試：從上到下閱讀，從右到左換列。這是一段用於測試真正 vertical writing mode 的文本。"
    "正確的閱讀順序是先讀完最右一列，再往左換列；不是從左往右，也不是一字一行。"
    "中文標點：，。！？；：「」『』。"
)


def _split_cn(text: str, n: int = 18) -> list[str]:
    return [text[i:i + n] for i in range(0, len(text), n)]


def _split_en(text: str, n: int = 48) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > n:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines


def _strip_tounicode(src: Path, dst: Path) -> None:
    reader = PdfReader(str(src))
    for page in reader.pages:
        resources = page.get("/Resources")
        fonts = resources.get("/Font") if resources else None
        if not fonts:
            continue
        for _, ref in fonts.items():
            font = ref.get_object()
            if "/ToUnicode" in font:
                del font["/ToUnicode"]
            if "/DescendantFonts" in font:
                for descendant in font["/DescendantFonts"]:
                    df = descendant.get_object()
                    if "/ToUnicode" in df:
                        del df["/ToUnicode"]
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with dst.open("wb") as fh:
        writer.write(fh)


def make_cid() -> None:
    soffice = shutil.which("soffice")
    if not soffice:
        print("skip CID fixture: soffice not found")
        return
    with tempfile.TemporaryDirectory(prefix="docarbiter-cid-") as tmp:
        tmp_path = Path(tmp)
        docx_path = tmp_path / "cid.docx"
        doc = Document()
        run = doc.add_paragraph().add_run(CID_TEXT)
        run.font.name = "Songti SC"
        run.font.size = Pt(12)
        doc.save(str(docx_path))

        profile = tmp_path / "lo-profile"
        profile.mkdir()
        subprocess.run(
            [
                soffice, "--headless",
                f"-env:UserInstallation=file://{profile}",
                "--convert-to", "pdf", "--outdir", str(tmp_path), str(docx_path),
            ],
            check=True,
            capture_output=True,
        )
        pdf = tmp_path / "cid.pdf"
        if not pdf.exists():
            raise RuntimeError("LibreOffice did not produce cid.pdf")
        _strip_tounicode(pdf, HERE / "zh-cid-no-tounicode.pdf")
        (HERE / "zh-cid-no-tounicode.txt").write_text(CID_TEXT + "\n", encoding="utf-8")
        print("wrote zh-cid-no-tounicode.pdf")


def make_traditional() -> None:
    c = canvas.Canvas(str(HERE / "zh-traditional.pdf"), pagesize=A4)
    c.setFont("STSong-Light", 14)
    c.drawString(50, 800, "繁體中文提取測試")
    y = 770
    for line in _split_cn(TRAD_TEXT, 24):
        c.drawString(50, y, line)
        y -= 20
    c.save()
    (HERE / "zh-traditional.txt").write_text("繁體中文提取測試\n" + TRAD_TEXT + "\n", encoding="utf-8")
    print("wrote zh-traditional.pdf")


def make_interleaved(stem: str, left: str, right: str, font: str, size: int, splitter) -> None:
    l_lines, r_lines = splitter(left), splitter(right)
    c = canvas.Canvas(str(HERE / f"{stem}.pdf"), pagesize=A4)
    c.setFont(font, size)
    title = "雙欄交錯測試" if font == "STSong-Light" else "Interleaved Two-Column Test"
    c.drawString(50, 805, title)
    y = 775
    for i in range(max(len(l_lines), len(r_lines))):
        if i < len(l_lines):
            c.drawString(45, y, l_lines[i])
        if i < len(r_lines):
            c.drawString(305, y, r_lines[i])
        y -= size + 4
    c.save()
    (HERE / f"{stem}.txt").write_text(title + "\n" + left + "\n" + right + "\n", encoding="utf-8")
    print(f"wrote {stem}.pdf")


def make_empty() -> None:
    c = canvas.Canvas(str(HERE / "zh-empty.pdf"), pagesize=A4)
    c.showPage()
    c.save()
    (HERE / "zh-empty.txt").write_text("", encoding="utf-8")
    print("wrote zh-empty.pdf")


def make_corrupt() -> None:
    (HERE / "corrupt.pdf").write_text("not a pdf\n", encoding="utf-8")
    (HERE / "corrupt.txt").write_text("", encoding="utf-8")
    print("wrote corrupt.pdf (intentionally invalid)")


def make_vertical() -> None:
    c = canvas.Canvas(str(HERE / "zh-vertical-sim.pdf"), pagesize=A4)
    c.setFont("STSong-Light", 16)
    c.drawString(300, 805, "豎排模擬")
    y = 770
    for ch in VERT_TEXT:
        c.drawString(310, y, ch)
        y -= 22
    c.save()
    (HERE / "zh-vertical-sim.txt").write_text("豎排模擬\n" + VERT_TEXT + "\n", encoding="utf-8")
    print("wrote zh-vertical-sim.pdf (simulation, not true vertical writing mode)")


def make_vertical_real() -> None:
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if not chrome:
        mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        chrome = str(mac) if mac.exists() else None
    if not chrome:
        print("skip true vertical fixture: Chrome not found")
        return
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: A4; margin: 12mm; }}
body {{ margin: 0; font-family: "Songti SC", "PingFang SC", serif; }}
.v {{ writing-mode: vertical-rl; text-orientation: upright; height: 255mm; font-size: 15pt; line-height: 1.9; }}
</style></head><body><div class="v">{VERT_REAL_TEXT}</div></body></html>"""
    html_path = HERE / "zh-vertical-real.html"
    html_path.write_text(html, encoding="utf-8")
    pdf_path = HERE / "zh-vertical-real.pdf"
    with tempfile.TemporaryDirectory(prefix="docarbiter-chrome-") as tmp:
        profile = Path(tmp) / "profile"
        profile.mkdir()
        subprocess.run(
            [
                chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                f"--user-data-dir={profile}", "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}", html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
    (HERE / "zh-vertical-real.txt").write_text(VERT_REAL_TEXT + "\n", encoding="utf-8")
    print("wrote zh-vertical-real.pdf (Chrome vertical-rl)")


if __name__ == "__main__":
    HERE.mkdir(parents=True, exist_ok=True)
    make_cid()
    make_traditional()
    make_interleaved("zh-two-column-interleaved", ZH_LEFT, ZH_RIGHT, "STSong-Light", 10, _split_cn)
    make_interleaved("en-two-column-interleaved", EN_LEFT, EN_RIGHT, "Helvetica", 10, _split_en)
    make_empty()
    make_corrupt()
    make_vertical()
    make_vertical_real()
