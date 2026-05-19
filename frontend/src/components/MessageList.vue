<template>
  <div class="message-list" ref="listRef">
    <WelcomeScreen
      v-if="messages.length === 0"
      :title="welcomeTitle"
      :description="welcomeDesc"
      :suggestions="suggestions"
      @select="$emit('quickAsk', $event)"
    />

    <MessageBubble
      v-for="(msg, idx) in messages"
      :key="idx"
      :message="msg"
      :index="idx"
      :is-streaming="isLoading && idx === messages.length - 1 && msg.role === 'assistant'"
      :expanded-steps="expandedSteps?.[idx]"
      @toggle-step="(msgIdx, stepIdx) => $emit('toggleStep', msgIdx, stepIdx)"
    />

    <!-- Loading indicator when messages exist and loading -->
    <div v-if="isLoading && messages.length > 0" class="loading-row">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>

    <div ref="bottomRef"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'
import MessageBubble from './MessageBubble.vue'
import type { ChatMessage } from './MessageBubble.vue'
import WelcomeScreen from './WelcomeScreen.vue'

interface Suggestion {
  key: string
  icon: string
  label: string
  hint: string
  query: string
}

defineProps<{
  messages: ChatMessage[]
  isLoading?: boolean
  expandedSteps?: Record<number, Record<number, boolean>>
  welcomeTitle?: string
  welcomeDesc?: string
  suggestions?: Suggestion[]
}>()

defineEmits<{
  toggleStep: [msgIndex: number, stepIndex: number]
  quickAsk: [query: string]
}>()

const listRef = ref<HTMLElement>()
const bottomRef = ref<HTMLElement>()

const scrollToBottom = () => {
  nextTick(() => bottomRef.value?.scrollIntoView({ behavior: 'smooth' }))
}

watch(() => listRef.value?.scrollHeight, scrollToBottom)
onMounted(scrollToBottom)
</script>

<style scoped>
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6) var(--space-6) var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
  max-width: var(--chat-max-w);
  margin: 0 auto;
  width: 100%;
}

.loading-row {
  display: flex;
  gap: var(--space-3);
  padding-left: 44px;
}

.typing-dots {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
  background: var(--bg-surface);
  border-radius: var(--radius-msg-assistant);
  border: 1px solid var(--border-default);
}

.typing-dots span {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-tertiary);
  animation: dotBounce 1.4s ease-in-out infinite;
}

.typing-dots span:nth-child(2) { animation-delay: 0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0.32s; }

@keyframes dotBounce {
  0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1.2); }
}

@media (max-width: 768px) {
  .message-list {
    padding: var(--space-4) var(--space-4) var(--space-3);
  }
}
</style>
