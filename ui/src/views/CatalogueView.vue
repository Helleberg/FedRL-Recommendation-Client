<template>
    <ViewHeader>
        <template #title>Catalogue</template>
    </ViewHeader>

    <!-- Filtering option based on category. As a dropdown -->
    <div class="group">
        <div class="category-filter">
            <DropdownSelect
                v-model="selectedCategory"
                :options="categories"
                labelKey="name"
                valueKey="id"
            />
        </div>

        <!-- Number of items in cart -->
        <div class="cart-count">
            {{ cart.items.length ?? 0 }} items in cart
        </div>
    </div>

    <!-- Product cards containing: Product Name, Description, Price, Sustainability Score -->
    <div class="catalogue-view">
        <div class="grid">
            <div class="item-wrapper">
                <div v-if="filteredItems.length === 0" class="empty-state">
                    No items found in this category.
                </div>
                <div v-else>
                    <FoodItemCard
                        v-for="item in filteredItems"
                        :key="item.id"
                        :item="item"
                        mode="add"
                        :is-adding="addingId === item.id"
                        @add-to-cart="handleAddToCart"
                        @view-details="handleViewDetails"
                    />
                </div>
            </div>
        </div>
    </div>

    <FoodItemDrawer
        v-model="isDrawerOpen"
        :item="selectedItem"
        @add-to-cart="handleDrawerAddToCart"
    />
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useCatalogueStore } from '@/stores/catalogue'
import { useCartStore } from '@/stores/cart'
import FoodItemCard from '@/components/FoodItemCard.vue'
import FoodItemDrawer from '@/components/FoodItemDrawer.vue'
import ViewHeader from '@/components/ViewHeader.vue'
import DropdownSelect from '@/components/DropdownSelect.vue'

// Type imports
import type { FoodItem, Category } from '@/types'

const catalogue = useCatalogueStore()
const cart = useCartStore()
const addingId = ref<string | null>(null)
const addedId = ref<string | null>(null)

const selectedCategory = ref<number>(0)
const isDrawerOpen = ref(false)
const selectedItem = ref<FoodItem | null>(null)

const categories = computed<Category[]>(() => [
  { id: 0, name: "All categories", code: "all" },
  ...catalogue.categories
])

const filteredItems = computed(() => {
    if (Number(selectedCategory.value) === 0) {
        return catalogue.items
    }
    return catalogue.items.filter((item: FoodItem) => item.category_id === Number(selectedCategory.value))
})

async function handleAddToCart(item: FoodItem) {
  if (addingId.value) return

  addingId.value = item.id
  try {
    await cart.addItem(item)
    addedId.value = item.id
    setTimeout(() => {
      if (addedId.value === item.id) {
        addedId.value = null
      }
    }, 1200)
  } finally {
    addingId.value = null
  }
}

async function handleDrawerAddToCart(payload: { item: FoodItem; quantity: number }) {
  if (addingId.value) return

  addingId.value = payload.item.id
  try {
    await cart.addItem(payload.item, payload.quantity)
    addedId.value = payload.item.id
    setTimeout(() => {
      if (addedId.value === payload.item.id) {
        addedId.value = null
      }
    }, 1200)
  } finally {
    addingId.value = null
    isDrawerOpen.value = false
  }
}

function handleViewDetails(item: FoodItem) {
  selectedItem.value = item
  isDrawerOpen.value = true
}

onMounted(async () => {
    await catalogue.fetchCategories()
    await catalogue.fetchCatalogue()
})
</script>

<style scoped>
    .catalogue-view {
        margin-bottom: 4rem;
    }

    .item-wrapper {
        margin-top: 1.5rem;
        padding: 1rem 1.2rem;
        display: grid;
        gap: 12px;
    }

    .group {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0 1.2rem;
    }

    .cart-count {
        font-size: 1.1rem;
        color: var(--text-muted);
    }
</style>