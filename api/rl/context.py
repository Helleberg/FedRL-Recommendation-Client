"""
ContextExtractor - builds a fixed-length float context vector.

The context is a 28-dimensional feature vector with the following layout:

 1.  original_co2
 2.  original_price
 3.  original_calories
 4.  original_protein
 5.  original_is_meat
 6.  original_is_dairy
 7.  original_is_plant_based
 8.  original_category_id
 9.  candidate_co2
10.  candidate_price
11.  candidate_calories
12.  candidate_protein
13.  candidate_is_meat
14.  candidate_is_dairy
15.  candidate_is_plant_based
16.  candidate_category_id
17.  co2_delta
18.  co2_reduction
19.  price_delta
20.  calorie_delta
21.  protein_delta
22.  same_category_flag
23.  similarity_score
24.  is_lower_co2_flag
25.  cart_size
26.  session_step
27.  previous_nudge_outcome
28.  nudges_shown_this_session

Output dimension must match CONTEXT_DIM in model_manager.py (28).
"""
from __future__ import annotations

from rl.config import CONTEXT_DIM, MAX_SESSION_HISTORY
from storage.catalogue import Catalogue

class ContextExtractor:
    def __init__(self, catalogue: Catalogue):
        self.catalogue = catalogue
        self._session_history: list[dict] = []  # recent interactions

    def build(self, original_id: str, candidate_id: str, cart: list[dict], similarity_score: float = 0.0) -> list[float]:
        """Build a 28-dim context vector for (original, candidate, session)."""
        item = self.catalogue.get_item(original_id)
        candidate = self.catalogue.get_item(candidate_id)

        # Helper to support both dataclass and dict representations
        def _get(obj, field: str, default: float = 0.0) -> float:
            if obj is None:
                return default
            if isinstance(obj, dict):
                return float(obj.get(field, default) or 0.0)
            return float(getattr(obj, field, default) or 0.0)

        # Original item features
        original_co2 = _get(item, "co2_kg_per_kg")
        original_price = _get(item, "price_eur")
        original_calories = _get(item, "calories_kcal")
        original_protein = _get(item, "protein_g")
        original_is_meat = 1.0 if getattr(item, "is_meat", False) else 0.0
        original_is_dairy = 1.0 if getattr(item, "is_dairy", False) else 0.0
        original_is_plant_based = 1.0 if getattr(item, "is_plant_based", False) else 0.0
        original_category_id = _get(item, "category_id")

        # Candidate-related features
        candidate_co2 = _get(candidate, "co2_kg_per_kg")
        candidate_price = _get(candidate, "price_eur")
        candidate_calories = _get(candidate, "calories_kcal")
        candidate_protein = _get(candidate, "protein_g")
        candidate_is_meat = 1.0 if getattr(candidate, "is_meat", False) else 0.0
        candidate_is_dairy = 1.0 if getattr(candidate, "is_dairy", False) else 0.0
        candidate_is_plant_based = 1.0 if getattr(candidate, "is_plant_based", False) else 0.0
        candidate_category_id = _get(candidate, "category_id")

        # Deltas (candidate - original). With unknown candidate we default to 0.
        co2_delta = candidate_co2 - original_co2
        co2_reduction = original_co2 - candidate_co2
        price_delta = candidate_price - original_price
        calorie_delta = candidate_calories - original_calories
        protein_delta = candidate_protein - original_protein

        # Same-category + similarity flags
        same_category_flag = 1.0 if original_category_id == candidate_category_id else 0.0
        is_lower_co2_flag = 1.0 if candidate_co2 < original_co2 else 0.0

        # Cart and session features
        cart_size = float(len(cart))
        session_step = float(len(self._session_history) + 1)
        previous_nudge_outcome = 0.0
        if self._session_history:
            previous_nudge_outcome = float(self._session_history[-1]["outcome"])
        nudges_shown_this_session = float(len(self._session_history))

        vec = [
            original_co2,              # 1
            original_price,            # 2
            original_calories,         # 3
            original_protein,          # 4
            original_is_meat,          # 5
            original_is_dairy,         # 6
            original_is_plant_based,   # 7
            original_category_id,      # 8
            candidate_co2,             # 9
            candidate_price,           # 10
            candidate_calories,        # 11
            candidate_protein,         # 12
            candidate_is_meat,         # 13
            candidate_is_dairy,        # 14
            candidate_is_plant_based,  # 15
            candidate_category_id,     # 16
            co2_delta,                 # 17
            co2_reduction,             # 18
            price_delta,               # 19
            calorie_delta,             # 20
            protein_delta,             # 21
            same_category_flag,        # 22
            similarity_score,          # 23
            is_lower_co2_flag,         # 24
            cart_size,                 # 25
            session_step,              # 26
            previous_nudge_outcome,    # 27
            nudges_shown_this_session, # 28
        ]
        assert len(vec) == CONTEXT_DIM, f"Expected {CONTEXT_DIM}, got {len(vec)}"
        return vec

    def record_outcome(self, action: str, reward: float):
        # Map action to nudge outcome: 1=accepted, 0=ignored/none, -1=rejected.
        if action == "accept":
            outcome = 1.0
        elif action == "dismiss":
            outcome = -1.0
        else:
            outcome = 0.0

        self._session_history.append({"action": action, "reward": reward, "outcome": outcome})
        # Keep a bounded session history in memory
        if len(self._session_history) > MAX_SESSION_HISTORY:
            self._session_history.pop(0)