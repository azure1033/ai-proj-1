<template>
  <div class="welcome">
    <div class="welcome-icon">
      <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
        <rect width="28" height="28" rx="8" fill="url(#g)"/>
        <path d="M8 14h4M16 14h4M14 8v4M14 16v4" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="28" y2="28">
            <stop stop-color="#7c3aed"/><stop offset="1" stop-color="#22d3ee"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
    <h2 class="welcome-title">{{ title }}</h2>
    <p class="welcome-desc">{{ description }}</p>
    <div class="suggestion-grid">
      <button
        v-for="item in suggestions"
        :key="item.key"
        class="suggestion-card"
        @click="$emit('select', item.query)"
      >
        <span class="card-icon">{{ item.icon }}</span>
        <span class="card-label">{{ item.label }}</span>
        <span class="card-hint">{{ item.hint }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Suggestion {
  key: string
  icon: string
  label: string
  hint: string
  query: string
}

defineProps<{
  title?: string
  description?: string
  suggestions?: Suggestion[]
}>()

defineEmits<{
  select: [query: string]
}>()
</script>

<style scoped>
.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 24px 32px;
  text-align: center;
}

.welcome-icon { margin-bottom: var(--space-5); opacity: 0.9; }

.welcome-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-2);
  letter-spacing: -0.02em;
}

.welcome-desc {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: var(--space-8);
  line-height: 1.6;
}

.suggestion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
  max-width: 520px;
  width: 100%;
}

.suggestion-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: var(--space-4);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
  cursor: pointer;
  text-align: left;
  transition: all var(--transition-fast);
  font-family: var(--font-sans);
}

.suggestion-card:hover {
  border-color: var(--accent-primary);
  background: var(--accent-primary-bg);
}

.card-icon { font-size: 16px; }
.card-label { font-size: 13px; font-weight: 500; color: var(--text-primary); }
.card-hint { font-size: 12px; color: var(--text-tertiary); }

@media (max-width: 600px) {
  .suggestion-grid { grid-template-columns: 1fr; }
  .welcome { padding: 32px 16px 24px; }
}
</style>
