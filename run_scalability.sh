#!/bin/bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
overall_status=0

for problem in problem1 problem2 problem3 problem4; do
    problem_script="$script_dir/$problem/run_scalability.sh"
    printf '========================================\n'
    printf 'Running %s\n' "${problem_script#"$script_dir"/}"
    printf '========================================\n'
    if ! "$problem_script"; then
        printf 'Problem scalability suite failed: %s\n' "${problem_script#"$script_dir"/}" >&2
        overall_status=1
    fi
done

exit "$overall_status"
