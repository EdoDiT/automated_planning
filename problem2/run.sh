#!/bin/bash

start=$(date +%s.%N)

planutils run ff "-o interplanetary_museum_domain_2.pddl -f problem_2.pddl" | grep '^[0-9]' > solution.plan

if [[ -f sas_plan ]]; then
    cp sas_plan solution.plan
else
    echo "Planner did not produce sas_plan" >&2
    exit 1
fi

end=$(date +%s.%N)

echo "Execution time: $(echo "$end - $start" | bc) seconds"