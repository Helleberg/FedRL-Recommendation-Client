<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="drawer-overlay"
      :class="{ 'drawer-overlay--visible': isVisible }"
      @click="startClose"
    >
      <section
        ref="drawerRef"
        class="drawer-sheet"
        :class="{
          'drawer-sheet--visible': isVisible,
          'drawer-sheet--dragging': isDragging
        }"
        :style="drawerStyle"
        @click.stop
      >
        <div
          class="drawer-drag-area"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        >
          <div class="drawer-handle-wrap">
            <div class="drawer-handle" />
          </div>

          <!--<div class="drawer-header">
            <h2 class="drawer-title">Item details</h2>

            <button
              type="button"
              class="drawer-close"
              @click="startClose"
              aria-label="Close item details"
            >
              ×
            </button>
          </div>-->
        </div>

        <div v-if="item" class="drawer-content">
          <!-- Card 1: image -->
          <section class="content-card image-card">
            <img
              class="item-image"
              :src="placeholderImage"
              :alt="item.name"
            />
          </section>

          <!-- Card 2: main item info -->
          <section class="content-card info-card">
            <div class="info-row info-row--top">
              <h3 class="item-name">{{ item.name }}</h3>
              <span class="item-unit">{{ item.serving_size_g }} g</span>
            </div>

            <div class="info-row info-row--middle">
              <div class="quantity-control">
                <button
                  type="button"
                  class="quantity-button"
                  @click="decreaseQuantity"
                  aria-label="Decrease quantity"
                >
                  −
                </button>

                <span class="quantity-value">{{ quantity }}</span>

                <button
                  type="button"
                  class="quantity-button"
                  @click="increaseQuantity"
                  aria-label="Increase quantity"
                >
                  +
                </button>
              </div>

              <button
                type="button"
                class="add-to-cart-button"
                @click="handleAddToCart"
              >
                Add to cart
              </button>
            </div>

            <div class="info-row info-row--bottom">
              <span class="co2-pill" :class="co2Class">
                {{ totalCo2PerSelection.toFixed(2) }} kg CO₂e
              </span>

              <span class="item-price">
                €{{ totalPrice.toFixed(2) }}
              </span>
            </div>
          </section>

          <!-- Card 3: climate stats -->
          <section class="content-card stats-card">
            <h4 class="stats-title">Climate impact</h4>

            <div class="stats-grid">
              <div class="stat-box">
                <span class="stat-label">Per serving</span>
                <span class="stat-value">
                  {{ item.co2_kg_per_serving.toFixed(2) }} kg CO₂e
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Per kg</span>
                <span class="stat-value">
                  {{ item.co2_kg_per_kg.toFixed(2) }} kg CO₂e
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Selected quantity</span>
                <span class="stat-value">
                  {{ quantity }} × {{ item.serving_size_g }} g
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Impact rating</span>
                <span class="stat-value" :class="co2TextClass">
                  {{ co2RatingLabel }}
                </span>
              </div>
            </div>

            <p class="stats-copy">
              This item has a
              <strong>{{ co2RatingLabel.toLowerCase() }}</strong>
              climate impact per serving compared with the thresholds used in the app.
            </p>
          </section>

          <!-- Card 3: Nutritional Values -->
          <section class="content-card stats-card">
            <h4 class="stats-title">Nutritional Values</h4>

            <div class="stats-grid">
              <div class="stat-box">
                <span class="stat-label">Calories</span>
                <span class="stat-value">
                  {{ item.calories_kcal }} kcal
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Fat grams</span>
                <span class="stat-value">
                  {{ item.fat_g }} g
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Carbs grams</span>
                <span class="stat-value">
                    {{ item.carbs_g }} g
                </span>
              </div>

              <div class="stat-box">
                <span class="stat-label">Fiber grams</span>
                <span class="stat-value">
                  {{ item.fiber_g }} g
                </span>
              </div>

                <div class="stat-box">
                    <span class="stat-label">Protein grams</span>
                    <span class="stat-value">
                    {{ item.protein_g }} g
                    </span>
                </div>

                <div class="stat-box">
                    <span class="stat-label">Sugar grams</span>
                    <span class="stat-value">
                    {{ item.sugar_g }} g
                    </span>
                </div>
            </div>
          </section>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue"
import type { FoodItem } from "@/types"
import placeholderImage from "@/assets/images/food_placeholder.png"

const props = defineProps<{
  modelValue: boolean
  item: FoodItem | null
}>()

const emit = defineEmits<{
  (e: "update:modelValue", value: boolean): void
  (e: "add-to-cart", payload: { item: FoodItem; quantity: number }): void
}>()

const drawerRef = ref<HTMLElement | null>(null)
const isVisible = ref(false)
const isDragging = ref(false)

const startY = ref(0)
const currentY = ref(0)
const dragOffset = ref(0)

const quantity = ref(1)

const CLOSE_THRESHOLD = 120
const ANIMATION_MS = 250

const drawerStyle = computed(() => ({
  transform: `translateY(${Math.max(0, dragOffset.value)}px)`
}))

const totalPrice = computed(() => {
  if (!props.item) return 0
  return props.item.price_eur * quantity.value
})

const totalCo2PerSelection = computed(() => {
  if (!props.item) return 0
  return props.item.co2_kg_per_serving * quantity.value
})

const co2Class = computed(() => {
  if (!props.item) return ""

  const co2 = props.item.co2_kg_per_serving

  if (co2 <= 0.8) return "co2-green"
  if (co2 <= 2.5) return "co2-yellow"
  return "co2-red"
})

const co2TextClass = computed(() => {
  if (!props.item) return ""

  const co2 = props.item.co2_kg_per_serving

  if (co2 <= 0.8) return "text-green"
  if (co2 <= 2.5) return "text-yellow"
  return "text-red"
})

