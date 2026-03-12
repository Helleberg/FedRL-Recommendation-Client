<script setup lang="ts">
import type { RecommendationWidget, NudgeType, InteractionAction } from '@/types'

const props = defineProps<{
    rec: RecommendationWidget
    itemId: string
    dismissing: boolean
}>()

const emit = defineEmits<{
    (e: 'interact', action: InteractionAction): void
}>()

const nudgeColors: Record<NudgeType, { bg: string; accent: string; border: string }> = {
    N1: { bg: '#edf5ed', accent: '#3a5c3a', border: '#c2dcc2' },
    N2: { bg: '#eef3f7', accent: '#5b8fa8', border: '#bdd4e0' },
    N3: { bg: '#fdf5ec', accent: '#b85c2a', border: '#e8ceaf' },
    N4: { bg: '#f5eef5', accent: '#7a5c8a', border: '#d4c0dc' },
}

const colors = nudgeColors[props.rec.type]

const iconPaths: Record<string, string> = {
    leaf: 'M12 2a10 10 0 0 1 10 10c0 5.52-4.48 10-10 10S2 17.52 2 12c0-2.76 1.12-5.26 2.93-7.07C6.74 3.12 9.24 2 12 2zm0 2c-1.93 0-3.68.74-5 1.93V12c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z',
    users: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zm14 10v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75',
    tag: 'M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82zM7 7h.01',
    heart: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z',
}
</script>

<template>
    <div class="widget" :style="{ background: colors.bg, borderColor: colors.border }" :class="{ dismissing }">
        <div class="widget-header">
            <span class="widget-icon" :style="{ color: colors.accent }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"
                    stroke-linejoin="round">
                    <path :d="iconPaths[rec.icon]" />
                </svg>
            </span>
            <div class="widget-headline" :style="{ color: colors.accent }">{{ rec.headline }}</div>
            <span class="nudge-badge" :style="{ background: colors.accent }">{{ rec.type }}</span>
        </div>

        <p class="widget-body">{{ rec.body }}</p>

        <div class="widget-alt">
            <div class="alt-info">
                <span class="alt-name">{{ rec.alternative_name }}</span>
                <span class="alt-meta">
                    {{ rec.alternative_co2e.toFixed(2) }} kg CO₂e ·
                    {{ rec.alternative_price.toFixed(2) }} kr
                </span>
            </div>
        </div>

        <div class="widget-actions">
            <button class="btn-accept" @click="emit('interact', 'accept')" :style="{ background: colors.accent }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" width="14" height="14">
                    <polyline points="20 6 9 17 4 12" />
                </svg>
                Swap
            </button>
            <button class="btn-dismiss" @click="emit('interact', 'dismiss')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="13" height="13">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
                Dismiss
            </button>
        </div>
    </div>
</template>

<style scoped>
.widget {
    border: 1.5px solid;
    border-radius: var(--radius);
    padding: 0.9rem;
    margin-top: 0.75rem;
    animation: fadeUp 0.3s ease both;
    transition: opacity 0.25s, transform 0.25s;
}

.widget.dismissing {
    opacity: 0;
    transform: translateX(20px);
}

.widget-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

.widget-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
}

.widget-icon svg {
    width: 100%;
    height: 100%;
}

.widget-headline {
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 0.9rem;
    flex: 1;
}

.nudge-badge {
    font-size: 0.65rem;
    font-weight: 600;
    color: #fff;
    padding: 2px 7px;
    border-radius: 100px;
    letter-spacing: 0.05em;
}

.widget-body {
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.5;
    margin-bottom: 0.75rem;
}

.widget-alt {
    background: rgba(255, 255, 255, 0.6);
    border-radius: 8px;
    padding: 0.5rem 0.75rem;
    margin-bottom: 0.75rem;
}

.alt-info {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
}

.alt-name {
    font-weight: 500;
    font-size: 0.875rem;
}

.alt-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.widget-actions {
    display: flex;
    gap: 0.5rem;
}

.btn-accept,
.btn-dismiss {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    border: none;
    border-radius: 100px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    padding: 0.45rem 0.9rem;
    transition: transform 0.15s, opacity 0.15s;
}

.btn-accept:active,
.btn-dismiss:active {
    transform: scale(0.96);
}

.btn-accept {
    color: #fff;
}

.btn-dismiss {
    background: rgba(255, 255, 255, 0.7);
    color: var(--text-muted);
    border: 1.5px solid var(--border);
}
</style>