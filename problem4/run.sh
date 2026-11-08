#!/bin/bash

set -o pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir" || exit 1

start=$(date +%s.%N)
planner_output=$(mktemp)
log_file="$script_dir/execution.log"
optic_plan="$script_dir/problem_4.pddl.plan"
solution_plan="$script_dir/solution.plan"
trap 'rm -f "$planner_output"' EXIT

rm -f "$optic_plan" "$solution_plan"

timeout 180s planutils run optic \
    "$script_dir/interplanetary_museum_domain_4.pddl $script_dir/problem_4.pddl" \
    > "$planner_output" 2>&1
planner_status=$?

if [[ -s "$optic_plan" ]]; then
    cp "$optic_plan" "$solution_plan"
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
    ' "$planner_output" > "$solution_plan"
fi

if [[ ! -s "$solution_plan" ]]; then
    printf 'Planner did not produce a solution plan.\n' >&2
    [[ "$planner_status" -eq 0 ]] && planner_status=1
elif grep -q '^;;;; Solution Found$' "$planner_output"; then
    # OPTIC can return non-zero after finding a valid plan while searching
    # for an improved one.
    planner_status=0
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
statistics=$(grep -E '^(Plan-Length|Metric \(Search\)|Planning Time \(msec\)|Heuristic Time \(msec\)|Search Time \(msec\)|Expanded Nodes|States Evaluated|Number of Dead-Ends detected|Number of Duplicates detected):' "$planner_output" || true)

if ! {
    cat "$planner_output"
    printf '\nPlanner exit status: %s\n' "$planner_status"
    if [[ -n "$statistics" ]]; then
        printf '%s\n' "$statistics"
    else
        printf 'Planner statistics: unavailable\n'
    fi
    printf 'Execution time: %s seconds\n\n' "$execution_time"
} > "$log_file"; then
    printf 'Unable to write execution log: %s\n' "$log_file" >&2
    exit 1
fi

cat "$log_file"
exit "$planner_status"
