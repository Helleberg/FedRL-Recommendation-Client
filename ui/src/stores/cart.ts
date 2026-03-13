import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CartItem, FoodItem, InteractionAction, NudgeType } from '@/types'
import { getCart, addToCart, removeFromCart, recordInteraction } from '@/api/client'

export const useCartStore = defineStore('cart', () => {
    const items = ref<CartItem[]>([])
    const loading = ref(false)
    const error = ref<string | null>(null)
    const clientId = ref<string>('')

    const totalPrice = computed(() =>
        items.value.reduce((sum: number, i: CartItem) => sum + i.price_eur * i.quantity, 0)
    )
    const totalCo2e = computed(() =>
        items.value.reduce((sum: number, i: CartItem) => sum + i.co2_kg_per_serving * i.quantity, 0)
    )
    const itemCount = computed(() =>
        items.value.reduce((sum: number, i: CartItem) => sum + i.quantity, 0)
    )

    async function fetchCart() {
        loading.value = true
        error.value = null
        try {
            const data = await getCart()
            items.value = data.items
            clientId.value = data.client_id
        } catch (e) {
            error.value = 'Failed to load cart'
            console.error(e)
        } finally {
            loading.value = false
        }
    }

    async function addItem(item: FoodItem, quantity = 1) {
        await addToCart(item.id, quantity)
        await fetchCart()
    }

    async function removeItem(itemId: string) {
        await removeFromCart(itemId)
        await fetchCart()
    }

    async function interact(
        itemId: string,
        substituteId: string,
        nudgeType: NudgeType,
        action: InteractionAction
    ) {
        await recordInteraction({ item_id: itemId, substitute_id: substituteId, nudge_type: nudgeType, action })
        // Refresh cart — accepted swaps will be reflected server-side
        await fetchCart()
    }

    return {
        items, loading, error, clientId,
        totalPrice, totalCo2e, itemCount,
        fetchCart, addItem, removeItem, interact,
    }
})