const co2RatingLabel = computed(() => {
  if (!props.item) return ""

  const co2 = props.item.co2_kg_per_serving

  if (co2 <= 0.8) return "Low impact"
  if (co2 <= 2.5) return "Medium impact"
  return "High impact"
})

function increaseQuantity() {
  quantity.value += 1
}

function decreaseQuantity() {
  if (quantity.value > 1) {
    quantity.value -= 1
  }
}

function handleAddToCart() {
  if (!props.item) return

  emit("add-to-cart", {
    item: props.item,
    quantity: quantity.value
  })
}

function resetDrag() {
  isDragging.value = false
  startY.value = 0
  currentY.value = 0
  dragOffset.value = 0
}

function lockBodyScroll() {
  const scrollbarWidth =
    window.innerWidth - document.documentElement.clientWidth

  document.body.style.overflow = "hidden"
  document.body.style.touchAction = "none"

  if (scrollbarWidth > 0) {
    document.body.style.paddingRight = `${scrollbarWidth}px`
  }
}

function unlockBodyScroll() {
  document.body.style.overflow = ""
  document.body.style.touchAction = ""
  document.body.style.paddingRight = ""
}

function startClose() {
  isVisible.value = false
  resetDrag()

  window.setTimeout(() => {
    emit("update:modelValue", false)
  }, ANIMATION_MS)
}

function onPointerDown(event: PointerEvent) {
  if (!props.modelValue) return

  isDragging.value = true
  startY.value = event.clientY
  currentY.value = event.clientY

  const target = event.currentTarget as HTMLElement | null
  target?.setPointerCapture?.(event.pointerId)
}

function onPointerMove(event: PointerEvent) {
  if (!isDragging.value) return

  currentY.value = event.clientY
  const delta = currentY.value - startY.value

  dragOffset.value = Math.max(0, delta)
}

function onPointerUp(event: PointerEvent) {
  if (!isDragging.value) return

  const target = event.currentTarget as HTMLElement | null
  target?.releasePointerCapture?.(event.pointerId)

  if (dragOffset.value > CLOSE_THRESHOLD) {
    startClose()
    return
  }

  resetDrag()
}

watch(
  () => props.modelValue,
  async (open) => {
    if (open) {
      lockBodyScroll()
      resetDrag()
      quantity.value = 1

      await nextTick()

      requestAnimationFrame(() => {
        isVisible.value = true
      })

      return
    }

    isVisible.value = false
    resetDrag()
    unlockBodyScroll()
  },
  { immediate: true }
)

watch(
  () => props.item,
  () => {
    quantity.value = 1
  }
)

onBeforeUnmount(() => {
  unlockBodyScroll()
})
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.28);
  display: flex;
  align-items: end;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.25s ease;
}

.drawer-overlay--visible {
  opacity: 1;
}

.drawer-sheet {
  width: 100%;
  max-width: 720px;
  min-height: 240px;
  max-height: 85vh;
  background: #f3f4f6;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.16);
  overflow: hidden;
  transform: translateY(100%);
  transition: transform 0.25s ease;
  will-change: transform;
}

.drawer-sheet--visible {
  transform: translateY(0);
}

.drawer-sheet--dragging {
  transition: none;
}

.drawer-drag-area {
  touch-action: none;
  user-select: none;
  background: #f3f4f6;
}

.drawer-handle-wrap {
  display: flex;
  justify-content: center;
  padding: 10px 0 6px;
}

.drawer-handle {
  width: 44px;
  height: 5px;
  border-radius: 999px;
  background: #d1d5db;
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px 12px;
}

.drawer-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.drawer-close {
  border: 0;
  background: transparent;
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
}

.drawer-content {
  padding: 0 16px 20px;
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  max-height: calc(85vh - 72px);
}

.content-card {
  background: #fff;
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.content-card + .content-card {
  margin-top: 12px;
}

.image-card {
  padding: 0;
  overflow: hidden;
}

.item-image {
  display: block;
  width: 100%;
  height: 220px;
  object-fit: cover;
}

.info-card {
  display: grid;
  gap: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.info-row--top {
  align-items: start;
}

.item-name {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.3;
}

.item-unit {
  color: #6b7280;
  white-space: nowrap;
}

.info-row--middle {
  align-items: center;
}

.quantity-control {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 999px;
  padding: 6px 10px;
}

.quantity-button {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 999px;
  background: #f3f4f6;
  font-size: 1.1rem;
  cursor: pointer;
}

.quantity-value {
  min-width: 16px;
  text-align: center;
  font-weight: 600;
}

.add-to-cart-button {
  border: 0;
  border-radius: 999px;
  padding: 10px 16px;
  background: #111827;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.info-row--bottom {
  align-items: center;
}

.item-price {
  font-size: 1.1rem;
  font-weight: 700;
}

.co2-pill {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 700;
}

.co2-green {
  background: #e7f7ed;
  color: #1f7a3f;
}

.co2-yellow {
  background: #fff4db;
  color: #a16207;
}

.co2-red {
  background: #fde8e8;
  color: #b91c1c;
}

.stats-card {
  display: grid;
  gap: 14px;
}

.stats-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 700;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.stat-box {
  display: grid;
  gap: 4px;
  padding: 12px;
  border-radius: 14px;
  background: #f9fafb;
}

.stat-label {
  font-size: 0.8rem;
  color: #6b7280;
}

.stat-value {
  font-size: 0.95rem;
  font-weight: 700;
}

.text-green {
  color: #1f7a3f;
}

.text-yellow {
  color: #a16207;
}

.text-red {
  color: #b91c1c;
}

.stats-copy {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}
</style>