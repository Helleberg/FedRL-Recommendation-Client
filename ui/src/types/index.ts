export type NudgeType = 'N1' | 'N2' | 'N3' | 'N4'
export type InteractionAction = 'accept' | 'dismiss' | 'ignore'
export type NudgeIcon = 'leaf' | 'users' | 'tag' | 'heart'

export interface FoodItem {
    id: string
    name: string
    category: string
    quantity: number
    price: number
    co2e: number
    sustainability_score: number
    alternatives?: string[]
}

export interface RecommendationWidget {
    type: NudgeType
    headline: string
    body: string
    icon: NudgeIcon
    alternative_id: string
    alternative_name: string
    alternative_co2e: number
    alternative_price: number
    alternative_category: string
}

export interface CartItem extends FoodItem {
    recommendation: RecommendationWidget | null
}

export interface CartResponse {
    items: CartItem[]
    client_id: string
}

export interface CatalogueResponse {
    items: FoodItem[]
    version: string
}

export interface HealthResponse {
    status: string
    client_id: string
    algorithm: string
    catalogue_version: string
    catalogue_size: number
}

export interface StatsResponse {
    interactions_total: number
    interactions_since_sync: number
    last_sync: number | null
    backbone_version: string
}

export interface InteractionPayload {
    item_id: string
    alternative_id: string
    nudge_type: NudgeType
    action: InteractionAction
}