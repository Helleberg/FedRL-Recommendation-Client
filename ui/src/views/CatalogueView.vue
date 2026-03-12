<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCatalogueStore } from '@/stores/catalogue'
import { useCartStore } from '@/stores/cart'
import type { FoodItem } from '@/types'

const catalogue = useCatalogueStore()
const cart = useCartStore()
const addingId = ref<string | null>(null)
const addedId = ref<string | null>(null)

onMounted(async () => {
    await catalogue.fetchCategories()
    await catalogue.fetchCatalogue()
})

async function addItem(item: FoodItem) {
    addingId.value = item.id
    await cart.addItem(item)
    addingId.value = null
    addedId.value = item.id
    setTimeout(() => { addedId.value = null }, 1500)
}

const sustainColor = (score: number) => {
    if (score > 0.66) return '#3a5c3a'
    if (score > 0.33) return '#b85c2a'
    return '#a03020'
}
</script>

<template>
    <div class="catalogue-view">
        <header class="view-header">
            <h1 class="view-title">Browse</h1>
            <span class="version-tag tag">v{{ catalogue.version }}</span>
        </header>

        <!-- Category filter chips -->
        <div class="category-scroll">
            <button class="chip" :class="{ active: catalogue.activeCategory === null }"
                @click="catalogue.setCategory(null)">All</button>
            <button v-for="cat in catalogue.categories" :key="cat" class="chip"
                :class="{ active: catalogue.activeCategory === cat }" @click="catalogue.setCategory(cat)">{{ cat
                }}</button>
        </div>

        <!-- Loading -->
        <div v-if="catalogue.loading" class="skeletons">
            <div v-for="n in 6" :key="n" class="skeleton-row" />
        </div>

        <!-- Grid -->
        <div v-else class="item-grid">
            <div v-for="(item, i) in catalogue.items" :key="item.id" class="item-tile fade-up"
                :style="{ animationDelay: `${i * 30}ms` }">
                <div class="tile-top">
                    <span class="tile-category tag">{{ item.category }}</span>
                    <span class="sust-dot" :style="{ background: sustainColor(item.sustainability_score) }"
                        :title="`Sustainability: ${(item.sustainability_score * 100).toFixed(0)}%`" />
                </div>
                <div class="tile-name">{{ item.name }}</div>
                <div class="tile-meta">
                    <span :style="{ color: sustainColor(item.sustainability_score) }">
                        {{ item.co2e.toFixed(2) }} kg CO₂e
                    </span>
                    <span>{{ item.price.toFixed(2) }} kr</span>
                </div>
                <button class="tile-add-btn" :class="{ added: addedId === item.id }" :disabled="addingId === item.id"
                    @click="addItem(item)">
                    <template v-if="addedId === item.id">✓ Added</template>
                    <template v-else-if="addingId === item.id">…</template>
                    <template v-else>+ Add</template>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.catalogue-view {
    padding-bottom: 1rem;
}

.view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.25rem;
}

.view-title {
    font-family: 'Fraunces', serif;
    font-size: 1.75rem;
    font-weight: 700;
}

.version-tag {
    font-size: 0.7rem;
    color: var(--text-muted);
}

/* Category chips */
.category-scroll {
    display: flex;
    gap: 0.5rem;
    overflow-x: auto;
    padding-bottom: 0.75rem;
    margin-bottom: 1rem;
    scrollbar-width: none;
}

.category-scroll::-webkit-scrollbar {
    display: none;
}

.chip {
    flex-shrink: 0;
    padding: 0.35rem 0.9rem;
    border-radius: 100px;
    border: 1.5px solid var(--border);
    background: #fff;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    color: var(--text-muted);
    transition: background 0.15s, color 0.15s, border-color 0.15s;
}

.chip.active {
    background: var(--moss);
    color: #fff;
    border-color: var(--moss);
}

/* Grid */
.item-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.item-tile {
    background: #fff;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 0.9rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    transition: box-shadow 0.2s;
}

.item-tile:hover {
    box-shadow: 0 4px 14px var(--shadow);
}

.tile-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.tile-category {
    font-size: 0.68rem;
}

.sust-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.tile-name {
    font-family: 'Fraunces', serif;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.25;
}

.tile-meta {
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: auto;
}

.tile-add-btn {
    margin-top: 0.65rem;
    width: 100%;
    padding: 0.5rem;
    border-radius: 8px;
    border: 1.5px solid var(--moss);
    background: transparent;
    color: var(--moss);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
}

.tile-add-btn:hover {
    background: var(--moss);
    color: #fff;
}

.tile-add-btn.added {
    background: var(--moss);
    color: #fff;
    border-color: var(--moss);
}

.tile-add-btn:disabled {
    opacity: 0.6;
    cursor: default;
}

/* Skeletons */
.skeletons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.skeleton-row {
    height: 130px;
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
</style>