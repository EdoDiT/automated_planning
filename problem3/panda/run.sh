#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_DIR="$(dirname "$SCRIPT_DIR")"

case "${1:-handover}" in
    handover)
        domain="$TASK_DIR/domain.hddl"
        ;;
    noho|no-handover)
        domain="$TASK_DIR/domain-noho.hddl"
        ;;
    *)
        echo "Usage: $0 [handover|noho]" >&2
        exit 2
        ;;
esac

problem="$TASK_DIR/problem.hddl"

# PANDA creates intermediate files in its current working directory. Run it in
# a temporary folder so that only the log and the final plan remain here.
work_dir="$(mktemp -d "$SCRIPT_DIR/.panda-run.XXXXXX")" || exit 1
cleanup() {
    rm -rf -- "$work_dir"
}
trap cleanup EXIT
cd "$work_dir" || exit 1

start=$(date +%s.%N)

planutils run panda "$domain" "$problem" | tee "$SCRIPT_DIR/panda.log"

grep -E '^[0-9]+ (visit|unvisit|mark-sensitive-done|mark-regular-done|move|move-through-narrow|take-empty-capsule|encapsulate-sample|pickup-sensitive-sample|drop-sensitive-sample|stabilize-capsule|store-sensitive-sample|pickup-regular-sample|drop-regular-sample|store-regular-sample) ' "$SCRIPT_DIR/panda.log" > "$SCRIPT_DIR/solution.plan"

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"
