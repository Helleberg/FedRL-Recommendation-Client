export type FoodItem = {
  id: string
  external_code: string
  name: string
  category_id: number

  market?: string | null
  brand?: string | null

  price_eur: number
  serving_size_g: number

  co2_kg_per_kg: number
  co2_kg_per_serving: number

  calories_kcal?: number | null
  protein_g?: number | null
  fat_g?: number | null
  carbs_g?: number | null
  fiber_g?: number | null
  sugar_g?: number | null

  is_meat: boolean
  is_dairy: boolean
  is_plant_based: boolean
  is_vegan: boolean
  is_vegetarian: boolean
  is_gluten_free: boolean

  allergens: string[]
}