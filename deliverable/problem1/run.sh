#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$SCRIPT_DIR/interplanetary_museum_domain_1.pddl"
PROBLEM="$SCRIPT_DIR/problem.pddl"
LOG_FILE="$SCRIPT_DIR/execution.log"
PLAN_FILE="$SCRIPT_DIR/solution.plan"

if ! command -v planutils >/dev/null 2>&1; then
    echo "planutils is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

planner_output="$(mktemp)"
trap 'rm -f "$planner_output"' EXIT
rm -f "$PLAN_FILE" "$SCRIPT_DIR/sas_plan"

start=$(date +%s.%N)
status=0

(
    cd "$SCRIPT_DIR" || exit 1
    planutils run downward \
        "$DOMAIN" \
        "$PROBLEM" \
        -- --search 'lazy_greedy([ff(),cea()],preferred=[ff(),cea()])'
) >"$planner_output" 2>&1 || status=$?

if [[ -f "$SCRIPT_DIR/sas_plan" ]]; then
    mv "$SCRIPT_DIR/sas_plan" "$PLAN_FILE"
elif [[ "$status" -eq 0 ]]; then
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
