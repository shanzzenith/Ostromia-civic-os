"""
Ostromia v1.1
• cadCAD demo with:
    – linear bonding-curve mint
    – 5-day half-life decay
    – Gold tier (+20 % reward above a threshold)
    – two parameter sweeps (base_reward = 10, 20)
"""

# ──────────────────────────────────────────────────────────────────────────────
# 1) DEPENDENCIES ─ install once then comment out
# ------------------------------------------------------------------------------
# !pip install --quiet cadCAD==0.5.3 pandas matplotlib dill

# ──────────────────────────────────────────────────────────────────────────────
# 2) IMPORTS & CONSTANTS
# ------------------------------------------------------------------------------
import random, math
from collections import deque
import pandas as pd
import matplotlib.pyplot as plt

from cadCAD.configuration.utils import config_sim
from cadCAD.configuration import Configuration
from cadCAD.engine         import ExecutionMode, ExecutionContext, Executor

from library.bonding_curve import LinearBondingCurve   # local helper

# --- global simulation knobs --------------------------------------------------
NUM_CITIZENS       = 10
SIM_DAYS           = 7
MAX_ACTIONS_DAY    = 5

# bonding-curve instance (slope a, intercept b)
curve = LinearBondingCurve(a=0.10, b=1.0)

# decay: ½-life = 5 days  →  daily_decay = 2^(-1/5)
DAILY_DECAY        = 0.5 ** (1/5)          # ≈ 0.87055

# gold tier
GOLD_THRESHOLD     = 50                    # pts
GOLD_BONUS         = 0.20                  # +20 %

# parameter sweep over two “base rewards”
BASE_REWARD_LIST   = [10, 20]


# ──────────────────────────────────────────────────────────────────────────────
# 3) INITIAL STATE  (identical for every run)
# ------------------------------------------------------------------------------
def initial_state():
    return dict(
        citizens      = {f"citizen_{i}": {"pts": 0} for i in range(NUM_CITIZENS)},
        total_supply  = 0,
        daily_log     = []
    )


# ──────────────────────────────────────────────────────────────────────────────
# 4) PARTIAL-STATE UPDATE BLOCK
# ------------------------------------------------------------------------------
def policy_actions(params, step, sL, s):
    """ pick 1-5 random citizens """
    return {"actors": random.choices(list(s["citizens"]), k=random.randint(1, MAX_ACTIONS_DAY))}


def state_decay(params, step, sL, s, _input):
    """apply exponential decay at the **start** of each day"""
    decayed = {
        cid: {"pts": int(data["pts"] * DAILY_DECAY)}
        for cid, data in s["citizens"].items()
    }
    return ("citizens", decayed)


def state_rewards(params, step, sL, s, _input):
    citizens = s["citizens"].copy()
    supply   = s["total_supply"]
    base_rwd = params["base_reward"]

    for cid in _input["actors"]:
        rwd = curve.reward(base_rwd, supply)

        # gold-tier bonus (compute on *pre-mint* points)
        if citizens[cid]["pts"] >= GOLD_THRESHOLD:
            rwd = int(rwd * (1 + GOLD_BONUS))

        citizens[cid]["pts"] += rwd
        supply               += 1

    return ("citizens", citizens)


def state_supply(params, step, sL, s, _input):
    return ("total_supply", s["total_supply"] + len(_input["actors"]))


def state_log(params, step, sL, s, _input):
    summary = dict(
        day          = step,
        total_supply = s["total_supply"],
        avg_points   = sum(c["pts"] for c in s["citizens"].values()) / NUM_CITIZENS,
    )
    new_log = s["daily_log"].copy(); new_log.append(summary)
    return ("daily_log", new_log)


psub = [{
    "policies":  {"pick": policy_actions},
    "variables": {
        "citizens":      state_decay,   # decay first
        "citizens_rwd":  state_rewards, # then add rewards
        "total_supply":  state_supply,
        "daily_log":     state_log,
    },
}]


# ──────────────────────────────────────────────────────────────────────────────
# 5) BUILD TWO cadCAD CONFIG OBJECTS (base_reward sweep)
# ------------------------------------------------------------------------------
configs = []
for base_rwd in BASE_REWARD_LIST:
    sim_cfg = config_sim({
        "T": range(SIM_DAYS),
        "N": 1,
        "M": {                 # params accessible as `params[...]`
            "base_reward": [base_rwd],
        },
    })

    cfg = Configuration(
        user_id      = "ostromia",
        model_id     = f"base{base_rwd}",
        subset_id    = "run",
        subset_window= deque([0]),
        initial_state= initial_state(),
        partial_state_update_blocks = psub,
        sim_config   = sim_cfg,
    )
    configs.append(cfg)


# ──────────────────────────────────────────────────────────────────────────────
# 6) EXECUTION
# ------------------------------------------------------------------------------
ctx             = ExecutionContext(context=ExecutionMode().single_mode)
raw, *_         = Executor(ctx, configs=configs).execute()
df              = pd.DataFrame(raw)
print(df.head(3))


# ──────────────────────────────────────────────────────────────────────────────
# 7) VISUALISATION
# ------------------------------------------------------------------------------
for mid, frame in df.groupby("model_id"):
    daily = pd.DataFrame(frame["daily_log"].iloc[-1])
    plt.plot(daily["day"], daily["total_supply"], label=f"supply (base={mid[4:]})")

plt.title("Ostromia — total-supply growth, two parameter sets")
plt.xlabel("Day"); plt.ylabel("City-Points"); plt.grid(); plt.legend(); plt.show()
