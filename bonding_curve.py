"""
Simple bonding-curve helpers
price  = a * supply + b
reward = ⌊ base_reward / price ⌋
"""

from dataclasses import dataclass

@dataclass
class LinearBondingCurve:
    a: float = 0.10   # slope
    b: float = 1.00   # intercept

    def price(self, supply: int) -> float:
        return self.a * supply + self.b

    def reward(self, base_reward: int, supply: int) -> int:
        """
        Number of tokens you can mint for a given spend (= base_reward).
        Rounded down to an integer so the simulation stays deterministic.
        """
        return int(base_reward / self.price(supply))


# convenient one-liner helpers
_default_curve = LinearBondingCurve()

price  = _default_curve.price
reward = _default_curve.reward
