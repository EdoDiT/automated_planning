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
    planner_output="$(mktemp)"
    optic_plan="$level_dir/${level}.pddl.plan"
    solution_plan="$level_dir/solution.plan"
    log_file="$level_dir/optic.log"

    rm -f "$optic_plan" "$solution_plan"

    (
        cd "$level_dir" || exit 1
        timeout 600s planutils run optic \
            "$domain $problem"
    ) >"$planner_output" 2>&1
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
        ' "$planner_output" >"$solution_plan"
    fi

    if [[ ! -s "$solution_plan" ]]; then
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
    } >"$log_file"
    rm -f "$planner_output"

    cat "$log_file"
    if [[ "$planner_status" -ne 0 ]]; then
        overall_status=1
    fi
done

exit "$overall_status"
