import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FoodItem } from '@/types'
import { getCatalogue, getCategories } from '@/api/client'

export const useCatalogueStore = defineStore('catalogue', () => {
    const items = ref<FoodItem[]>([])
    const categories = ref<string[]>([])
    const loading = ref(false)
    const version = ref('0')
    const activeCategory = ref<string | null>(null)

    async function fetchCatalogue(category?: string) {
        loading.value = true
        try {
            const data = await getCatalogue(category)
            items.value = data.items
            version.value = data.version
        } finally {
            loading.value = false
        }
    }

    async function fetchCategories() {
        const data = await getCategories()
        categories.value = data.categories
    }

    function setCategory(cat: string | null) {
        activeCategory.value = cat
        fetchCatalogue(cat ?? undefined)
    }

    return { items, categories, loading, version, activeCategory, fetchCatalogue, fetchCategories, setCategory }
})