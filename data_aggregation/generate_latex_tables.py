#!/usr/bin/env python3
"""
Generate LaTeX (booktabs) tables from aggregated_stats.json.

Outputs in data_aggregation/output/tables/:
  - table_problem_instances.tex
  - table_problem1_results.tex
  - table_problem2_results.tex
  - table_problem3_results.tex
  - table_problem4_5_results.tex
  - table_action_breakdown.tex
  - all_tables.tex
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "output" / "aggregated_stats.json"
TABLES_DIR = BASE_DIR / "output" / "tables"


def fmt_int(val: Optional[int]) -> str:
    if val is None:
        return "---"
    return f"{int(val):,}"


def fmt_float(val: Optional[float], decimals: int = 2) -> str:
    if val is None:
        return "---"
    if abs(val) < 0.01 and val != 0:
        return f"{val:.4f}"
    return f"{val:.{decimals}f}"


def fmt_status(status: str, solved: bool) -> str:
    mapping = {
        "solved": r"\textbf{Yes}",
        "solved_anytime_timeout": r"\textbf{Yes}$^{\dagger}$",
        "timeout": "No (TO)",
        "out_of_memory": "No (OOM)",
        "unsolvable_exhausted": "No (Exh.)",
        "relaxed_plan_error": "No (Err.)",
        "unsupported_fluents": "No (Unsupp.)",
        "error": "No (Err.)",
    }
    return mapping.get(status, r"\textbf{Yes}" if solved else "No")


def tex_escape(s: str) -> str:
    return s.replace("_", r"\_")


def generate_problem_instances_table(data: Dict[str, Any]) -> str:
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Problem Instances and Active Domain Entities across Problems 1--5. "
        r"Artifacts are broken down into Sturdy (St.), Thermosensitive (Th.), Seismic-sensitive (Se.), "
        r"and Thermo+Seismic-sensitive (Both). Robots are broken down into Standard/Tank/Drone curators (S/T/D). "
        r"Rooms include active rooms in \texttt{:objects} plus \texttt{hall\_beta} when declared in domain \texttt{:constants}.}",
        r"\label{tab:problem_instances}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lll rrrrrr rr rr rr}",
        r"\toprule",
        r" & & & \multicolumn{6}{c}{\textbf{Active Artifacts}} & \multicolumn{2}{c}{\textbf{Active Robots}} & \multicolumn{2}{c}{\textbf{Pods \& Rooms}} & \multicolumn{2}{c}{\textbf{Init / Goal}} \\",
        r"\cmidrule(lr){4-9} \cmidrule(lr){10-11} \cmidrule(lr){12-13} \cmidrule(lr){14-15}",
        r"\textbf{Problem} & \textbf{Variant} & \textbf{Level} & \textbf{Tot.} & \textbf{St.} & \textbf{Th.} & \textbf{Se.} & \textbf{Both} & \textbf{Move} & \textbf{Tot.} & \textbf{(S/T/D)} & \textbf{Pods} & \textbf{Rooms (Loc.)} & \textbf{Init} & \textbf{Goal} \\",
        r"\midrule",
    ]

    # Deduplicate identical problem definitions or show all distinct problem sets
    seen_Order = []
    for p in data["problems"]:
        pid = p["problem_id"]
        var = p["variant"]
        lvl = p["level"]
        # Skip duplicate negative_preconditions problem rows if identical to no_negative_preconditions, or show concisely
        seen_Order.append((pid, var, lvl, p))

    last_pid = None
    for pid, var, lvl, p in seen_Order:
        if last_pid is not None and pid != last_pid:
            lines.append(r"\midrule")
        last_pid = pid

        art = p["active_artifacts"]
        rob = p["active_robots"]
        pods = p["active_pods"]["total"]
        rms = p["active_rooms"]
        ini = p["init_stats"]

        var_short = {
            "default": "Default",
            "no_negative_preconditions": "No Neg. Prec.",
            "negative_preconditions": "Neg. Prec.",
            "hard_versions/no_negative_preconditions": "Hard Ver. (No Neg.)",
            "hard_versions/negative_preconditions": "Hard Ver. (Neg.)",
            "fluent_version": "Fluent HTN",
        }.get(var, tex_escape(var))

        std_c = rob["standard_curator"]
        tnk_c = rob["tank_curator"]
        drn_c = rob["drone_curator"]

        lines.append(
            f"{tex_escape(pid)} & {var_short} & {tex_escape(lvl)} & "
            f"{art['total']} & {art['sturdy']} & {art['thermosensitive_only']} & "
            f"{art['seismic_sensitive_only']} & {art['thermo_and_seismic_sensitive']} & {art['requiring_movement']} & "
            f"{rob['total']} & ({std_c}/{tnk_c}/{drn_c}) & "
            f"{pods} & {rms['total_active_rooms']} ({rms['total_locations']}) & "
            f"{ini['total_init_facts']} & {ini['goal_conditions_count']} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def generate_problem1_table(data: Dict[str, Any]) -> str:
    runs = [r for r in data["runs"] if r["problem_id"] == "problem1"]
    level_order = {"easy": 0, "middle": 1, "default": 2, "hard": 3}
    runs.sort(key=lambda r: (r["planner_family"], r["planner_config"], level_order.get(r["level"], 99)))

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Problem 1 (Classical Planning) Results across ENHSP and Fast Downward Configurations. "
        r"Instances: \texttt{easy} (3 artifacts, 1 robot), \texttt{middle} (5 artifacts, 2 robots), "
        r"\texttt{default} (10 artifacts, 1 robot), \texttt{hard} (10 artifacts, 3 robots). "
        r"For OOM/TO runs, expanded and evaluated states reflect the last logged search frontier before termination.}",
        r"\label{tab:problem1_results}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lll rrr c rrr rr}",
        r"\toprule",
        r"\textbf{Planner} & \textbf{Configuration} & \textbf{Level} & \textbf{Art.} & \textbf{Rob.} & \textbf{Actions ($|A|$)} & \textbf{Solved} & \textbf{Search Time (s)} & \textbf{Total Time (s)} & \textbf{Expanded States} & \textbf{Evaluated States} & \textbf{Plan Len.} \\",
        r"\midrule",
    ]

    last_cfg = None
    for r in runs:
        cfg_key = (r["planner_family"], r["planner_config"])
        if last_cfg is not None and cfg_key != last_cfg:
            lines.append(r"\midrule")
        last_cfg = cfg_key

        ps = r["problem_stats"]
        lines.append(
            f"{tex_escape(r['planner_family'])} & \\texttt{{{tex_escape(r['planner_config'])}}} & {tex_escape(r['level'])} & "
            f"{ps['active_artifacts']} & {ps['active_robots']} & {fmt_int(r.get('grounded_actions'))} & "
            f"{fmt_status(r['status'], r['solution_found'])} & "
            f"{fmt_float(r.get('search_time_sec'), 3)} & {fmt_float(r.get('execution_time_sec'), 2)} & "
            f"{fmt_int(r.get('expanded_states'))} & {fmt_int(r.get('evaluated_states'))} & "
            f"{fmt_int(r.get('plan_length'))} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def generate_problem2_table(data: Dict[str, Any]) -> str:
    runs = [r for r in data["runs"] if r["problem_id"] == "problem2" and r["planner_family"] == "ENHSP"]
    by_key = {(r["variant"], r["planner_config"], r["level"]): r for r in runs}

    configs = ["opt-blind", "opt-hmax", "sat-aibr", "sat-hadd"]
    levels = ["easy", "middle", "default", "hard"]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Problem 2 (Numeric Planning with Fluents \& Earthquakes) Results using ENHSP: "
        r"Comparison between \texttt{no\_negative\_preconditions} and \texttt{negative\_preconditions}. "
        r"(Note: Fast Downward configurations \texttt{astar-blind}, \texttt{seq-opt-lmcut}, and \texttt{lama-first} "
        r"abort during translation on all Problem 2 instances with exit code 31 because PDDL \texttt{:fluents} are unsupported.)}",
        r"\label{tab:problem2_results}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{ll rr crrr crrr}",
        r"\toprule",
        r" & & & & \multicolumn{4}{c}{\textbf{No Negative Preconditions}} & \multicolumn{4}{c}{\textbf{With Negative Preconditions}} \\",
        r"\cmidrule(lr){5-8} \cmidrule(lr){9-12}",
        r"\textbf{Config.} & \textbf{Level} & \textbf{Art.} & \textbf{Rob.} & "
        r"\textbf{Solved} & \textbf{Time (s)} & \textbf{Expanded} & \textbf{Len.} & "
        r"\textbf{Solved} & \textbf{Time (s)} & \textbf{Expanded} & \textbf{Len.} \\",
        r"\midrule",
    ]

    for idx, cfg in enumerate(configs):
        if idx > 0:
            lines.append(r"\midrule")
        for lvl in levels:
            r_no = by_key.get(("no_negative_preconditions", cfg, lvl), {})
            r_neg = by_key.get(("negative_preconditions", cfg, lvl), {})
            ps = r_no.get("problem_stats") or r_neg.get("problem_stats") or {}

            lines.append(
                f"\\texttt{{{tex_escape(cfg)}}} & {tex_escape(lvl)} & "
                f"{ps.get('active_artifacts', '---')} & {ps.get('active_robots', '---')} & "
                f"{fmt_status(r_no.get('status', ''), r_no.get('solution_found', False))} & "
                f"{fmt_float(r_no.get('time_spent_sec'), 2)} & {fmt_int(r_no.get('expanded_states'))} & {fmt_int(r_no.get('plan_length'))} & "
                f"{fmt_status(r_neg.get('status', ''), r_neg.get('solution_found', False))} & "
                f"{fmt_float(r_neg.get('time_spent_sec'), 2)} & {fmt_int(r_neg.get('expanded_states'))} & {fmt_int(r_neg.get('plan_length'))} \\\\"
            )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def generate_problem3_table(data: Dict[str, Any]) -> str:
    runs = [r for r in data["runs"] if r["problem_id"] == "problem3"]
    level_order = {"easy": 0, "middle": 1, "hard": 2, "default": 3}
    runs.sort(key=lambda r: (0 if r["planner_family"] == "PANDA" else 1, level_order.get(r["level"], 99)))

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Problem 3 (Hierarchical Task Network / HTN Planning) Results comparing PANDA (Progression Search with \texttt{hhRC2(ff)}) "
        r"and Lilotane (Tree-Rex SAT-based HTN Planner with Glucose4). "
        r"For PANDA, Expanded/Evaluated/Generated refer to unique visited states, heuristic evaluations, and generated search nodes; "
        r"HTN Steps is total decomposition length while Plan Len.\ is primitive action count. "
        r"For Lilotane, Expanded/Evaluated/Generated refer to instantiated positions, instantiated actions, and encoded SAT clauses.}",
        r"\label{tab:problem3_results}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lll rr c rr rrr rr}",
        r"\toprule",
        r"\textbf{Planner} & \textbf{Method} & \textbf{Level} & \textbf{Art.} & \textbf{Rob.} & \textbf{Solved} & "
        r"\textbf{Search Time (s)} & \textbf{Total Time (s)} & \textbf{Visited / Pos.} & \textbf{Eval. / Inst. Act.} & \textbf{Gen. Nodes / Clauses} & \textbf{HTN / Layer} & \textbf{Primitive Len.} \\",
        r"\midrule",
    ]

    last_fam = None
    for r in runs:
        if last_fam is not None and r["planner_family"] != last_fam:
            lines.append(r"\midrule")
        last_fam = r["planner_family"]
        ps = r["problem_stats"]

        if r["planner_family"] == "PANDA":
            htn_or_layer = fmt_int(r.get("htn_decomposition_length"))
        else:
            lyr = r.get("solution_layer") or r.get("max_layer_reached")
            htn_or_layer = f"Layer {lyr}" if lyr is not None else "---"

        lines.append(
            f"{tex_escape(r['planner_family'])} & \\texttt{{{tex_escape(r['planner_config'])}}} & {tex_escape(r['level'])} & "
            f"{ps['active_artifacts']} & {ps['active_robots']} & "
            f"{fmt_status(r['status'], r['solution_found'])} & "
            f"{fmt_float(r.get('search_time_sec'), 3)} & {fmt_float(r.get('execution_time_sec'), 2)} & "
            f"{fmt_int(r.get('expanded_states'))} & {fmt_int(r.get('evaluated_states'))} & "
            f"{fmt_int(r.get('generated_states'))} & {htn_or_layer} & {fmt_int(r.get('plan_length'))} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def generate_problem4_5_table(data: Dict[str, Any]) -> str:
    runs = [r for r in data["runs"] if r["problem_id"] in ("problem4", "problem5")]
    level_order = {"default": 0, "easy": 1, "middle": 2, "hard": 3}
    fam_order = {"TFD": 0, "LPG-TD": 1, "OPTIC": 2, "PlanSys2 (Kairos)": 3}
    runs.sort(key=lambda r: (r["problem_id"], fam_order.get(r["planner_family"], 99), level_order.get(r["level"], 99)))

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Problem 4 (Temporal \& Numeric Planning with Durative Actions and Battery Management) and "
        r"Problem 5 (ROS 2 PlanSys2 Execution with Kairos) Results. "
        r"$^{\dagger}$On \texttt{easy} and \texttt{middle}, OPTIC finds a valid temporal plan in 0.31\,s and 31.75\,s respectively, "
        r"and then continues anytime WA* search until the 600\,s time limit.}",
        r"\label{tab:problem4_5_results}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{lll rrrr c rr rr rr}",
        r"\toprule",
        r"\textbf{Problem} & \textbf{Planner} & \textbf{Level} & \textbf{Art.} & \textbf{Rob.} & \textbf{Pods} & \textbf{Rooms} & "
        r"\textbf{Solved} & \textbf{Sol. Time (s)} & \textbf{Exec. Time (s)} & \textbf{Expanded} & \textbf{Evaluated} & \textbf{Plan Len.} & \textbf{Makespan} \\",
        r"\midrule",
    ]

    last_group = None
    for r in runs:
        grp = (r["problem_id"], r["planner_family"])
        if last_group is not None and grp != last_group:
            lines.append(r"\midrule")
        last_group = grp
        ps = r["problem_stats"]

        lines.append(
            f"{tex_escape(r['problem_id'])} & {tex_escape(r['planner_family'])} & {tex_escape(r['level'])} & "
            f"{ps['active_artifacts']} & {ps['active_robots']} & {ps['active_pods']} & {ps['active_rooms']} & "
            f"{fmt_status(r['status'], r['solution_found'])} & "
            f"{fmt_float(r.get('time_spent_sec'), 2)} & {fmt_float(r.get('execution_time_sec'), 2)} & "
            f"{fmt_int(r.get('expanded_states'))} & {fmt_int(r.get('evaluated_states'))} & "
            f"{fmt_int(r.get('plan_length'))} & {fmt_float(r.get('makespan'), 2)} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def generate_action_breakdown_table(data: Dict[str, Any]) -> str:
    """Table showing primitive action category distribution and robot utilization on solved runs."""
    solved_runs = [r for r in data["runs"] if r.get("solution_found") and r.get("action_analysis")]

    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Action Category Breakdown and Robot Workload Distribution across Representative Solved Runs.}",
        r"\label{tab:action_breakdown}",
        r"\resizebox{\textwidth}{!}{%",
        r"\begin{tabular}{llll r rrrrrr rrr}",
        r"\toprule",
        r" & & & & & \multicolumn{6}{c}{\textbf{Action Categories}} & \multicolumn{3}{c}{\textbf{Actions per Robot}} \\",
        r"\cmidrule(lr){6-11} \cmidrule(lr){12-14}",
        r"\textbf{Problem} & \textbf{Variant/Level} & \textbf{Planner} & \textbf{Config.} & \textbf{Total} & "
        r"\textbf{Move/Fly} & \textbf{Pickup} & \textbf{Drop} & \textbf{Pod} & \textbf{Seal} & \textbf{Quake} & "
        r"\textbf{Curator(s)} & \textbf{Biggie} & \textbf{Bee} \\",
        r"\midrule",
    ]

    last_pid = None
    for r in solved_runs:
        pid = r["problem_id"]
        if last_pid is not None and pid != last_pid:
            lines.append(r"\midrule")
        last_pid = pid

        aa = r["action_analysis"]
        cat = aa["by_category"]
        rob = aa["by_robot"]

        var_lvl = r["level"] if r["variant"] == "default" else f"{r['variant'][:6]}./{r['level']}"
        cur_tot = rob.get("curator", 0) + rob.get("curator_2", 0) + rob.get("curator_3", 0)
        big_tot = rob.get("biggie", 0)
        bee_tot = rob.get("bee", 0)

        lines.append(
            f"{tex_escape(pid)} & {tex_escape(var_lvl)} & {tex_escape(r['planner_family'])} & "
            f"\\texttt{{{tex_escape(r['planner_config'])}}} & {aa['total_actions']} & "
            f"{cat['move_or_fly']} & {cat['pickup_artifact']} & {cat['drop_artifact']} & "
            f"{cat['pod_operations']} & {cat['seal_unseal']} & {cat['earthquake']} & "
            f"{cur_tot} & {big_tot} & {bee_tot} \\\\"
        )

    lines.extend([
        r"\bottomrule",
        r"\end{tabular}%",
        r"}",
        r"\end{table}",
    ])
    return "\n".join(lines)


def main() -> None:
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Run parse_and_aggregate.py first; missing {JSON_PATH}")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    tables = {
        "table_problem_instances.tex": generate_problem_instances_table(data),
        "table_problem1_results.tex": generate_problem1_table(data),
        "table_problem2_results.tex": generate_problem2_table(data),
        "table_problem3_results.tex": generate_problem3_table(data),
        "table_problem4_5_results.tex": generate_problem4_5_table(data),
        "table_action_breakdown.tex": generate_action_breakdown_table(data),
    }

    for fname, content in tables.items():
        out_p = TABLES_DIR / fname
        out_p.write_text(content + "\n", encoding="utf-8")
        print(f"[OK] Wrote LaTeX table: {out_p}")

    # Also write a combined all_tables.tex file
    combined = [
        "% Auto-generated LaTeX tables for Automated Planning Final Project",
        "% Requires \\usepackage{booktabs} and \\usepackage{graphicx}",
        "",
    ]
    for fname, content in tables.items():
        combined.append(f"% ==================== {fname} ====================")
        combined.append(content)
        combined.append("\n\\clearpage\n")

    all_p = TABLES_DIR / "all_tables.tex"
    all_p.write_text("\n".join(combined), encoding="utf-8")
    print(f"[OK] Wrote combined LaTeX tables: {all_p}")


if __name__ == "__main__":
    main()
