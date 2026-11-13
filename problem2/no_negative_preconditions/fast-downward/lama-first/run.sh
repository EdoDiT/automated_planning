#!/bin/bash
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$script_dir/../../../_run_planner.sh" "$script_dir" downward \
    'lazy_greedy([ff(),cea()],preferred=[ff(),cea()])' \
    "$script_dir/../../interplanetary_museum_domain_2.pddl" "$script_dir/../../problem_2.pddl"
