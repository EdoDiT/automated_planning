#!/usr/bin/env python3
"""
Parse and aggregate statistics from all PDDL/HDDL problem/domain files,
planner execution logs, and output plans across problem1..problem5.

Outputs:
  - data_aggregation/output/aggregated_stats.json
  - data_aggregation/output/runs_flat.csv
"""

from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


# ============================================================================
# 1. PDDL / HDDL S-Expression & Problem/Domain Parser
# ============================================================================

def strip_comments(text: str) -> str:
    return re.sub(r";.*$", "", text, flags=re.MULTILINE)


def tokenize_sexp(text: str) -> List[str]:
    return re.findall(r"\(|\)|[^\s()]+", text)


def parse_sexp(tokens: List[str]) -> Any:
    if not tokens:
        return []
    stack: List[List[Any]] = [[]]
    for token in tokens:
        if token == "(":
            new_list: List[Any] = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif token == ")":
            if len(stack) > 1:
                stack.pop()
        else:
            stack[-1].append(token)
    return stack[0][0] if stack[0] else []


def find_section(tree: List[Any], keyword: str) -> Optional[List[Any]]:
    keyword_lower = keyword.lower()
    for item in tree:
        if isinstance(item, list) and item and isinstance(item[0], str):
            if item[0].lower() == keyword_lower:
                return item
    return None


def parse_typed_list(tokens: List[Any]) -> List[Tuple[str, str]]:
    """Parse PDDL typed list `a b - type1 c - type2` into [(name, type), ...]."""
    flat = [str(t) for t in tokens if isinstance(t, str)]
    result: List[Tuple[str, str]] = []
    current: List[str] = []
    i = 0
    while i < len(flat):
        if flat[i] == "-" and i + 1 < len(flat):
            obj_type = flat[i + 1].lower()
            for obj in current:
                result.append((obj, obj_type))
            current = []
            i += 2
        else:
            current.append(flat[i])
            i += 1
    for obj in current:
        result.append((obj, "object"))
    return result


