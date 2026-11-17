# Automated Planning Final Project — Deliverable

This folder contains the self-contained deliverable for the **Interplanetary Museum Vault** automated planning project across all five tasks:

- **Problems 1–4**: One validated PDDL/HDDL domain and problem pair per task, together with a `run.sh` script specifying the chosen planner and all execution parameters.
- **Problem 5**: The complete ROS 2 / PlanSys2 package (`plansys2_interplanetary_museum`) with its dedicated Docker environment and launch scripts.
- **Docker Environment (Problems 1–4)**: `Dockerfile` and `start_docker.sh` at the root of `deliverable/` to build and run the `planutils` + `enhsp` + `lilotane` container.

## Directory Structure

```text
deliverable/
├── Dockerfile                          # Planutils-based Docker image for Problems 1–4
├── start_docker.sh                     # Helper script to build/start the Docker container
├── README.md                           # This file
├── problem1/
│   ├── interplanetary_museum_domain_1.pddl
│   ├── problem.pddl
│   └── run.sh                          # Runs Fast Downward (lama-first)
├── problem2/
│   ├── interplanetary_museum_domain_2.pddl
│   ├── problem_2.pddl
│   └── run.sh                          # Runs ENHSP (sat-hadd)
├── problem3/
│   ├── interplanetary_museum_domain_3.hddl
│   ├── problem_3.hddl
│   └── run.sh                          # Runs PANDA (progression-rc2-ff)
├── problem4/
│   ├── interplanetary_museum_domain_4.pddl
│   ├── problem_4.pddl
│   └── run.sh                          # Runs OPTIC
└── problem5/
    ├── Dockerfile                      # ROS 2 Humble + PlanSys2 + Kairos Docker image
    ├── start_docker.sh                 # Helper script for the PlanSys2 container
    ├── setup.sh                        # Parses PDDL and builds the ROS 2 workspace
    ├── terminal_1.sh                   # Launches PlanSys2 nodes and action executors
    ├── terminal_2.sh                   # Starts plansys2_terminal
    ├── README.md                       # Detailed instructions for Problem 5
    ├── plan_output.txt                 # Reference execution plan output
    └── plansys2_interplanetary_museum/ # ROS 2 package source (C++, PDDL, config, launch, utils)
```

---

## Chosen Planners, Parameters, and Rationale

### Problem 1 — Classical STRIPS Planning (`problem1/`)
- **Files**: `interplanetary_museum_domain_1.pddl`, `problem.pddl`
- **Chosen Planner**: **Fast Downward** (`downward` via `planutils`)
- **Options**:
  ```bash
  planutils run downward interplanetary_museum_domain_1.pddl problem.pddl \
      -- --search 'lazy_greedy([ff(),cea()],preferred=[ff(),cea()])'
  ```
- **Rationale**: Problem 1 uses only `:strips` and `:typing` (no negative preconditions or fluents) for broad planner compatibility. Fast Downward with the `lama-first` configuration (`lazy_greedy` with `ff()` and `cea()` heuristics and preferred operators) solved the baseline 10-artifact instance in **0.010 s** (154 expanded nodes), outperforming ENHSP (`sat-aibr`: 0.520 s) and optimal searches (`astar(lmcut())`: 54.006 s, `astar(blind())`: 9.361 s).

### Problem 2 — Numeric Planning (`problem2/`)
- **Files**: `interplanetary_museum_domain_2.pddl`, `problem_2.pddl` (from the `negative_preconditions` variant)
- **Chosen Planner**: **ENHSP** (`enhsp`)
- **Options**:
  ```bash
  enhsp -o interplanetary_museum_domain_2.pddl -f problem_2.pddl -planner sat-hadd -sp solution.plan
  ```
- **Rationale**: Problem 2 introduces `:fluents` (multi-item robot capacities and the cyclic `seismic_counter`), which Fast Downward does not support. Using native `:negative-preconditions` avoids redundant positive complement predicates and shrinks the state space. Among ENHSP configurations, `-planner sat-hadd` was the fastest (solving the baseline 5-artifact instance in **0.954 s** with 6,899 expanded nodes), compared to `sat-aibr` (131.530 s), `opt-hmax` (68.416 s), and `opt-blind` (61.038 s).

