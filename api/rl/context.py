"""
ContextExtractor - builds a fixed-length float context vector from:
  item features, alternative metadata, session history, time of day, prev outcome.
  
Output dimension must match CONTEXT_DIM in model_manager.py (16).
"""
from __future__ import annotations

import datetime
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from storage.catalogue import Catalogue

CONTEXT_DIM = 28


class ContextExtractor:
    def __init__(self, catalogue: "Catalogue"):
        self.catalogue = catalogue
        self._session_history: list[dict] = []  # recent interactions

    def build(self, item_id: str, cart: list[dict]) -> list[float]:
        item = self.catalogue.get_item(item_id) or {}
        alts = self.catalogue.get_alternatives(item_id)

        # 0: item CO2e (normalised 0-1, assume max 20 kg CO2e/kg)
        co2e_norm = min(item.get("co2e", 0.0) / 20.0, 1.0)

        # 1: item price (normalised, assume max 50)
        price_norm = min(item.get("price", 0.0) / 50.0, 1.0)

        # 2: number of alternatives (normalised, max 10)
        n_alts = min(len(alts) / 10.0, 1.0)

        # 3: raw price (used by price head)
        raw_price = item.get("price", 0.0)

        # 4: best alternative CO2e saving (relative)
        best_co2e_saving = 0.0
        if alts:
            best_alt = min(alts, key=lambda a: a.get("co2e", 999))
            item_co2e = item.get("co2e", 0.0)
            if item_co2e > 0:
                best_co2e_saving = max(0.0, (item_co2e - best_alt.get("co2e", 0.0)) / item_co2e)

        # 5: best alternative price delta (negative = cheaper alt)
        best_price_delta = 0.0
        if alts:
            best_alt_price = min(a.get("price", 999) for a in alts)
            best_price_delta = (best_alt_price - raw_price) / max(raw_price, 0.01)
            best_price_delta = max(-1.0, min(1.0, best_price_delta))

        # 6: cart size (normalised, max 20 items)
        cart_size = min(len(cart) / 20.0, 1.0)

        # 7-8: time of day as sin/cos encoding
        now = datetime.datetime.now()
        hour_frac = (now.hour + now.minute / 60.0) / 24.0
        tod_sin = math.sin(2 * math.pi * hour_frac)
        tod_cos = math.cos(2 * math.pi * hour_frac)

        # 9: day of week (normalised)
        dow = now.weekday() / 6.0

        # 10-13: last 4 rewards from session history (0 if not enough history)
        recent_rewards = [h["reward"] for h in self._session_history[-4:]]
        while len(recent_rewards) < 4:
            recent_rewards.insert(0, 0.0)

        # 14: accept rate in session
        if self._session_history:
            accept_rate = sum(1 for h in self._session_history if h["action"] == "accept") / len(
                self._session_history
            )
        else:
            accept_rate = 0.5  # Prior

        # 15: sustainability score of item
        sust_score = item.get("sustainability_score", 0.5)

        vec = [
            co2e_norm,          # 0
            price_norm,         # 1
            n_alts,             # 2
            raw_price,          # 3 — used by price head, not normalised
            best_co2e_saving,   # 4
            best_price_delta,   # 5
            cart_size,          # 6
            tod_sin,            # 7
            tod_cos,            # 8
            dow,                # 9
            *recent_rewards,    # 10-13
            accept_rate,        # 14
            sust_score,         # 15
        ]
        assert len(vec) == CONTEXT_DIM, f"Expected {CONTEXT_DIM}, got {len(vec)}"
        return vec

    def record_outcome(self, action: str, reward: float):
        self._session_history.append({"action": action, "reward": reward})
        # Keep last 20 interactions in memory
        if len(self._session_history) > 20:
            self._session_history.pop(0)