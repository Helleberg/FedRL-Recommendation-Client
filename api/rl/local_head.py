"""
Thompson Sampling (LinTS) local head - pure NumPy, never leaves the device.

Three sub-heads:
  - ItemHead:  tracks which substitute items this user tends to accept
  - PriceHead: learns correlation between price delta and accept probability
  - NudgeHead: tracks per-nudge-type responsiveness; round-robin cold-start
"""
from __future__ import annotations

import numpy as np

NUDGE_TYPES = ["N1", "N2", "N3", "N4"]


class ItemHead:
    """LinTS per candidate item using 32-dim backbone embedding."""

    def __init__(self, latent_dim: int = 32, alpha: float = 1.0):
        self.latent_dim = latent_dim
        self.alpha = alpha  # Exploration noise
        # Map item_id → (mu, Sigma_inv) for Thompson sampling
        self._params: dict[str, dict] = {}

    def _init_item(self, item_id: str):
        d = self.latent_dim
        self._params[item_id] = {
            "mu": np.zeros(d),
            "A": np.eye(d) * self.alpha,     # A = X^T X + alpha*I
            "b": np.zeros(d),                # b = X^T r
        }

    def sample_score(self, item_id: str, embedding: np.ndarray) -> float:
        if item_id not in self._params:
            self._init_item(item_id)
        p = self._params[item_id]
        A_inv = np.linalg.inv(p["A"])
        mu_hat = A_inv @ p["b"]
        cov = A_inv * self.alpha
        theta = np.random.multivariate_normal(mu_hat, cov)
        return float(embedding @ theta)

    def update(self, item_id: str, embedding: np.ndarray, reward: float):
        if item_id not in self._params:
            self._init_item(item_id)
        p = self._params[item_id]
        p["A"] += np.outer(embedding, embedding)
        p["b"] += reward * embedding

    def state_dict(self) -> dict:
        return {k: {kk: v.tolist() for kk, v in vv.items()} for k, vv in self._params.items()}

    def load_state_dict(self, d: dict):
        self._params = {k: {kk: np.array(v) for kk, v in vv.items()} for k, vv in d.items()}


class PriceHead:
    """
    Learns a scalar price-sensitivity coefficient via online ridge regression.
    Outputs a price offset applied to item scores.
    """

    def __init__(self, alpha: float = 1.0):
        self.alpha = alpha
        self._A = alpha       # scalar ridge regression accumulator
        self._b = 0.0

    def price_offset(self, price_delta: float) -> float:
        """Sample a price sensitivity coefficient and return offset."""
        mu = self._b / self._A
        var = 1.0 / self._A
        beta = np.random.normal(mu, np.sqrt(var))
        return float(beta * price_delta)

    def update(self, price_delta: float, reward: float):
        self._A += price_delta ** 2
        self._b += reward * price_delta

    def state_dict(self) -> dict:
        return {"A": self._A, "b": self._b}

    def load_state_dict(self, d: dict):
        self._A = d["A"]
        self._b = d["b"]


class NudgeHead:
    """
    Beta-TS per nudge type. Cold-start: forced round-robin for first N recs.
    """

    def __init__(self, cold_start_recs: int = 8):
        self.cold_start_recs = cold_start_recs
        self._interaction_count = 0
        self._rr_index = 0
        # Beta distribution parameters per nudge type
        self._alpha = {n: 1.0 for n in NUDGE_TYPES}
        self._beta_param = {n: 1.0 for n in NUDGE_TYPES}

    def select_nudge(self) -> str:
        if self._interaction_count < self.cold_start_recs:
            # Round-robin cold start (FR-2.7)
            nudge = NUDGE_TYPES[self._rr_index % len(NUDGE_TYPES)]
            self._rr_index += 1
            return nudge
        # Thompson sample from Beta distributions
        samples = {n: np.random.beta(self._alpha[n], self._beta_param[n]) for n in NUDGE_TYPES}
        return max(samples, key=samples.__getitem__)

    def update(self, nudge_type: str, reward: float):
        self._interaction_count += 1
        if reward > 0:
            self._alpha[nudge_type] += reward
        else:
            self._beta_param[nudge_type] += 1.0

    def state_dict(self) -> dict:
        return {
            "interaction_count": self._interaction_count,
            "rr_index": self._rr_index,
            "alpha": self._alpha,
            "beta": self._beta_param,
        }

    def load_state_dict(self, d: dict):
        self._interaction_count = d["interaction_count"]
        self._rr_index = d["rr_index"]
        self._alpha = d["alpha"]
        self._beta_param = d["beta"]