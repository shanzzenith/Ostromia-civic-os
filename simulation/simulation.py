import random
from collections import deque

import pandas as pd
import matplotlib.pyplot as plt
from cadCAD.configuration import Configuration
from cadCAD.configuration.utils import config_sim
from cadCAD.engine import ExecutionMode, ExecutionContext, Executor

# ---------- PARAMETERS ----------
NUM_CITIZENS = 10
SIM_DAYS = 7
MAX_ACTIONS = 5
A, B = 0.10, 1.0  # bonding-curve: price = A*supply + B

# ---------- INITIAL STATE ----------
initial_state = {
    "citizens": {f"citizen_{i}": {"points": 0} for i in range(NUM_CITIZENS)},
    "total_supply": 0,
    "daily_log": []
}

# ---------- POLICIES ----------
def civic_actions(p, step, sL, s):
    """Pick random citizens who perform a civic action today."""
    return {
        "actions": random.choices(list(s["citizens"]), k=random.randint(1, MAX_ACTIONS))
    }

# ---------- STATE UPDATES ----------
def update_points(p, step, sL, s, _in):
    citizens = s["citizens"].copy()
    supply = s["total_supply"]
    for cid in _in["actions"]:
        price = A * supply + B
        reward = int(10 / price)
        citizens[cid]["points"] += reward
        supply += 1
    return "citizens", citizens

def update_supply(p, step, sL, s, _in):
    return "total_supply", s["total_supply"] + len(_in["actions"])

def log_day(p, step, sL, s, _in):
    summary = {
        "day": step,
        "total_supply": s["total_supply"],
        "avg_points": sum(c["points"] for c in s["citizens"].values()) / NUM_CITIZENS,
    }
    log = s["daily_log"].copy()
    log.append(summary)
    return "daily_log", log

# ---------- PARTIAL STATE UPDATE BLOCK ----------
psubs = [{
    "policies": {"civic_actions": civic_actions},
    "variables": {
        "citizens": update_points,
        "total_supply": update_supply,
        "daily_log": log_day,
    },
}]

# ---------- SIM CONFIG ----------
sim_config = config_sim({"T": range(SIM_DAYS), "N": 1})  # no "M" key

# ---------- CONFIGURATION ----------
configuration = Configuration(
    user_id="demo_user",
    model_id="ostromia_minimal",
    subset_id="run_1",
    subset_window=deque([0]),
    initial_state=initial_state,
    partial_state_update_blocks=psubs,
    sim_config=sim_config,
)

def run_simulation():
    """Execute the cadCAD simulation and visualize results."""
    exec_ctx = ExecutionContext(context=ExecutionMode().single_mode)
    raw_result, *_ = Executor(exec_ctx, configs=[configuration]).execute()
    results_df = pd.DataFrame(raw_result)
    daily = pd.DataFrame(results_df["daily_log"].iloc[-1])

    plt.figure(figsize=(8, 4))
    plt.plot(daily["day"], daily["total_supply"], label="Total City Points")
    plt.plot(daily["day"], daily["avg_points"], label="Avg Points per Citizen")
    plt.title("Ostromia: 7-Day City-Points Growth")
    plt.xlabel("Day")
    plt.ylabel("Points")
    plt.legend()
    plt.grid()
    plt.show()

    print(daily)
    return daily


if __name__ == "__main__":
    run_simulation()