def parse_commented_objects(raw_text: str) -> Dict[str, List[str]]:
    """Extract commented-out object declarations inside (:objects ...) for reference."""
    m = re.search(r"\(:objects(.*?)\)", raw_text, re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    block = m.group(1)
    commented_lines: List[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith(";"):
            uncommented = stripped.lstrip(";").strip()
            if "-" in uncommented:
                commented_lines.append(uncommented)
    pairs = parse_typed_list(tokenize_sexp("\n".join(commented_lines)))
    by_type: Dict[str, List[str]] = {}
    for name, typ in pairs:
        by_type.setdefault(typ, []).append(name)
    return by_type


def extract_goal_atoms(expr: Any) -> List[List[str]]:
    """Recursively collect atomic goal predicates like ['at', 'artifact_1', 'cryo_chamber']."""
    if not isinstance(expr, list) or not expr:
        return []
    head = str(expr[0]).lower() if isinstance(expr[0], str) else ""
    if head in ("and", "or", "imply"):
        out: List[List[str]] = []
        for sub in expr[1:]:
            out.extend(extract_goal_atoms(sub))
        return out
    if head == "not":
        return []
    if all(isinstance(x, str) for x in expr):
        return [[str(x) for x in expr]]
    out = []
    for sub in expr:
        out.extend(extract_goal_atoms(sub))
    return out


def parse_problem_and_domain(
    problem_path: Path,
    domain_path: Path,
    problem_id: str,
    variant: str,
    level: str,
) -> Dict[str, Any]:
    raw_problem = problem_path.read_text(errors="replace")
    raw_domain = domain_path.read_text(errors="replace")

    clean_problem = strip_comments(raw_problem)
    clean_domain = strip_comments(raw_domain)

    prob_tree = parse_sexp(tokenize_sexp(clean_problem))
    dom_tree = parse_sexp(tokenize_sexp(clean_domain))

    # Parse domain types & constants
    types_sec = find_section(dom_tree, ":types")
    type_parents: Dict[str, str] = {}
    if types_sec:
        for child, parent in parse_typed_list(types_sec[1:]):
            type_parents[child.lower()] = parent.lower()

    def is_subtype_of(t: str, target: str) -> bool:
        curr = t.lower()
        target = target.lower()
        seen = set()
        while curr and curr not in seen:
            if curr == target:
                return True
            seen.add(curr)
            curr = type_parents.get(curr, "")
        return False

    constants_sec = find_section(dom_tree, ":constants")
    domain_constants = parse_typed_list(constants_sec[1:]) if constants_sec else []

    objects_sec = find_section(prob_tree, ":objects")
    problem_objects = parse_typed_list(objects_sec[1:]) if objects_sec else []

    commented_objs = parse_commented_objects(raw_problem)

    # Categorize problem objects
    artifacts: List[str] = []
    pods: List[str] = []
    robots_by_type: Dict[str, List[str]] = {
        "standard_curator": [],
        "tank_curator": [],
        "drone_curator": [],
    }
    all_robots: List[str] = []
    rooms_in_problem: List[str] = []
    other_locations_in_problem: List[str] = []

    for name, typ in problem_objects:
        if is_subtype_of(typ, "artifact") or typ == "artifact":
            artifacts.append(name)
        elif is_subtype_of(typ, "pod") or typ == "pod":
            pods.append(name)
        elif is_subtype_of(typ, "robot") or typ in ("standard_curator", "tank_curator", "drone_curator", "sealing_curators"):
            all_robots.append(name)
            if typ in robots_by_type:
                robots_by_type[typ].append(name)
            else:
                robots_by_type.setdefault(typ, []).append(name)
        elif is_subtype_of(typ, "room") or typ == "room":
            rooms_in_problem.append(name)
        elif is_subtype_of(typ, "location") or typ == "location":
            other_locations_in_problem.append(name)

    rooms_in_constants: List[str] = []
    other_locations_in_constants: List[str] = []
    for name, typ in domain_constants:
        if is_subtype_of(typ, "room") or typ == "room":
            rooms_in_constants.append(name)
        elif is_subtype_of(typ, "location") or typ == "location":
            other_locations_in_constants.append(name)

    # Parse :init
    init_sec = find_section(prob_tree, ":init")
    init_items = init_sec[1:] if init_sec else []

    init_predicates: List[List[str]] = []
    init_functions: List[Any] = []
    connected_locations = set()
    initial_locations: Dict[str, str] = {}

    sturdy_artifacts = set()
    sensitive_artifacts = set()
    thermo_artifacts = set()
    seismic_artifacts = set()
    thermo_and_seismic_artifacts = set()

    for expr in init_items:
        if not isinstance(expr, list) or not expr:
            continue
        head = str(expr[0]).lower()
        if head == "=":
            init_functions.append(expr)
        elif head == "not" and len(expr) > 1 and isinstance(expr[1], list):
            inner = expr[1]
            if inner and str(inner[0]).lower() == "is_sensitive" and len(inner) > 1:
                sturdy_artifacts.add(str(inner[1]))
            init_predicates.append(["not"] + [str(x) for x in inner])
        else:
            flat_pred = [str(x) for x in expr if isinstance(x, str)]
            init_predicates.append(flat_pred)
            if head == "at" and len(flat_pred) >= 3:
                initial_locations[flat_pred[1]] = flat_pred[2]
            elif head in ("connected", "are_connected"):
                for loc in flat_pred[1:]:
                    connected_locations.add(loc)
            elif head == "is_sturdy" and len(flat_pred) >= 2:
                sturdy_artifacts.add(flat_pred[1])
            elif head == "is_sensitive" and len(flat_pred) >= 2:
                sensitive_artifacts.add(flat_pred[1])
            elif head == "is_thermosensitive" and len(flat_pred) >= 2:
                thermo_artifacts.add(flat_pred[1])
            elif head == "is_seismic_sensitive" and len(flat_pred) >= 2:
                seismic_artifacts.add(flat_pred[1])
            elif head == "is_thermo_and_seismic_sensitive" and len(flat_pred) >= 2:
                thermo_and_seismic_artifacts.add(flat_pred[1])

    # Normalize artifact sensitivity categories for active artifacts
    active_set = set(artifacts)
    both_sens = set()
    thermo_only = set()
    seismic_only = set()
    sturdy_only = set()

    for art in artifacts:
        is_both = (art in thermo_and_seismic_artifacts) or (art in thermo_artifacts and art in seismic_artifacts)
        if is_both:
            both_sens.add(art)
        elif art in thermo_artifacts:
            thermo_only.add(art)
        elif art in seismic_artifacts:
            seismic_only.add(art)
        elif art in sensitive_artifacts and art not in sturdy_artifacts:
            # In problem5, dual-sensitive artifacts are marked with (is_sensitive X)
            both_sens.add(art)
        elif art in sturdy_artifacts or art not in sensitive_artifacts:
            sturdy_only.add(art)

    # Active rooms: union of rooms_in_problem and rooms_in_constants that are active/connected
    all_rooms = list(dict.fromkeys(rooms_in_problem + [
        r for r in rooms_in_constants if r in connected_locations or not connected_locations
    ]))
    all_other_locations = list(dict.fromkeys(other_locations_in_problem + other_locations_in_constants))

    # Parse :goal
    goal_sec = find_section(prob_tree, ":goal")
    goal_atoms = extract_goal_atoms(goal_sec[1]) if (goal_sec and len(goal_sec) > 1) else []
    goal_artifact_targets: Dict[str, str] = {}
    for atom in goal_atoms:
        if len(atom) >= 3 and atom[0].lower() == "at" and atom[1] in active_set:
            goal_artifact_targets[atom[1]] = atom[2]

    artifacts_requiring_movement = [
        art for art, dest in goal_artifact_targets.items()
        if initial_locations.get(art) != dest
    ]

    earth_artifacts = [a for a in artifacts if not a.startswith("martian_")]
    martian_artifacts = [a for a in artifacts if a.startswith("martian_")]

    commented_artifacts_count = len(commented_objs.get("artifact", []))
    commented_robots_count = sum(
        len(commented_objs.get(k, []))
        for k in ("standard_curator", "tank_curator", "drone_curator", "robot")
    )
    commented_pods_count = len(commented_objs.get("pod", []))
    commented_rooms_count = len(commented_objs.get("room", []))

    return {
        "problem_id": problem_id,
        "variant": variant,
        "level": level,
        "problem_file": str(problem_path.relative_to(PROJECT_ROOT)),
        "domain_file": str(domain_path.relative_to(PROJECT_ROOT)),
        "is_htn": problem_path.suffix.lower() == ".hddl",
        "active_artifacts": {
            "total": len(artifacts),
            "earth_artifacts": len(earth_artifacts),
            "martian_artifacts": len(martian_artifacts),
            "sturdy": len(sturdy_only),
            "sensitive_total": len(thermo_only) + len(seismic_only) + len(both_sens),
            "thermosensitive_only": len(thermo_only),
            "seismic_sensitive_only": len(seismic_only),
            "thermo_and_seismic_sensitive": len(both_sens),
            "in_goal": len(goal_artifact_targets),
            "requiring_movement": len(artifacts_requiring_movement),
            "names": artifacts,
        },
        "active_robots": {
            "total": len(all_robots),
            "standard_curator": len(robots_by_type.get("standard_curator", [])),
            "tank_curator": len(robots_by_type.get("tank_curator", [])),
            "drone_curator": len(robots_by_type.get("drone_curator", [])),
            "names": all_robots,
            "by_type": robots_by_type,
        },
        "active_pods": {
            "total": len(pods),
            "names": pods,
        },
        "active_rooms": {
            "rooms_in_problem_objects": len(rooms_in_problem),
            "rooms_in_domain_constants": len(rooms_in_constants),
            "total_active_rooms": len(all_rooms),
            "other_locations": len(all_other_locations),
            "total_locations": len(all_rooms) + len(all_other_locations),
            "room_names": all_rooms,
            "other_location_names": all_other_locations,
        },
        "commented_out_objects": {
            "artifacts": commented_artifacts_count,
            "robots": commented_robots_count,
            "pods": commented_pods_count,
            "rooms": commented_rooms_count,
        },
        "init_stats": {
            "predicates_count": len(init_predicates),
            "functions_count": len(init_functions),
            "total_init_facts": len(init_predicates) + len(init_functions),
            "goal_conditions_count": len(goal_atoms),
        },
    }


# ============================================================================
# 2. Plan Action Analyzer
# ============================================================================

def analyze_plan_actions(action_strings: List[str]) -> Dict[str, Any]:
    """Categorize a list of primitive action strings like 'move curator tunnel hall_alpha'."""
    categories = {
        "move_or_fly": 0,
        "pickup_artifact": 0,
        "drop_artifact": 0,
        "pod_operations": 0,
        "seal_unseal": 0,
        "earthquake": 0,
        "wait_or_charge": 0,
        "activate_robot": 0,
        "other": 0,
    }
    by_robot: Dict[str, int] = {}
    known_robots = {"curator", "curator_2", "curator_3", "biggie", "bee"}

    for raw in action_strings:
        cleaned = raw.strip().strip("()[]")
        if not cleaned:
            continue
        tokens = re.split(r"[\s,\[\]]+", cleaned)
        if not tokens:
            continue
        act = tokens[0].lower()
        if act in ("move", "move_in_room", "move_out_room", "fly"):
            categories["move_or_fly"] += 1
        elif act.startswith("pickup_"):
            categories["pickup_artifact"] += 1
        elif act.startswith("drop_") and "pod" not in act or act.startswith("safe_drop_"):
            categories["drop_artifact"] += 1
        elif act in ("take_pod", "drop_pod"):
            categories["pod_operations"] += 1
        elif act in ("seal", "unseal"):
            categories["seal_unseal"] += 1
        elif act in ("start_earthquake", "stop_earthquake"):
            categories["earthquake"] += 1
        elif act in ("wait", "charge_battery"):
            categories["wait_or_charge"] += 1
        elif act == "activate_robot":
            categories["activate_robot"] += 1
        else:
            categories["other"] += 1

        for tok in tokens[1:]:
            t_low = tok.lower()
            if t_low in known_robots:
                by_robot[t_low] = by_robot.get(t_low, 0) + 1
                break

    return {
        "total_actions": len(action_strings),
        "by_category": categories,
        "by_robot": by_robot,
    }


# ============================================================================
# 3. Planner Log & Plan Parsers
# ============================================================================

def parse_enhsp_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    solved = "Problem Solved" in text

    exit_m = re.search(r"Exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else None

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    plan_len_m = re.search(r"Plan-Length:\s*(\d+)", text)
    metric_m = re.search(r"Metric \(Search\):\s*([0-9.eE+-]+)", text)
    plan_time_m = re.search(r"Planning Time \(msec\):\s*(\d+)", text)
    heur_time_m = re.search(r"Heuristic Time \(msec\):\s*(\d+)", text)
    search_time_m = re.search(r"Search Time \(msec\):\s*(\d+)", text)
    ground_time_m = re.search(r"Grounding Time:\s*(\d+)", text)

    exp_m = re.search(r"^Expanded Nodes:\s*(\d+)", text, re.MULTILINE)
    eval_m = re.search(r"^States Evaluated:\s*(\d+)", text, re.MULTILINE)
    dead_m = re.search(r"Number of Dead-Ends detected:\s*(\d+)", text)
    dup_m = re.search(r"Number of Duplicates detected:\s*(\d+)", text)

    # Grounded size
    f_m = re.search(r"\|F\|:\s*(\d+)", text)
    x_m = re.search(r"\|X\|:\s*(\d+)", text)
    a_m = re.search(r"\|A\|:\s*(\d+)", text)

    # Fallback expanded/evaluated states from progress lines if OOM/timeout
    expanded_nodes = int(exp_m.group(1)) if exp_m else None
    evaluated_states = int(eval_m.group(1)) if eval_m else None
    if expanded_nodes is None:
        all_exp = re.findall(r"Expanded Nodes:\s*(\d+)", text)
        if all_exp:
            expanded_nodes = int(all_exp[-1])
    if evaluated_states is None:
        all_eval = re.findall(r"Evaluated States:\s*(\d+)", text)
        if all_eval:
            evaluated_states = int(all_eval[-1])

    # Extract plan actions
    plan_actions: List[str] = []
    if plan_path and plan_path.exists() and plan_path.stat().st_size > 0:
        for line in plan_path.read_text(errors="replace").splitlines():
            m = re.match(r"^\s*[0-9.]+:\s*\((.+?)\)\s*$", line)
            if m:
                plan_actions.append(m.group(1))
    if not plan_actions and solved:
        for line in text.splitlines():
            m = re.match(r"^\s*[0-9.]+:\s*\((.+?)\)\s*$", line)
            if m:
                plan_actions.append(m.group(1))

    plan_length = int(plan_len_m.group(1)) if plan_len_m else (len(plan_actions) if solved else None)

    if solved:
        status = "solved"
    elif "OutOfMemoryError" in text:
        status = "out_of_memory"
    elif exit_status == 124 or (exec_time and exec_time >= 580):
        status = "timeout"
    elif "Problem Unsolvable" in text:
        status = "unsolvable"
    else:
        status = "error"

    planning_time_sec = int(plan_time_m.group(1)) / 1000.0 if plan_time_m else None
    search_time_sec = int(search_time_m.group(1)) / 1000.0 if search_time_m else None

    return {
        "solution_found": solved,
        "status": status,
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "planning_time_sec": planning_time_sec,
        "search_time_sec": search_time_sec,
        "heuristic_time_sec": int(heur_time_m.group(1)) / 1000.0 if heur_time_m else None,
        "grounding_time_sec": int(ground_time_m.group(1)) / 1000.0 if ground_time_m else None,
        "time_spent_sec": planning_time_sec if planning_time_sec is not None else exec_time,
        "expanded_states": expanded_nodes,
        "evaluated_states": evaluated_states,
        "generated_states": None,
        "dead_ends": int(dead_m.group(1)) if dead_m else None,
        "duplicates": int(dup_m.group(1)) if dup_m else None,
        "plan_length": plan_length,
        "plan_cost": float(metric_m.group(1)) if metric_m else (float(plan_length) if plan_length is not None else None),
        "makespan": None,
        "grounded_facts": int(f_m.group(1)) if f_m else None,
        "grounded_numeric_vars": int(x_m.group(1)) if x_m else None,
        "grounded_actions": int(a_m.group(1)) if a_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_fast_downward_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    solved = "Solution found!" in text or "Solution found." in text

    exit_m = re.search(r"Exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else None

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    planner_time_m = re.search(r"INFO\s+Planner time:\s*([0-9.eE+-]+)s", text)
    total_time_m = re.search(r"Total time:\s*([0-9.eE+-]+)s", text)
    search_time_m = re.search(r"Search time:\s*([0-9.eE+-]+)s", text)

    exp_m = re.search(r"Expanded\s+(\d+)\s+state\(s\)\.", text)
    eval_m = re.search(r"Evaluated\s+(\d+)\s+state\(s\)\.", text)
    gen_m = re.search(r"Generated\s+(\d+)\s+state\(s\)\.", text)
    reopen_m = re.search(r"Reopened\s+(\d+)\s+state\(s\)\.", text)
    evals_m = re.search(r"Evaluations:\s*(\d+)", text)
    dead_m = re.search(r"Dead ends:\s*(\d+)\s+state\(s\)\.", text)
    mem_m = re.findall(r"Peak memory:\s*(\d+)\s*KB", text)

    plan_len_m = re.search(r"Plan length:\s*(\d+)\s+step\(s\)\.", text)
    plan_cost_m = re.search(r"Plan cost:\s*([0-9.eE+-]+)", text)

    trans_vars_m = re.search(r"Translator variables:\s*(\d+)", text)
    trans_facts_m = re.search(r"Translator facts:\s*(\d+)", text)
    trans_ops_m = re.search(r"Translator operators:\s*(\d+)", text)
    trans_size_m = re.search(r"Translator task size:\s*(\d+)", text)

    expanded_states = int(exp_m.group(1)) if exp_m else None
    evaluated_states = int(eval_m.group(1)) if eval_m else None
    if expanded_states is None:
        prog_exp = re.findall(r"(\d+)\s+evaluated,\s+(\d+)\s+expanded", text)
        if prog_exp:
            evaluated_states = int(prog_exp[-1][0])
            expanded_states = int(prog_exp[-1][1])

    search_time_sec = float(search_time_m.group(1)) if search_time_m else None
    if search_time_sec is None:
        t_stamps = re.findall(r"\[t=([0-9.]+)s,", text)
        if t_stamps:
            search_time_sec = float(t_stamps[-1])

    plan_actions: List[str] = []
    if plan_path and plan_path.exists() and plan_path.stat().st_size > 0:
        for line in plan_path.read_text(errors="replace").splitlines():
            line_s = line.strip()
            if not line_s or line_s.startswith(";"):
                continue
            plan_actions.append(line_s.strip("()"))

    plan_length = int(plan_len_m.group(1)) if plan_len_m else (len(plan_actions) if solved else None)

    if solved:
        status = "solved"
    elif "Invalid requirement. Got: :fluents" in text:
        status = "unsupported_fluents"
    elif exit_status == 124 or "caught signal 15" in text:
        status = "timeout"
    else:
        status = "error"

    total_time_sec = float(total_time_m.group(1)) if total_time_m else (
        float(planner_time_m.group(1)) if planner_time_m else exec_time
    )

    return {
        "solution_found": solved,
        "status": status,
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "planning_time_sec": float(planner_time_m.group(1)) if planner_time_m else total_time_sec,
        "search_time_sec": search_time_sec,
        "time_spent_sec": total_time_sec if solved else exec_time,
        "expanded_states": expanded_states,
        "evaluated_states": evaluated_states,
        "generated_states": int(gen_m.group(1)) if gen_m else None,
        "reopened_states": int(reopen_m.group(1)) if reopen_m else None,
        "evaluations": int(evals_m.group(1)) if evals_m else None,
        "dead_ends": int(dead_m.group(1)) if dead_m else None,
        "peak_memory_kb": int(mem_m[-1]) if mem_m else None,
        "plan_length": plan_length,
        "plan_cost": float(plan_cost_m.group(1)) if plan_cost_m else None,
        "makespan": None,
        "grounded_facts": int(trans_facts_m.group(1)) if trans_facts_m else None,
        "grounded_variables": int(trans_vars_m.group(1)) if trans_vars_m else None,
        "grounded_actions": int(trans_ops_m.group(1)) if trans_ops_m else None,
        "translator_task_size": int(trans_size_m.group(1)) if trans_size_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_panda_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    solved = "- Status: Solved" in text

    exit_m = re.search(r"Exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else (0 if solved else 1)

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    search_m = re.search(r"-\s*Search time\s+([0-9.eE+-]+)\s+seconds", text)
    search_time = float(search_m.group(1)) if search_m else None

    vis_time_m = re.search(r"-\s*Visited list time\s+([0-9.eE+-]+)\s+seconds", text)
    vis_ins_m = re.search(r"-\s*Visited list inserts\s+(\d+)", text)
    vis_cont_m = re.search(r"-\s*Visited list contains\s+(\d+)", text)
    gen_m = re.search(r"-\s*Generated\s+(\d+)\s+search nodes", text)
    heur_m = re.search(r"Calculated heuristic for\s+(\d+)\s+nodes", text)
    rate_m = re.search(r"-\s*Generated\s+(\d+)\s+nodes per second", text)
    fringe_m = re.search(r"-\s*Final fringe contains\s+(\d+)\s+nodes", text)

    sol_len_m = re.search(r"-\s*Found solution of length\s+(\d+)", text)
    act_cost_m = re.search(r"-\s*Total costs of actions:\s*(\d+)", text)

    bits_m = re.search(r"-\s*State has\s+(\d+)\s+bits", text)
    dom_act_m = re.search(r"-\s*Domain contains\s+(\d+)\s+actions\.", text)
    dom_tasks_m = re.search(r"-\s*Domain contains\s+(\d+)\s+tasks\.", text)
    dom_meth_m = re.search(r"-\s*Domain contains\s+(\d+)\s+methods\.", text)

    # Extract primitive actions from ==> ... root
    plan_actions: List[str] = []
    in_plan = False
    for line in text.splitlines():
        line_s = line.strip()
        if line_s == "==>":
            in_plan = True
            continue
        if in_plan:
            if line_s.startswith("root ") or line_s == "<==":
                break
            m = re.match(r"^\d+\s+(.+)$", line_s)
            if m:
                act_str = m.group(1).strip()
                if not act_str.startswith("__"):
                    # Convert name[a,b] -> name a b
                    act_clean = act_str.replace("[", " ").replace("]", "").replace(",", " ").strip()
                    plan_actions.append(act_clean)

    primitive_len = int(act_cost_m.group(1)) if act_cost_m else (len(plan_actions) if plan_actions else None)
    htn_len = int(sol_len_m.group(1)) if sol_len_m else None

    return {
        "solution_found": solved,
        "status": "solved" if solved else "error",
        "exit_status": exit_status,
        "execution_time_sec": exec_time if exec_time is not None else search_time,
        "planning_time_sec": search_time,
        "search_time_sec": search_time,
        "visited_list_time_sec": float(vis_time_m.group(1)) if vis_time_m else None,
        "time_spent_sec": exec_time if exec_time is not None else search_time,
        "expanded_states": int(vis_cont_m.group(1)) if vis_cont_m else None,
        "evaluated_states": int(heur_m.group(1)) if heur_m else None,
        "generated_states": int(gen_m.group(1)) if gen_m else None,
        "visited_list_inserts": int(vis_ins_m.group(1)) if vis_ins_m else None,
        "nodes_per_sec": int(rate_m.group(1)) if rate_m else None,
        "final_fringe_nodes": int(fringe_m.group(1)) if fringe_m else None,
        "plan_length": primitive_len,
        "htn_decomposition_length": htn_len,
        "plan_cost": float(primitive_len) if primitive_len is not None else None,
        "makespan": None,
        "grounded_facts": int(bits_m.group(1)) if bits_m else None,
        "grounded_actions": int(dom_act_m.group(1)) if dom_act_m else None,
        "grounded_tasks": int(dom_tasks_m.group(1)) if dom_tasks_m else None,
        "grounded_methods": int(dom_meth_m.group(1)) if dom_meth_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_lilotane_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    sol_layer_m = re.search(r"([0-9.]+)\s+Found a solution at layer\s+(\d+)\.", text)
    solved = sol_layer_m is not None

    exit_m = re.search(r"Exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else (0 if solved else 124)

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    end_sol_m = re.search(r"([0-9.]+)\s+End of solution plan\.\s*\(counted length of\s+(\d+)\)", text)
    term_m = re.search(r"([0-9.]+)\s+Termination signal caught\.", text)

    clauses_m = re.search(r"Total amount of clauses encoded:\s*(\d+)", text)
    pos_m = re.search(r"# instantiated positions:\s*(\d+)", text)
    act_m = re.search(r"# instantiated actions:\s*(\d+)", text)
    red_m = re.search(r"# instantiated reductions:\s*(\d+)", text)
    pconst_m = re.search(r"# introduced pseudo-constants:\s*(\d+)", text)

    # Parse per-layer progression
    layers: List[Dict[str, Any]] = []
    iter_matches = list(re.finditer(r"([0-9.]+)\s+Iteration\s+(\d+)\.", text))
    for idx, m in enumerate(iter_matches):
        start_pos = m.start()
        end_pos = iter_matches[idx + 1].start() if idx + 1 < len(iter_matches) else len(text)
        chunk = text[start_pos:end_pos]
        t_start = float(m.group(1))
        layer_num = int(m.group(2))
        sz_m = re.search(r"(?:New layer size|Creating initial layer of size):?\s*(\d+)", chunk)
        facts_m = re.search(r"Collected\s+(\d+)\s+relevant facts", chunk)
        f_m = re.search(
            r"([0-9.]+)\s+Attempting to solve formula with\s+(\d+)\s+clauses\s+\((\d+)\s+literals\)\s+and\s+(\d+)\s+assumptions",
            chunk,
        )
        end_t_m = re.search(r"([0-9.]+)\s+(?:Unsolvable at layer|Found a solution at layer|Termination signal caught)", chunk)
        t_end = float(end_t_m.group(1)) if end_t_m else None
        layers.append({
            "layer": layer_num,
            "start_time_sec": t_start,
            "end_time_sec": t_end,
            "duration_sec": round(t_end - t_start, 4) if t_end is not None else None,
            "layer_size": int(sz_m.group(1)) if sz_m else None,
            "relevant_facts": int(facts_m.group(1)) if facts_m else None,
            "clauses": int(f_m.group(2)) if f_m else None,
            "literals": int(f_m.group(3)) if f_m else None,
            "assumptions": int(f_m.group(4)) if f_m else None,
        })

    solver_time = float(end_sol_m.group(1)) if end_sol_m else (
        float(term_m.group(1)) if term_m else exec_time
    )
    if exec_time is None:
        exec_time = solver_time

    # Extract primitive actions
    plan_actions: List[str] = []
    in_plan = False
    for line in text.splitlines():
        line_s = line.strip()
        if line_s == "==>":
            in_plan = True
            continue
        if in_plan:
            if line_s.startswith("root ") or line_s == "<==":
                break
            m = re.match(r"^\d+\s+(.+)$", line_s)
            if m:
                plan_actions.append(m.group(1).strip())

    counted_len = int(end_sol_m.group(2)) if end_sol_m else (len(plan_actions) if solved else None)
    max_facts = max((l["relevant_facts"] for l in layers if l["relevant_facts"] is not None), default=None)

    return {
        "solution_found": solved,
        "status": "solved" if solved else ("timeout" if term_m or exit_status == 124 else "error"),
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "planning_time_sec": solver_time,
        "search_time_sec": float(sol_layer_m.group(1)) if sol_layer_m else solver_time,
        "time_spent_sec": exec_time,
        "expanded_states": int(pos_m.group(1)) if pos_m else None,  # instantiated positions in SAT-HTN
        "evaluated_states": int(act_m.group(1)) if act_m else None,  # instantiated actions in SAT-HTN
        "generated_states": int(clauses_m.group(1)) if clauses_m else None,  # total SAT clauses encoded
        "sat_clauses": int(clauses_m.group(1)) if clauses_m else None,
        "instantiated_positions": int(pos_m.group(1)) if pos_m else None,
        "instantiated_actions": int(act_m.group(1)) if act_m else None,
        "instantiated_reductions": int(red_m.group(1)) if red_m else None,
        "pseudo_constants": int(pconst_m.group(1)) if pconst_m else None,
        "max_layer_reached": layers[-1]["layer"] if layers else None,
        "solution_layer": int(sol_layer_m.group(2)) if sol_layer_m else None,
        "plan_length": counted_len,
        "plan_cost": float(counted_len) if counted_len is not None else None,
        "makespan": None,
        "grounded_facts": max_facts,
        "grounded_actions": int(act_m.group(1)) if act_m else None,
        "layers_progression": layers,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_tfd_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    solved = "New solution has been found." in text or "Plan length:" in text

    exit_m = re.search(r"Planner exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else None

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    search_m = re.search(r"Search time:\s*([0-9.eE+-]+)\s*seconds\s*-\s*Walltime:\s*([0-9.eE+-]+)\s*seconds", text)
    total_m = re.search(r"Total time:\s*([0-9.eE+-]+)\s*seconds\s*-\s*Walltime:\s*([0-9.eE+-]+)\s*seconds", text)

    plan_len_list = re.findall(r"Plan length:\s*(\d+)\s*step\(s\)\.", text)
    makespan_list = re.findall(r"^Makespan\s*:\s*([0-9.eE+-]+)", text, re.MULTILINE)
    resched_list = re.findall(r"Rescheduled Makespan\s*:\s*([0-9.eE+-]+)", text)

    vars_m = re.search(r"(\d+)\s+variables of\s+(\d+)\s+necessary", text)
    ops_m = re.search(r"(\d+)\s+of\s+(\d+)\s+operators necessary\.", text)

    # Expanded & generated nodes
    exp_list = re.findall(r"Expanded Nodes:\s*(\d+)\s+state\(s\)\.", text)
    gen_list = re.findall(r"Generated Nodes:\s*(\d+)\s+state\(s\)\.", text)
    heur_list = re.findall(r"Heuristic Computations \(per heuristic\):\s*(\d+)", text)

    expanded_states: Optional[int] = int(exp_list[-1]) if exp_list else None
    generated_states: Optional[int] = int(gen_list[-1]) if gen_list else None
    heuristic_evals: Optional[int] = int(heur_list[-1]) if heur_list else None

    if expanded_states is None:
        # Sum across resets when search finishes in < 10s
        phases = text.split("RESET!")
        total_exp = 0
        for phase in phases:
            now_at = re.findall(r"now at\s+(\d+)", phase)
            exp_in_phase = re.findall(r"\[expanded\s+(\d+)\s+state\(s\)\]", phase)
            if now_at:
                total_exp += int(now_at[-1])
            elif exp_in_phase:
                total_exp += int(exp_in_phase[-1])
        if total_exp > 0:
            expanded_states = total_exp

    plan_actions: List[str] = []
    if plan_path and plan_path.exists() and plan_path.stat().st_size > 0:
        last_ts = -1.0
        for line in plan_path.read_text(errors="replace").splitlines():
            m = re.match(r"^\s*([0-9.]+):\s*\((.+?)\)\s*\[[0-9.]+\]", line)
            if m:
                ts = float(m.group(1))
                if last_ts > 5.0 and ts < 1.0:
                    # Anytime planner concatenated a new plan starting at t~0
                    plan_actions = []
                last_ts = ts
                plan_actions.append(m.group(2))

    if solved:
        status = "solved"
    elif "Completely explored state space -- no solution!" in text:
        status = "unsolvable_exhausted"
    elif exit_status == 124:
        status = "timeout"
    else:
        status = "error"

    search_time_sec = float(search_m.group(1)) if search_m else None
    wall_time_sec = float(total_m.group(2)) if total_m else exec_time
    if search_time_sec is None:
        s_times = re.findall(r"Search Time:\s*(\d+)\s*sec\.", text)
        if s_times:
            search_time_sec = float(s_times[-1])

    makespan = float(resched_list[-1]) if resched_list else (float(makespan_list[-1]) if makespan_list else None)

    return {
        "solution_found": solved,
        "status": status,
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "planning_time_sec": wall_time_sec,
        "search_time_sec": search_time_sec,
        "time_spent_sec": wall_time_sec if solved else exec_time,
        "expanded_states": expanded_states,
        "evaluated_states": heuristic_evals if heuristic_evals is not None else expanded_states,
        "generated_states": generated_states,
        "plan_length": int(plan_len_list[-1]) if plan_len_list else (len(plan_actions) if solved else None),
        "plan_cost": makespan,
        "makespan": makespan,
        "grounded_variables": int(vars_m.group(1)) if vars_m else None,
        "grounded_actions": int(ops_m.group(1)) if ops_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_lpg_td_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")
    solved = "Solution found:" in text or "Plan computed:" in text

    exit_m = re.search(r"Planner exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else None

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None
    if exec_time is not None and exec_time < 0:
        exec_time = abs(exec_time)

    tot_m = re.search(r"Total time:\s*([0-9.eE+-]+)", text)
    srch_m = re.search(r"Search time:\s*([0-9.eE+-]+)", text)
    act_m = re.search(r"Actions:\s*(\d+)", text)
    cost_m = re.search(r"Execution cost:\s*([0-9.eE+-]+)", text)
    dur_m = re.search(r"Duration:\s*([0-9.eE+-]+)", text)

    plan_actions: List[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*[0-9.]+:\s*\((.+?)\)\s*\[D:", line)
        if m:
            plan_actions.append(m.group(1))

    if solved:
        status = "solved"
    elif "ERROR in file H_relaxed.c" in text:
        status = "relaxed_plan_error"
    elif exit_status == 124:
        status = "timeout"
    else:
        status = "error"

    total_time = float(tot_m.group(1)) if tot_m else exec_time

    return {
        "solution_found": solved,
        "status": status,
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "planning_time_sec": total_time,
        "search_time_sec": float(srch_m.group(1)) if srch_m else None,
        "time_spent_sec": total_time if solved else exec_time,
        "expanded_states": None,
        "evaluated_states": None,
        "generated_states": None,
        "plan_length": int(act_m.group(1)) if act_m else (len(plan_actions) if solved else None),
        "plan_cost": float(cost_m.group(1)) if cost_m else None,
        "makespan": float(dur_m.group(1)) if dur_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_optic_run(log_path: Path, plan_path: Optional[Path]) -> Dict[str, Any]:
    text = log_path.read_text(errors="replace")

    exit_m = re.search(r"Planner exit status:\s*(-?\d+)", text)
    exit_status = int(exit_m.group(1)) if exit_m else None

    exec_m = re.search(r"Execution time:\s*([0-9.eE+-]+)\s*seconds", text)
    exec_time = float(exec_m.group(1)) if exec_m else None

    lit_m = re.search(r"Number of literals:\s*(\d+)", text)

    # First plan found block (; Plan found with metric X)
    first_metric_m = re.search(r";\s*Plan found with metric\s+([0-9.eE+-]+)", text)
    first_states_m = re.search(r";\s*States evaluated so far:\s*(\d+)", text)
    first_time_m = re.search(r";\s*Time\s+([0-9.eE+-]+)", text)

    # Final solution block (;;;; Solution Found)
    anytime_completed = ";;;; Solution Found" in text
    final_states_m = re.search(r";\s*States evaluated:\s*(\d+)", text)
    final_cost_m = re.search(r";\s*Cost:\s*([0-9.eE+-]+)", text)
    all_times = re.findall(r";\s*Time\s+([0-9.eE+-]+)", text)

    solved = (first_metric_m is not None) or anytime_completed

    # Extract the last complete plan in the log
    plan_blocks: List[List[str]] = []
    current_block: List[str] = []
    for line in text.splitlines():
        m = re.match(r"^\s*([0-9.]+):\s*\((.+?)\)\s*\[([0-9.]+)\]", line)
        if m:
            current_block.append(m.group(2))
        else:
            if current_block:
                plan_blocks.append(current_block)
                current_block = []
    if current_block:
        plan_blocks.append(current_block)

    plan_actions = plan_blocks[-1] if plan_blocks else []
    plan_length = len(plan_actions) if plan_actions else None

    first_time = float(first_time_m.group(1)) if first_time_m else None
    final_time = float(all_times[-1]) if all_times else first_time
    first_states = int(first_states_m.group(1)) if first_states_m else None
    final_states = int(final_states_m.group(1)) if final_states_m else first_states
    makespan = float(final_cost_m.group(1)) if final_cost_m else (
        float(first_metric_m.group(1)) if first_metric_m else None
    )

    if anytime_completed:
        status = "solved"
    elif solved and exit_status == 124:
        status = "solved_anytime_timeout"
    elif solved:
        status = "solved"
    elif exit_status == 124:
        status = "timeout"
    else:
        status = "error"

    return {
        "solution_found": solved,
        "anytime_completed": anytime_completed,
        "status": status,
        "exit_status": exit_status,
        "execution_time_sec": exec_time,
        "first_plan_time_sec": first_time,
        "planning_time_sec": final_time if anytime_completed else first_time,
        "search_time_sec": first_time,
        "time_spent_sec": first_time if (solved and not anytime_completed) else (final_time or exec_time),
        "expanded_states": first_states,
        "evaluated_states": final_states,
        "first_plan_evaluated_states": first_states,
        "generated_states": None,
        "plan_length": plan_length,
        "plan_cost": makespan,
        "makespan": makespan,
        "grounded_facts": int(lit_m.group(1)) if lit_m else None,
        "action_analysis": analyze_plan_actions(plan_actions) if plan_actions else None,
    }


def parse_plansys2_run(plan_output_path: Path) -> Dict[str, Any]:
    text = plan_output_path.read_text(errors="replace")
    plan_actions: List[str] = []
    max_end_time = 0.0
    for line in text.splitlines():
        m = re.match(r"^\s*([0-9.]+):\s*\((.+?)\)\s*\[([0-9.]+)\]", line)
        if m:
            start_t = float(m.group(1))
            act = m.group(2)
            dur = float(m.group(3))
            plan_actions.append(act)
            if start_t + dur > max_end_time:
                max_end_time = round(start_t + dur, 3)

    solved = len(plan_actions) > 0
    return {
        "solution_found": solved,
        "status": "solved" if solved else "error",
        "exit_status": 0 if solved else 1,
        "execution_time_sec": None,
        "planning_time_sec": None,
        "search_time_sec": None,
        "time_spent_sec": None,
        "expanded_states": None,
        "evaluated_states": None,
        "generated_states": None,
        "plan_length": len(plan_actions),
        "plan_cost": max_end_time,
        "makespan": max_end_time,
        "action_analysis": analyze_plan_actions(plan_actions),
    }


# ============================================================================
# 4. Full Workspace Discovery & Aggregation
# ============================================================================

def collect_all_data() -> Dict[str, Any]:
    problems_list: List[Dict[str, Any]] = []
    problem_lookup: Dict[Tuple[str, str, str], Dict[str, Any]] = {}

    def register_problem(prob_path: Path, dom_path: Path, pid: str, variant: str, level: str) -> None:
        info = parse_problem_and_domain(prob_path, dom_path, pid, variant, level)
        problems_list.append(info)
        problem_lookup[(pid, variant, level)] = info

    # Problem 1
    p1_dom = PROJECT_ROOT / "problem1" / "interplanetary_museum_domain_1.pddl"
    register_problem(PROJECT_ROOT / "problem1" / "problem.pddl", p1_dom, "problem1", "default", "default")
    for lvl in ("easy", "middle", "hard"):
        register_problem(PROJECT_ROOT / "problem1" / "scalability" / f"{lvl}.pddl", p1_dom, "problem1", "default", lvl)

    # Problem 2
    for variant in ("no_negative_preconditions", "negative_preconditions"):
        p2_dom = PROJECT_ROOT / "problem2" / variant / "interplanetary_museum_domain_2.pddl"
        register_problem(PROJECT_ROOT / "problem2" / variant / "problem_2.pddl", p2_dom, "problem2", variant, "default")
        for lvl in ("easy", "middle", "hard"):
            register_problem(
                PROJECT_ROOT / "problem2" / variant / "scalability" / f"{lvl}.pddl",
                p2_dom,
                "problem2",
                variant,
                lvl,
            )
        # Hard versions
        hv_dir = PROJECT_ROOT / "problem2" / "hard_versions" / variant
        if (hv_dir / "problem_2.pddl").exists():
            register_problem(
                hv_dir / "problem_2.pddl",
                hv_dir / "interplanetary_museum_domain_2.pddl",
                "problem2",
                f"hard_versions/{variant}",
                "default",
            )

    # Problem 3
    p3_dom = PROJECT_ROOT / "problem3" / "interplanetary_museum_domain_3.hddl"
    register_problem(PROJECT_ROOT / "problem3" / "problem_3.hddl", p3_dom, "problem3", "default", "default")
    for lvl in ("easy", "middle", "hard"):
        register_problem(PROJECT_ROOT / "problem3" / "scalability" / f"{lvl}.hddl", p3_dom, "problem3", "default", lvl)
    if (PROJECT_ROOT / "problem3" / "fluent_version" / "problem_3.hddl").exists():
        register_problem(
            PROJECT_ROOT / "problem3" / "fluent_version" / "problem_3.hddl",
            PROJECT_ROOT / "problem3" / "fluent_version" / "interplanetary_museum_domain_3.hddl",
            "problem3",
            "fluent_version",
            "default",
        )

    # Problem 4
    p4_dom = PROJECT_ROOT / "problem4" / "interplanetary_museum_domain_4.pddl"
    register_problem(PROJECT_ROOT / "problem4" / "problem_4.pddl", p4_dom, "problem4", "default", "default")
    for lvl in ("easy", "middle", "hard"):
        register_problem(PROJECT_ROOT / "problem4" / "scalability" / f"{lvl}.pddl", p4_dom, "problem4", "default", lvl)

    # Problem 5
    p5_dom = PROJECT_ROOT / "problem5" / "plansys2_interplanetary_museum" / "pddl" / "domain.pddl"
    register_problem(
        PROJECT_ROOT / "problem5" / "plansys2_interplanetary_museum" / "pddl" / "problem.pddl",
        p5_dom,
        "problem5",
        "default",
        "default",
    )
    for lvl in ("easy", "middle", "hard"):
        p5_scal = PROJECT_ROOT / "problem5" / "plansys2_interplanetary_museum" / "pddl" / "scalability" / f"{lvl}.pddl"
        if p5_scal.exists():
            register_problem(
                p5_scal,
                p5_dom,
                "problem5",
                "default",
                lvl,
            )

    # Now collect all runs!
    runs_list: List[Dict[str, Any]] = []

    def add_run(
        problem_id: str,
        variant: str,
        level: str,
        planner_family: str,
        planner_config: str,
        log_path: Path,
        plan_path: Optional[Path],
        parsed: Dict[str, Any],
    ) -> None:
        prob_info = problem_lookup.get((problem_id, variant, level), {})
        run_record = {
            "problem_id": problem_id,
            "variant": variant,
            "level": level,
            "planner_family": planner_family,
            "planner_config": planner_config,
            "planner_label": f"{planner_family} ({planner_config})" if planner_config != planner_family else planner_family,
            "log_file": str(log_path.relative_to(PROJECT_ROOT)),
            "plan_file": str(plan_path.relative_to(PROJECT_ROOT)) if (plan_path and plan_path.exists() and plan_path.stat().st_size > 0) else None,
            "problem_stats": {
                "active_artifacts": prob_info.get("active_artifacts", {}).get("total"),
                "goal_artifacts": prob_info.get("active_artifacts", {}).get("in_goal"),
                "active_robots": prob_info.get("active_robots", {}).get("total"),
                "active_pods": prob_info.get("active_pods", {}).get("total"),
                "active_rooms": prob_info.get("active_rooms", {}).get("total_active_rooms"),
            },
            **parsed,
        }
        runs_list.append(run_record)

    # Problem 1 runs
    for family, configs in [
        ("ENHSP", ["opt-blind", "opt-hmax", "sat-aibr"]),
        ("Fast Downward", ["astar-blind", "seq-opt-lmcut", "lama-first"]),
    ]:
        fam_dir = "enhsp" if family == "ENHSP" else "fast-downward"
        parser_fn = parse_enhsp_run if family == "ENHSP" else parse_fast_downward_run
        for cfg in configs:
            base_dir = PROJECT_ROOT / "problem1" / fam_dir / cfg
            for lvl, sub in [("easy", "scalability/easy"), ("middle", "scalability/middle"), ("default", ""), ("hard", "scalability/hard")]:
                run_dir = base_dir / sub if sub else base_dir
                log_f = run_dir / "execution.log"
                plan_f = run_dir / "solution.plan"
                if log_f.exists():
                    add_run("problem1", "default", lvl, family, cfg, log_f, plan_f, parser_fn(log_f, plan_f))

    # Problem 2 runs
    for variant in ("no_negative_preconditions", "negative_preconditions"):
        for family, configs in [
            ("ENHSP", ["opt-blind", "opt-hmax", "sat-aibr", "sat-hadd"]),
            ("Fast Downward", ["astar-blind", "seq-opt-lmcut", "lama-first"]),
        ]:
            fam_dir = "enhsp" if family == "ENHSP" else "fast-downward"
            parser_fn = parse_enhsp_run if family == "ENHSP" else parse_fast_downward_run
            for cfg in configs:
                base_dir = PROJECT_ROOT / "problem2" / variant / fam_dir / cfg
                for lvl, sub in [("easy", "scalability/easy"), ("middle", "scalability/middle"), ("default", ""), ("hard", "scalability/hard")]:
                    run_dir = base_dir / sub if sub else base_dir
                    log_f = run_dir / "execution.log"
                    plan_f = run_dir / "solution.plan"
                    if log_f.exists():
                        add_run("problem2", variant, lvl, family, cfg, log_f, plan_f, parser_fn(log_f, plan_f))

    # Problem 3 runs (PANDA & Lilotane)
    for lvl, sub in [("easy", "panda/scalability/easy"), ("middle", "panda/scalability/middle"), ("hard", "panda/scalability/hard"), ("default", "")]:
        run_dir = PROJECT_ROOT / "problem3" / sub if sub else PROJECT_ROOT / "problem3"
        log_f = run_dir / "panda.log"
        plan_f = run_dir / "solution.plan"
        if log_f.exists():
            add_run("problem3", "default", lvl, "PANDA", "progression-rc2-ff", log_f, plan_f, parse_panda_run(log_f, plan_f))

    for lvl, sub in [("easy", "scalability/easy"), ("middle", "scalability/middle"), ("hard", "scalability/hard"), ("default", "")]:
        run_dir = PROJECT_ROOT / "problem3" / "lilotane" / sub if sub else PROJECT_ROOT / "problem3" / "lilotane"
        log_f = run_dir / "lilotane.log"
        plan_f = run_dir / "solution.plan"
        if log_f.exists():
            add_run("problem3", "default", lvl, "Lilotane", "sat-glucose4", log_f, plan_f, parse_lilotane_run(log_f, plan_f))

    # Problem 4 runs (LPG-TD, OPTIC)
    for planner_family, folder, log_name, parser_fn in [
        ("LPG-TD", "lpg-td", "lpg-td.log", parse_lpg_td_run),
        ("OPTIC", "optic", "optic.log", parse_optic_run),
    ]:
        base_dir = PROJECT_ROOT / "problem4" / folder
        for lvl, sub in [("default", ""), ("easy", "scalability/easy"), ("middle", "scalability/middle"), ("hard", "scalability/hard")]:
            run_dir = base_dir / sub if sub else base_dir
            log_f = run_dir / log_name
            plan_f = run_dir / "solution.plan"
            if log_f.exists():
                add_run("problem4", "default", lvl, planner_family, planner_family.lower(), log_f, plan_f, parser_fn(log_f, plan_f))

    # Problem 5 run (PlanSys2 / Kairos)
    p5_plan = PROJECT_ROOT / "problem5" / "plan_output.txt"
    if p5_plan.exists():
        add_run(
            "problem5",
            "default",
            "default",
            "PlanSys2 (Kairos)",
            "kairos",
            p5_plan,
            p5_plan,
            parse_plansys2_run(p5_plan),
        )

    # Compute high-level summary per problem
    summary_by_problem: Dict[str, Any] = {}
    for pid in ("problem1", "problem2", "problem3", "problem4", "problem5"):
        p_runs = [r for r in runs_list if r["problem_id"] == pid]
        solved_runs = [r for r in p_runs if r["solution_found"]]
        times = [r["time_spent_sec"] for r in solved_runs if r["time_spent_sec"] is not None]
        lengths = [r["plan_length"] for r in solved_runs if r["plan_length"] is not None]
        summary_by_problem[pid] = {
            "total_runs": len(p_runs),
            "solved_runs": len(solved_runs),
            "coverage_ratio": round(len(solved_runs) / len(p_runs), 4) if p_runs else 0.0,
            "min_time_sec": min(times) if times else None,
            "max_time_sec": max(times) if times else None,
            "min_plan_length": min(lengths) if lengths else None,
            "max_plan_length": max(lengths) if lengths else None,
        }

    return {
        "metadata": {
            "project": "Automated Planning - Interplanetary Museum",
            "total_problem_files_parsed": len(problems_list),
            "total_planner_runs_parsed": len(runs_list),
        },
        "summary_by_problem": summary_by_problem,
        "problems": problems_list,
        "runs": runs_list,
    }


def write_outputs(data: Dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / "aggregated_stats.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    csv_path = OUTPUT_DIR / "runs_flat.csv"
    fieldnames = [
        "problem_id",
        "variant",
        "level",
        "planner_family",
        "planner_config",
        "active_artifacts",
        "goal_artifacts",
        "active_robots",
        "active_pods",
        "active_rooms",
        "solution_found",
        "status",
        "time_spent_sec",
        "execution_time_sec",
        "search_time_sec",
        "expanded_states",
        "evaluated_states",
        "generated_states",
        "plan_length",
        "plan_cost",
        "makespan",
        "log_file",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in data["runs"]:
            pstats = r.get("problem_stats", {})
            writer.writerow({
                "problem_id": r.get("problem_id"),
                "variant": r.get("variant"),
                "level": r.get("level"),
                "planner_family": r.get("planner_family"),
                "planner_config": r.get("planner_config"),
                "active_artifacts": pstats.get("active_artifacts"),
                "goal_artifacts": pstats.get("goal_artifacts"),
                "active_robots": pstats.get("active_robots"),
                "active_pods": pstats.get("active_pods"),
                "active_rooms": pstats.get("active_rooms"),
                "solution_found": r.get("solution_found"),
                "status": r.get("status"),
                "time_spent_sec": r.get("time_spent_sec"),
                "execution_time_sec": r.get("execution_time_sec"),
                "search_time_sec": r.get("search_time_sec"),
                "expanded_states": r.get("expanded_states"),
                "evaluated_states": r.get("evaluated_states"),
                "generated_states": r.get("generated_states"),
                "plan_length": r.get("plan_length"),
                "plan_cost": r.get("plan_cost"),
                "makespan": r.get("makespan"),
                "log_file": r.get("log_file"),
            })

    print(f"[OK] Wrote JSON stats to: {json_path}")
    print(f"[OK] Wrote flat CSV to:   {csv_path}")


if __name__ == "__main__":
    aggregated = collect_all_data()
    write_outputs(aggregated)
