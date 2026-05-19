<template>
  <div class="chat-view">
    <!-- Header -->
    <header class="chat-header">
      <div class="header-left">
        <button
          v-if="isMobile"
          class="hamburger"
          @click="toggleSidebar"
          aria-label="菜单"
        >
          <svg width="18" height="18" viewBox="0 0 18 18"><path d="M2 4.5h14M2 9h14M2 13.5h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        </button>
        <div class="header-title">
          <h2>{{ currentSession?.name || 'AI 智能助手' }}</h2>
        </div>
      </div>
      <div class="header-right">
        <button class="header-btn" @click="clearHistory" :disabled="isLoading" title="清空对话">
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M3 4h10M6 4V2.5h4V4M4.5 4v9.5h7V4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
        <button class="header-btn" @click="showKnowledge = !showKnowledge" title="知识库">
          <svg width="16" height="16" viewBox="0 0 16 16"><path d="M2 3h4v10H2V3zM8 3h6v10H8V3z" stroke="currentColor" stroke-width="1.5"/></svg>
        </button>
        <button class="header-btn" @click="showSettings = true" title="设置">
          <svg width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.5v2M8 12.5v2M2.5 8h2M11.5 8h2M3.4 3.4l1.4 1.4M11.2 11.2l1.4 1.4M12.6 3.4l-1.4 1.4M4.8 11.2l-1.4 1.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </button>
      </div>
    </header>

    <!-- Messages -->
    <MessageList
      :messages="messages"
      :is-loading="isLoading"
      :expanded-steps="expandedSteps"
      :welcome-title="t('welcomeTitle')"
      :welcome-desc="t('welcomeDesc')"
      :suggestions="suggestionCards"
      @toggle-step="onToggleStep"
      @quick-ask="quickAsk"
    />

    <!-- Input -->
    <ChatInput
      :disabled="isLoading"
      :placeholder="t('placeholder')"
      @send="sendMessage"
    />

    <!-- Knowledge panel -->
    <Teleport to="body">
      <div v-if="showKnowledge" class="kb-overlay" @click.self="showKnowledge = false">
        <div class="kb-drawer">
          <button class="kb-close-btn" @click="showKnowledge = false" aria-label="关闭知识库">✕</button>
          <KnowledgePanel :session-id="currentSessionId || ''" @document-changed="onDocChanged" />
        </div>
      </div>
    </Teleport>

    <!-- Settings -->
    <SettingsModal :visible="showSettings" @close="showSettings = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed, inject } from 'vue'
import MessageList from './MessageList.vue'
import ChatInput from './ChatInput.vue'
import KnowledgePanel from './KnowledgePanel.vue'
import SettingsModal from './SettingsModal.vue'
import type { Session, ChatMessage, AgentStep } from '../types'

const props = defineProps<{
  sessions: Session[]
  currentSessionId: string | null
  locale: 'zh' | 'en'
}>()

// --- i18n ---
const tr: Record<string, Record<string, string>> = {
  zh: {
    welcomeTitle: '有什么我可以帮你的？',
    welcomeDesc: '支持天气查询、问答、总结、翻译和代码解释',
    placeholder: '输入消息...',
    errorDefault: '请求失败，请稍后重试',
  },
  en: {
    welcomeTitle: 'How can I help you?',
    welcomeDesc: 'Weather, Q&A, summarize, translate, and code explanation',
    placeholder: 'Type a message...',
    errorDefault: 'Request failed. Please try again.',
  },
}
const t = (key: string) => tr[props.locale]?.[key] || tr.zh[key] || key

// --- Suggestions ---
const suggestionCards = computed(() => {
  const isZh = props.locale === 'zh'
  return [
    { key: 'weather', icon: '🌤️', label: isZh ? '天气查询' : 'Weather', hint: isZh ? '今天北京天气怎么样？' : 'What\'s the weather today?', query: isZh ? '今天北京天气怎么样？' : 'What\'s the weather today?' },
    { key: 'qa', icon: '💬', label: isZh ? '知识问答' : 'Q&A', hint: isZh ? '什么是机器学习？' : 'What is machine learning?', query: isZh ? '什么是机器学习？' : 'What is machine learning?' },
    { key: 'summarize', icon: '📝', label: isZh ? '文本总结' : 'Summarize', hint: isZh ? '帮我总结一段文本' : 'Summarize a text for me', query: isZh ? '请帮我总结以下内容' : 'Please summarize the following' },
    { key: 'translate', icon: '🌐', label: isZh ? '翻译' : 'Translate', hint: isZh ? '翻译一段英文到中文' : 'Translate English to Chinese', query: isZh ? '请翻译：Hello, how are you?' : 'Translate: 你好，最近怎么样？' },
  ]
})

// --- State ---
const messages = ref<ChatMessage[]>([])
const isLoading = ref(false)
const showKnowledge = ref(false)
const showSettings = ref(false)
const expandedSteps = ref<Record<number, Record<number, boolean>>>({})
const streamingSteps = ref<AgentStep[]>([])

// Sidebar toggle (injected from App.vue)
const toggleSidebar = inject<() => void>('toggleSidebar', () => {})
const isMobile = ref(false)
onMounted(() => { isMobile.value = window.innerWidth < 768 })

