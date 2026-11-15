#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "[INFO] Virtual environment not found at .venv; using system python3..."
    VENV_PYTHON="python3"
fi

echo "=== 1/3 Parsing and aggregating problem & planner run statistics ==="
"$VENV_PYTHON" "$SCRIPT_DIR/parse_and_aggregate.py"

echo "=== 2/3 Generating LaTeX tables ==="
"$VENV_PYTHON" "$SCRIPT_DIR/generate_latex_tables.py"

echo "=== 3/3 Generating plots (PDF & PNG) ==="
"$VENV_PYTHON" "$SCRIPT_DIR/generate_plots.py"

echo "=== Done! All outputs are in $SCRIPT_DIR/output/ ==="
