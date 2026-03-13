import { createRouter, createWebHistory } from 'vue-router'
import CartView from '@/views/CartView.vue'
import CatalogueView from '@/views/CatalogueView.vue'
import StatsView from '@/views/StatsView.vue'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        { path : '/', name: 'home', component: HomeView },
        { path: '/cart', name: 'cart', component: CartView },
        { path: '/catalogue', name: 'catalogue', component: CatalogueView },
        { path: '/stats', name: 'stats', component: StatsView },
    ],
})

export default router