#!/bin/bash
# mineru-doc — stable wrapper for opendatalab/MinerU.
# Original code (MIT), not copied from upstream.
#
# Why the wrapper exists:
#   - MinerU resolves its cache from the current working directory. Starting
#     `mineru server start` in a project folder leaves blobs/ (~13MB) and
#     .mineru-service.lock there. This wrapper always starts the server from
#     ~/.mineru.
#   - The first engine load takes 8-15s. A direct `mineru parse` fails with
#     "No basic/standard/advanced engine available"; this wrapper retries.
#
# Usage: mineru-doc <file> [extra mineru parse args...]
set -u

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

环境: 本地 server 与解析引擎会自动就绪；模型约 860MB 在 ~/.mineru
USAGE
}

if [ $# -eq 0 ]; then usage; exit 1; fi
case "${1:-}" in -h|--help) usage; exit 0 ;; esac

if ! command -v mineru >/dev/null 2>&1; then
  echo "缺少 mineru。安装: pip install mineru==4.1.7" >&2
  exit 1
fi

mkdir -p "$HOME/.mineru"

server_ready() {
  local out
  out=$(mineru server status 2>&1 || true)
  case "$out" in *PID*) return 0 ;; *) return 1 ;; esac
}

if ! server_ready; then
  echo "[mineru-doc] 启动本地服务..." >&2
  # Do not remove the cd: MinerU uses CWD for cache paths.
  (cd "$HOME/.mineru" && mineru server start) >/dev/null 2>&1 || true
  for _ in $(seq 1 30); do
    sleep 1
    server_ready && break
  done
fi

has_wait=0
for a in "$@"; do [ "$a" = "--wait" ] && has_wait=1; done
extra=""
[ "$has_wait" -eq 0 ] && extra="--wait 300"

attempt=0
max_attempts=10
while [ "$attempt" -lt "$max_attempts" ]; do
  out=$(mineru parse "$@" $extra 2>&1)
  rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '%s\n' "$out"
    exit 0
  fi
  case "$out" in
    *"engine available"*|*"server is not running"*)
      attempt=$((attempt + 1))
      echo "[mineru-doc] 解析引擎加载中，等待重试 ($attempt/$max_attempts)..." >&2
      (cd "$HOME/.mineru" && mineru server start) >/dev/null 2>&1 || true
      sleep 8
      ;;
    *)
      printf '%s\n' "$out" >&2
      exit "$rc"
      ;;
  esac
done

echo "[mineru-doc] 引擎始终未就绪。诊断: mineru server status; mineru-kit models show" >&2
exit 1
