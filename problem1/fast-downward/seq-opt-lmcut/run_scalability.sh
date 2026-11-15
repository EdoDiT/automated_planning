#!/bin/bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
problem_dir="$(cd "$script_dir/../.." && pwd)"
domain_file="$problem_dir/interplanetary_museum_domain_1.pddl"
scalability_dir="$script_dir/scalability"
overall_status=0

for level in easy middle hard; do
    level_dir="$scalability_dir/$level"
    mkdir -p "$level_dir"
    problem_file="$problem_dir/scalability/${level}.pddl"
    log_file="$level_dir/execution.log"
    plan_file="$level_dir/solution.plan"
    planner_output="$(mktemp)"
    start=$(date +%s.%N)
    status=0

    rm -f "$plan_file" "$level_dir/sas_plan"

    (
        cd "$level_dir" || exit 1
        timeout 600s \
            planutils run downward \
            "$domain_file" \
            "$problem_file" \
            -- --search 'astar(lmcut())'
    ) >"$planner_output" 2>&1 || status=$?

    if [[ -f "$level_dir/sas_plan" ]]; then
        mv "$level_dir/sas_plan" "$plan_file"
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
    } >"$log_file"
    rm -f "$planner_output"

    if [[ "$status" -ne 0 ]]; then
        overall_status=1
    fi
done

exit "$overall_status"
