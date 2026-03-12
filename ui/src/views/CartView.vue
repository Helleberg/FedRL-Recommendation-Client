<script setup lang="ts">
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import CartItemCard from '@/components/CartItemCard.vue'
import { useRouter } from 'vue-router'

const cart = useCartStore()
const router = useRouter()

onMounted(() => cart.fetchCart())
</script>

<template>
    <div class="cart-view">
        <!-- Header -->
        <header class="view-header">
            <div>
                <h1 class="view-title">Your Cart</h1>
                <p class="view-sub" v-if="cart.clientId">{{ cart.clientId }}</p>
            </div>
            <div class="cart-summary">
                <span class="co2e-total">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" width="14"
                        height="14">
                        <path
                            d="M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12c0-2.76 1.12-5.26 2.93-7.07C6.74 3.12 9.24 2 12 2z" />
                    </svg>
                    {{ cart.totalCo2e.toFixed(2) }} kg CO₂e
                </span>
                <span class="price-total">{{ cart.totalPrice.toFixed(2) }} kr</span>
            </div>
        </header>

        <!-- Loading skeleton -->
        <div v-if="cart.loading" class="skeletons">
            <div v-for="n in 4" :key="n" class="skeleton-card" />
        </div>

        <!-- Error -->
        <div v-else-if="cart.error" class="empty-state error">
            <p>{{ cart.error }}</p>
            <button class="btn btn-primary" @click="cart.fetchCart()">Retry</button>
        </div>

        <!-- Empty cart -->
        <div v-else-if="cart.items.length === 0" class="empty-state">
            <div class="empty-icon">🛒</div>
            <p class="empty-title">Your cart is empty</p>
            <p class="empty-sub">Browse the catalogue to add sustainable foods</p>
            <button class="btn btn-primary" @click="router.push({ name: 'catalogue' })">
                Browse catalogue
            </button>
        </div>

        <!-- Cart items -->
        <div v-else class="item-list">
            <CartItemCard v-for="(item, i) in cart.items" :key="item.id" :item="item" :index="i" />
        </div>

        <!-- Footer: checkout summary bar -->
        <div v-if="cart.items.length > 0" class="checkout-bar">
            <div class="checkout-inner">
                <div class="checkout-line">
                    <span>{{ cart.itemCount }} items</span>
                    <span class="checkout-price">{{ cart.totalPrice.toFixed(2) }} kr</span>
                </div>
                <button class="btn btn-primary checkout-btn">Checkout</button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.cart-view {
    padding-bottom: 1rem;
}

.view-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1.5px solid var(--border);
}

.view-title {
    font-family: 'Fraunces', serif;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.view-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

.cart-summary {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.2rem;
}

.co2e-total {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.8rem;
    color: var(--moss);
    font-weight: 500;
}

.price-total {
    font-size: 1rem;
    font-weight: 600;
    color: var(--bark);
}

.item-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

/* Skeletons */
.skeletons {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.skeleton-card {
    height: 100px;
    background: linear-gradient(90deg, var(--parchment) 25%, #ede5d4 50%, var(--parchment) 75%);
    background-size: 200% 100%;
    border-radius: var(--radius-lg);
    animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
    to {
        background-position: -200% 0;
    }
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

.empty-icon {
    font-size: 2.5rem;
}

.empty-title {
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
    font-weight: 500;
}

.empty-sub {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.error {
    color: var(--rust);
}

/* Checkout bar */
.checkout-bar {
    position: fixed;
    bottom: 64px;
    left: 0;
    right: 0;
    padding: 0 1rem;
    z-index: 50;
    pointer-events: none;
}

.checkout-inner {
    max-width: 480px;
    margin: 0 auto;
    background: var(--bark);
    color: #fff;
    border-radius: var(--radius-lg);
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    pointer-events: all;
    box-shadow: 0 8px 24px rgba(61, 43, 31, 0.25);
}

.checkout-line {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    font-size: 0.8rem;
    opacity: 0.85;
}

.checkout-price {
    font-size: 1.1rem;
    font-weight: 600;
    opacity: 1;
    color: var(--wheat);
}

.checkout-btn {
    background: var(--wheat);
    color: var(--bark);
    font-weight: 600;
    flex-shrink: 0;
}

.checkout-btn:hover {
    background: #dbb97e;
}
</style>