// --- SSE Streaming ---
const sendMessage = async (query: string) => {
  if (!query.trim() || isLoading.value) return
  messages.value.push({ role: 'user', content: query })
  isLoading.value = true
  const assistantMsg: ChatMessage = { role: 'assistant', content: '', steps: [] }
  messages.value.push(assistantMsg)
  const msgIdx = messages.value.length - 1
  try {
    const res = await fetch(`/api/ask?stream=true`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: props.currentSessionId }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      let eventType = ''
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          const dataStr = line.slice(6)
          try {
            const data = JSON.parse(dataStr)
            handleSSE(msgIdx, eventType, data)
          } catch {
            if (eventType === 'token') messages.value[msgIdx].content += dataStr
          }
          eventType = ''
        }
      }
    }
  } catch (err: any) {
    messages.value[msgIdx].content = err.message || t('errorDefault')
  } finally {
    isLoading.value = false
    messages.value[msgIdx].steps = [...streamingSteps.value]
    streamingSteps.value = []
  }
}

const handleSSE = (msgIdx: number, eventType: string, data: any) => {
  switch (eventType) {
    case 'token':
      messages.value[msgIdx].content += data
      break
    case 'step':
      streamingSteps.value.push({ thought: '', tool: data.tool || 'unknown', tool_input: data.input || '', observation: '' })
      messages.value[msgIdx].steps = [...streamingSteps.value]
      break
    case 'step_done':
      if (streamingSteps.value.length > 0)
        streamingSteps.value[streamingSteps.value.length - 1].observation = data.output || ''
      messages.value[msgIdx].steps = [...streamingSteps.value]
      break
    case 'error':
      messages.value[msgIdx].content += `\n\n[${t('errorDefault')}: ${data.message || ''}]`
      break
  }
}

// --- Actions ---
const quickAsk = (query: string) => sendMessage(query)

const clearHistory = async () => {
  try {
    await fetch(`/api/history/clear?session_id=${props.currentSessionId || ''}`, { method: 'POST' })
    messages.value = []
  } catch { /* silent */ }
}

const onToggleStep = (msgIdx: number, stepIdx: number) => {
  if (!expandedSteps.value[msgIdx]) expandedSteps.value[msgIdx] = {}
  expandedSteps.value[msgIdx][stepIdx] = !expandedSteps.value[msgIdx][stepIdx]
}

const onDocChanged = () => {}

// --- Session ---
const currentSession = computed(() =>
  props.sessions.find(s => s.id === props.currentSessionId) || null
)

const initMessages = () => {
  messages.value = [{
    role: 'assistant',
    content: props.locale === 'zh'
      ? '👋 欢迎使用 AI 智能助手！\n\n我支持以下功能：\n- **天气查询**：询问天气和穿衣建议\n- **问答**：回答各类问题\n- **总结**：总结长文本内容\n- **翻译**：多语言翻译\n- **代码解释**：解释代码逻辑\n\n请直接输入您的问题！'
      : '👋 Welcome to AI Assistant!\n\nI support:\n- **Weather**: weather and clothing advice\n- **Q&A**: answer questions\n- **Summarize**: summarize text\n- **Translate**: multilingual translation\n- **Code**: explain code\n\nAsk me anything!',
  }]
}

onMounted(initMessages)

watch(() => props.currentSessionId, async (newId) => {
  messages.value = []
  if (!newId) { initMessages(); return }
  try {
    const res = await fetch(`/api/sessions/${newId}/history`)
    const data = await res.json()
    messages.value = data.messages?.length > 0 ? data.messages : [{
      role: 'assistant',
      content: props.locale === 'zh' ? '👋 欢迎回来！继续之前的对话吧。' : '👋 Welcome back! Continue your conversation.'
    }]
  } catch { initMessages() }
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  height: 100dvh;
  background: var(--bg-primary);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--space-6);
  height: 52px;
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.header-left { display: flex; align-items: center; gap: var(--space-3); }

.hamburger {
  width: 36px; height: 36px;
  border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-tertiary);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.hamburger:hover { background: var(--bg-elevated); color: var(--text-primary); }

.header-title h2 { font-size: 15px; font-weight: 600; color: var(--text-primary); }

.header-right { display: flex; gap: var(--space-1); }

.header-btn {
  width: 34px; height: 34px;
  border: none; border-radius: var(--radius-sm);
  background: transparent; color: var(--text-tertiary);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition-fast);
}
.header-btn:hover:not(:disabled) { background: var(--bg-elevated); color: var(--text-primary); }
.header-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* KB drawer */
.kb-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.4); backdrop-filter: blur(4px);
  z-index: 300;
  display: flex; justify-content: flex-end;
}
.kb-drawer {
  width: 420px; max-width: 92vw; height: 100dvh;
  overflow-y: auto;
  background: var(--bg-surface);
  box-shadow: var(--shadow-lg);
  padding: var(--space-6);
  position: relative;
}
.kb-close-btn {
  position: absolute; top: var(--space-4); right: var(--space-4);
  width: 32px; height: 32px;
  border: 1px solid var(--border-default); border-radius: var(--radius-sm);
  background: var(--bg-surface); color: var(--text-tertiary);
  font-size: 16px; cursor: pointer; z-index: 10;
  display: flex; align-items: center; justify-content: center;
}
.kb-close-btn:hover { background: var(--bg-elevated); }

@media (max-width: 768px) {
  .chat-header { padding: 0 var(--space-4); }
}
</style>
