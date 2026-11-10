#!/usr/bin/env bash
# doctor.sh — read-only health check for the docarbiter toolchain.
# Never installs, deletes, or edits anything.
set -u

CHECK_CONFLICTS=0
for a in "$@"; do
  case "$a" in
    --check-conflicts) CHECK_CONFLICTS=1 ;;
    -h|--help)
      cat <<'USAGE'
用法: ./scripts/doctor.sh [--check-conflicts]

检查:
  - core / extra 命令是否存在
  - Python 包版本
  - Tesseract 中文语言包
  - MinerU 模型目录
  - ~/.claude/skills 等目录里的重名技能与双路由器

退出码: 0 = core 完整；1 = core 缺项
USAGE
      exit 0 ;;
    *) echo "未知参数: $a" >&2; exit 2 ;;
  esac
done

ok=0
missing=0
warn=0

row() { printf "%-26s %-10s %s\n" "$1" "$2" "$3"; }

echo "== docarbiter doctor =="
echo
printf "%-26s %-10s %s\n" "检查项" "状态" "详情"
printf "%-26s %-10s %s\n" "------" "----" "----"

check_cmd() {
  local name="$1" required="$2" hint="$3"
  if command -v "$name" >/dev/null 2>&1; then
    row "$name" "OK" "$(command -v "$name")"
    ok=$((ok + 1))
  else
    if [ "$required" = "1" ]; then
      row "$name" "MISSING" "$hint"
      missing=$((missing + 1))
    else
      row "$name" "optional" "$hint"
      warn=$((warn + 1))
    fi
  fi
}

check_pkg() {
  local pkg="$1" required="$2" expected="${3:-}"
  local ver
  ver="$(python3 -c "import importlib.metadata as m; print(m.version('$pkg'))" 2>/dev/null || true)"
  if [ -n "$ver" ]; then
    if [ -n "$expected" ] && [ "$ver" != "$expected" ]; then
      row "py:$pkg" "WARN" "$ver (expected $expected)"
      warn=$((warn + 1))
    else
      row "py:$pkg" "OK" "$ver"
      ok=$((ok + 1))
    fi
  else
    if [ "$required" = "1" ]; then
      row "py:$pkg" "MISSING" "pip install $pkg"
      missing=$((missing + 1))
    else
      row "py:$pkg" "optional" "pip install $pkg"
      warn=$((warn + 1))
    fi
  fi
}

echo "-- core --"
check_cmd pdftotext 1 "brew install poppler / apt install poppler-utils"
check_pkg mineru 1 4.1.7
check_pkg docling 1 2.149.0
check_pkg liteparse 1 2.18.0
check_pkg markitdown 1 0.1.9
check_pkg rapidocr 1 3.10.0
check_pkg ocrmypdf 1 17.12.1
check_pkg pdfplumber 1 0.11.10
check_cmd mineru-doc 1 "安装本仓库 wrappers 到 ~/.local/bin"
check_cmd liteparse-doc 1 "安装本仓库 wrappers 到 ~/.local/bin"
if command -v liteparse-doc >/dev/null 2>&1; then
  if liteparse-doc --help >/dev/null 2>&1; then
    row "liteparse-doc --help" "OK" "本仓库封装（支持 --help）"
  else
    row "liteparse-doc --help" "WARN" "旧封装（--help 被当文件名）；跑 install.sh 更新"
    warn=$((warn + 1))
  fi
fi

echo
echo "-- extra (optional) --"
check_cmd paddleocr 0 "pip install paddleocr paddlepaddle"
check_cmd marker_single 0 "pip install marker-pdf"
check_cmd olmocr 0 "pip install olmocr"
check_cmd tesseract 0 "brew install tesseract tesseract-lang"
check_cmd qpdf 0 "brew install qpdf"
check_pkg pypdf 0
check_pkg pdfminer.six 0
check_pkg camelot 0

echo
echo "-- tesseract languages --"
if command -v tesseract >/dev/null 2>&1; then
  langs="$(tesseract --list-langs 2>/dev/null | tr '\n' ' ')"
  for l in chi_sim chi_tra eng; do
    case " $langs " in
      *" $l "*) row "tesseract:$l" "OK" "installed" ;;
      *) row "tesseract:$l" "MISSING" "brew install tesseract-lang" ;;
    esac
  done
else
  row "tesseract" "optional" "未安装"
fi

echo
echo "-- mineru models --"
if [ -d "$HOME/.mineru/models" ]; then
  row "~/.mineru/models" "OK" "$(du -sh "$HOME/.mineru/models" 2>/dev/null | awk '{print $1}')"
else
  row "~/.mineru/models" "MISSING" "首次运行 mineru 会下载（约 860MB）"
fi

echo
echo "-- skill conflicts --"
skill_dirs=()
for d in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.zcode/skills" "$HOME/.dsh/skills"; do
  [ -d "$d" ] && skill_dirs+=("$d")
done

if [ ${#skill_dirs[@]} -eq 0 ]; then
  row "skills" "none" "未找到 harness 技能目录"
else
  routers=""
  for d in "${skill_dirs[@]}"; do
    found=""
    for name in docarbiter doc-extract; do
      [ -f "$d/$name/SKILL.md" ] && found="$found $name"
    done
    if [ -n "$found" ]; then
      row "$(basename "$(dirname "$d")")" "router" "$found"
      case "$found" in *docarbiter*) routers="$routers docarbiter" ;; esac
      case "$found" in *doc-extract*) routers="$routers doc-extract" ;; esac
    else
      row "$(basename "$(dirname "$d")")" "ok" "无路由器"
    fi
    if [ "$CHECK_CONFLICTS" = "1" ]; then
      for t in mineru liteparse docling markitdown rapidocr ocrmypdf pdfplumber pdftotext paddleocr marker unstructured olmocr; do
        if [ -f "$d/$t/SKILL.md" ] && [ -f "$d/docarbiter/SKILL.md" ]; then
          row "conflict:$t" "WARN" "$d 同时有工具技能与 docarbiter；--profile full 下属预期"
          warn=$((warn + 1))
        fi
      done
    fi
  done
  if printf '%s' "$routers" | grep -q docarbiter && printf '%s' "$routers" | grep -q doc-extract; then
    row "dual-router" "WARN" "docarbiter 与旧 doc-extract 同时存在；建议只保留一个"
    warn=$((warn + 1))
  elif printf '%s' "$routers" | grep -q doc-extract; then
    row "legacy-router" "note" "检测到旧 doc-extract；安装 docarbiter 后建议移除旧的"
  fi
fi

echo
echo "summary: ok=$ok missing=$missing optional=$warn"
if [ "$missing" -gt 0 ]; then
  echo "结论: core 不完整。先跑 ./scripts/install.sh --profile core"
  exit 1
fi
echo "结论: core 完整。"
exit 0
