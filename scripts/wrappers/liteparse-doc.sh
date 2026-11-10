#!/bin/bash
# liteparse-doc — stable wrapper for run-llama/liteparse.
# Upstream ships a Python package but no CLI. This wrapper is original code
# (MIT), not copied from upstream.
#
# Why the wrapper exists:
#   - liteparse defaults to OCR, which tries to download tessdata and can block
#     for ~123s when GitHub is unreachable. OCR is forced off unless --ocr.
#   - The wrapper exposes only the options this collection tests.
#
# Usage: liteparse-doc <file> [--pages N-M|all] [--json] [--ocr]
set -u

usage() {
  cat >&2 <<'USAGE'
用法: liteparse-doc <文件> [选项]

  --pages N-M    只解析指定页范围；--pages all 表示全部
  --ocr          强制启用 OCR（需先配好 tessdata，否则很慢）
  --json         输出 JSON（含词级坐标、字体、字号）
  -h, --help     显示本帮助

示例:
  liteparse-doc book.pdf --pages 99-110
  liteparse-doc book.pdf --json
  liteparse-doc paper.pdf
USAGE
}

if [ $# -eq 0 ]; then usage; exit 1; fi
case "${1:-}" in -h|--help) usage; exit 0 ;; esac

exec python3 -I - "$@" <<'PY'
import json
import sys
import time

args = sys.argv[1:]
path = args[0]
pages = None
ocr = False
as_json = False

rest = args[1:]
i = 0
while i < len(rest):
    a = rest[i]
    if a in ("-h", "--help"):
        print("用法: liteparse-doc <文件> [--pages N-M|all] [--json] [--ocr]", file=sys.stderr)
        sys.exit(0)
    if a == "--pages" and i + 1 < len(rest):
        pages = rest[i + 1]
        i += 2
        continue
    if a == "--ocr":
        ocr = True
        i += 1
        continue
    if a == "--json":
        as_json = True
        i += 1
        continue
    print(f"未知参数: {a}", file=sys.stderr)
    sys.exit(2)

try:
    from liteparse import LiteParse
except ImportError:
    print("缺少 liteparse。安装: pip install liteparse==2.18.0", file=sys.stderr)
    sys.exit(1)

kw = dict(ocr_enabled=ocr, quiet=True, output_format="markdown")
if pages and pages.lower() != "all":
    kw["target_pages"] = pages

t0 = time.time()
try:
    res = LiteParse(**kw).parse(path)
except FileNotFoundError:
    print(f"文件不存在: {path}", file=sys.stderr)
    sys.exit(1)
except Exception as exc:  # noqa: BLE001 - surface upstream error verbatim
    print(f"liteparse 失败: {exc}", file=sys.stderr)
    sys.exit(1)
dt = time.time() - t0

if as_json:
    out = [
        {
            "page": p.page_num,
            "text": p.text,
            "items": [
                {
                    "text": it.text,
                    "x": it.x,
                    "y": it.y,
                    "w": it.width,
                    "h": it.height,
                    "font": it.font_name,
                    "size": it.font_size,
                }
                for it in (p.text_items or [])
            ],
        }
        for p in res.pages
    ]
    print(json.dumps(out, ensure_ascii=False, indent=1))
else:
    for p in res.pages:
        print(p.markdown or p.text or "")

print(f"\n<!-- liteparse: {res.num_pages} 页, {dt:.2f}s -->", file=sys.stderr)
PY
