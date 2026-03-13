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

export type CartItem = {
  id: string
  name: string
  category: string
  quantity: number
  price: number
  co2e: number
  sustainability_score: number
  recommendation?: unknown
}

export type CartResponse = {
  items: CartItem[]
  client_id: string
}

export type InteractionPayload = {
  item_id: string
  alternative_id: string
  nudge_type: string
  action: InteractionAction
}

export type InteractionAction = 'accept' | 'dismiss' | 'ignore'

export type NudgeType = 'N1' | 'N2' | 'N3' | 'N4' | string

// Re-export shared types
import type { FoodItem } from './FoodItem'
export type { FoodItem }
