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
SKILL_MODE="auto"
SKILLS_DIRS=()

usage() {
  cat <<'USAGE'
用法: ./scripts/install.sh [选项]

  --profile core|extra|full   core=8 个核心工具（默认）；extra=+重型工具；full=全部
  --skills-dir DIR            注册技能的目录，可重复；默认自动检测
  --skill-mode auto|dir|file|copy
                              技能注册方式：dir=整目录软链，file=目录+SKILL.md 软链，
                              copy=目录+SKILL.md 实体副本
                              auto: ~/.agents 用 dir；~/.codex 用 copy；其余已知目录用 file
  --no-skills                 只装工具，不注册技能
  --skills-only               只注册技能/装 wrapper，不装工具（用于快速试用）
  --force                     覆盖已存在的同名技能（先备份为 .bak.<时间>）
  --latest                    装最新版（不固定版本；不保证与实测命令一致）
  -h, --help                  显示本帮助

示例:
  ./scripts/install.sh --profile core
  ./scripts/install.sh --profile extra --skills-dir ~/.claude/skills
  ./scripts/install.sh --profile full --force
  ./scripts/install.sh --skills-only --skill-mode copy --skills-dir ~/.codex/skills
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="${2:-}"; shift 2 ;;
    --skills-dir)
      [ -n "${2:-}" ] || { echo "--skills-dir 需要一个目录" >&2; exit 2; }
      SKILLS_DIRS+=("$2"); shift 2 ;;
    --skill-mode) SKILL_MODE="${2:-}"; shift 2 ;;
    --no-skills) REGISTER_SKILLS=0; shift ;;
    --skills-only) SKILLS_ONLY=1; shift ;;
    --force) FORCE=1; shift ;;
    --latest) LATEST=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage; exit 2 ;;
  esac
done

case "$PROFILE" in core|extra|full) ;; *) echo "profile 必须是 core / extra / full" >&2; exit 2 ;; esac
case "$SKILL_MODE" in auto|dir|file|copy) ;; *) echo "skill-mode 必须是 auto / dir / file / copy" >&2; exit 2 ;; esac

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
  name="$(basename "$w" .sh)"
  dest="$BIN_DIR/$name"
  if [ -e "$dest" ] && ! cmp -s "$w" "$dest"; then
    backup="$dest.bak.$(date +%Y%m%d%H%M%S)"
    cp -p "$dest" "$backup"
    echo "[install] backup wrapper: $backup"
  fi
  install -m 0755 "$w" "$dest"
  echo "[install] wrapper: $dest"
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

SKILL_SRC_DIR="$REPO_ROOT/skills/docarbiter"
SKILL_SRC_FILE="$SKILL_SRC_DIR/SKILL.md"
INSTALL_ERRORS=0

