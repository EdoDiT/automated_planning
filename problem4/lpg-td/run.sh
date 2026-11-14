#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
domain="$PROJECT_DIR/interplanetary_museum_domain_4.pddl"
problem="$PROJECT_DIR/problem_4.pddl"

set -o pipefail

start=$(date +%s.%N)
planner_output="$SCRIPT_DIR/lpg-td.log"
solution_plan="$SCRIPT_DIR/solution.plan"

rm -f "$solution_plan"

timeout 180s planutils run lpg-td "$domain" "$problem" \
    >"$planner_output" 2>&1
planner_status=$?

grep -E '^[[:space:]]*[0-9]+(\.[0-9]+)?:' "$planner_output" \
    >"$solution_plan" || true

if [[ ! -s "$solution_plan" ]]; then
    printf 'Planner did not produce a solution plan.\n' >>"$planner_output"
    [[ "$planner_status" -eq 0 ]] && planner_status=1
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
printf '\nPlanner exit status: %s\nExecution time: %s seconds\n' \
    "$planner_status" "$execution_time" >>"$planner_output"

cat "$planner_output"
exit "$planner_status"
