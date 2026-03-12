<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import type { StatsResponse, HealthResponse } from '@/types'
import { getStats, getHealth } from '@/api/client'

const stats = ref<StatsResponse | null>(null)
const health = ref<HealthResponse | null>(null)
const loading = ref(true)
let interval: ReturnType<typeof setInterval>

async function load() {
    try {
        const [s, h] = await Promise.all([getStats(), getHealth()])
        stats.value = s
        health.value = h
    } finally {
        loading.value = false
    }
}

function formatTime(ts: number | null): string {
    if (!ts) return 'Never'
    return new Date(ts * 1000).toLocaleTimeString()
}

onMounted(() => {
    load()
    interval = setInterval(load, 5000)
})
onUnmounted(() => clearInterval(interval))
</script>

<template>
    <div class="stats-view">
        <header class="view-header">
            <h1 class="view-title">Status</h1>
            <span class="live-dot" title="Live data" />
        </header>

        <div v-if="loading" class="skeletons">
            <div v-for="n in 4" :key="n" class="skeleton-block" />
        </div>

        <div v-else class="stats-grid">
            <!-- Health card -->
            <div class="stat-card accent-green" v-if="health">
                <div class="stat-label">Client</div>
                <div class="stat-value mono">{{ health.client_id }}</div>
                <div class="stat-sub">{{ health.algorithm }}</div>
            </div>

            <div class="stat-card" v-if="health">
                <div class="stat-label">Catalogue</div>
                <div class="stat-value">{{ health.catalogue_size }}</div>
                <div class="stat-sub">items · v{{ health.catalogue_version }}</div>
            </div>

            <div class="stat-card" v-if="stats">
                <div class="stat-label">Total interactions</div>
                <div class="stat-value">{{ stats.interactions_total }}</div>
            </div>

            <div class="stat-card" v-if="stats">
                <div class="stat-label">Since last sync</div>
                <div class="stat-value">{{ stats.interactions_since_sync }}</div>
                <div class="stat-sub">interactions queued</div>
            </div>

            <div class="stat-card wide" v-if="stats">
                <div class="stat-label">Last sync</div>
                <div class="stat-value">{{ formatTime(stats.last_sync) }}</div>
            </div>

            <div class="stat-card wide" v-if="stats">
                <div class="stat-label">Backbone version</div>
                <div class="stat-value mono">{{ stats.backbone_version }}</div>
            </div>

            <!-- Status -->
            <div class="stat-card wide accent-green" v-if="health">
                <div class="status-row">
                    <span class="status-dot" />
                    <span class="stat-value">{{ health.status }}</span>
                </div>
                <div class="stat-sub">API reachable</div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.stats-view {
    padding-bottom: 1rem;
}

.view-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.view-title {
    font-family: 'Fraunces', serif;
    font-size: 1.75rem;
    font-weight: 700;
}

.live-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--sage);
    animation: pulse-soft 2s infinite;
}

.stats-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.stat-card {
    background: #fff;
    border: 1.5px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
    animation: fadeUp 0.35s ease both;
}

.stat-card.wide {
    grid-column: span 2;
}

.stat-card.accent-green {
    border-color: #c2dcc2;
    background: #edf5ed;
}

.stat-label {
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

.stat-value {
    font-family: 'Fraunces', serif;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--bark);
    line-height: 1;
}

.stat-value.mono {
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 1rem;
}

.stat-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.status-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--moss);
    animation: pulse-soft 2s infinite;
}

/* Skeletons */
.skeletons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}

.skeleton-block {
    height: 90px;
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