normalize_dir() {
  local d="${1:-}"
  case "$d" in
    "~") d="$HOME" ;;
    "~/"*) d="$HOME/${d#\~/}" ;;
  esac
  while [ "${d%/}" != "$d" ] && [ "$d" != "/" ]; do d="${d%/}"; done
  case "$d" in
    /*) ;;
    *) d="$PWD/$d" ;;
  esac
  printf '%s\n' "$d"
}

realpath_py() {
  python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$1"
}

backup_path() {
  local target="$1"
  local backup="$target.bak.$(date +%Y%m%d%H%M%S)"
  [ -e "$backup" ] && backup="$backup.$$"
  mv "$target" "$backup"
  echo "[skills] backup: $backup" >&2
}

same_source_link() {
  local target="$1" src="$2"
  [ -L "$target" ] || return 1
  [ "$(realpath_py "$target")" = "$(realpath_py "$src")" ]
}

same_source_skill_file() {
  local target="$1" src="$2" expected="$3"
  [ -e "$target" ] || return 1
  if [ -L "$target" ]; then
    same_source_link "$target" "$src" && return 0
    return 1
  fi
  [ -f "$target" ] || return 1
  cmp -s "$target" "$src" && return 0
  # An older/partially edited copy of the same skill: same frontmatter name.
  grep -q "^name:[[:space:]]*${expected}[[:space:]]*$" "$target" 2>/dev/null
}

same_source_skill_dir() {
  local target="$1" src="$2" expected="$3"
  [ -d "$target" ] || [ -L "$target" ] || return 1
  [ -e "$target/SKILL.md" ] || return 1
  if [ -L "$target" ]; then
    same_source_link "$target" "$src" && return 0
    return 1
  fi
  same_source_skill_file "$target/SKILL.md" "$src/SKILL.md" "$expected"
}

link_skill() {
  local src="$1" name="$2" dir="$3"
  local target_dir="$dir/$name"
  local target="$target_dir/SKILL.md"
  mkdir -p "$target_dir"
  if same_source_link "$target" "$src"; then
    echo "[skills] 已安装: $name -> $src"
    return 0
  fi
  if [ -e "$target" ] || [ -L "$target" ]; then
    if same_source_skill_file "$target" "$src" "$name"; then
      backup_path "$target"
    elif [ "$FORCE" = "1" ]; then
      backup_path "$target"
    else
      echo "[warn] 已存在且不是本仓库技能: ${target}（用 --force 覆盖）" >&2
      return 1
    fi
  fi
  ln -sfn "$src" "$target"
  echo "[skills] $name -> $src"
}

# Some harnesses (MiniMax) skip a symlinked SKILL.md file but follow a
# whole-directory symlink.
link_skill_dir() {
  local src="$1" name="$2" dir="$3"
  local target="$dir/$name"
  mkdir -p "$dir"
  if same_source_link "$target" "$src"; then
    echo "[skills] 已安装: $name -> $src"
    return 0
  fi
  if [ -e "$target" ] || [ -L "$target" ]; then
    if same_source_skill_dir "$target" "$src" "$name"; then
      # Same skill in a different shape (entity copy or stale link): normalize.
      backup_path "$target"
    elif [ "$FORCE" = "1" ]; then
      backup_path "$target"
    else
      echo "[warn] 已存在且不是本仓库技能: ${target}（用 --force 覆盖）" >&2
      return 1
    fi
  fi
  ln -sfn "$src" "$target"
  echo "[skills] $name -> $src (directory symlink)"
}

# Codex is known to work with a real SKILL.md copy; update.sh refreshes it.
copy_skill_dir() {
  local src="$1" name="$2" dir="$3"
  local target="$dir/$name"
  local src_file="$src/SKILL.md"
  local target_file="$target/SKILL.md"
  mkdir -p "$dir"

  if [ -L "$target" ]; then
    if same_source_link "$target" "$src"; then
      backup_path "$target"
    elif [ "$FORCE" = "1" ]; then
      backup_path "$target"
    else
      echo "[warn] 已存在且不是本仓库技能: ${target}（用 --force 覆盖）" >&2
      return 1
    fi
  elif [ -d "$target" ]; then
    if [ -f "$target_file" ] && [ ! -L "$target_file" ] && cmp -s "$src_file" "$target_file"; then
      echo "[skills] 已安装: $name (copy, up to date)"
      return 0
    fi
    if [ -e "$target_file" ] || [ -L "$target_file" ]; then
      if same_source_skill_file "$target_file" "$src_file" "$name"; then
        backup_path "$target_file"
      elif [ "$FORCE" = "1" ]; then
        backup_path "$target_file"
      else
        echo "[warn] 已存在且不是本仓库技能: ${target_file}（用 --force 覆盖）" >&2
        return 1
      fi
    fi
  elif [ -e "$target" ]; then
    if same_source_skill_file "$target" "$src_file" "$name" || [ "$FORCE" = "1" ]; then
      backup_path "$target"
    else
      echo "[warn] 已存在且不是本仓库技能: ${target}（用 --force 覆盖）" >&2
      return 1
    fi
  fi

  mkdir -p "$target"
  install -m 0644 "$src_file" "$target_file"
  echo "[skills] $name -> $target_file (copy)"
}

verify_install() {
  local name="$1" dir="$2" mode="$3"
  local target="$dir/$name"
  local target_file="$target/SKILL.md"
  local problem=""

  if [ ! -e "$target_file" ]; then
    problem="SKILL.md is missing"
  elif [ "$mode" = "dir" ]; then
    [ -L "$target" ] || problem="expected a whole-directory symlink at $target"
    if [ -z "$problem" ] && [ -L "$target_file" ]; then
      problem="SKILL.md inside a directory symlink must resolve to a real file"
    fi
  elif [ "$mode" = "copy" ]; then
    [ -L "$target" ] && problem="expected a real directory, found a symlink at $target"
    if [ -z "$problem" ] && [ -L "$target_file" ]; then
      problem="expected a real SKILL.md copy, found a symlink"
    fi
    if [ -z "$problem" ] && ! cmp -s "$SKILL_SRC_FILE" "$target_file"; then
      problem="SKILL.md copy is stale; expected byte-identical to the repo"
    fi
  else
    if [ -z "$problem" ] && ! same_source_link "$target_file" "$SKILL_SRC_FILE"; then
      problem="expected SKILL.md to be a symlink to the repo"
    fi
  fi

  if [ -z "$problem" ]; then
    local fm_name
    fm_name="$(sed -n 's/^name:[[:space:]]*//p' "$target_file" | head -1)"
    [ "$fm_name" = "$name" ] || problem="frontmatter name is '${fm_name}', expected '${name}'"
  fi

  if [ -n "$problem" ]; then
    echo "[error] 技能自检失败: $target ($mode): $problem" >&2
    echo "        修复: ./scripts/install.sh --skills-only --skills-dir \"$dir\" --skill-mode $mode --force" >&2
    return 1
  fi
  echo "[skills] 自检通过: $name ($mode) at $target"
}

