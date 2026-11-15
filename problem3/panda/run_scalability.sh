#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
domain="$PROJECT_DIR/interplanetary_museum_domain_3.hddl"
scalability_dir="$SCRIPT_DIR/scalability"
overall_status=0

if ! command -v planutils >/dev/null 2>&1; then
    echo "planutils is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

planutils install -y panda

for level in easy middle hard; do
    level_dir="$scalability_dir/$level"
    mkdir -p "$level_dir"
    problem="$PROJECT_DIR/scalability/${level}.hddl"
    log_file="$level_dir/panda.log"
    plan_file="$level_dir/solution.plan"

    work_dir="$(mktemp -d "$SCRIPT_DIR/.panda-run.XXXXXX")" || exit 1
    rm -f "$plan_file"

    start=$(date +%s.%N)

    set -o pipefail
    (
        cd "$work_dir" || exit 1
        timeout 600s \
            planutils run panda "$domain" "$problem"
    ) 2>&1 | tee "$log_file"
    planner_status=${PIPESTATUS[0]}
    set +o pipefail

    rm -rf -- "$work_dir"

    if [[ "$planner_status" -eq 0 ]]; then
        grep -E '^[[:space:]]*[0-9]+ ' "$log_file" > "$plan_file" || true
        if [[ ! -s "$plan_file" ]]; then
            echo "PANDA did not produce a solution plan." >> "$log_file"
            planner_status=1
        fi
    else
        echo "PANDA failed on $level; see $log_file" >&2
    fi

    end=$(date +%s.%N)
    execution_time=$(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }')
    {
        printf '\nExecution time: %s seconds\n' "$execution_time"
        printf 'Exit status: %s\n' "$planner_status"
    } >> "$log_file"

    if [[ "$planner_status" -ne 0 ]]; then
        overall_status=1
    fi
done

exit "$overall_status"
