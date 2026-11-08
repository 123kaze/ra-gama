#!/usr/bin/env bash
# Exercise the frozen cache implementation without downloading datasets or building C++ drivers.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
PY=${PYTHON:-python3}
if ! "$PY" -c 'import numpy, numba' >/dev/null 2>&1; then
  echo '需要含 numpy、numba 的 Python；可设置 PYTHON=/path/to/.condaenv/bin/python。不会自动安装。' >&2
  exit 1
fi
"$PY" "$ROOT/windows_research/round10_fpcache/src/test_cache_fp.py"
