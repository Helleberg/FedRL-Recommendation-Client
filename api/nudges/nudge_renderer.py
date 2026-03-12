"""
NudgeRenderer - generates the N1-N4 nudge framing for a recommendation widget.
Nudge types are data-driven; adding a new type requires no model changes (FR-3.6).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from storage.catalogue import Catalogue

# kg CO2e per km driven by average car
# TODO: Should be from some scientific source, but for now we use a reasonable estimate.
CO2E_PER_KM = 0.12


def _co2e_saving_kg(original: dict, alternative: dict) -> float:
    return max(0.0, original.get("co2e", 0.0) - alternative.get("co2e", 0.0))


def _price_saving(original: dict, alternative: dict) -> float:
    return original.get("price", 0.0) - alternative.get("price", 0.0)


NUDGE_BUILDERS = {
    "N1": lambda orig, alt, _: {
        "type": "N1",
        "headline": "Better for the planet",
        "body": (
            f"Swapping to {alt['name']} saves "
            f"{_co2e_saving_kg(orig, alt):.2f} kg CO₂e — equivalent to "
            f"{_co2e_saving_kg(orig, alt) / CO2E_PER_KM:.1f} km of driving."
        ),
        "icon": "leaf",
    },
    "N2": lambda orig, alt, _: {
        "type": "N2",
        "headline": "Popular choice",
        "body": f"Most shoppers in your area choose {alt['name']} over {orig['name']}.",
        "icon": "users",
    },
    "N3": lambda orig, alt, _: {
        "type": "N3",
        "headline": "Greener and cheaper",
        "body": (
            f"{alt['name']} costs {abs(_price_saving(orig, alt)):.2f} kr less "
            f"and produces {_co2e_saving_kg(orig, alt):.2f} kg less CO₂e."
            if _price_saving(orig, alt) > 0
            else f"{alt['name']} is a greener option at a similar price."
        ),
        "icon": "tag",
    },
    "N4": lambda orig, alt, _: {
        "type": "N4",
        "headline": "Healthier & greener",
        "body": (
            f"{alt['name']} has a better nutritional profile and "
            f"{_co2e_saving_kg(orig, alt):.2f} kg lower CO₂e footprint."
        ),
        "icon": "heart",
    },
}


class NudgeRenderer:
    def render(self, recommendation: dict, catalogue: "Catalogue") -> dict | None:
        alt = recommendation.get("alternative")
        nudge_type = recommendation.get("nudge_type", "N1")

        if not alt:
            return None

        # Find the original item from the cart context — best effort
        original = catalogue.get_item(alt.get("replaces_id", "")) or {
            "name": "current item",
            "co2e": alt.get("co2e", 0.0) + 1.0,
            "price": alt.get("price", 0.0),
        }

        builder = NUDGE_BUILDERS.get(nudge_type, NUDGE_BUILDERS["N1"])
        widget = builder(original, alt, catalogue)
        widget["alternative_id"] = alt["id"]
        widget["alternative_name"] = alt["name"]
        widget["alternative_co2e"] = alt.get("co2e", 0.0)
        widget["alternative_price"] = alt.get("price", 0.0)
        widget["alternative_category"] = alt.get("category", "")
        return widget