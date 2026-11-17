#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="$SCRIPT_DIR/interplanetary_museum_domain_4.pddl"
PROBLEM="$SCRIPT_DIR/problem_4.pddl"
LOG_FILE="$SCRIPT_DIR/optic.log"
PLAN_FILE="$SCRIPT_DIR/solution.plan"
OPTIC_PLAN="$SCRIPT_DIR/problem_4.pddl.plan"

if ! command -v planutils >/dev/null 2>&1; then
    echo "planutils is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

cd "$SCRIPT_DIR" || exit 1

planner_output="$(mktemp)"
trap 'rm -f "$planner_output"' EXIT
rm -f "$OPTIC_PLAN" "$PLAN_FILE"

start=$(date +%s.%N)
planner_status=0
timeout 180s planutils run optic "-N $DOMAIN $PROBLEM" >"$planner_output" 2>&1 || planner_status=$?

if [[ -s "$OPTIC_PLAN" ]]; then
    cp "$OPTIC_PLAN" "$PLAN_FILE"
else
    awk '
        /;;;; Solution Found/ || /Found new plan:/ {
            capture=1
            count=0
            next
        }
        /Solution with original makespan/ {capture=0}
        capture && /^[[:space:]]*[0-9]+\.[0-9]+:/ {
            plan[++count]=$0
        }
        END {
            for (i=1; i<=count; i++) print plan[i]
        }
    ' "$planner_output" >"$PLAN_FILE"
fi

if [[ ! -s "$PLAN_FILE" ]]; then
    printf 'Planner did not produce a solution plan.\n' >>"$planner_output"
    [[ "$planner_status" -eq 0 ]] && planner_status=1
elif grep -q '^;;;; Solution Found$' "$planner_output"; then
    planner_status=0
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')

{
    cat "$planner_output"
    printf '\nPlanner exit status: %s\n' "$planner_status"
    printf 'Execution time: %s seconds\n' "$execution_time"
} >"$LOG_FILE"

cat "$LOG_FILE"
exit "$planner_status"
