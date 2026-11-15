#!/usr/bin/env bash

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
domain="$PROJECT_DIR/interplanetary_museum_domain_3.hddl"
scalability_dir="$SCRIPT_DIR/scalability"
overall_status=0

for level in easy middle hard; do
    level_dir="$scalability_dir/$level"
    mkdir -p "$level_dir"
    problem="$PROJECT_DIR/scalability/${level}.hddl"
    log_file="$level_dir/lilotane.log"
    plan_file="$level_dir/solution.plan"

    rm -f "$plan_file"
    start=$(date +%s.%N)

    set -o pipefail
    (
        cd "$level_dir" || exit 1
        timeout 600s \
            lilotane "$domain" "$problem" -v=2 -co=0
    ) 2>&1 | tee "$log_file"
    planner_status=${PIPESTATUS[0]}
    set +o pipefail

    if [[ "$planner_status" -eq 124 ]]; then
        echo "Lilotane timed out after 600 seconds on $level; see $log_file." >&2
    elif [[ "$planner_status" -ne 0 ]]; then
        echo "Lilotane failed on $level; see $log_file." >&2
    else
        awk '/==>/{flag=1; next} /<==/{flag=0} flag' "$log_file" \
        | grep -E '^[0-9]+ (activate_robot|move|fly|seal|unseal|take_pod|drop_pod|pickup_[^ ]+|drop_[^ ]+|safe_drop_[^ ]+) ' \
        > "$plan_file" || true

        if [[ ! -s "$plan_file" ]]; then
            echo "Lilotane finished without producing a museum action plan; see $log_file." >&2
            planner_status=1
        fi
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
