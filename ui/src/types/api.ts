export type HealthResponse = {
  status: string
  client_id: string
  algorithm: string
  catalogue_version: string
  catalogue_size: number
}

export type StatsResponse = {
  interactions_total: number
  interactions_since_sync: number
  last_sync: number | null
  backbone_version: string
}

export type CatalogueResponse = {
  items: FoodItem[]
  version: string
}

export type CartItem = FoodItem & {
  quantity: number
  recommendation?: unknown
}

export type CartResponse = {
  items: CartItem[]
  client_id: string
}

export type InteractionPayload = {
  item_id: string
  substitute_id: string
  nudge_type: string
  action: InteractionAction
}

export type InteractionAction = 'accept' | 'dismiss' | 'ignore'

export type NudgeType = 'N1' | 'N2' | 'N3' | 'N4' | string

export type Recommendation = {
  type: NudgeType
  headline: string
  body: string
  icon: string
  substitute_id: string
  substitute_name: string
  substitute_co2e: number
  substitute_price: number
  substitute_category: number
}

// Re-export shared types
import type { FoodItem } from './FoodItem'
export type { FoodItem }
