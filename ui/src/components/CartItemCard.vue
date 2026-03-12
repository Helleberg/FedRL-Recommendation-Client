<script setup lang="ts">
import { ref } from 'vue'
import type { CartItem, InteractionAction } from '@/types'
import RecommendationWidget from './RecommendationWidget.vue'
import { useCartStore } from '@/stores/cart'

const props = defineProps<{ item: CartItem; index: number }>()
const cart = useCartStore()

const interacting = ref(false)
const dismissing = ref(false)
const showRec = ref(true)

async function handleInteract(action: InteractionAction) {
    if (!props.item.recommendation) return
    interacting.value = true
    if (action === 'dismiss') dismissing.value = true

    await cart.interact(
        props.item.id,
        props.item.recommendation.alternative_id,
        props.item.recommendation.type,
        action
    )
    showRec.value = false
    interacting.value = false
    dismissing.value = false
}

async function removeItem() {
    await cart.removeItem(props.item.id)
}

const co2eColor = (score: number) => {
    if (score < 0.33) return '#3a5c3a'
    if (score < 0.66) return '#b85c2a'
    return '#a03020'
}
</script>

<template>
    <div class="cart-card fade-up" :style="{ animationDelay: `${index * 60}ms` }">
        <div class="card-main">
            <div class="item-info">
                <div class="item-category tag">{{ item.category }}</div>
                <div class="item-name">{{ item.name }}</div>
                <div class="item-meta">
                    <span class="co2e" :style="{ color: co2eColor(item.sustainability_score) }">
                        {{ item.co2e.toFixed(2) }} kg CO₂e
                    </span>
                    <span class="separator">·</span>
                    <span>{{ item.price.toFixed(2) }} kr</span>
                </div>
            </div>

            <div class="item-right">
                <div class="qty-pill">× {{ item.quantity }}</div>
                <button class="remove-btn" @click="removeItem" aria-label="Remove">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6" />
                        <path d="M10 11v6M14 11v6" />
                    </svg>
                </button>
            </div>
        </div>

        <Transition name="rec">
            <RecommendationWidget v-if="item.recommendation && showRec" :rec="item.recommendation" :item-id="item.id"
                :dismissing="dismissing" @interact="handleInteract" />
        </Transition>
    </div>
</template>

<style scoped>
.cart-card {
    background: #fff;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem;
    transition: box-shadow 0.2s;
}

.cart-card:hover {
    box-shadow: 0 4px 16px var(--shadow);
}

.card-main {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.75rem;
}

.item-category {
    margin-bottom: 0.3rem;
}

.item-name {
    font-family: 'Fraunces', serif;
    font-size: 1.05rem;
    font-weight: 500;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.item-meta {
    font-size: 0.8rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 0.4rem;
}

.co2e {
    font-weight: 500;
}

.separator {
    opacity: 0.4;
}

.item-right {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.5rem;
    flex-shrink: 0;
}

.qty-pill {
    background: var(--parchment);
    border-radius: 100px;
    padding: 0.2rem 0.65rem;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-muted);
}

.remove-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    padding: 4px;
    border-radius: 6px;
    transition: color 0.15s, background 0.15s;
    display: flex;
}

.remove-btn:hover {
    color: var(--rust);
    background: #fdf0ec;
}

/* Transition for recommendation widget */
.rec-enter-active {
    animation: fadeUp 0.3s ease;
}

.rec-leave-active {
    transition: opacity 0.2s, transform 0.2s;
}

.rec-leave-to {
    opacity: 0;
    transform: translateY(-6px);
}
</style>