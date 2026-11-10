#!/usr/bin/env bash
# install.sh — install upstream tools and register the docarbiter skill.
# This repository contains no upstream code; this script only calls package
# managers and links our own thin-shell skills.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PROFILE="core"
REGISTER_SKILLS=1
FORCE=0
LATEST=0
SKILLS_ONLY=0
SKILLS_DIRS=()

usage() {
  cat <<'USAGE'
用法: ./scripts/install.sh [选项]

  --profile core|extra|full   core=8 个核心工具（默认）；extra=+重型工具；full=全部
  --skills-dir DIR            注册技能的目录，可重复；默认自动检测
  --no-skills                 只装工具，不注册技能
  --skills-only               只注册技能/装 wrapper，不装工具（用于快速试用）
  --force                     覆盖已存在的同名技能（先备份为 .bak.<时间>）
  --latest                    装最新版（不固定版本；不保证与实测命令一致）
  -h, --help                  显示本帮助

示例:
  ./scripts/install.sh --profile core
  ./scripts/install.sh --profile extra --skills-dir ~/.claude/skills
  ./scripts/install.sh --profile full --force
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --skills-dir) SKILLS_DIRS+=("${2:-}"); shift 2 ;;
    --no-skills) REGISTER_SKILLS=0; shift ;;
    --skills-only) SKILLS_ONLY=1; shift ;;
    --force) FORCE=1; shift ;;
    --latest) LATEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 2 ;;
  esac
done

case "$PROFILE" in core|extra|full) ;; *) echo "profile 必须是 core / extra / full" >&2; exit 2 ;; esac

command -v python3 >/dev/null 2>&1 || { echo "缺少 python3（建议 3.10+）" >&2; exit 1; }
PY_VER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "[install] Python $PY_VER, profile=$PROFILE"
case "$PY_VER" in
  3.10|3.11|3.12) ;;
  *) echo "[warn] 本项目在 Python 3.11.11 上实测；$PY_VER 未验证，MinerU/Docling 可能装不上" >&2 ;;
esac

# ---------------------------------------------------------------- system deps
install_system_deps() {
  # Do not upgrade formulas that are already installed: `brew install` can
  # upgrade dependencies (observed: poppler 26.08 -> 26.11 and pcre2/glib/cairo).
  # Only install what is missing.
  if [ "$(uname -s)" = "Darwin" ]; then
    command -v brew >/dev/null 2>&1 || { echo "[warn] 没有 Homebrew；跳过系统依赖" >&2; return; }
    for pkg in poppler tesseract tesseract-lang qpdf; do
      if brew list --versions "$pkg" >/dev/null 2>&1; then
        echo "[install] brew $pkg already installed; skip (no upgrade)"
      else
        echo "[install] brew install $pkg"
        HOMEBREW_NO_AUTO_UPDATE=1 brew install "$pkg" || echo "[warn] brew 安装 $pkg 未成功" >&2
      fi
    done
  elif command -v apt-get >/dev/null 2>&1; then
    echo "[install] apt: poppler-utils tesseract-ocr tesseract-ocr-chi-sim qpdf"
    sudo apt-get update -qq && sudo apt-get install -y --no-upgrade \
      poppler-utils tesseract-ocr tesseract-ocr-chi-sim qpdf \
      || echo "[warn] apt 安装未完全成功（可能需要 sudo）" >&2
  else
    echo "[warn] 未识别的平台；请手动安装 poppler / tesseract(chi_sim) / qpdf" >&2
  fi
}

install_pip_lock() {
  local lock="$1"; local fatal="$2"
  [ -f "$lock" ] || { echo "[warn] 缺少 $lock" >&2; return; }
  while IFS= read -r line; do
    case "$line" in ''|'#'*) continue ;; esac
    echo "[install] pip install $line"
    if ! python3 -m pip install "$line"; then
      if [ "$fatal" = "1" ]; then echo "[error] 核心依赖安装失败: $line" >&2; exit 1; fi
      echo "[warn] 跳过失败的可选依赖: $line" >&2
    fi
  done < "$lock"
}

install_pip_latest() {
  local names=("$@")
  for n in "${names[@]}"; do
    echo "[install] pip install --upgrade $n"
    python3 -m pip install --upgrade "$n" || echo "[warn] $n 安装失败（未验证版本）" >&2
  done
}

