<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppNav from '@/components/AppNav.vue'
</script>

<template>
  <div class="app-shell">
    <AppNav />
    <main class="app-content">
      <RouterView />
    </main>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');
:root {
  --cream: #f5f0e8;
  --parchment: #ede5d4;
  --bark: #3d2b1f;
  --blue: #417fd0;
  --sage: #7a9e7e;
  --fern: #5c7f5c;
  --rust: #b85c2a;
  --wheat: #c9a96e;
  --sky: #5b8fa8;
  --mist: #d4e4ec;
  --text: #17181b;
  --text-muted: #434346;
  --border: #c5c5c5;
  --shadow: rgba(61, 43, 31, 0.1);
  --radius: 12px;
  --radius-lg: 20px;
  --bg-gradient-start: #d4e4ec;
  --bg-gradient-end: #d4f0d4;
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: 'Outfit', sans-serif;
  color: var(--text);
  min-height: 100dvh;
  -webkit-font-smoothing: antialiased;
  background-color: #ffffff;
  background: #52b3d9;
  background: linear-gradient(165deg, rgba(82, 179, 217, 1) 0%, rgba(57, 212, 122, 0.79) 30%, rgba(255, 255, 255, 1) 55%);
  background-position: 0 0;
  background-attachment: fixed;
}

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.app-content {
  flex: 1;
  max-width: 480px;
  margin: 0 auto;
  width: 100%;
}

/* Shared utility classes */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1.2rem;
  border-radius: 100px;
  border: none;
  font-family: 'DM Sans', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s, background 0.15s;
}

.btn:active {
  transform: scale(0.97);
}

.btn-primary {
  background: var(--moss);
  color: #fff;
}

.btn-primary:hover {
  background: var(--fern);
  box-shadow: 0 4px 12px rgba(58, 92, 58, 0.3);
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border: 1.5px solid var(--border);
}

.btn-ghost:hover {
  background: var(--parchment);
}

.btn-danger {
  background: var(--rust);
  color: #fff;
}

.btn-danger:hover {
  background: #a04e22;
}

.card {
  background: #fff;
  border-radius: var(--radius-lg);
  border: 1.5px solid var(--border);
  overflow: hidden;
}

.tag {
  display: inline-block;
  padding: 0.2rem 0.65rem;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--parchment);
  color: var(--text-muted);
}

.tag-green {
  background: #e4f0e4;
  color: var(--moss);
}

/* Animations */
@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(14px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-soft {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: 0.6;
  }
}

.fade-up {
  animation: fadeUp 0.35s ease both;
}
</style>