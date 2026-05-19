<template>
  <div class="chat-input-wrapper">
    <div class="input-container">
      <textarea
        ref="textareaRef"
        v-model="localInput"
        :placeholder="placeholder"
        :disabled="disabled"
        rows="1"
        class="input-textarea"
        @input="autoResize"
        @keydown="handleKeydown"
      ></textarea>
      <button
        class="send-button"
        :disabled="disabled || !localInput.trim()"
        @click="emitSend"
        :aria-label="disabled ? '发送中...' : '发送'"
      >
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M3 9h12M9 3l6 6-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    <div class="disclaimer">
      AI 智能助手 — 答案可能不准确，请核实重要信息
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'

const props = defineProps<{
  disabled?: boolean
  placeholder?: string
  modelValue?: string
}>()

const emit = defineEmits<{
  send: [query: string]
  'update:modelValue': [value: string]
}>()

const textareaRef = ref<HTMLTextAreaElement>()
const localInput = ref(props.modelValue || '')

watch(() => props.modelValue, (val) => {
  if (val !== undefined) localInput.value = val
})

const autoResize = () => {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey && (e.ctrlKey || e.metaKey)) {
    e.preventDefault()
    emitSend()
  }
}

const emitSend = () => {
  const text = localInput.value.trim()
  if (!text || props.disabled) return
  emit('send', text)
  localInput.value = ''
  emit('update:modelValue', '')
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

defineExpose({ focus: () => textareaRef.value?.focus() })
</script>

<style scoped>
.chat-input-wrapper {
  padding: var(--space-4) var(--space-6) var(--space-5);
  flex-shrink: 0;
}

.input-container {
  max-width: var(--chat-max-w);
  margin: 0 auto;
  display: flex;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-2) var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-default);
  background: var(--bg-input);
  transition: border-color var(--transition-fast);
}

.input-container:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-glow);
}

.input-textarea {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 14px;
  font-family: var(--font-sans);
  line-height: 1.5;
  resize: none;
  outline: none;
  padding: 6px 0;
  min-height: 24px;
  max-height: 160px;
}

.input-textarea::placeholder {
  color: var(--text-tertiary);
}

.send-button {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--accent-primary);
  border: none;
  color: #fff;
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  align-self: flex-end;
}

.send-button:hover:not(:disabled) {
  background: var(--accent-primary-hover);
}

.send-button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.disclaimer {
  text-align: center;
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: var(--space-2);
  max-width: var(--chat-max-w);
  margin-left: auto;
  margin-right: auto;
}
</style>
