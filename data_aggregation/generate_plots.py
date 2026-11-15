#!/usr/bin/env python3
"""
Generate publication-quality plots (both PDF for LaTeX and PNG for preview)
from `output/aggregated_stats.json`.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Ensure matplotlib cache dir is writable in restricted environments
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
STATS_PATH = BASE_DIR / "output" / "aggregated_stats.json"
PLOTS_DIR = BASE_DIR / "output" / "plots"

# Consistent styling for academic / LaTeX plots
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 8.5,
    "figure.titlesize": 13,
    "figure.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})


def save_fig(fig: plt.Figure, name: str) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = PLOTS_DIR / f"{name}.pdf"
    png_path = PLOTS_DIR / f"{name}.png"
    fig.savefig(pdf_path, bbox_inches="tight")
    fig.savefig(png_path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] Saved plot: {pdf_path} & {png_path}")


def find_run(
    runs: List[Dict[str, Any]],
    problem_id: str,
    planner_family: str,
    planner_config: str,
    level: str,
    variant: str = "default",
) -> Optional[Dict[str, Any]]:
    for r in runs:
        if (
            r["problem_id"] == problem_id
            and r["planner_family"] == planner_family
            and r["planner_config"] == planner_config
            and r["level"] == level
            and r["variant"] == variant
        ):
            return r
    return None


# ============================================================================
# Plot 1: Problem Instances Overview (Active Artifacts, Robots, Pods, Rooms)
# ============================================================================

def plot_problem_instances_overview(data: Dict[str, Any]) -> None:
    problems_by_key = {
        (p["problem_id"], p["variant"], p["level"]): p
        for p in data["problems"]
    }

    selected_keys = [
        (("problem1", "default", "easy"), "P1\neasy"),
        (("problem1", "default", "middle"), "P1\nmiddle"),
        (("problem1", "default", "default"), "P1\ndefault"),
        (("problem1", "default", "hard"), "P1\nhard"),
        (("problem2", "no_negative_preconditions", "easy"), "P2\neasy"),
        (("problem2", "no_negative_preconditions", "middle"), "P2\nmid/def"),
        (("problem2", "no_negative_preconditions", "hard"), "P2\nhard"),
        (("problem2", "hard_versions/no_negative_preconditions", "default"), "P2\nhard_v"),
        (("problem3", "default", "easy"), "P3\neasy"),
        (("problem3", "default", "middle"), "P3\nmiddle"),
        (("problem3", "default", "hard"), "P3\nhard"),
        (("problem3", "default", "default"), "P3\ndefault"),
        (("problem3", "fluent_version", "default"), "P3\nfluent"),
        (("problem4", "default", "default"), "P4\ndefault"),
        (("problem4", "default", "easy"), "P4\neasy"),
        (("problem4", "default", "middle"), "P4\nmiddle"),
        (("problem4", "default", "hard"), "P4\nhard"),
        (("problem5", "default", "easy"), "P5\neasy"),
        (("problem5", "default", "middle"), "P5\nmiddle"),
        (("problem5", "default", "hard"), "P5\nhard"),
        (("problem5", "default", "default"), "P5\ndefault"),
    ]

    labels = []
    sturdy = []
    thermo = []
    seismic = []
    both = []

    std_rob = []
    tank_rob = []
    drone_rob = []
    pods = []
    rooms = []

    for key, label in selected_keys:
        if key not in problems_by_key:
            continue
        p = problems_by_key[key]
        labels.append(label)
        a_bd = p["active_artifacts"]
        sturdy.append(a_bd["sturdy"])
        thermo.append(a_bd["thermosensitive_only"])
        seismic.append(a_bd["seismic_sensitive_only"])
        both.append(a_bd["thermo_and_seismic_sensitive"])

        r_bd = p["active_robots"]
        std_rob.append(r_bd["standard_curator"])
        tank_rob.append(r_bd["tank_curator"])
        drone_rob.append(r_bd["drone_curator"])
        pods.append(p["active_pods"]["total"])
        rooms.append(p["active_rooms"]["total_active_rooms"])

    x = np.arange(len(labels))
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.5, 7.5), sharex=True)

    # Panel A: Active Artifacts stacked by sensitivity
    w = 0.62
    b1 = np.array(sturdy)
    b2 = np.array(thermo)
    b3 = np.array(seismic)
    b4 = np.array(both)

    ax1.bar(x, b1, w, label="Sturdy", color="#4C78A8", edgecolor="white")
    ax1.bar(x, b2, w, bottom=b1, label="Thermosensitive", color="#F58518", edgecolor="white")
    ax1.bar(x, b3, w, bottom=b1 + b2, label="Seismic-sensitive", color="#E45756", edgecolor="white")
    ax1.bar(x, b4, w, bottom=b1 + b2 + b3, label="Thermo + Seismic", color="#72B7B2", edgecolor="white")

    totals = b1 + b2 + b3 + b4
    for i, tot in enumerate(totals):
        ax1.text(i, tot + 0.35, str(tot), ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax1.set_ylabel("Active Artifacts (Count)")
    ax1.set_ylim(0, max(totals) + 3)
    ax1.set_title("(a) Active Artifacts by Sensitivity Category across Problem Instances")
    ax1.legend(loc="upper left", ncol=4, frameon=True)

    # Vertical separators between problems
    sep_indices = [3.5, 7.5, 12.5, 16.5]
    for s_idx in sep_indices:
        ax1.axvline(s_idx, color="#555555", linestyle=":", linewidth=1.1)
        ax2.axvline(s_idx, color="#555555", linestyle=":", linewidth=1.1)

    # Panel B: Active Robots (stacked), Active Pods, Active Rooms
    rw = 0.26
    r1 = np.array(std_rob)
    r2 = np.array(tank_rob)
    r3 = np.array(drone_rob)

    ax2.bar(x - rw, r1, rw, label="Robot: Standard Curator", color="#54A24B", edgecolor="white")
    ax2.bar(x - rw, r2, rw, bottom=r1, label="Robot: Tank Curator (biggie)", color="#EECA3B", edgecolor="white")
    ax2.bar(x - rw, r3, rw, bottom=r1 + r2, label="Robot: Drone Curator (bee)", color="#B279A2", edgecolor="white")

    ax2.bar(x, pods, rw, label="Active Pods", color="#FF9DA6", edgecolor="white")
    ax2.bar(x + rw, rooms, rw, label="Active Rooms", color="#9D755D", edgecolor="white")

    ax2.set_ylabel("Active Entities (Count)")
    ax2.set_ylim(0, 5.2)
    ax2.set_yticks(range(0, 6))
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_title("(b) Active Robots (by Type), Pods, and Rooms across Problem Instances")
    ax2.legend(loc="upper right", ncol=3, frameon=True)

    fig.suptitle("Domain & Problem Instance Sizing Overview (Problems 1–5)", y=1.01)
    fig.tight_layout()
    save_fig(fig, "plot_problem_instances_overview")


# ============================================================================
# Plot 2: Problem 1 Scalability (Search Time, Expanded States, Plan Length)
# ============================================================================

def plot_problem1_scalability(data: Dict[str, Any]) -> None:
    runs = data["runs"]
    levels = ["easy", "middle", "default", "hard"]
    level_labels = [
        "easy\n(3 art, 1 rob)",
        "middle\n(5 art, 2 rob)",
        "default\n(10 art, 1 rob)",
        "hard\n(10 art, 3 rob)",
    ]

    configs = [
        ("ENHSP", "opt-blind", "ENHSP (opt-blind)", "#1f77b4", "o", "-"),
        ("ENHSP", "opt-hmax", "ENHSP (opt-hmax)", "#ff7f0e", "s", "-"),
        ("ENHSP", "sat-aibr", "ENHSP (sat-aibr)", "#2ca02c", "^", "--"),
        ("Fast Downward", "astar-blind", "FD (astar-blind)", "#d62728", "D", "-"),
        ("Fast Downward", "seq-opt-lmcut", "FD (seq-opt-lmcut)", "#9467bd", "v", "-"),
        ("Fast Downward", "lama-first", "FD (lama-first)", "#17becf", "P", "--"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    ax_time, ax_exp, ax_len = axes
    x = np.arange(len(levels))

    for planner, cfg, label, color, marker, ls in configs:
        times = []
        exps = []
        lengths = []
        statuses = []

        for lv in levels:
            r = find_run(runs, "problem1", planner, cfg, lv)
            if not r:
                times.append(np.nan)
                exps.append(np.nan)
                lengths.append(np.nan)
                statuses.append("missing")
                continue

            st = r["status"]
            statuses.append(st)
            if r["solution_found"]:
                t_val = r["search_time_sec"] if r["search_time_sec"] is not None else r["time_spent_sec"]
                times.append(max(t_val, 1e-3))
                lengths.append(r["plan_length"])
            else:
                times.append(600.0)  # Cap at timeout line for visualization
                lengths.append(np.nan)

            exps.append(r["expanded_states"] if r["expanded_states"] else np.nan)

        # Plot Search Time
        ax_time.plot(x, times, label=label, color=color, marker=marker, linestyle=ls, linewidth=1.8, markersize=6)
        for i, st in enumerate(statuses):
            if st != "solved":
                ax_time.scatter(x[i], times[i], color="black", marker="x", s=55, zorder=5)

        # Plot Expanded States
        ax_exp.plot(x, exps, label=label, color=color, marker=marker, linestyle=ls, linewidth=1.8, markersize=6)
        for i, st in enumerate(statuses):
            if st != "solved" and not np.isnan(exps[i]):
                ax_exp.scatter(x[i], exps[i], color="black", marker="x", s=55, zorder=5)

        # Plot Plan Length
        ax_len.plot(x, lengths, label=label, color=color, marker=marker, linestyle=ls, linewidth=1.8, markersize=6)

    ax_time.axhline(600.0, color="red", linestyle=":", linewidth=1.1, label="Timeout / OOM Cap (600s)")
    ax_time.set_yscale("log")
    ax_time.set_xticks(x)
    ax_time.set_xticklabels(level_labels)
    ax_time.set_ylabel("Search Time (seconds, log scale)")
    ax_time.set_title("(a) Search Time vs. Difficulty")

    ax_exp.set_yscale("log")
    ax_exp.set_xticks(x)
    ax_exp.set_xticklabels(level_labels)
    ax_exp.set_ylabel("Expanded States (log scale)")
    ax_exp.set_title("(b) Expanded States vs. Difficulty")

    ax_len.set_xticks(x)
    ax_len.set_xticklabels(level_labels)
    ax_len.set_ylabel("Solution Plan Length (actions)")
    ax_len.set_title("(c) Solution Plan Length")

    handles, labels_leg = ax_time.get_legend_handles_labels()
    fig.legend(handles, labels_leg, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.14), frameon=True)
    fig.suptitle("Problem 1 (Classical Planning): Scalability of ENHSP & Fast Downward Configurations", y=1.02)
    fig.tight_layout()
    save_fig(fig, "plot_problem1_scalability")


# ============================================================================
# Plot 3: Problem 2 Negative Preconditions vs No Negative Preconditions
# ============================================================================

def plot_problem2_neg_vs_noneg(data: Dict[str, Any]) -> None:
    runs = data["runs"]
    configs = ["opt-blind", "opt-hmax", "sat-aibr", "sat-hadd"]
    x = np.arange(len(configs))
    w = 0.35

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    ax_easy_t, ax_mid_t, ax_mid_exp = axes

    # Panel A: Easy instance planning time
    t_noneg_easy = []
    t_neg_easy = []
    for cfg in configs:
        r_no = find_run(runs, "problem2", "ENHSP", cfg, "easy", "no_negative_preconditions")
        r_neg = find_run(runs, "problem2", "ENHSP", cfg, "easy", "negative_preconditions")
        t_noneg_easy.append(r_no["time_spent_sec"] if r_no else 0)
        t_neg_easy.append(r_neg["time_spent_sec"] if r_neg else 0)

    rects1 = ax_easy_t.bar(x - w / 2, t_noneg_easy, w, label="No Negative Preconditions", color="#E45756")
    rects2 = ax_easy_t.bar(x + w / 2, t_neg_easy, w, label="With Negative Preconditions", color="#4C78A8")
    for rect in rects1:
        h = rect.get_height()
        ax_easy_t.text(rect.get_x() + rect.get_width() / 2, h * 1.05, f"{h:.2f}s", ha="center", va="bottom", fontsize=8)
    for rect in rects2:
        h = rect.get_height()
        ax_easy_t.text(rect.get_x() + rect.get_width() / 2, h * 1.05, f"{h:.2f}s", ha="center", va="bottom", fontsize=8)

    ax_easy_t.set_yscale("log")
    ax_easy_t.set_ylim(0.03, 10.0)
    ax_easy_t.set_xticks(x)
    ax_easy_t.set_xticklabels(configs)
    ax_easy_t.set_ylabel("Planning Time (seconds, log scale)")
    ax_easy_t.set_title("(a) Easy (3 Art., 1 Rob.): Planning Time")
    ax_easy_t.legend(loc="upper right")

    # Panel B: Middle/Default instance planning time
    t_noneg_mid = []
    t_neg_mid = []
    st_noneg_mid = []
    for cfg in configs:
        r_no = find_run(runs, "problem2", "ENHSP", cfg, "middle", "no_negative_preconditions")
        r_neg = find_run(runs, "problem2", "ENHSP", cfg, "middle", "negative_preconditions")
        t_noneg_mid.append(r_no["time_spent_sec"] if r_no else 0)
        t_neg_mid.append(r_neg["time_spent_sec"] if r_neg else 0)
        st_noneg_mid.append(r_no["status"] if r_no else "")

    rects3 = ax_mid_t.bar(x - w / 2, t_noneg_mid, w, label="No Negative Preconditions", color="#E45756")
    rects4 = ax_mid_t.bar(x + w / 2, t_neg_mid, w, label="With Negative Preconditions", color="#4C78A8")
    for idx, rect in enumerate(rects3):
        h = rect.get_height()
        lbl = f"OOM\n({h:.0f}s)" if st_noneg_mid[idx] == "out_of_memory" else f"{h:.1f}s"
        ax_mid_t.text(rect.get_x() + rect.get_width() / 2, h * 1.08, lbl, ha="center", va="bottom", fontsize=8, fontweight="bold" if "OOM" in lbl else "normal")
    for rect in rects4:
        h = rect.get_height()
        ax_mid_t.text(rect.get_x() + rect.get_width() / 2, h * 1.08, f"{h:.1f}s", ha="center", va="bottom", fontsize=8)

    ax_mid_t.set_yscale("log")
    ax_mid_t.set_ylim(0.5, 1000.0)
    ax_mid_t.set_xticks(x)
    ax_mid_t.set_xticklabels(configs)
    ax_mid_t.set_ylabel("Planning Time (seconds, log scale)")
    ax_mid_t.set_title("(b) Middle/Default (5 Art., 2 Rob.): Time")

    # Panel C: Middle/Default Expanded States
    exp_noneg_mid = []
    exp_neg_mid = []
    for cfg in configs:
        r_no = find_run(runs, "problem2", "ENHSP", cfg, "middle", "no_negative_preconditions")
        r_neg = find_run(runs, "problem2", "ENHSP", cfg, "middle", "negative_preconditions")
        exp_noneg_mid.append(r_no["expanded_states"] if r_no else 0)
        exp_neg_mid.append(r_neg["expanded_states"] if r_neg else 0)

    ax_mid_exp.bar(x - w / 2, exp_noneg_mid, w, label="No Negative Preconditions", color="#E45756")
    ax_mid_exp.bar(x + w / 2, exp_neg_mid, w, label="With Negative Preconditions", color="#4C78A8")
    ax_mid_exp.set_yscale("log")
    ax_mid_exp.set_ylim(1e3, 2e7)
    ax_mid_exp.set_xticks(x)
    ax_mid_exp.set_xticklabels(configs)
    ax_mid_exp.set_ylabel("Expanded States (log scale)")
    ax_mid_exp.set_title("(c) Middle/Default (5 Art., 2 Rob.): Expanded States")

    fig.suptitle("Problem 2 (Numeric Fluents & Earthquakes): Impact of Native Negative Preconditions in ENHSP", y=1.02)
    fig.tight_layout()
    save_fig(fig, "plot_problem2_neg_vs_noneg")


# ============================================================================
# Plot 4: Problem 3 HTN Comparison (PANDA vs Lilotane)
# ============================================================================

def plot_problem3_htn_comparison(data: Dict[str, Any]) -> None:
    runs = data["runs"]
    levels = ["easy", "middle", "hard", "default"]
    level_labels = [
        "easy\n(3 art, 1 rob)",
        "middle\n(5 art, 2 rob)",
        "hard\n(10 art, 3 rob)",
        "default\n(13 art, 2 rob)",
    ]
    x = np.arange(len(levels))
    w = 0.36

    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.8))
    ax_time, ax_len, ax_layers = axes

    panda_times = []
    lilo_times = []
    panda_lens = []
    lilo_lens = []
    lilo_statuses = []

    for lv in levels:
        rp = find_run(runs, "problem3", "PANDA", "progression-rc2-ff", lv)
        rl = find_run(runs, "problem3", "Lilotane", "sat-glucose4", lv)
        panda_times.append(rp["execution_time_sec"] if rp else 0)
        lilo_times.append(rl["execution_time_sec"] if rl else 0)
        panda_lens.append(rp["plan_length"] if rp and rp["plan_length"] else 0)
        lilo_lens.append(rl["plan_length"] if rl and rl["plan_length"] else 0)
        lilo_statuses.append(rl["status"] if rl else "")

    # Panel A: Execution Time
    b1 = ax_time.bar(x - w / 2, panda_times, w, label="PANDA (progression-rc2-ff)", color="#4C78A8")
    b2 = ax_time.bar(x + w / 2, lilo_times, w, label="Lilotane (SAT-Glucose4)", color="#F58518")

    for rect in b1:
        h = rect.get_height()
        ax_time.text(rect.get_x() + rect.get_width() / 2, h * 1.08, f"{h:.2f}s", ha="center", va="bottom", fontsize=8)
    for idx, rect in enumerate(b2):
        h = rect.get_height()
        lbl = f"TO\n({h:.0f}s)" if lilo_statuses[idx] == "timeout" else f"{h:.2f}s"
        ax_time.text(rect.get_x() + rect.get_width() / 2, h * 1.08, lbl, ha="center", va="bottom", fontsize=8, fontweight="bold" if "TO" in lbl else "normal")

    ax_time.set_yscale("log")
    ax_time.set_ylim(0.1, 1200.0)
    ax_time.set_xticks(x)
    ax_time.set_xticklabels(level_labels)
    ax_time.set_ylabel("Total Execution Time (seconds, log scale)")
    ax_time.set_title("(a) Execution Time: PANDA vs. Lilotane")
    ax_time.legend(loc="upper left")

    # Panel B: Primitive Plan Length
    b3 = ax_len.bar(x - w / 2, panda_lens, w, label="PANDA", color="#4C78A8")
    b4 = ax_len.bar(x + w / 2, lilo_lens, w, label="Lilotane", color="#F58518")

    for rect in b3:
        h = rect.get_height()
        if h > 0:
            ax_len.text(rect.get_x() + rect.get_width() / 2, h + 8, str(int(h)), ha="center", va="bottom", fontsize=8.5)
    for idx, rect in enumerate(b4):
        h = rect.get_height()
        if h > 0:
            ax_len.text(rect.get_x() + rect.get_width() / 2, h + 8, str(int(h)), ha="center", va="bottom", fontsize=8.5)
        else:
            ax_len.text(rect.get_x() + rect.get_width() / 2, 12, "TO", ha="center", va="bottom", fontsize=8.5, color="red", fontweight="bold")

    ax_len.set_ylim(0, max(panda_lens) + 55)
    ax_len.set_xticks(x)
    ax_len.set_xticklabels(level_labels)
    ax_len.set_ylabel("Primitive Plan Length (actions)")
    ax_len.set_title("(b) Solution Plan Length (Primitive Actions)")

    # Panel C: Lilotane SAT Clause Growth per Layer
    colors_lilo = {"easy": "#2ca02c", "middle": "#1f77b4", "hard": "#ff7f0e", "default": "#d62728"}
    markers_lilo = {"easy": "o", "middle": "s", "hard": "^", "default": "X"}
    for lv in levels:
        rl = find_run(runs, "problem3", "Lilotane", "sat-glucose4", lv)
        if not rl or not rl.get("layers_progression"):
            continue
        layers = [item["layer"] for item in rl["layers_progression"] if item.get("clauses") is not None]
        clauses = [item["clauses"] for item in rl["layers_progression"] if item.get("clauses") is not None]
        ax_layers.plot(layers, clauses, label=f"Lilotane ({lv})", color=colors_lilo[lv], marker=markers_lilo[lv], linewidth=1.8)

    ax_layers.set_yscale("log")
    ax_layers.set_xlabel("Hierarchy Layer Depth")
    ax_layers.set_ylabel("Cumulative SAT Clauses (log scale)")
    ax_layers.set_title("(c) Lilotane Formula Growth across Layers")
    ax_layers.legend(loc="lower right")

    fig.suptitle("Problem 3 (HTN Planning): Progression Search (PANDA) vs. SAT-Based HTN (Lilotane)", y=1.02)
    fig.tight_layout()
    save_fig(fig, "plot_problem3_htn_comparison")


# ============================================================================
# Plot 5: Problem 4 Temporal Planners Comparison (TFD, LPG-TD, OPTIC)
# ============================================================================

def plot_problem4_temporal_comparison(data: Dict[str, Any]) -> None:
    runs = data["runs"]
    levels = ["default", "easy", "middle", "hard"]
    level_labels = [
        "default\n(1 art, 1 rob, 0 pod)",
        "easy\n(3 art, 1 rob, 2 pod)",
        "middle\n(5 art, 2 rob, 2 pod)",
        "hard\n(10 art, 3 rob, 2 pod)",
    ]
    planners = [
        ("TFD", "tfd", "TFD", "#4C78A8"),
        ("LPG-TD", "lpg-td", "LPG-TD", "#E45756"),
        ("OPTIC", "optic", "OPTIC", "#54A24B"),
    ]

    x = np.arange(len(levels))
    w = 0.26

    fig, (ax_time, ax_qual) = plt.subplots(1, 2, figsize=(13.5, 4.8))

    # Panel A: Time to Solution (or Termination)
    for idx_p, (p_key, c_key, p_label, color) in enumerate(planners):
        times = []
        annotations = []
        for lv in levels:
            r = find_run(runs, "problem4", p_key, c_key, lv)
            if not r:
                times.append(0)
                annotations.append("")
                continue
            t = r["time_spent_sec"] if r["time_spent_sec"] is not None else r["execution_time_sec"]
            times.append(max(t, 0.05))
            st = r["status"]
            if r["solution_found"]:
                annotations.append(f"{t:.2f}s")
            elif st == "timeout":
                annotations.append("TO")
            elif st == "unsolvable_exhausted":
                annotations.append("Exh.")
            else:
                annotations.append("Err.")

        offset = (idx_p - 1) * w
        rects = ax_time.bar(x + offset, times, w, label=p_label, color=color, edgecolor="white")
        for i, rect in enumerate(rects):
            h = rect.get_height()
            ann = annotations[i]
            is_fail = ann in ("TO", "Exh.", "Err.")
            ax_time.text(
                rect.get_x() + rect.get_width() / 2,
                h * 1.12,
                ann,
                ha="center",
                va="bottom",
                fontsize=8,
                color="darkred" if is_fail else "black",
                fontweight="bold" if is_fail else "normal",
            )

    ax_time.set_yscale("log")
    ax_time.set_ylim(0.05, 1500.0)
    ax_time.set_xticks(x)
    ax_time.set_xticklabels(level_labels)
    ax_time.set_ylabel("Time to Solution / Termination (s, log scale)")
    ax_time.set_title("(a) Solution Time & Termination Status across Instances")
    ax_time.legend(loc="upper left")

    # Panel B: Makespan & Plan Length for Solved Temporal Runs (Problem 4 & Problem 5)
    solved_items = [
        ("P4 default\n(LPG-TD)", find_run(runs, "problem4", "LPG-TD", "lpg-td", "default")),
        ("P4 default\n(OPTIC)", find_run(runs, "problem4", "OPTIC", "optic", "default")),
        ("P4 easy\n(OPTIC)", find_run(runs, "problem4", "OPTIC", "optic", "easy")),
        ("P4 middle\n(TFD)", find_run(runs, "problem4", "TFD", "tfd", "middle")),
        ("P4 middle\n(OPTIC)", find_run(runs, "problem4", "OPTIC", "optic", "middle")),
        ("P5 default\n(PlanSys2)", find_run(runs, "problem5", "PlanSys2 (Kairos)", "kairos", "default")),
    ]

    s_labels = [lbl for lbl, r in solved_items if r is not None]
    s_len = [r["plan_length"] for _, r in solved_items if r is not None]
    s_mk = [r["makespan"] for _, r in solved_items if r is not None]

    xs = np.arange(len(s_labels))
    w2 = 0.35
    ax_qual_mk = ax_qual.twinx()

    b_len = ax_qual.bar(xs - w2 / 2, s_len, w2, label="Plan Length (Actions)", color="#4C78A8")
    b_mk = ax_qual_mk.bar(xs + w2 / 2, s_mk, w2, label="Makespan (Seconds)", color="#F58518")

    for rect in b_len:
        h = rect.get_height()
        ax_qual.text(rect.get_x() + rect.get_width() / 2, h + 3, str(int(h)), ha="center", va="bottom", fontsize=8, color="#2b4c7e", fontweight="bold")
    for rect in b_mk:
        h = rect.get_height()
        ax_qual_mk.text(rect.get_x() + rect.get_width() / 2, h * 1.12, f"{h:.1f}", ha="center", va="bottom", fontsize=8, color="#b85d00", fontweight="bold")

    ax_qual.set_xticks(xs)
    ax_qual.set_xticklabels(s_labels)
    ax_qual.set_ylabel("Plan Length (Number of Actions)", color="#2b4c7e")
    ax_qual.set_ylim(0, max(s_len) + 30)
    ax_qual_mk.set_yscale("log")
    ax_qual_mk.set_ylim(5.0, 15000.0)
    ax_qual_mk.set_ylabel("Temporal Makespan (s, log scale)", color="#b85d00")
    ax_qual_mk.grid(False)
    ax_qual.set_title("(b) Solved Temporal Runs (Problems 4 & 5): Plan Length & Makespan")

    lines1, labels1 = ax_qual.get_legend_handles_labels()
    lines2, labels2 = ax_qual_mk.get_legend_handles_labels()
    ax_qual.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    fig.suptitle("Problems 4 & 5 (Temporal Planning & ROS 2 PlanSys2 Execution): Performance & Plan Quality", y=1.02)
    fig.tight_layout()
    save_fig(fig, "plot_problem4_temporal_comparison")


# ============================================================================
# Plot 6: Action Category Distribution & Multi-Robot Workload Breakdown
# ============================================================================

def plot_action_distribution_and_problem5(data: Dict[str, Any]) -> None:
    runs = data["runs"]

    representative = [
        ("P1 default\n(FD lmcut)", find_run(runs, "problem1", "Fast Downward", "seq-opt-lmcut", "default")),
        ("P1 hard\n(FD lama)", find_run(runs, "problem1", "Fast Downward", "lama-first", "hard")),
        ("P2 mid (NoNeg)\n(ENHSP hmax)", find_run(runs, "problem2", "ENHSP", "opt-hmax", "middle", "no_negative_preconditions")),
        ("P2 mid (Neg)\n(ENHSP hmax)", find_run(runs, "problem2", "ENHSP", "opt-hmax", "middle", "negative_preconditions")),
        ("P2 mid (Neg)\n(ENHSP aibr)", find_run(runs, "problem2", "ENHSP", "sat-aibr", "middle", "negative_preconditions")),
        ("P3 hard\n(PANDA)", find_run(runs, "problem3", "PANDA", "progression-rc2-ff", "hard")),
        ("P3 hard\n(Lilotane)", find_run(runs, "problem3", "Lilotane", "sat-glucose4", "hard")),
        ("P4 middle\n(TFD)", find_run(runs, "problem4", "TFD", "tfd", "middle")),
        ("P4 middle\n(OPTIC)", find_run(runs, "problem4", "OPTIC", "optic", "middle")),
        ("P5 default\n(PlanSys2)", find_run(runs, "problem5", "PlanSys2 (Kairos)", "kairos", "default")),
    ]

    labels = []
    move_c = []
    pickup_c = []
    drop_c = []
    pod_c = []
    seal_c = []
    quake_c = []

    std_r = []
    biggie_r = []
    bee_r = []

    for lbl, r in representative:
        if not r or not r.get("action_analysis"):
            continue
        labels.append(lbl)
        cat = r["action_analysis"]["by_category"]
        move_c.append(cat.get("move_or_fly", 0))
        pickup_c.append(cat.get("pickup_artifact", 0))
        drop_c.append(cat.get("drop_artifact", 0))
        pod_c.append(cat.get("pod_operations", 0))
        seal_c.append(cat.get("seal_unseal", 0))
        quake_c.append(cat.get("earthquake", 0) + cat.get("activate_robot", 0))

        rob = r["action_analysis"]["by_robot"]
        std_r.append(rob.get("curator", 0) + rob.get("curator_1", 0) + rob.get("curator_2", 0) + rob.get("curator_3", 0))
        biggie_r.append(rob.get("biggie", 0))
        bee_r.append(rob.get("bee", 0))

    x = np.arange(len(labels))
    w = 0.58

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13.5, 7.5), sharex=True)

    # Panel A: Action Category Breakdown
    c1 = np.array(move_c)
    c2 = np.array(pickup_c)
    c3 = np.array(drop_c)
    c4 = np.array(pod_c)
    c5 = np.array(seal_c)
    c6 = np.array(quake_c)

    ax1.bar(x, c1, w, label="Move / Fly", color="#4C78A8", edgecolor="white")
    ax1.bar(x, c2, w, bottom=c1, label="Pickup Artifact", color="#54A24B", edgecolor="white")
    ax1.bar(x, c3, w, bottom=c1 + c2, label="Drop Artifact", color="#72B7B2", edgecolor="white")
    ax1.bar(x, c4, w, bottom=c1 + c2 + c3, label="Pod Ops (take/drop)", color="#F58518", edgecolor="white")
    ax1.bar(x, c5, w, bottom=c1 + c2 + c3 + c4, label="Seal / Unseal Robot", color="#EECA3B", edgecolor="white")
    ax1.bar(x, c6, w, bottom=c1 + c2 + c3 + c4 + c5, label="Earthquake / Activate", color="#E45756", edgecolor="white")

    tot_act = c1 + c2 + c3 + c4 + c5 + c6
    for i, t in enumerate(tot_act):
        ax1.text(i, t + 2.5, str(int(t)), ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax1.set_ylabel("Number of Actions in Plan")
    ax1.set_ylim(0, max(tot_act) + 22)
    ax1.set_title("(a) Action Category Breakdown across Representative Plans (Problems 1–5)")
    ax1.legend(loc="upper left", ncol=3, frameon=True)

    # Panel B: Robot Workload Breakdown
    r1 = np.array(std_r)
    r2 = np.array(biggie_r)
    r3 = np.array(bee_r)

    ax2.bar(x, r1, w, label="Standard Curator (curator / curator_1..3)", color="#54A24B", edgecolor="white")
    ax2.bar(x, r2, w, bottom=r1, label="Tank Curator (biggie)", color="#EECA3B", edgecolor="white")
    ax2.bar(x, r3, w, bottom=r1 + r2, label="Drone Curator (bee)", color="#B279A2", edgecolor="white")

    tot_rob = r1 + r2 + r3
    for i, t in enumerate(tot_rob):
        ax2.text(i, t + 2.5, str(int(t)), ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    ax2.set_ylabel("Robot Actions Assigned")
    ax2.set_ylim(0, max(tot_rob) + 22)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_title("(b) Robot Workload Allocation across Representative Plans (Problems 1–5)")
    ax2.legend(loc="upper left", ncol=3, frameon=True)

    fig.suptitle("Solution Plan Composition: Action Categories & Multi-Robot Task Allocation", y=1.01)
    fig.tight_layout()
    save_fig(fig, "plot_action_distribution_and_problem5")


def main() -> None:
    if not STATS_PATH.exists():
        raise FileNotFoundError(f"Missing {STATS_PATH}. Run parse_and_aggregate.py first.")
    data = json.loads(STATS_PATH.read_text(encoding="utf-8"))

    plot_problem_instances_overview(data)
    plot_problem1_scalability(data)
    plot_problem2_neg_vs_noneg(data)
    plot_problem3_htn_comparison(data)
    plot_problem4_temporal_comparison(data)
    plot_action_distribution_and_problem5(data)


if __name__ == "__main__":
    main()
