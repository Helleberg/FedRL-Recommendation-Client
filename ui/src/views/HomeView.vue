<template>
    <ViewHeader>
        <template #title>Nudge2Green</template>
        <template #subtitle>FedRL Recommendation System</template>
    </ViewHeader>

    <div class="cards-container">
        <div class="card">
            <div class="card-content">
                <h2 class="card-title">Master Thesis</h2>
                <p class="card-text">Federated Reinforcement Learning for Sustainable Recommendation Systems</p>
            </div>
        </div>

        <div class="cards-section-title">
            <h2 class="section-title">Getting Started</h2>
        </div>

        <!-- Getting started card with a button navigating to the cart view -->
        <div class="card">
            <div class="card-content">
                <h2 class="card-title">Build your cart!</h2>
                <p class="card-text">Add items to your cart to begin training</p>
                <div class="action-container">
                    <p class="action-text">Go to cart view</p>
                    <RouterLink :to="{ name: 'cart' }" class="card-btn">Start</RouterLink>
                </div>
            </div>
        </div>

    </div>
</template>
<script setup lang="ts">
    import { onMounted } from 'vue'
    import ViewHeader from '@/components/ViewHeader.vue'

    onMounted(() => {
        console.log('HomeView mounted')
    })
</script>

<style scoped>

header {
    display: flex;
    flex-direction: column;
}

.view-title {
    font-family: 'Outfit', serif;
    font-size: 2rem;
    font-weight: 600;
    margin-bottom: 0.4rem;
}

.view-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

.cards-container {
    margin: 0 1.2rem;
    margin-top: 2rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.card {
    background: rgba(255, 255, 255, 0.55);
    border-radius: 16px;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(5px);
    -webkit-backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.24);
}

.card-content {
    padding: 1.2rem;
}

.card-title {
    font-family: 'Outfit', serif;
    font-size: 1.25rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
}

.card-text {
    font-size: 0.9rem;
    color: var(--text-muted);
}

.cards-section-title {
    margin-top: 1rem;
}

.section-title {
    font-family: 'Outfit', serif;
    font-size: 1.2rem;
    font-weight: 500;
    letter-spacing: -0.02em;
}

.action-container {
    margin-top: 1rem;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 0.6rem 1rem;
}

.action-text {
    font-size: 0.85rem;
    color: var(--text-muted);
}

.card-btn {
    background-color: var(--blue);
    color: white;
    padding: 0.4rem 0.6rem;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 500;
    transition: background-color 0.2s;
}

</style>