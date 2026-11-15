#!/bin/bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pddl_dir="$script_dir/plansys2_interplanetary_museum/pddl"
launch_scalability_dir="$script_dir/plansys2_interplanetary_museum/launch/scalability"

mkdir -p "$launch_scalability_dir"

python3 - "$pddl_dir" "$launch_scalability_dir" <<'PY'
import sys
from pathlib import Path

pddl_dir = Path(sys.argv[1])
out_dir = Path(sys.argv[2])
sys.path.insert(0, str(pddl_dir.parent / "utils"))

from pddl_parser import DomainHierarchy, PDDLProblemParser

domain = DomainHierarchy(str(pddl_dir / "domain.pddl"))
for level in ("easy", "middle", "hard"):
    problem_path = pddl_dir / "scalability" / f"{level}.pddl"
    output_path = out_dir / f"problem_{level}"
    parser = PDDLProblemParser(str(problem_path), domain)
    parser.convert_and_write_output(str(output_path))
    print(f"Written output to {output_path}")
PY
