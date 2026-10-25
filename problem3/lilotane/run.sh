#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_DIR="$(dirname "$SCRIPT_DIR")"
domain="$TASK_DIR/interplanetary_museum_domain_3.hddl"

problem="$TASK_DIR/problem_3.hddl"

start=$(date +%s.%N)

lilotane "$domain" "$problem" -v=2 -co=0 | tee "$SCRIPT_DIR/lilotane.log"

awk '/==>/{flag=1; next} /<==/{flag=0} flag' "$SCRIPT_DIR/lilotane.log" \
| grep -E '^[0-9]+ (visit|unvisit|mark-sensitive-done|mark-regular-done|move|move-through-narrow|take-empty-capsule|encapsulate-sample|pickup-sensitive-sample|drop-sensitive-sample|stabilize-capsule|store-sensitive-sample|pickup-regular-sample|drop-regular-sample|store-regular-sample|mark-sensitive-done|mark-regular-done) ' > "$SCRIPT_DIR/solution.plan"

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"
