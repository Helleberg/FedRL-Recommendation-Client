<template>
    <ViewHeader>
        <template #title>Shopping List</template>
    </ViewHeader>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useRouter } from 'vue-router'
import ViewHeader from '@/components/ViewHeader.vue'

const cart = useCartStore()

// log all cart items
console.log(cart.items)

const router = useRouter()

onMounted(() => cart.fetchCart())
</script>

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