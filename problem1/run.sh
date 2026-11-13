#!/bin/bash

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
overall_status=0

while IFS= read -r planner_script; do
    printf 'Running %s\n' "${planner_script#"$script_dir"/}"
    if ! "$planner_script"; then
        printf 'Planner failed: %s\n' "${planner_script#"$script_dir"/}" >&2
        overall_status=1
    fi
done < <(find "$script_dir" -mindepth 3 -maxdepth 3 -type f -name run.sh -print | sort)

exit "$overall_status"
