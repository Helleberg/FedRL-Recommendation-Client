<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useCartStore } from '@/stores/cart'

const route = useRoute()
const cart = useCartStore()

const isActive = (name: string) => route.name === name
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink :to="{ name: 'cart' }" class="nav-item" :class="{ active: isActive('cart') }">
      <span class="nav-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <circle cx="9" cy="21" r="1" />
          <circle cx="20" cy="21" r="1" />
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
        </svg>
        <span v-if="cart.itemCount > 0" class="badge">{{ cart.itemCount }}</span>
      </span>
      <span class="nav-label">Cart</span>
    </RouterLink>

    <RouterLink :to="{ name: 'catalogue' }" class="nav-item" :class="{ active: isActive('catalogue') }">
      <span class="nav-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M3 3h18v4H3zM3 10h18v4H3zM3 17h18v4H3z" />
        </svg>
      </span>
      <span class="nav-label">Browse</span>
    </RouterLink>

    <RouterLink :to="{ name: 'stats' }" class="nav-item" :class="{ active: isActive('stats') }">
      <span class="nav-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </svg>
      </span>
      <span class="nav-label">Stats</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: rgba(245, 240, 232, 0.95);
  backdrop-filter: blur(12px);
  border-top: 1.5px solid var(--border);
  padding: 0.5rem 1rem calc(0.5rem + env(safe-area-inset-bottom));
  z-index: 100;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  text-decoration: none;
  color: var(--text-muted);
  transition: color 0.2s;
  padding: 0.25rem 1.5rem;
}

.nav-item.active {
  color: var(--moss);
}

.nav-icon {
  position: relative;
  width: 24px;
  height: 24px;
}

.nav-icon svg {
  width: 100%;
  height: 100%;
}

.badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background: var(--rust);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 600;
  border-radius: 100px;
  padding: 1px 5px;
  min-width: 16px;
  text-align: center;
}

.nav-label {
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.02em;
}
</style>