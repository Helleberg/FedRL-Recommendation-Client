<template>
    <header>
        <h1 class="view-title"><slot name="title" /></h1>
        <p class="view-sub"><slot name="subtitle" /></p>
    </header>
</template>

<script setup lang="ts">

</script>

<style scoped>
header {
    padding: 2rem 1.2rem 0.8rem;
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
    font-size: 1rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}
</style>