#!/bin/bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
problem_dir="$(cd "$script_dir/../.." && pwd)"
log_file="$script_dir/execution.log"
plan_file="$script_dir/solution.plan"
planner_output="$(mktemp)"
start=$(date +%s.%N)
status=0

trap 'rm -f "$planner_output"' EXIT
rm -f "$plan_file"

(
    cd "$script_dir" || exit 1
    enhsp -o "$problem_dir/interplanetary_museum_domain_1.pddl" \
        -f "$problem_dir/problem.pddl" \
        -planner opt-hmax \
        -sp "$plan_file"
) >"$planner_output" 2>&1 || status=$?

if [[ ! -f "$plan_file" && "$status" -eq 0 ]]; then
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
