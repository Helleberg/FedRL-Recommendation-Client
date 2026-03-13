<template>
    <ViewHeader>
        <template #title>Shopping List</template>
        <template #subtitle>{{ cart.itemCount }} items · €{{ cart.totalPrice.toFixed(2) }}</template>
    </ViewHeader>

    <section class="cart-view">
        <div v-if="cart.error" class="error">
            {{ cart.error }}
        </div>

        <div v-else-if="cartItems.length === 0" class="empty-state">
            <div class="empty-title">Your cart is empty</div>
            <div class="empty-sub">
                Add items from the catalogue to start building your shopping list.
            </div>
            <div>
                <button class="cart-button" @click="$router.push({ name: 'catalogue' })">
                    Browse catalogue
                </button>
            </div>
        </div>

        <div v-else class="item-list">
            <FoodItemCard
                v-for="item in cartItems"
                :key="item.id"
                :item="item"
                mode="remove"
                :is-removing="removingId === item.id"
                @remove-from-cart="remove"
                @view-details="handleViewDetails"
            />

            <!-- Add more items -->
            <div class="add-items">
                <button class="add-more" @click="$router.push({ name: 'catalogue' })">
                    <span class="plus-icon">+</span>
                    Add items
                </button>
            </div>
        </div>
    </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'
import FoodItemCard from '@/components/FoodItemCard.vue'
import type { CartItem, FoodItem } from '@/types'
import ViewHeader from '@/components/ViewHeader.vue'

const cart = useCartStore()
const cartItems = computed<CartItem[]>(() => cart.items)
const router = useRouter()
const removingId = ref<string | null>(null)

async function remove(itemId: string) {
    if (removingId.value) return

    removingId.value = itemId
    try {
        await cart.removeItem(itemId)
    } finally {
        removingId.value = null
    }
}

function onCheckout() {
    // Placeholder: extend with real checkout flow.
    router.push({ name: 'home' })
}

function handleViewDetails(item: FoodItem & { quantity?: number }) {
    // For now, do nothing or perhaps open drawer if needed
    console.log('View details for', item)
}

onMounted(() => {
    cart.fetchCart()
})
</script>

<style scoped>
.item-list {
    margin-top: 1rem;
}

/* Empty state */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 3rem 1rem;
    gap: 0.75rem;
}

.empty-title {
    font-size: 1.4rem;
    font-weight: 500;
}

.empty-sub {
    color: var(--text-muted);
    font-size: 1rem;
    margin-bottom: 1rem;
}

.error {
    color: var(--rust);
}

.cart-button {
    background: var(--blue);
    color: #ffffff;
    padding: 0.75rem 2.5rem;
    border: none;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
}

/* Add items button */
.add-items {
    padding: 1rem;
    text-align: center;
}

.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: var(--radius-lg);
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s;
}

.btn-primary {
    background: var(--bark);
    color: var(--wheat);
}

.btn-primary:hover {
    background: #3d2b1f;
}

.plus-icon {
    font-size: 1.2rem;
}

.add-items {
    display: flex;
    justify-content: center;
}

.add-more {
    margin-top: 1rem;
    background: none;
    border: none;
    text-decoration: none;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    font-size: 1rem;
    font-weight: 600;
}

.add-more > span {
    display: inline-flex;
    align-items: center;
    color: white;
    justify-content: center;
    background: var(--blue);
    width: 32px;
    height: 32px;
    border-radius: 50px;
}
</style>