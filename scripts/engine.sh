#!/bin/sh
cd "$(dirname "$0")/.." || exit 1
PY="${PYTHON:-python3}"
if ! "$PY" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY=/opt/homebrew/bin/python3
fi
exec "$PY" uci.py
