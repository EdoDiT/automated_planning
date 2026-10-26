#!/bin/bash

start=$(date +%s.%N)

planutils run tfd "interplanetary_museum_domain_4.pddl problem_4.pddl" \
| tee >(awk '
    /Found new plan:/ {capture=1; next}
    /Solution with original makespan/ {capture=0}
    capture && /^[0-9]+\.[0-9]+:/ {print}
' > solution.plan)
    
end=$(date +%s.%N)

echo "Execution time: $(awk -v start="$start" -v end="$end" 'BEGIN { print end - start }') seconds"
