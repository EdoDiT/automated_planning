#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$SCRIPT_DIR/interplanetary_museum_domain_3.hddl"
PROBLEM="$SCRIPT_DIR/problem_3.hddl"
LOG_FILE="$SCRIPT_DIR/panda.log"
PLAN_FILE="$SCRIPT_DIR/solution.plan"

if ! command -v planutils >/dev/null 2>&1; then
    echo "planutils is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

# PANDA writes intermediate files in the current working directory.
work_dir="$(mktemp -d "$SCRIPT_DIR/.panda-run.XXXXXX")" || exit 1
cleanup() {
    rm -rf -- "$work_dir"
}
trap cleanup EXIT
cd "$work_dir" || exit 1

rm -f "$PLAN_FILE" "$LOG_FILE"

start=$(date +%s.%N)
planutils run panda "$DOMAIN" "$PROBLEM" 2>&1 | tee "$LOG_FILE"
planner_status=${PIPESTATUS[0]}

if [[ "$planner_status" -ne 0 ]]; then
    echo "PANDA failed; see $LOG_FILE" >&2
    exit "$planner_status"
fi

grep -E '^[[:space:]]*[0-9]+ ' "$LOG_FILE" >"$PLAN_FILE" || true

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
echo "Execution time: $execution_time seconds" | tee -a "$LOG_FILE"
