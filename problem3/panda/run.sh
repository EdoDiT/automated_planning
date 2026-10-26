#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASK_DIR="$(dirname "$SCRIPT_DIR")"

case "${1:-handover}" in
    handover)
        domain="$TASK_DIR/interplanetary_museum_domain_3.hddl"
        ;;
    noho|no-handover)
        domain="$TASK_DIR/interplanetary_museum_domain_3.hddl"
        ;;
    *)
        echo "Usage: $0 [handover|noho]" >&2
        exit 2
        ;;
esac

problem="$TASK_DIR/problem_3.hddl"

# PANDA creates intermediate files in its current working directory. Run it in
# a temporary folder so that only the log and the final plan remain here.
work_dir="$(mktemp -d "$SCRIPT_DIR/.panda-run.XXXXXX")" || exit 1
cleanup() {
    rm -rf -- "$work_dir"
}
trap cleanup EXIT
cd "$work_dir" || exit 1

start=$(date +%s.%N)

if ! command -v planutils >/dev/null 2>&1; then
    echo "planutils is not installed. Run this script inside the project Docker image." >&2
    exit 1
fi

# The image may have been created before PANDA was added to the Dockerfile.
# Installing it here also makes the runner work in an already-running image.
planutils install -y panda

set -o pipefail
planutils run panda "$domain" "$problem" 2>&1 | tee "$SCRIPT_DIR/panda.log"
planner_status=${PIPESTATUS[0]}
set +o pipefail

if [[ "$planner_status" -ne 0 ]]; then
    echo "PANDA failed; see $SCRIPT_DIR/panda.log" >&2
    exit "$planner_status"
fi

grep -E '^[[:space:]]*[0-9]+ ' "$SCRIPT_DIR/panda.log" > "$SCRIPT_DIR/solution.plan"

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"
