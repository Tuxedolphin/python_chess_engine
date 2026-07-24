#!/bin/sh
cd "$(dirname "$0")/.." || exit 1

supports() {
    command -v "$1" >/dev/null 2>&1 &&
    "$1" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' 2>/dev/null
}

if [ -n "$PYTHON" ]; then
    PY="$PYTHON"
else
    for candidate in pypy3.11 pypy3 python3 /opt/homebrew/bin/python3; do
        if supports "$candidate"; then
            PY="$candidate"
            break
        fi
    done
fi

exec "${PY:-python3}" uci.py
