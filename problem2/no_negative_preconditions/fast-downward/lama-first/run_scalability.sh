#!/bin/bash
set -u
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
overall_status=0

for level in easy middle hard; do
    level_dir="$script_dir/scalability/$level"
    mkdir -p "$level_dir"
    if ! "$script_dir/../../../_run_planner.sh" "$level_dir" downward \
        'lazy_greedy([ff(),cea()],preferred=[ff(),cea()])' \
        "$script_dir/../../interplanetary_museum_domain_2.pddl" \
        "$script_dir/../../scalability/${level}.pddl"; then
        overall_status=1
    fi
done

exit "$overall_status"
