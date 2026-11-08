#!/bin/bash

start=$(date +%s.%N)
planner_output=$(mktemp)
log_file="execution.log"
trap 'rm -f "$planner_output"' EXIT

rm -f sas_plan solution.plan

enhsp \
    -o interplanetary_museum_domain_1.pddl \
    -f problem.pddl \
    -planner opt-blind \
    -sp sas_plan > "$planner_output" 2>&1

if [[ -f sas_plan ]]; then
    cp sas_plan solution.plan
else
    echo "Planner did not produce sas_plan" >&2
    exit 1
fi

end=$(date +%s.%N)
execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
statistics=$(grep -E '^(Plan-Length|Metric \(Search\)|Planning Time \(msec\)|Heuristic Time \(msec\)|Search Time \(msec\)|Expanded Nodes|States Evaluated|Number of Dead-Ends detected|Number of Duplicates detected):' "$planner_output" || true)

{
    printf '%s\n' "$statistics"
    printf 'Execution time: %s seconds\n\n' "$execution_time"
} | tee -a "$log_file"