if [ ${#SKILLS_DIRS[@]} -eq 0 ]; then
  # ~/.agents/skills is the shared global root for pi-agent harnesses
  # (MiniMax Code and others); check it first so one install covers them.
  for d in "$HOME/.agents/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.zcode/skills" "$HOME/.dsh/skills"; do
    [ -d "$d" ] && SKILLS_DIRS+=("$d")
  done
  [ ${#SKILLS_DIRS[@]} -eq 0 ] && SKILLS_DIRS=("$HOME/.claude/skills")
fi

for raw_dir in "${SKILLS_DIRS[@]}"; do
  dir="$(normalize_dir "$raw_dir")"
  mode="$SKILL_MODE"
  if [ "$mode" = "auto" ]; then
    case "$dir" in
      "$HOME/.agents/skills") mode="dir" ;;
      "$HOME/.codex/skills") mode="copy" ;;
      "$HOME/.claude/skills"|"$HOME/.dsh/skills"|"$HOME/.zcode/skills") mode="file" ;;
      "$HOME/.minimax/skills")
        echo "[warn] ${dir} 不被 MiniMax Code 扫描；请改用 ~/.agents/skills" >&2
        mode="file"
        ;;
      *)
        echo "[error] 未知技能目录: ${dir}" >&2
        echo "        请显式指定 --skill-mode dir|file|copy" >&2
        exit 2
        ;;
    esac
  fi
  mkdir -p "$dir"
  if ! {
    if [ "$mode" = "dir" ]; then
      link_skill_dir "$SKILL_SRC_DIR" "docarbiter" "$dir"
    elif [ "$mode" = "copy" ]; then
      copy_skill_dir "$SKILL_SRC_DIR" "docarbiter" "$dir"
    else
      link_skill "$SKILL_SRC_FILE" "docarbiter" "$dir"
    fi
  }; then
    INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
    continue
  fi
  if ! verify_install "docarbiter" "$dir" "$mode"; then
    INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
  fi
  if [ "$PROFILE" = "full" ]; then
    for f in "$REPO_ROOT"/skills/_tools/*.md; do
      [ -f "$f" ] || continue
      link_skill "$f" "$(basename "$f" .md)" "$dir" || INSTALL_ERRORS=$((INSTALL_ERRORS + 1))
    done
  fi
  if [ -f "$dir/doc-extract/SKILL.md" ]; then
    echo "[warn] 检测到另一个文档提取路由器: $dir/doc-extract" >&2
    echo "       它与 docarbiter 功能重叠；建议只保留一个，或运行 doctor.sh --check-conflicts" >&2
  fi
done

if [ "$INSTALL_ERRORS" -gt 0 ]; then
  echo "[install] 技能注册自检未通过（$INSTALL_ERRORS 项）；按上面的修复命令处理。" >&2
  exit 1
fi

echo "[install] 完成。运行 ./scripts/doctor.sh 体检。"
