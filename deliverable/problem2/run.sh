#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$SCRIPT_DIR/interplanetary_museum_domain_2.pddl"
PROBLEM="$SCRIPT_DIR/problem_2.pddl"
LOG_FILE="$SCRIPT_DIR/execution.log"
PLAN_FILE="$SCRIPT_DIR/solution.plan"

if ! command -v enhsp >/dev/null 2>&1; then
    echo "enhsp is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

planner_output="$(mktemp)"
trap 'rm -f "$planner_output"' EXIT
rm -f "$PLAN_FILE"

start=$(date +%s.%N)
status=0

(
    cd "$SCRIPT_DIR" || exit 1
    enhsp \
        -o "$DOMAIN" \
        -f "$PROBLEM" \
        -planner sat-hadd \
        -sp "$PLAN_FILE"
) >"$planner_output" 2>&1 || status=$?

if [[ ! -f "$PLAN_FILE" && "$status" -eq 0 ]]; then
    printf 'Planner did not produce a plan.\n' >>"$planner_output"
    status=1
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')

{
    cat "$planner_output"
    printf '\nExecution time: %s seconds\n' "$execution_time"
    printf 'Exit status: %s\n' "$status"
} >"$LOG_FILE"

cat "$LOG_FILE"
exit "$status"
