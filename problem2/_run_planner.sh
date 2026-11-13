#!/bin/bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
planner_dir="$1"
planner="$2"
heuristic="$3"
domain_file="$4"
problem_file="$5"
log_file="$planner_dir/execution.log"
plan_file="$planner_dir/solution.plan"
planner_output="$(mktemp)"
start=$(date +%s.%N)
status=0

trap 'rm -f "$planner_output"' EXIT
rm -f "$plan_file" "$planner_dir/sas_plan"

(
    cd "$planner_dir" || exit 1
    if [[ "$planner" == "downward" ]]; then
        planutils run downward "$domain_file" "$problem_file" \
            -- --search "$heuristic"
    else
        enhsp -o "$domain_file" -f "$problem_file" \
            -planner "$heuristic" -sp "$plan_file"
    fi
) >"$planner_output" 2>&1 || status=$?

if [[ "$planner" == "downward" && -f "$planner_dir/sas_plan" ]]; then
    mv "$planner_dir/sas_plan" "$plan_file"
elif [[ ! -f "$plan_file" && "$status" -eq 0 ]]; then
    printf 'Planner did not produce a plan.\n' >>"$planner_output"
    status=1
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
{
    cat "$planner_output"
    printf '\nExecution time: %s seconds\n' "$execution_time"
    printf 'Exit status: %s\n' "$status"
} >"$log_file"

exit "$status"