if [ "$SKILLS_ONLY" = "0" ]; then
  install_system_deps

  if [ "$LATEST" = "1" ]; then
    install_pip_latest mineru docling liteparse markitdown rapidocr ocrmypdf pdfplumber
  else
    install_pip_lock "$REPO_ROOT/requirements-core.lock" 1
  fi

  # MinerU config (idempotent; safe to re-run)
  if command -v mineru >/dev/null 2>&1; then
    mkdir -p "$HOME/.mineru"
    mineru config set parse_server.local.managed_tier basic >/dev/null 2>&1 || true
    mineru config set parse_server.local.mode managed >/dev/null 2>&1 || true
  fi

  if [ "$PROFILE" = "extra" ] || [ "$PROFILE" = "full" ]; then
    if [ "$LATEST" = "1" ]; then
      install_pip_latest paddleocr paddlepaddle marker-pdf surya-ocr unstructured olmocr camelot-py pytesseract pypdf pdfminer.six
    else
      install_pip_lock "$REPO_ROOT/requirements-extra.lock" 0
    fi
  fi
else
  echo "[install] --skills-only: 跳过工具安装"
fi

# ---------------------------------------------------------------- wrappers
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
for w in "$REPO_ROOT"/scripts/wrappers/*.sh; do
  [ -f "$w" ] || continue
  install -m 0755 "$w" "$BIN_DIR/$(basename "$w" .sh)"
  echo "[install] wrapper: $BIN_DIR/$(basename "$w" .sh)"
done
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) echo "[warn] $BIN_DIR 不在 PATH；请把下面一行加入 shell 配置：" >&2
     echo "       export PATH=\"$BIN_DIR:\$PATH\"" >&2 ;;
esac
for name in liteparse-doc mineru-doc; do
  resolved="$(command -v "$name" 2>/dev/null || true)"
  if [ -n "$resolved" ] && [ "$resolved" != "$BIN_DIR/$name" ]; then
    echo "[warn] PATH 中的 $name 是 ${resolved}，不是 $BIN_DIR/$name" >&2
    echo "       请把 $BIN_DIR 放到 PATH 前面，否则会继续调用旧封装" >&2
  fi
done

# ---------------------------------------------------------------- skills
if [ "$REGISTER_SKILLS" = "0" ]; then
  echo "[install] 跳过技能注册"
  exit 0
fi

if [ ${#SKILLS_DIRS[@]} -eq 0 ]; then
  for d in "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.zcode/skills" "$HOME/.dsh/skills"; do
    [ -d "$d" ] && SKILLS_DIRS+=("$d")
  done
  [ ${#SKILLS_DIRS[@]} -eq 0 ] && SKILLS_DIRS=("$HOME/.claude/skills")
fi

link_skill() {
  local src="$1" name="$2" dir="$3"
  local target_dir="$dir/$name"
  local target="$target_dir/SKILL.md"
  mkdir -p "$target_dir"
  if [ -L "$target" ]; then
    local current
    current="$(readlink "$target" || true)"
    if [ "$current" = "$src" ]; then
      echo "[skills] 已安装: $name -> $src"
      return
    fi
  fi
  if [ -e "$target" ] && [ "$FORCE" != "1" ]; then
    echo "[warn] 已存在且不是本仓库链接: ${target}（用 --force 覆盖）" >&2
    return
  fi
  if [ -e "$target" ] && [ "$FORCE" = "1" ]; then
    mv "$target" "$target.bak.$(date +%Y%m%d%H%M%S)"
  fi
  ln -sfn "$src" "$target"
  echo "[skills] $name -> $src"
}

for dir in "${SKILLS_DIRS[@]}"; do
  mkdir -p "$dir"
  link_skill "$REPO_ROOT/skills/docarbiter/SKILL.md" "docarbiter" "$dir"
  if [ "$PROFILE" = "full" ]; then
    for f in "$REPO_ROOT"/skills/_tools/*.md; do
      [ -f "$f" ] || continue
      link_skill "$f" "$(basename "$f" .md)" "$dir"
    done
  fi
  if [ -f "$dir/doc-extract/SKILL.md" ]; then
    echo "[warn] 检测到另一个文档提取路由器: $dir/doc-extract" >&2
    echo "       它与 docarbiter 功能重叠；建议只保留一个，或运行 doctor.sh --check-conflicts" >&2
  fi
done

echo "[install] 完成。运行 ./scripts/doctor.sh 体检。"
