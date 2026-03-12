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
        items.value.reduce((sum, i) => sum + i.price * i.quantity, 0)
    )
    const totalCo2e = computed(() =>
        items.value.reduce((sum, i) => sum + i.co2e * i.quantity, 0)
    )
    const itemCount = computed(() =>
        items.value.reduce((sum, i) => sum + i.quantity, 0)
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

    async function addItem(item: FoodItem) {
        await addToCart(item.id)
        await fetchCart()
    }

    async function removeItem(itemId: string) {
        await removeFromCart(itemId)
        await fetchCart()
    }

    async function interact(
        itemId: string,
        alternativeId: string,
        nudgeType: NudgeType,
        action: InteractionAction
    ) {
        await recordInteraction({ item_id: itemId, alternative_id: alternativeId, nudge_type: nudgeType, action })
        // Refresh cart — accepted swaps will be reflected server-side
        await fetchCart()
    }

    return {
        items, loading, error, clientId,
        totalPrice, totalCo2e, itemCount,
        fetchCart, addItem, removeItem, interact,
    }
})