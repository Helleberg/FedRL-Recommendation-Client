from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class FoodCategory:
    id: int
    code: str
    name: str

@dataclass
class FoodItem:
    id: str
    external_code: str
    name: str
    category_id: int
    market: str
    brand: str | None
    price_eur: float
    serving_size_g: float
    co2_kg_per_kg: float
    co2_kg_per_serving: float
    is_meat: bool
    is_dairy: bool
    is_plant_based: bool
    is_vegan: bool
    is_vegetarian: bool
    is_gluten_free: bool
    allergens: list[str] = field(default_factory=list)
    # Nutritional fields — optional, only needed for N4 nudge framing
    calories_kcal: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    carbs_g: float | None = None
    fiber_g: float | None = None
    sugar_g: float | None = None
    processing_level: int | None = None
    created_at: str | None = None

@dataclass
class SubstitutionGroup:
    id: int
    code: str
    name: str
    items: list[str]
    description: str | None = None

@dataclass
class FoodItemSubstitutionGroup:
    food_item_id: str
    substitution_group_id: int
    group_priority: int = 1