### Problem 3 — Hierarchical Task Network (HTN) Planning (`problem3/`)
- **Files**: `interplanetary_museum_domain_3.hddl`, `problem_3.hddl`
- **Chosen Planner**: **PANDA** (`panda` via `planutils`, default `progression-rc2-ff` search)
- **Options**:
  ```bash
  planutils run panda interplanetary_museum_domain_3.hddl problem_3.hddl
  ```
- **Rationale**: Problem 3 models the museum scenario in HDDL (`:hierarchy`). Progression search in PANDA solved the 13-artifact baseline instance in **0.620 s** (7,349 expanded nodes, plan length 144) and scaled reliably across difficulty levels, whereas SAT-based Lilotane timed out (283.855 s) due to growing SAT clause counts.

### Problem 4 — Temporal & Numeric Planning (`problem4/`)
- **Files**: `interplanetary_museum_domain_4.pddl`, `problem_4.pddl`
- **Chosen Planner**: **OPTIC** (`optic` via `planutils`)
- **Options**:
  ```bash
  planutils run optic "-N interplanetary_museum_domain_4.pddl problem_4.pddl"
  ```
  *(where `-N` disables anytime optimization so OPTIC stops immediately after finding the first valid plan)*
- **Rationale**: Problem 4 introduces `:durative-actions` alongside numeric fluents (battery consumption, capacities, and cyclic `seismic_counter` resets). Standard temporal planners such as POPF and TFD fail on cyclic numeric counter resets (TFD exhausts search at 50.370 s). OPTIC natively handles both durative actions and cyclic numeric fluents deterministically, solving the instance in **0.640 s** (34 expanded nodes, makespan **17.01**). *(Note: `lpg-td` is also installed in the Docker image and solves the instance in 0.040 s via stochastic local search.)*

### Problem 5 — ROS 2 Execution with PlanSys2 (`problem5/`)
- **Planner**: **Kairos** (PlanSys2's integrated temporal/numeric planner, configured via `plansys2_interplanetary_museum`)
- **Rationale**: Executes the temporal-numeric domain on a full 20-artifact, 3-robot (`curator`, `biggie`, `bee`) scenario using ROS 2 Humble lifecycle action nodes (`move_action_node`, `fly_action_node`, `seal_action_node`, etc.).

---

## How to Run Problems 1–4

1. From inside `deliverable/`, build and start the Docker container:
   ```bash
   ./start_docker.sh
   ```
   *(Pass `--rebuild` to force a clean rebuild, or `--clean` to remove the container and image.)*

2. Inside the container (`/project`), run any problem's script:
   ```bash
   ./problem1/run.sh
   ./problem2/run.sh
   ./problem3/run.sh
   ./problem4/run.sh
   ```
   Each script writes the resulting plan to `solution.plan` and the full planner output to `execution.log` (or `panda.log` / `optic.log`) inside its respective folder.

---

## How to Run Problem 5 (PlanSys2 / ROS 2)

Problem 5 uses its own ROS 2 Humble Docker image and requires two terminals connected to the same container.

1. Navigate to `deliverable/problem5/` and start the container in **Terminal 1**:
   ```bash
   cd problem5
   ./start_docker.sh
   ```
2. Inside the container (Terminal 1), build the workspace and launch PlanSys2:
   ```bash
   ./setup.sh
   ./terminal_1.sh
   ```
3. In **Terminal 2**, attach to the running container and start the PlanSys2 shell:
   ```bash
   sudo docker exec -it plansys2-humble-container bash
   ./terminal_2.sh
   ```
4. Inside `plansys2_terminal`, load the generated problem, plan, and execute:
   ```text
   source ./plansys2_interplanetary_museum/launch/problem 1
   get plan
   run
   ```

For full details on Problem 5, see `problem5/README.md`.
