"""Reward function (FR-2.6 reward signal specification)."""

REWARDS = {
    "accept": 1.0,
    "accept_cheap": 1.2,   # Accept when alternative is also cheaper
    "dismiss": -0.2,
    "ignore": 0.0,
}


def compute_reward(action: str, price_delta: float | None = None) -> float:
    if action == "accept":
        if price_delta is not None and price_delta < 0:
            return REWARDS["accept_cheap"]
        return REWARDS["accept"]
    return REWARDS.get(action, 0.0)