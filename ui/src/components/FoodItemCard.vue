<template>
  <article
    class="food-card"
    role="button"
    tabindex="0"
    @click="handleCardClick"
    @keydown.enter="handleCardClick"
  >
    <!-- LEFT: IMAGE -->
    <div class="food-card__image">
      <img
        :src=placeholderImage
        :alt="item.name"
      />
    </div>

    <!-- MIDDLE: INFO -->
    <div class="food-card__info">
      <h3 class="food-card__title">
        {{ item.name }}
      </h3>
      
      <div class="food-card__group">
        <span class="food-card__price">
          €{{ item.price_eur.toFixed(2) }}
        </span>
        <span class="food-card__unit">
          {{ item.serving_size_g }} g
        </span>
        <span v-if="mode === 'remove' && item.quantity" class="food-card__quantity">
          × {{ item.quantity }}
        </span>
      </div>

      <span class="food-card__co2" :class="co2Class">
        {{ item.co2_kg_per_serving.toFixed(2) }} kg CO₂e
      </span>
    </div>

    <!-- RIGHT: ACTION BUTTON -->
    <div class="food-card__actions">
      <button
        class="action-button"
        :class="mode === 'add' ? 'btn-green' : 'btn-red'"
        @click.stop="mode === 'add' ? handleAddToCart() : handleRemoveFromCart()"
        :disabled="buttonDisabled"
        :aria-label="buttonAriaLabel"
      >
        {{ buttonLabel }}
      </button>
    </div>
  </article>
</template>

<script setup lang="ts">
import type { FoodItem } from "@/types"
import placeholderImage from "@/assets/images/food_placeholder.png"
import { computed } from "vue";

const props = defineProps<{
  item: FoodItem & { quantity?: number }
  mode: 'add' | 'remove'
  isAdding?: boolean
  isRemoving?: boolean
}>()

const emit = defineEmits<{
  (e: "add-to-cart", item: FoodItem): void
  (e: "remove-from-cart", itemId: string): void
  (e: "view-details", item: FoodItem): void
}>()

function handleAddToCart() {
  if (props.isAdding) return
  emit("add-to-cart", props.item)
}

function handleRemoveFromCart() {
  if (props.isRemoving) return
  emit("remove-from-cart", props.item.id)
}

function handleCardClick() {
  emit("view-details", props.item)
}

const buttonLabel = computed(() => {
  if (props.mode === 'add') {
    if (props.isAdding) return "…"
    return "+"
  } else {
    if (props.isRemoving) return "Removing…"
    return "-"
  }
})

const buttonDisabled = computed(() => {
  return (props.mode === 'add' && props.isAdding) || (props.mode === 'remove' && props.isRemoving)
})

const buttonAriaLabel = computed(() => {
  if (props.mode === 'add') return props.isAdding ? 'Adding' : 'Add to cart'
  return props.isRemoving ? 'Removing' : 'Remove from cart'
})

const co2Class = computed(() => {
  const co2 = props.item.co2_kg_per_serving

  if (co2 <= 0.8) return "co2-green"
  if (co2 <= 2.5) return "co2-yellow"
  return "co2-red"
})
</script>

<style scoped>
.food-card {
  display: grid;
  grid-template-columns: 90px 1fr 40px;
  align-items: center;
  gap: 14px;

  padding: 10px 12px;
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border-radius: 12px;
  box-shadow: 0px 8px 6px rgba(3, 7, 18, 0.04),
  0px 32px 24px rgba(3, 7, 18, 0.08);

  cursor: pointer;
  margin-bottom: 8px;
}

.food-card:hover {
  box-shadow: 0 3px 10px rgba(0,0,0,0.06);
}

.food-card__image img {
  max-width: 80px;
  object-fit: cover;
  border-radius: 6px;
}

.food-card__info {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.food-card__title {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 500;
}

.food-card__group {
  display: flex;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 4px;
}

.food-card__unit {
  font-size: 0.85rem;
  color: #666;
}

.food-card__quantity {
  font-size: 0.85rem;
  color: #666;
  margin-left: 8px;
}

.food-card__price {
  font-weight: 600;
}

.food-card__co2 {
  font-size: 0.85rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 999px;
  width: fit-content;
}

/* Low emissions */
.co2-green {
  background: #cff1dc;
  color: #1f7a3f;
}

/* Medium emissions */
.co2-yellow {
  background: #f6eacd;
  color: #b7791f;
}

/* High emissions */
.co2-red {
  background: #fde8e8;
  color: #c53030;
}

.food-card__actions {
  display: flex;
  justify-content: center;
}

.action-button {
  min-width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;

  border-radius: 14px;
  border: none;

  background: #5d9ad7;
  color: white;
  font-size: 14px;
  line-height: 1;

  cursor: pointer;
}

.btn-red {
  background: #e53e3e;
}

.btn-green {
  background: var(--blue);
}

.action-button:hover {
  background: #356595;
}
</style>