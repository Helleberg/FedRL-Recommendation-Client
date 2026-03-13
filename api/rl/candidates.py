from __future__ import annotations

"""
Candidate generation and filtering logic.

This module provides a `CandidateGenerator` that:
- starts from catalogue-derived substitutes for an original item
- applies a series of hard filters (eligibility)
- scores remaining candidates with a simple similarity heuristic
- returns candidates sorted by descending similarity score.

Rules can be tightened/loosened or the scoring can be changed.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, List, Tuple

if TYPE_CHECKING:
    from storage.catalogue import Catalogue
    from storage.models import FoodItem


class CandidateGenerator:
    def __init__(self, catalogue: "Catalogue"):
        self.catalogue = catalogue

    def generate(self, original_id: str) -> List[Tuple[str, float]]:
        """
        Generate a ranked list of candidate items for `original_id`.

        Current strategy:
        - Start from substitution groups for the original item
        - Hard filters:
          - Same market
          - Same or compatible category
        """
        original = self.catalogue.get_item(original_id)
        if original is None:
            return []

        raw_candidates = self.catalogue.get_substitutes(original_id)
        out: List[Tuple[str, float]] = []

        for cand in raw_candidates:
            if cand.id == original.id:
                continue

            if not self._passes_hard_filters(original, cand):
                continue

            score = self._similarity_score(original, cand)
            out.append((cand.id, score))

        return out

    # internal helpers
    def _passes_hard_filters(self, original: "FoodItem", candidate: "FoodItem") -> bool:
        """Apply strict eligibility filters for candidates."""

        # 1) Reject if candidate is >= 50% more expensive than original
        o_price = float(getattr(original, "price_eur", 0.0) or 0.0)
        c_price = float(getattr(candidate, "price_eur", 0.0) or 0.0)
        if o_price > 0.0 and c_price >= 1.5 * o_price:
            return False

        # 2) Reject if candidate CO2e is not at least 10% better (lower) than original
        o_co2 = float(getattr(original, "co2_kg_per_kg", 0.0) or 0.0)
        c_co2 = float(getattr(candidate, "co2_kg_per_kg", 0.0) or 0.0)
        if o_co2 > 0.0:
            # Require candidate <= 90% of original CO2e
            if c_co2 >= 0.9 * o_co2:
                return False

        return True

    def _similarity_score(self, original: "FoodItem", candidate: "FoodItem") -> float:
        """
        Heuristic similarity:
        - base score from CO2 reduction (more reduction is better)
        - penalise large price deltas
        - reward similar calories and protein
        """
        o_co2 = float(getattr(original, "co2_kg_per_kg", 0.0) or 0.0)
        c_co2 = float(getattr(candidate, "co2_kg_per_kg", 0.0) or 0.0)
        o_price = float(getattr(original, "price_eur", 0.0) or 0.0)
        c_price = float(getattr(candidate, "price_eur", 0.0) or 0.0)
        o_cal = float(getattr(original, "calories_kcal", 0.0) or 0.0)
        c_cal = float(getattr(candidate, "calories_kcal", 0.0) or 0.0)
        o_prot = float(getattr(original, "protein_g", 0.0) or 0.0)
        c_prot = float(getattr(candidate, "protein_g", 0.0) or 0.0)

        co2_reduction = max(0.0, o_co2 - c_co2)
        price_delta = abs(c_price - o_price)
        cal_diff = abs(c_cal - o_cal)
        prot_diff = abs(c_prot - o_prot)

        score = 0.0
        score += 1.0 * co2_reduction
        score -= 0.1 * price_delta
        score -= 0.01 * cal_diff
        score -= 0.05 * prot_diff

        return score

