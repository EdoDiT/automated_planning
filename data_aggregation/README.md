# Automated Planning Final Project — Data Aggregation, LaTeX Tables & Plots

This folder contains the complete Python pipeline to parse all PDDL/HDDL domain and problem files, planner logs, and output plans across `problem1`–`problem5`, normalize the results into structured JSON and CSV files, export publication-ready LaTeX (`booktabs`) tables, and generate vector PDF and high-DPI PNG figures.

## Quick Start

A Python virtual environment (`.venv`) with `matplotlib` and `numpy` is already set up in this directory, and all outputs have been generated in `output/`.

To re-run the entire pipeline at any time:

```bash
./run_all.sh
```

Or run individual scripts using `.venv/bin/python3`:

```bash
.venv/bin/python3 parse_and_aggregate.py
.venv/bin/python3 generate_latex_tables.py
.venv/bin/python3 generate_plots.py
```

---

## Directory Structure

- `parse_and_aggregate.py`: Parses all 27 PDDL/HDDL problem/domain pairs and all 101 planner runs across `problem1`–`problem5`:
  - Extracts active (uncommented) vs. commented-out objects (`artifacts` by sensitivity category, `robots` by curator subtype, `pods`, and `rooms` combining `:objects` and domain `:constants`).
  - Extracts planner performance metrics (`solution_found`, `status`, `search_time_sec`, `planning_time_sec`, `execution_time_sec`, `expanded_states`, `evaluated_states`, `generated_states` / SAT clauses, `plan_length`, `makespan`, and action category + per-robot workload breakdowns).
- `generate_latex_tables.py`: Reads `output/aggregated_stats.json` and writes standalone and combined LaTeX tables using `booktabs` and `\resizebox{\textwidth}{!}{...}`.
- `generate_plots.py`: Reads `output/aggregated_stats.json` and generates 6 multi-panel figures in both `.pdf` (vector, for LaTeX `\includegraphics`) and `.png` formats.
- `output/`
  - `aggregated_stats.json`: Complete normalized dataset (problem instance metadata, per-run metrics, and summary statistics).
  - `runs_flat.csv`: Flattened table of all 101 runs for spreadsheet/pandas inspection.
  - `tables/`
    - `table_problem_instances.tex`: Active artifacts (by sensitivity), robots (Standard/Tank/Drone), pods, rooms, initial state size, and goal size across all problem files.
    - `table_problem1_results.tex`: Problem 1 classical planning scalability across ENHSP (`opt-blind`, `opt-hmax`, `sat-aibr`) and Fast Downward (`astar-blind`, `seq-opt-lmcut`, `lama-first`).
    - `table_problem2_results.tex`: Problem 2 numeric planning comparison of `no_negative_preconditions` vs. `negative_preconditions` in ENHSP (`opt-blind`, `opt-hmax`, `sat-aibr`, `sat-hadd`).
    - `table_problem3_results.tex`: Problem 3 HTN comparison of PANDA (`progression-rc2-ff`) vs. Lilotane (`sat-glucose4`).
    - `table_problem4_5_results.tex`: Problem 4 temporal planning (`TFD`, `LPG-TD`, `OPTIC`) and Problem 5 ROS 2 PlanSys2 (`Kairos`) results.
    - `table_action_breakdown.tex`: Action category breakdown (Move/Fly, Pickup, Drop, Pod Ops, Seal/Unseal, Earthquake) and robot workload distribution across solved plans.
    - `all_tables.tex`: Single file combining all 6 LaTeX tables.
  - `plots/`
    - `plot_problem1_scalability.png`
    - `plot_problem2_neg_vs_noneg.png`
    - `plot_problem3_htn_comparison.png`
