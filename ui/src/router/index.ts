import { createRouter, createWebHistory } from 'vue-router'
import CartView from '@/views/CartView.vue'
import CatalogueView from '@/views/CatalogueView.vue'
import StatsView from '@/views/StatsView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', name: 'cart', component: CartView },
        { path: '/catalogue', name: 'catalogue', component: CatalogueView },
        { path: '/stats', name: 'stats', component: StatsView },
    ],
})

export default router