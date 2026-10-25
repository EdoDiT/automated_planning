#!/bin/bash

start=$(date +%s.%N)

rm -f sas_plan solution.plan

enhsp \
    -o interplanetary_museum_domain_1.pddl \
    -f problem.pddl \
    -planner opt-blind \
    -sp sas_plan

if [[ -f sas_plan ]]; then
    cp sas_plan solution.plan
else
    echo "Planner did not produce sas_plan" >&2
    exit 1
fi

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"