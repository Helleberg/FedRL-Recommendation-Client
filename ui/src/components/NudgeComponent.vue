<template>
  <section class="nudge-card">
    <div class="nudge-header">
      <div class="nudge-icon">
        <span class="icon" :class="iconClass">{{ iconSymbol }}</span>
      </div>
      <h4 class="nudge-headline">{{ recommendation.headline }}</h4>
    </div>

    <p class="nudge-body">{{ recommendation.body }}</p>

    <div class="nudge-alternative">
      <div class="alternative-info">
        <span class="alternative-name">{{ recommendation.substitute_name }}</span>
        <span class="alternative-price">€{{ recommendation.substitute_price }}</span>
      </div>
      <span class="alternative-co2">{{ recommendation.substitute_co2e }} kg CO₂e</span>
    </div>

    <div class="nudge-actions">
      <button
        type="button"
        class="nudge-button nudge-button--reject"
        @click="handleReject"
      >
        No thanks
      </button>
      <button
        type="button"
        class="nudge-button nudge-button--accept"
        @click="handleAccept"
      >
        Swap to {{ recommendation.substitute_name }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Recommendation } from '@/types'
import { recordInteraction } from '@/api/client'

const props = defineProps<{
  recommendation: Recommendation
  itemId: string
}>()

const emit = defineEmits<{
  (e: 'accept', substituteId: string): void
  (e: 'reject'): void
}>()

const iconClass = computed(() => {
  switch (props.recommendation.icon) {
    case 'leaf':
      return 'icon-leaf'
    default:
      return 'icon-default'
  }
})

const iconSymbol = computed(() => {
  switch (props.recommendation.icon) {
    case 'leaf':
      return '🌿'
    default:
      return '💡'
  }
})

async function handleAccept() {
  await recordInteraction({
    item_id: props.itemId,
    substitute_id: props.recommendation.substitute_id,
    nudge_type: props.recommendation.type,
    action: 'accept'
  })
  emit('accept', props.recommendation.substitute_id)
}

async function handleReject() {
  await recordInteraction({
    item_id: props.itemId,
    substitute_id: props.recommendation.substitute_id,
    nudge_type: props.recommendation.type,
    action: 'dismiss'
  })
  emit('reject')
}
</script>

<style scoped>
.nudge-card {
  background: #f0f9f0;
  border: 1px solid #d4edda;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
}

.nudge-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.nudge-icon .icon {
  font-size: 20px;
}

.nudge-headline {
  font-size: 16px;
  font-weight: 600;
  color: #155724;
  margin: 0;
}

.nudge-body {
  font-size: 14px;
  color: #155724;
  margin: 8px 0;
  line-height: 1.4;
}

.nudge-alternative {
  background: white;
  border-radius: 6px;
  padding: 12px;
  margin: 12px 0;
  border: 1px solid #c3e6cb;
}

.alternative-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.alternative-name {
  font-weight: 600;
  color: #155724;
}

.alternative-price {
  color: #28a745;
  font-weight: 600;
}

.alternative-co2 {
  font-size: 12px;
  color: #6c757d;
}

.nudge-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.nudge-button {
  flex: 1;
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.nudge-button--reject {
  background: #6c757d;
  color: white;
}

.nudge-button--reject:hover {
  background: #5a6268;
}

.nudge-button--accept {
  background: #28a745;
  color: white;
}

.nudge-button--accept:hover {
  background: #218838;
}
</style>