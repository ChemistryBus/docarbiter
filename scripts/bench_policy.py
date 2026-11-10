#!/usr/bin/env python3
"""P0 policy benchmark: fixed tools vs router vs oracle on cached results.

This does NOT re-run extraction. It reads the cached per-document results under
benchmarks/private/policy-cache/ and computes:

  - fixed single-tool policies (pdftotext / liteparse / markitdown / pdfplumber /
    MinerU / Docling)
  - router policies (quality: manuscript/table; speed: speed/table)
  - a runtime-observable verify heuristic (no truth used for selection)
  - the oracle upper bound (best tool per document, by CER)

Metrics: success rate, median/worst CER, total and average time.
Caveat: fixed-tool rows only cover documents where that tool was run; `n` is
reported. Router/oracle use the same cached rows. No document text is stored.

Run:
    python3 -I scripts/bench_policy.py
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import route  # noqa: E402

TOOLS = ["pdftotext", "liteparse", "markitdown", "pdfplumber", "mineru", "docling"]
BERT = "benchmarks/fixtures/real/bert-abstract-2p.pdf"


def load_cache(cache: Path) -> tuple[dict, list[str]]:
    data: dict[str, dict[str, dict]] = defaultdict(dict)
    docs: set[str] = set()
    for path in sorted(cache.glob("*.csv")):
        with path.open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if "doc" in r and r["doc"]:
                    doc = r["doc"].strip()
                else:
                    doc = BERT
                # Normalise absolute paths under the repo.
                try:
                    abs_doc = Path(doc)
                    if abs_doc.is_absolute():
                        doc = abs_doc.relative_to(REPO).as_posix()
                except ValueError:
                    doc = Path(doc).name
                tool = r.get("tool", "").strip()
                if tool not in TOOLS:
                    continue
                cer_raw = r.get("cer_text") or r.get("cer") or ""
                cer = float(cer_raw) if cer_raw not in ("", None) else None
                secs_raw = r.get("seconds", "")
                try:
                    secs = float(secs_raw)
                except (TypeError, ValueError):
                    secs = None
                chars_pred_raw = r.get("chars_pred") or r.get("pred_chars") or ""
                chars_truth_raw = r.get("chars_truth") or r.get("truth_chars") or ""
                entry = {
                    "status": r.get("status", ""),
                    "cer": cer,
                    "seconds": secs,
                    "chars_pred": int(float(chars_pred_raw)) if chars_pred_raw not in ("", None) else None,
                    "chars_truth": int(float(chars_truth_raw)) if chars_truth_raw not in ("", None) else None,
                    "coverage": float(r["coverage"]) if r.get("coverage") not in (None, "") else None,
                    "ctrl_ratio": float(r["ctrl_ratio"]) if r.get("ctrl_ratio") not in (None, "") else None,
                }
                data[doc][tool] = entry
                docs.add(doc)
    return data, sorted(docs)


def summarize(entries: list[dict]) -> dict:
    cers = [e["cer"] for e in entries if e["cer"] is not None]
    secs = [e["seconds"] for e in entries if e["seconds"] is not None]
    ok = [e for e in entries if e["status"] == "ok" and e["cer"] is not None]
    return {
        "n": len(entries),
        "ok": len(ok),
        "success_rate": len(ok) / len(entries) if entries else 0.0,
        "median_cer": statistics.median(cers) if cers else None,
        "worst_cer": max(cers) if cers else None,
        "total_s": sum(secs) if secs else 0.0,
        "avg_s": sum(secs) / len(secs) if secs else 0.0,
    }


def goal_for(doc: str, policy: str) -> str:
    if "table" in Path(doc).name.lower():
        return "table"
    if policy == "quality":
        return "manuscript"
    if policy == "text":
        return "text"
    return "speed"


def router_entries(data: dict, docs: list[str], policy: str) -> list[dict]:
    out = []
    for doc in docs:
        path = REPO / doc
        if not path.exists():
            continue
        decision = route.route(path, goal_for(doc, policy))
        tool = decision["intended"]
        entry = data.get(doc, {}).get(tool)
        if entry is None:
            out.append({"doc": doc, "tool": tool, "status": "missing", "cer": None,
                        "seconds": None, "chars_pred": None, "chars_truth": None,
                        "coverage": None, "ctrl_ratio": None})
        else:
            out.append({"doc": doc, "tool": tool, **entry})
    return out


def oracle_entries(data: dict, docs: list[str]) -> list[dict]:
    out = []
    for doc in docs:
        candidates = [(tool, e) for tool, e in data.get(doc, {}).items()
                      if e["status"] == "ok" and e["cer"] is not None]
        if not candidates:
            continue
        tool, entry = min(candidates, key=lambda x: x[1]["cer"])
        out.append({"doc": doc, "tool": tool, **entry})
    return out


def verify_entries(data: dict, docs: list[str]) -> list[dict]:
    """Quality router + a runtime-observable fallback heuristic.

    Selection uses only status/chars_pred/ctrl_ratio, never CER.
    """
    out = []
    for doc in docs:
        path = REPO / doc
        if not path.exists():
            continue
        primary = route.route(path, goal_for(doc, "quality"))["intended"]
        secondary = "mineru" if primary != "mineru" else "liteparse"
        p = data.get(doc, {}).get(primary)
        s = data.get(doc, {}).get(secondary)
        chosen = p
        chosen_tool = primary
        if p is None or p["status"] != "ok" or (p["chars_pred"] or 0) < 50 or (p["ctrl_ratio"] or 0) > 0.10:
            if s is not None and s["status"] == "ok":
                chosen = s
                chosen_tool = secondary
        if chosen is None:
            out.append({"doc": doc, "tool": primary, "status": "missing", "cer": None,
                        "seconds": None, "chars_pred": None, "chars_truth": None,
                        "coverage": None, "ctrl_ratio": None})
        else:
            out.append({"doc": doc, "tool": chosen_tool, **chosen})
    return out


def fmt(v, digits=4):
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.{digits}f}"
    return str(v)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default=str(REPO / "benchmarks" / "private" / "policy-cache"))
    ap.add_argument("--out", default=str(REPO / "benchmarks" / "private" / "policy.md"))
    ap.add_argument("--json-out", default=str(REPO / "benchmarks" / "private" / "policy.json"))
    args = ap.parse_args()
    data, docs = load_cache(Path(args.cache))
    if not docs:
        print(f"no cached results under {args.cache}; run bench.py first", file=sys.stderr)
        return 2

    policies: dict[str, list[dict]] = {}
    for tool in TOOLS:
        policies[f"fixed:{tool}"] = [
            {"doc": doc, "tool": tool, **data[doc][tool]}
            for doc in docs if tool in data.get(doc, {})
        ]
    policies["router:quality"] = router_entries(data, docs, "quality")
    policies["router:speed"] = router_entries(data, docs, "speed")
    policies["router:text"] = router_entries(data, docs, "text")
    policies["verify:quality"] = verify_entries(data, docs)
    policies["oracle"] = oracle_entries(data, docs)

    summary = {name: summarize(entries) for name, entries in policies.items()}

    rows = []
    for name, s in summary.items():
        rows.append({
            "policy": name,
            "n": s["n"],
            "ok": s["ok"],
            "success": f"{s['success_rate']:.1%}",
            "median_cer": s["median_cer"],
            "worst_cer": s["worst_cer"],
            "total_s": s["total_s"],
            "avg_s": s["avg_s"],
        })

    oracle_by_doc = {e["doc"]: e for e in policies["oracle"]}
    quality_by_doc = {e["doc"]: e for e in policies["router:quality"]}
    speed_by_doc = {e["doc"]: e for e in policies["router:speed"]}
    text_by_doc = {e["doc"]: e for e in policies["router:text"]}
    verify_by_doc = {e["doc"]: e for e in policies["verify:quality"]}

    lines = [
        "# P0 policy benchmark (cached results)",
        "",
        "> Fixed tools vs router vs oracle on the cached mixed corpus.",
        "> **CER is meaningful only where an answer key exists.** Fixed-tool `n` differs",
        "> because not every tool was run on every document.",
        "> No document text is stored.",
        "",
        "| policy | n | ok | success | median CER | worst CER | total s | avg s |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['policy']} | {r['n']} | {r['ok']} | {r['success']} | "
            f"{fmt(r['median_cer'])} | {fmt(r['worst_cer'])} | {fmt(r['total_s'], 2)} | {fmt(r['avg_s'], 3)} |"
        )
    lines += [
        "",
        "## Per-document router vs oracle",
        "",
        "| document | quality route | CER | speed route | CER | text route | CER | verify | CER | oracle | CER |",
        "|---|---|---:|---|---:|---|---:|---|---:|---|---:|",
    ]
    for doc in docs:
        q = quality_by_doc.get(doc, {})
        sp = speed_by_doc.get(doc, {})
        t = text_by_doc.get(doc, {})
        v = verify_by_doc.get(doc, {})
        o = oracle_by_doc.get(doc, {})
        lines.append(
            f"| {doc} | {q.get('tool','—')} | {fmt(q.get('cer'))} | "
            f"{sp.get('tool','—')} | {fmt(sp.get('cer'))} | "
            f"{t.get('tool','—')} | {fmt(t.get('cer'))} | "
            f"{v.get('tool','—')} | {fmt(v.get('cer'))} | "
            f"{o.get('tool','—')} | {fmt(o.get('cer'))} |"
        )
    lines += [
        "",
        "## Notes",
        "",
        "- `fixed:*` n is the number of cached documents for that tool; missing tools are not imputed.",
        "- `router:*` uses `route.py` before seeing any extraction result.",
        "- `verify:quality` uses only runtime-observable signals: status, chars_pred, ctrl_ratio; it never uses CER.",
        "- `oracle` is the best per-document tool by CER; it is an upper bound, not a runnable policy.",
        "- Real-workspace PDFs without an independent answer key are not included in CER.",
    ]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_out = Path(args.json_out)
    json_out.write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"report: {out}")
    for r in rows:
        print(f"{r['policy']:20} n={r['n']:2} ok={r['ok']:2} success={r['success']:>6} "
              f"median={fmt(r['median_cer'])} worst={fmt(r['worst_cer'])} total={fmt(r['total_s'],2)}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
