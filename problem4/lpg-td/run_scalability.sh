#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
domain="$PROJECT_DIR/interplanetary_museum_domain_4.pddl"
scalability_dir="$SCRIPT_DIR/scalability"
overall_status=0

for level in easy middle hard; do
    level_dir="$scalability_dir/$level"
    mkdir -p "$level_dir"
    problem="$PROJECT_DIR/scalability/${level}.pddl"

    set -o pipefail

    start=$(date +%s.%N)
    planner_output="$level_dir/lpg-td.log"
    solution_plan="$level_dir/solution.plan"

    rm -f "$solution_plan"

    (
        cd "$level_dir" || exit 1
        timeout 600s planutils run lpg-td "$domain" "$problem"
    ) >"$planner_output" 2>&1
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
    if [[ "$planner_status" -ne 0 ]]; then
        overall_status=1
    fi
done

exit "$overall_status"
