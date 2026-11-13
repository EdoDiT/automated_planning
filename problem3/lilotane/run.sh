#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
domain="$SCRIPT_DIR/../interplanetary_museum_domain_3.hddl"
problem="$SCRIPT_DIR/../problem_3.hddl"

start=$(date +%s.%N)

set -o pipefail
timeout --signal=TERM --kill-after=5s 300s \
    lilotane "$domain" "$problem" -v=2 -co=0 2>&1 \
    | tee "$SCRIPT_DIR/lilotane.log"
planner_status=${PIPESTATUS[0]}
set +o pipefail

if [[ "$planner_status" -eq 124 ]]; then
    echo "Lilotane timed out after 300 seconds; see $SCRIPT_DIR/lilotane.log." >&2
    exit "$planner_status"
fi

if [[ "$planner_status" -ne 0 ]]; then
    echo "Lilotane failed; see $SCRIPT_DIR/lilotane.log." >&2
    exit "$planner_status"
fi

awk '/==>/{flag=1; next} /<==/{flag=0} flag' "$SCRIPT_DIR/lilotane.log" \
| grep -E '^[0-9]+ (activate_robot|move|fly|seal|unseal|take_pod|drop_pod|pickup_[^ ]+|drop_[^ ]+|safe_drop_[^ ]+) ' \
> "$SCRIPT_DIR/solution.plan"

if [[ ! -s "$SCRIPT_DIR/solution.plan" ]]; then
    echo "Lilotane finished without producing a museum action plan; see $SCRIPT_DIR/lilotane.log." >&2
    exit 1
fi

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"
