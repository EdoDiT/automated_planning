#!/bin/bash

start=$(date +%s.%N)

enhsp -o interplanetary_museum_domain_2.pddl -f problem_2.pddl -planner sat-hadd | grep '^[0-9]' > solution.plan

end=$(date +%s.%N)

echo "Execution time: $(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }') seconds"