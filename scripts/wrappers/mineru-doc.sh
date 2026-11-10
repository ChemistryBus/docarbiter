#!/bin/bash
# mineru-doc — stable wrapper for opendatalab/MinerU.
# Original code (MIT), not copied from upstream.
#
# Why the wrapper exists:
#   - MinerU resolves its cache from the current working directory. Starting
#     `mineru server start` in a project folder leaves blobs/ (~13MB) and
#     .mineru-service.lock there. This wrapper always starts the server from
#     MINERU_HOME (default: ~/.mineru).
#   - The first engine load takes 8-15s. A direct `mineru parse` fails with
#     "server is not running"; this wrapper retries only recoverable states.
#   - A missing engine configuration is NOT a slow start. Retrying it 10 times
#     only hides the real error, so it exits immediately with the first
#     diagnostic.
#
# Usage: mineru-doc <file> [extra mineru parse args...]
set -u

MINERU_HOME="${MINERU_HOME:-$HOME/.mineru}"

usage() {
  cat >&2 <<'USAGE'
用法: mineru-doc <文件> [额外参数]

常用:
  mineru-doc a.pdf                      # 前 10 页（MinerU 默认）
  mineru-doc a.pdf --pages 1-5          # 指定页
  mineru-doc a.pdf --pages all          # 全部
  mineru-doc a.pdf -o out.md            # 落盘
  mineru-doc a.pdf --tier flash         # 免服务，纯文字快速预览
  mineru-doc -h | --help                # 本帮助

环境:
  MINERU_HOME   服务启动目录与缓存根；默认 ~/.mineru
                隔离测试时设为临时目录，避免与正在运行的服务抢锁
USAGE
}

if [ $# -eq 0 ]; then usage; exit 1; fi
case "${1:-}" in -h|--help) usage; exit 0 ;; esac

if ! command -v mineru >/dev/null 2>&1; then
  echo "缺少 mineru。安装: pip install mineru==4.1.7" >&2
  exit 1
fi

mkdir -p "$MINERU_HOME"

# `--tier flash` does not need the local server at all.
use_flash=0
for a in "$@"; do
  case "$a" in flash|--tier=flash) use_flash=1 ;; esac
done
for ((i = 1; i <= $#; i++)); do
  if [ "${!i}" = "--tier" ]; then
    j=$((i + 1))
    [ "$j" -le "$#" ] && [ "${!j}" = "flash" ] && use_flash=1
  fi
done

server_ready() {
  local out
  out=$(mineru server status 2>&1 || true)
  case "$out" in
    *"not running"*|*"stopped"*) return 1 ;;
    *PID*|*"running"*|*"online"*) return 0 ;;
    *) return 1 ;;
  esac
}

start_server() {
  # MinerU resolves its cache from the CWD; keep that inside MINERU_HOME so a
  # project directory never gets blobs/ or .mineru-service.lock.
  (cd "$MINERU_HOME" && mineru server start) >/dev/null 2>&1 || true
}

if [ "$use_flash" = "0" ] && ! server_ready; then
  echo "[mineru-doc] 启动本地服务（MINERU_HOME=${MINERU_HOME}）..." >&2
  start_server
  for _ in $(seq 1 30); do
    sleep 1
    server_ready && break
  done
fi

has_wait=0
for a in "$@"; do [ "$a" = "--wait" ] && has_wait=1; done
extra=""
[ "$has_wait" -eq 0 ] && extra="--wait 300"

first_diag=""
record_diag() {
  [ -z "$first_diag" ] && first_diag="$1"
}

attempt=0
max_attempts=10
while [ "$attempt" -lt "$max_attempts" ]; do
  out=$(mineru parse "$@" $extra 2>&1)
  rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$out"
    exit 0
  fi

  record_diag "$out"

  # Non-recoverable: the engine is not configured. Retrying cannot fix it.
  case "$out" in
    *"No basic/standard/advanced engine available"*|*"engine not configured"*|*"not configured"*|*"No models"*|*"license"*)
      echo "[mineru-doc] 解析引擎未就绪，且不是可重试的启动状态。" >&2
      echo "[mineru-doc] 首次诊断:" >&2
      printf '%s\n' "$first_diag" >&2
      echo "[mineru-doc] 检查: mineru config show; mineru-kit models show" >&2
      echo "[mineru-doc] MINERU_HOME=$MINERU_HOME" >&2
      exit 3
      ;;
  esac

  # Recoverable: the server is starting or not reachable yet.
  case "$out" in
    *"server is not running"*|*"Connection refused"*|*"connection refused"*|*"engine is loading"*|*"engine is not ready"*|*"not ready"*|*"loading"*)
      attempt=$((attempt + 1))
      echo "[mineru-doc] 解析引擎加载中，等待重试 ($attempt/$max_attempts)..." >&2
      [ "$use_flash" = "0" ] && start_server
      sleep 8
      ;;
    *)
      printf '%s\n' "$out" >&2
      exit "$rc"
      ;;
  esac
done

echo "[mineru-doc] 引擎始终未就绪（可重试状态已用尽）。" >&2
if [ -n "$first_diag" ]; then
  echo "[mineru-doc] 首次诊断:" >&2
  printf '%s\n' "$first_diag" >&2
fi
echo "[mineru-doc] 检查: mineru server status; mineru-kit models show; MINERU_HOME=$MINERU_HOME" >&2
exit 1
