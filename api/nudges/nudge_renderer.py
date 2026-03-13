"""
NudgeRenderer - generates the N1-N4 nudge framing for a recommendation widget.
Nudge types are data-driven; adding a new type requires no model changes (FR-3.6).
"""
from __future__ import annotations

from dataclasses import asdict

from storage.catalogue import Catalogue

# kg CO2e per km driven by average car
# TODO: Should be from some scientific source, but for now we use a reasonable estimate.
CO2E_PER_KM = 0.12


def _co2e_saving_kg(original: dict, substitute: dict) -> float:
    return max(0.0, original.get("co2e", 0.0) - substitute.get("co2e", 0.0))


def _price_saving(original: dict, substitute: dict) -> float:
    return original.get("price", 0.0) - substitute.get("price", 0.0)


NUDGE_BUILDERS = {
    "N1": lambda orig, substitute, _: {
        "type": "N1",
        "headline": "Better for the planet",
        "body": (
            f"Swapping to {substitute['name']} saves "
            f"{_co2e_saving_kg(orig, substitute):.2f} kg CO₂e — equivalent to "
            f"{_co2e_saving_kg(orig, substitute) / CO2E_PER_KM:.1f} km of driving."
        ),
        "icon": "leaf",
    },
    "N2": lambda orig, substitute, _: {
        "type": "N2",
        "headline": "Popular choice",
        "body": f"Most shoppers in your area choose {substitute['name']} over {orig['name']}.",
        "icon": "users",
    },
    "N3": lambda orig, substitute, _: {
        "type": "N3",
        "headline": "Greener and cheaper",
        "body": (
            f"{substitute['name']} costs {abs(_price_saving(orig, substitute)):.2f} kr less "
            f"and produces {_co2e_saving_kg(orig, substitute):.2f} kg less CO₂e."
            if _price_saving(orig, substitute) > 0
            else f"{substitute['name']} is a greener option at a similar price."
        ),
        "icon": "tag",
    },
    "N4": lambda orig, substitute, _: {
        "type": "N4",
        "headline": "Healthier & greener",
        "body": (
            f"{substitute['name']} has a better nutritional profile and "
            f"{_co2e_saving_kg(orig, substitute):.2f} kg lower CO₂e footprint."
        ),
        "icon": "heart",
    },
}


class NudgeRenderer:
    def render(self, recommendation: dict, original_item, catalogue: Catalogue) -> dict | None:
        """
        Build a nudge widget from the model's recommendation.

        `recommendation` is expected to have:
          - substitute_id: ID of the recommended candidate item
          - nudge_type: one of N1–N4
        """
        substitute_id = recommendation.get("substitute_id")
        nudge_type = recommendation.get("nudge_type", "N1")

        if not substitute_id:
            return None

        substitute_obj = catalogue.get_item(substitute_id)
        if substitute_obj is None:
            return None

        # Normalise original / substitute into the dict shape expected by NUDGE_BUILDERS
        def _to_widget_item(obj):
            # Support both dataclass and dict representations
            if isinstance(obj, dict):
                return obj
            d = asdict(obj)
            return {
                "id": d.get("id"),
                "name": d.get("name", "item"),
                "co2e": d.get("co2_kg_per_serving") or d.get("co2_kg_per_kg") or 0.0,
                "price": d.get("price_eur", 0.0),
                "category": d.get("category_id", ""),
            }

        original = _to_widget_item(original_item)
        substitute = _to_widget_item(substitute_obj)

        builder = NUDGE_BUILDERS.get(nudge_type, NUDGE_BUILDERS["N1"])
        widget = builder(original, substitute, catalogue)
        widget["substitute_id"] = substitute["id"]
        widget["substitute_name"] = substitute["name"]
        widget["substitute_co2e"] = substitute.get("co2e", 0.0)
        widget["substitute_price"] = substitute.get("price", 0.0)
        widget["substitute_category"] = substitute.get("category", "")
        return widget