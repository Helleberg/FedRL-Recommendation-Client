import axios from 'axios'
import type {
    CartResponse,
    CatalogueResponse,
    HealthResponse,
    StatsResponse,
    InteractionPayload,
    Recommendation,
} from '@/types'

const api = axios.create({
    // In Docker: Nginx proxies /api/ → FastAPI container on internal network.
    // In local dev: set VITE_API_URL=http://localhost:8000 in your .env file.
    baseURL: import.meta.env.VITE_API_URL || '/api',
    timeout: 10_000,
    headers: { 'Content-Type': 'application/json' },
})

export const getHealth = (): Promise<HealthResponse> =>
    api.get<HealthResponse>('/health').then(r => r.data)

export const getCart = (): Promise<CartResponse> =>
    api.get<CartResponse>('/cart').then(r => r.data)

export const addToCart = (item_id: string, quantity = 1) =>
    api.post('/cart/add', { item_id, quantity }).then(r => r.data)

export const removeFromCart = (item_id: string) =>
    api.delete(`/cart/${item_id}`).then(r => r.data)

export const getCatalogue = (categoryId?: string): Promise<CatalogueResponse> => {
    const params = categoryId ? { category_id: categoryId } : {}
    return api.get<CatalogueResponse>('/catalogue', { params }).then(r => r.data)
}

export const getCategories = (): Promise<{ categories: string[] }> =>
    api.get('/catalogue/categories').then(r => r.data)

export const recordInteraction = (payload: InteractionPayload) =>
    api.post('/interact', payload).then(r => r.data)

export const getStats = (): Promise<StatsResponse> =>
    api.get<StatsResponse>('/stats').then(r => r.data)

export const checkRecommendation = (item_uuid: string): Promise<Recommendation | null> =>
    api.get<Recommendation | null>(`/recommendation/${item_uuid}`).then(r => r.data)