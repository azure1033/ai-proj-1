# Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor 1800-line ChatAssistant.vue into 6 focused components with dark-first Linear/Vercel design system.

**Architecture:** Claude-style layout — sidebar always visible (260px desktop, drawer on mobile), chat area centered at max-w-[720px], input pinned to bottom. Components communicate via props down / emits up, no Pinia.

**Tech Stack:** Vue 3 + TypeScript + Vite, marked for Markdown, no new dependencies.

---

### Task 1: Rewrite style.css with dark-first design tokens

**Files:**
- Modify: `frontend/src/style.css`

- [ ] **Step 1: Replace style.css with dark-first token system**

The entire file is rewritten. Inter font import stays, all CSS variables replaced with dark-first palette. Light mode becomes an optional `@media (prefers-color-scheme: light)` override (inverted from previous approach).

```css
/* ═══════════════════════════════════════════════════════════
   AI 智能助手 — Dark-First Design System
   Style: Linear/Vercel dark + Claude layout
   ═══════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  /* Background hierarchy */
  --bg-primary: #0f0e1a;
  --bg-surface: #1c1a2e;
  --bg-elevated: #232140;
  --bg-input: #1c1a2e;

  /* Text */
  --text-primary: #f1f0fb;
  --text-secondary: #c4c2d4;
  --text-tertiary: #7a7890;

  /* Accent */
  --accent-primary: #7c3aed;
  --accent-primary-hover: #8b5cf6;
  --accent-primary-bg: rgba(124, 58, 237, 0.12);
  --accent-primary-glow: rgba(124, 58, 237, 0.25);
  --accent-cyan: #22d3ee;
  --accent-cyan-hover: #67e8f9;
  --accent-cyan-bg: rgba(34, 211, 238, 0.08);

  /* Semantic */
  --color-success: #34d399;
  --color-success-bg: rgba(52, 211, 153, 0.1);
  --color-warning: #fbbf24;
  --color-warning-bg: rgba(251, 191, 36, 0.1);
  --color-destructive: #f87171;
  --color-destructive-hover: #ef4444;
  --color-destructive-bg: rgba(248, 113, 113, 0.1);

  /* Borders */
  --border-default: #1e1d2e;
  --border-subtle: #2e2c44;
  --border-active: rgba(167, 139, 250, 0.3);

  /* Message bubble corners */
  --radius-msg: 14px;
  --radius-msg-assistant: 12px 12px 12px 3px;
  --radius-msg-user: 12px 12px 3px 12px;

  /* General radii */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.4);
  --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.5);

  /* Typography */
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  --font-mono: 'SF Mono', 'Cascadia Code', 'Fira Code', ui-monospace, monospace;

  /* Spacing */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);

  /* Layout */
  --sidebar-width: 260px;
  --chat-max-w: 720px;

  /* Base */
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-secondary);
  background: var(--bg-primary);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

/* Light mode override (respects OS preference) */
@media (prefers-color-scheme: light) {
  :root {
    --bg-primary: #fafafa;
    --bg-surface: #ffffff;
    --bg-elevated: #f5f5f5;
    --bg-input: #f9fafb;
    --text-primary: #18181b;
    --text-secondary: #52525b;
    --text-tertiary: #a1a1aa;
    --border-default: #e4e4e7;
    --border-subtle: #f4f4f5;
    --border-active: rgba(124, 58, 237, 0.3);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 2px 8px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.1);
  }
}

/* Reset */
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; overflow: hidden; }
h1, h2, h3, h4 { font-family: var(--font-sans); font-weight: 600; color: var(--text-primary); margin: 0; }
p { margin: 0; }

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border-subtle); border-radius: var(--radius-full); }
::-webkit-scrollbar-thumb:hover { background: var(--text-tertiary); }

/* Focus */
:focus-visible { outline: 2px solid var(--accent-primary); outline-offset: 2px; }

/* Selection */
::selection { background: var(--accent-primary-bg); color: var(--accent-primary); }

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 5`

Expected: Vite HMR shows no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/style.css
git commit -m "feat: dark-first design tokens, Linear/Vercel palette

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: Create ChatInput.vue

**Files:**
- Create: `frontend/src/components/ChatInput.vue`

- [ ] **Step 1: Write ChatInput.vue**

```vue
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
import { ref, watch, onMounted, nextTick } from 'vue'

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
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 3`

Expected: no error lines.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatInput.vue
git commit -m "feat: add ChatInput component — textarea + send button + disclaimer

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: Create MessageBubble.vue

**Files:**
- Create: `frontend/src/components/MessageBubble.vue`

- [ ] **Step 1: Write MessageBubble.vue**

```vue
<template>
  <div class="message-wrapper" :class="message.role">
    <div class="message-avatar" :class="message.role">
      <svg v-if="message.role === 'assistant'" width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="8" r="6" stroke="currentColor" stroke-width="1.5"/>
        <path d="M5 7h6M5 9.5h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
      <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
        <circle cx="8" cy="6" r="3.5" stroke="currentColor" stroke-width="1.5"/>
        <path d="M3 14c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
      </svg>
    </div>

    <div class="message-body">
      <!-- Intent badge -->
      <div v-if="message.role === 'assistant' && message.intent" class="intent-badge">
        {{ intentLabel }}
      </div>

      <!-- Agent steps -->
      <div v-if="message.role === 'assistant' && message.steps?.length" class="agent-steps">
        <div
          v-for="(step, si) in message.steps"
          :key="si"
          class="step-item"
          :class="{ expanded: expandedMap?.[si] }"
        >
          <div class="step-header" @click="toggleStep(si)">
            <svg class="step-chevron" :class="{ open: expandedMap?.[si] }" width="12" height="12" viewBox="0 0 12 12">
              <path d="M4 2.5L8 6l-4 3.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="step-tool-name">{{ formatToolName(step.tool) }}</span>
            <span v-if="step.observation" class="step-dot done"></span>
            <span v-else class="step-dot pending"></span>
          </div>
          <div v-if="expandedMap?.[si]" class="step-body">
            <div class="step-row"><span class="step-label">输入</span> {{ step.tool_input }}</div>
            <div v-if="step.observation" class="step-row"><span class="step-label">输出</span> {{ step.observation }}</div>
            <div v-else class="step-row muted">执行中...</div>
          </div>
        </div>
      </div>

      <!-- Message text -->
      <div
        class="message-bubble"
        :class="{ streaming: isStreaming }"
        v-html="renderedContent"
      ></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { marked } from 'marked'

marked.setOptions({ breaks: true, gfm: true })

export interface AgentStep {
  thought?: string
  tool: string
  tool_input: string
  observation: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  steps?: AgentStep[]
}

const props = defineProps<{
  message: ChatMessage
  index: number
  isStreaming?: boolean
  expandedSteps?: Record<number, boolean>
}>()

const emit = defineEmits<{
  toggleStep: [msgIndex: number, stepIndex: number]
}>()

const expandedMap = reactive<Record<number, boolean>>({})

const renderedContent = computed(() => {
  try { return marked.parse(props.message.content) as string }
  catch { return props.message.content }
})

const intentLabel = computed(() => {
  const map: Record<string, string> = {
    '天气查询': '🌤️ 天气',
    '问答': '💬 问答',
    '总结': '📝 总结',
    '翻译': '🌐 翻译',
    '代码解释': '💻 代码',
    '文档问答': '📄 文档',
    'Agent': '🤖 Agent',
  }
  return map[props.message.intent || ''] || props.message.intent || ''
})

const toolNames: Record<string, string> = {
  get_weather: '🌤️ 天气查询',
  web_search: '🔍 网页搜索',
  summarize_text: '📝 文本总结',
  translate_text: '🌐 文本翻译',
  explain_code: '💻 代码解释',
  calculator: '🧮 计算器',
  search_knowledge_base: '📚 知识库',
}

const formatToolName = (tool: string) => toolNames[tool] || tool

const toggleStep = (si: number) => {
  expandedMap[si] = !expandedMap[si]
  emit('toggleStep', props.index, si)
}
</script>

<style scoped>
.message-wrapper {
  display: flex;
  gap: var(--space-3);
  max-width: 100%;
  animation: msgIn 0.2s ease-out;
}
@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.message-avatar.assistant {
  background: var(--accent-cyan-bg);
  color: var(--accent-cyan);
}
.message-avatar.user {
  background: var(--accent-primary-bg);
  color: var(--accent-primary);
}

.message-body {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.message-wrapper.user .message-body {
  align-items: flex-end;
}

.intent-badge {
  font-size: 11px;
  color: var(--text-tertiary);
  padding-left: 2px;
}

.message-bubble {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-msg-assistant);
  font-size: 14px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: var(--bg-surface);
  color: var(--text-secondary);
  border: 1px solid var(--border-default);
}
.message-wrapper.user .message-bubble {
  border-radius: var(--radius-msg-user);
  background: linear-gradient(135deg, var(--accent-primary), #8b5cf6);
  color: #fff;
  border: none;
}
.message-bubble.streaming {
  border-color: var(--accent-primary);
}

/* Markdown overrides */
.message-bubble :deep(code) {
  background: var(--accent-primary-bg);
  color: var(--accent-primary);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 12px;
}
.message-wrapper.user .message-bubble :deep(code) {
  background: rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.9);
}
.message-bubble :deep(pre) {
  background: var(--bg-primary);
  border: 1px solid var(--border-default);
  padding: var(--space-3);
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 8px 0;
}
.message-bubble :deep(pre code) { background: none; padding: 0; }
.message-bubble :deep(strong) { font-weight: 600; color: var(--text-primary); }
.message-wrapper.user .message-bubble :deep(strong) { color: #fff; }
.message-bubble :deep(a) { color: var(--accent-cyan); }
.message-bubble :deep(blockquote) {
  border-left: 3px solid var(--accent-primary);
  margin: 8px 0;
  padding: 2px var(--space-3);
  color: var(--text-tertiary);
}

/* Agent steps */
.agent-steps {
  margin-bottom: var(--space-1);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-primary);
}
.step-item { border-bottom: 1px solid var(--border-default); }
.step-item:last-child { border-bottom: none; }
.step-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  cursor: pointer;
  font-size: 12px;
  transition: background var(--transition-fast);
}
.step-header:hover { background: var(--accent-primary-bg); }
.step-chevron {
  flex-shrink: 0;
  color: var(--text-tertiary);
  transition: transform var(--transition-fast);
}
.step-chevron.open { transform: rotate(90deg); }
.step-tool-name { flex: 1; color: var(--text-secondary); font-weight: 500; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.step-dot.done { background: var(--color-success); }
.step-dot.pending { background: var(--color-warning); animation: pulse 1.2s infinite; }
@keyframes pulse { 0%,100%{opacity:0.4} 50%{opacity:1} }

.step-body {
  padding: 8px 10px 10px 28px;
  font-size: 12px;
  line-height: 1.5;
}
.step-row { color: var(--text-secondary); margin-bottom: 4px; word-break: break-all; }
.step-row.muted { color: var(--text-tertiary); font-style: italic; }
.step-label { color: var(--text-tertiary); margin-right: 4px; }
</style>
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 3`

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MessageBubble.vue
git commit -m "feat: add MessageBubble — avatar, markdown, agent steps panel

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: Create WelcomeScreen.vue

**Files:**
- Create: `frontend/src/components/WelcomeScreen.vue`

- [ ] **Step 1: Write WelcomeScreen.vue**

```vue
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

.welcome-icon {
  margin-bottom: var(--space-5);
  opacity: 0.9;
}

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
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 3`

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/WelcomeScreen.vue
git commit -m "feat: add WelcomeScreen — empty state with 2x2 suggestion grid

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: Create MessageList.vue

**Files:**
- Create: `frontend/src/components/MessageList.vue`

- [ ] **Step 1: Write MessageList.vue**

```vue
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

    <!-- Loading indicator -->
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
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 3`

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/MessageList.vue
git commit -m "feat: add MessageList — scroll-to-bottom, typing indicator, WelcomeScreen integration

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: Create AppSidebar.vue

**Files:**
- Create: `frontend/src/components/AppSidebar.vue`

- [ ] **Step 1: Write AppSidebar.vue**

```vue
<template>
  <!-- Mobile overlay -->
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="isMobile && modelValue" class="drawer-overlay" @click="$emit('update:modelValue', false)">
        <aside class="sidebar" @click.stop>
          <SidebarContent />
        </aside>
      </div>
    </Transition>
  </Teleport>

  <!-- Desktop sidebar -->
  <aside v-if="!isMobile" class="sidebar">
    <SidebarContent />
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Session } from '../types'

defineProps<{
  sessions: Session[]
  currentSessionId: string | null
  modelValue?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [val: boolean]
  select: [sessionId: string]
  create: []
  rename: [sessionId: string, name: string]
  delete: [sessionId: string]
}>()

const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))
</script>

<script lang="ts">
// This separate script block is used for the SidebarContent renderless component pattern.
// In Vue 3 SFCs, defineOptions and defineSlots are compile-time macros.
</script>
```

Wait — the SidebarContent pattern with two script blocks is fragile. Let me use a simpler approach: extract the sidebar content inline.

Actually, for a cleaner design, let me make AppSidebar.vue self-contained with the full template. No Inner component needed — conditionally apply the overlay wrapper.

```vue
<template>
  <!-- Mobile drawer -->
  <Teleport to="body" v-if="isMobile">
    <Transition name="drawer">
      <div
        v-if="modelValue"
        class="drawer-overlay"
        @click.self="$emit('update:modelValue', false)"
      >
        <aside class="sidebar sidebar-drawer" @click.stop>
          <div class="sidebar-inner">
            <slot name="header" />
            <slot name="list" />
            <slot name="footer" />
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>

  <!-- Desktop -->
  <aside v-if="!isMobile" class="sidebar sidebar-desktop">
    <div class="sidebar-inner">
      <slot name="header" />
      <slot name="list" />
      <slot name="footer" />
    </div>
  </aside>
</template>
```

Hmm, using slots makes AppSidebar too generic. The spec says AppSidebar should own the session list rendering, search, CRUD. Let me write it as a self-contained component with all that logic built-in, using props and emits. No slots — keep it focused.

- [ ] **Step 1 (revised): Write AppSidebar.vue** — self-contained, all session logic inside

```vue
<template>
  <!-- Mobile -->
  <Teleport to="body" v-if="isMobile">
    <Transition name="drawer">
      <div v-if="showMobile" class="drawer-overlay" @click.self="showMobile = false">
        <aside class="sidebar sidebar-drawer" @click.stop>
          <SidebarInner />
        </aside>
      </div>
    </Transition>
  </Teleport>

  <!-- Desktop -->
  <aside v-else class="sidebar sidebar-desktop">
    <SidebarInner />
  </aside>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { type Session } from '../types'

// Props
const props = defineProps<{
  sessions: Session[]
  currentSessionId: string | null
}>()

const emit = defineEmits<{
  select: [id: string]
  create: []
  rename: [id: string, name: string]
  delete: [id: string]
}>()

const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))

// Mobile drawer toggle
const showMobile = ref(false)
const toggleMobile = () => { showMobile.value = !showMobile.value }
defineExpose({ toggleMobile })

// Sorted sessions
const sorted = computed(() =>
  [...props.sessions].sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )
)

// Search
const searchQuery = ref('')
const filtered = computed(() =>
  searchQuery.value.trim()
    ? sorted.value.filter(s => s.name.toLowerCase().includes(searchQuery.value.toLowerCase()))
    : sorted.value
)

// Rename
const renamingId = ref<string | null>(null)
const renameInput = ref('')
const startRename = (s: Session) => {
  renamingId.value = s.id
  renameInput.value = s.name
}
const confirmRename = (id: string) => {
  if (renameInput.value.trim()) {
    emit('rename', id, renameInput.value.trim())
  }
  renamingId.value = null
}

// Delete confirm
const deletingId = ref<string | null>(null)
const confirmDelete = (id: string) => {
  deletingId.value = null
  emit('delete', id)
}
</script>
```

Wait, I can't use a separate component `SidebarInner` inside the same file without defining it. Vue 3 SFCs with `<script setup>` don't support local component registration easily. Let me just inline everything.

Let me write the complete, self-contained version:

- [ ] **Step 1: Write AppSidebar.vue (complete)**

(See next message for full file — this one is too long for a single step.)

Actually, the plan needs to show the full code. Let me write it all in one step. The template is the bulk of the work.

```vue
<template>
  <!-- Mobile drawer -->
  <Teleport to="body" v-if="isMobile">
    <Transition name="drawer">
      <div v-if="showMobile" class="drawer-overlay" @click.self="showMobile = false">
        <aside class="sidebar" @click.stop>
          <!-- Header -->
          <div class="sidebar-header">
            <div class="sidebar-brand">
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#7c3aed"/><path d="M5 10h4M11 10h4M10 5v4M10 11v4" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>
              <span>AI 智能助手</span>
            </div>
          </div>

          <!-- Search -->
          <div class="sidebar-search">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.5"/><path d="M9.5 9.5L12.5 12.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            <input v-model="searchQuery" placeholder="搜索会话..." class="search-input" />
          </div>

          <!-- Session list -->
          <div class="session-list">
            <div
              v-for="s in filtered"
              :key="s.id"
              class="session-item"
              :class="{ active: s.id === currentSessionId }"
              @click="emit('select', s.id)"
            >
              <!-- Rename mode -->
              <template v-if="renamingId === s.id">
                <input
                  v-model="renameInput"
                  class="rename-input"
                  @keydown.enter="confirmRename(s.id)"
                  @keydown.escape="renamingId = null"
                  @click.stop
                  @blur="confirmRename(s.id)"
                  autofocus
                />
              </template>
              <!-- Normal display -->
              <template v-else>
                <div class="session-info">
                  <div class="session-name">{{ s.name || '新会话' }}</div>
                  <div class="session-meta">
                    <span>{{ s.message_count }} 条</span>
                    <span>{{ formatTime(s.updated_at) }}</span>
                  </div>
                </div>
                <div class="session-actions">
                  <button class="action-btn" @click.stop="startRename(s)" title="重命名">
                    <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 8.5V10h1.5l5.5-5.5L7.5 3 2 8.5zM10.5 3L9 1.5 7.8 2.7l1.5 1.5L10.5 3z" fill="currentColor"/></svg>
                  </button>
                  <button class="action-btn danger" @click.stop="deletingId = s.id" title="删除">
                    <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 3.5h8M4.5 3V2h3v1M3.5 3.5v6.5h5V3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                </div>
              </template>
            </div>

            <div v-if="filtered.length === 0" class="empty-list">
              {{ searchQuery ? '无匹配会话' : '暂无会话' }}
            </div>
          </div>

          <!-- New chat button -->
          <div class="sidebar-footer">
            <button class="new-chat-btn" @click="emit('create')">+ 新对话</button>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>

  <!-- Desktop sidebar — same content, no overlay -->
  <aside v-if="!isMobile" class="sidebar">
    <!-- Header -->
    <div class="sidebar-header">
      <div class="sidebar-brand">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#7c3aed"/><path d="M5 10h4M11 10h4M10 5v4M10 11v4" stroke="#fff" stroke-width="1.5" stroke-linecap="round"/></svg>
        <span>AI 智能助手</span>
      </div>
    </div>

    <div class="sidebar-search">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><circle cx="6" cy="6" r="4.5" stroke="currentColor" stroke-width="1.5"/><path d="M9.5 9.5L12.5 12.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
      <input v-model="searchQuery" placeholder="搜索会话..." class="search-input" />
    </div>

    <div class="session-list">
      <div
        v-for="s in filtered"
        :key="s.id"
        class="session-item"
        :class="{ active: s.id === currentSessionId }"
        @click="emit('select', s.id)"
      >
        <template v-if="renamingId === s.id">
          <input
            v-model="renameInput"
            class="rename-input"
            @keydown.enter="confirmRename(s.id)"
            @keydown.escape="renamingId = null"
            @click.stop
            @blur="confirmRename(s.id)"
            autofocus
          />
        </template>
        <template v-else>
          <div class="session-info">
            <div class="session-name">{{ s.name || '新会话' }}</div>
            <div class="session-meta">
              <span>{{ s.message_count }} 条</span>
              <span>{{ formatTime(s.updated_at) }}</span>
            </div>
          </div>
          <div class="session-actions">
            <button class="action-btn" @click.stop="startRename(s)" title="重命名">
              <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 8.5V10h1.5l5.5-5.5L7.5 3 2 8.5zM10.5 3L9 1.5 7.8 2.7l1.5 1.5L10.5 3z" fill="currentColor"/></svg>
            </button>
            <button class="action-btn danger" @click.stop="deletingId = s.id" title="删除">
              <svg width="12" height="12" viewBox="0 0 12 12"><path d="M2 3.5h8M4.5 3V2h3v1M3.5 3.5v6.5h5V3.5" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
        </template>
      </div>

      <div v-if="filtered.length === 0" class="empty-list">
        {{ searchQuery ? '无匹配会话' : '暂无会话' }}
      </div>
    </div>

    <div class="sidebar-footer">
      <button class="new-chat-btn" @click="emit('create')">+ 新对话</button>
    </div>
  </aside>

  <!-- Delete confirm modal -->
  <Teleport to="body">
    <div v-if="deletingId" class="modal-overlay" @click.self="deletingId = null">
      <div class="modal-card">
        <h3>删除会话</h3>
        <p>确定要删除这个会话吗？此操作不可撤销。</p>
        <div class="modal-btns">
          <button class="modal-btn cancel" @click="deletingId = null">取消</button>
          <button class="modal-btn danger-btn" @click="confirmDelete(deletingId!)">删除</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

export interface Session {
  id: string
  name: string
  preview?: string
  message_count: number
  created_at: string
  updated_at: string
}

const props = defineProps<{
  sessions: Session[]
  currentSessionId: string | null
}>()

const emit = defineEmits<{
  select: [id: string]
  create: []
  rename: [id: string, name: string]
  delete: [id: string]
}>()

// Mobile detection
const isMobile = ref(false)
const checkMobile = () => { isMobile.value = window.innerWidth < 768 }
onMounted(() => { checkMobile(); window.addEventListener('resize', checkMobile) })
onUnmounted(() => window.removeEventListener('resize', checkMobile))

const showMobile = ref(false)
const toggleMobile = () => { showMobile.value = !showMobile.value }
defineExpose({ toggleMobile })

// Search
const searchQuery = ref('')
const sorted = computed(() =>
  [...props.sessions].sort((a, b) =>
    new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )
)
const filtered = computed(() =>
  searchQuery.value.trim()
    ? sorted.value.filter(s => (s.name || '').toLowerCase().includes(searchQuery.value.toLowerCase()))
    : sorted.value
)

// Rename
const renamingId = ref<string | null>(null)
const renameInput = ref('')
const startRename = (s: Session) => { renamingId.value = s.id; renameInput.value = s.name || '' }
const confirmRename = (id: string) => {
  const name = renameInput.value.trim()
  if (name) emit('rename', id, name)
  renamingId.value = null
}

// Delete
const deletingId = ref<string | null>(null)
const confirmDelete = (id: string) => { emit('delete', id); deletingId.value = null }

// Time formatting
const formatTime = (ts: string) => {
  if (!ts) return ''
  const diff = Date.now() - new Date(ts).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 1) return '刚刚'
  if (m < 60) return `${m}分钟前`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}小时前`
  return `${Math.floor(h / 24)}天前`
}
</script>

<style scoped>
/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  height: 100dvh;
  background: var(--bg-surface);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-drawer {
  width: 280px;
  box-shadow: var(--shadow-lg);
}

.sidebar-header {
  padding: var(--space-4) var(--space-4) var(--space-3);
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Search */
.sidebar-search {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  margin: 0 var(--space-3) var(--space-3);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  background: var(--bg-primary);
  color: var(--text-tertiary);
}

.search-input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-sans);
  outline: none;
}

.search-input::placeholder { color: var(--text-tertiary); }

/* Session list */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 var(--space-2);
}

.session-item {
  display: flex;
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 2px;
}

.session-item:hover { background: var(--bg-elevated); }
.session-item.active {
  background: var(--accent-primary-bg);
  border: 1px solid var(--accent-primary);
}

.session-info { flex: 1; min-width: 0; }
.session-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  gap: var(--space-2);
  font-size: 11px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.session-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
}

.session-item:hover .session-actions { display: flex; }

.action-btn {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.action-btn:hover { background: var(--accent-primary-bg); color: var(--accent-primary); }
.action-btn.danger:hover { background: var(--color-destructive-bg); color: var(--color-destructive); }

.rename-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid var(--accent-primary);
  border-radius: var(--radius-sm);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: 13px;
  font-family: var(--font-sans);
  outline: none;
}

.empty-list {
  text-align: center;
  padding: var(--space-8) var(--space-4);
  color: var(--text-tertiary);
  font-size: 13px;
}

/* Footer */
.sidebar-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--border-default);
  flex-shrink: 0;
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: var(--accent-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.new-chat-btn:hover { background: var(--accent-primary-hover); }

/* Mobile drawer */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 200;
}

.drawer-enter-active { transition: opacity 0.25s ease; }
.drawer-enter-active .sidebar { transition: transform 0.25s cubic-bezier(0.4,0,0.2,1); }
.drawer-leave-active { transition: opacity 0.2s ease; }
.drawer-leave-active .sidebar { transition: transform 0.2s ease; }
.drawer-enter-from { opacity: 0; }
.drawer-enter-from .sidebar { transform: translateX(-100%); }
.drawer-leave-to { opacity: 0; }
.drawer-leave-to .sidebar { transform: translateX(-100%); }

/* Delete modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
}

.modal-card {
  background: var(--bg-surface);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  width: 90%;
  max-width: 360px;
  box-shadow: var(--shadow-lg);
}

.modal-card h3 {
  margin-bottom: var(--space-3);
  font-size: 16px;
  color: var(--text-primary);
}

.modal-card p {
  margin-bottom: var(--space-5);
  font-size: 13px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.modal-btns {
  display: flex;
  gap: var(--space-3);
  justify-content: flex-end;
}

.modal-btn {
  padding: 8px 18px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.modal-btn.cancel {
  background: transparent;
  border: 1px solid var(--border-default);
  color: var(--text-secondary);
}

.modal-btn.cancel:hover { background: var(--bg-elevated); }

.modal-btn.danger-btn {
  background: var(--color-destructive);
  border: none;
  color: #fff;
}

.modal-btn.danger-btn:hover { background: var(--color-destructive-hover); }
</style>
```

- [ ] **Step 2: Create types.ts**

We need a shared `Session` type. Create `frontend/src/types.ts`:

```typescript
export interface Session {
  id: string
  name: string
  preview?: string
  message_count: number
  created_at: string
  updated_at: string
}

export interface AgentStep {
  thought?: string
  tool: string
  tool_input: string
  observation: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  steps?: AgentStep[]
}
```

- [ ] **Step 3: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 3`

Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/AppSidebar.vue frontend/src/types.ts
git commit -m "feat: add AppSidebar — session list, search, rename, delete, mobile drawer

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: Create ChatView.vue

**Files:**
- Create: `frontend/src/components/ChatView.vue`

- [ ] **Step 1: Write ChatView.vue**

This is the core orchestration component, inheriting the SSE streaming logic from ChatAssistant.vue.

```vue
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
      ref="messageListRef"
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
      ref="inputRef"
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
    streamingStep: '执行中...',
  },
  en: {
    welcomeTitle: 'How can I help you?',
    welcomeDesc: 'Weather, Q&A, summarize, translate, and code explanation',
    placeholder: 'Type a message...',
    errorDefault: 'Request failed. Please try again.',
    streamingStep: 'Running...',
  },
}
const t = (key: string) => tr[props.locale]?.[key] || tr.zh[key] || key

// --- Suggestion cards ---
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

// Sidebar toggle for mobile (injected from App.vue)
const toggleSidebar = inject<() => void>('toggleSidebar', () => {})
const isMobile = ref(false)
onMounted(() => { isMobile.value = window.innerWidth < 768 })

// --- SSE streaming ---
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
            if (eventType === 'token') {
              messages.value[msgIdx].content += dataStr
            }
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
      if (streamingSteps.value.length > 0) {
        streamingSteps.value[streamingSteps.value.length - 1].observation = data.output || ''
      }
      messages.value[msgIdx].steps = [...streamingSteps.value]
      break
    case 'error':
      messages.value[msgIdx].content += `\n\n[${t('errorDefault')}: ${data.message || ''}]`
      break
  }
}

// --- Other actions ---
const quickAsk = (query: string) => {
  sendMessage(query)
}

const clearHistory = async () => {
  try {
    await fetch('/api/history/clear?session_id=' + (props.currentSessionId || ''), { method: 'POST' })
    messages.value = []
  } catch { /* silent */ }
}

const onToggleStep = (msgIdx: number, stepIdx: number) => {
  if (!expandedSteps.value[msgIdx]) expandedSteps.value[msgIdx] = {}
  expandedSteps.value[msgIdx][stepIdx] = !expandedSteps.value[msgIdx][stepIdx]
}

const onDocChanged = () => {}

// --- Session-based init ---
const currentSession = computed(() =>
  props.sessions.find(s => s.id === props.currentSessionId) || null
)

const initMessages = () => {
  messages.value = []
  // Welcome message
  if (props.locale === 'zh') {
    messages.value.push({
      role: 'assistant',
      content: '👋 欢迎使用 AI 智能助手！\n\n我支持以下功能：\n- **天气查询**：询问天气和穿衣建议\n- **问答**：回答各类问题\n- **总结**：总结长文本内容\n- **翻译**：多语言翻译\n- **代码解释**：解释代码逻辑\n\n请直接输入您的问题！',
    })
  }
}

onMounted(initMessages)

// Listen for session changes from parent (App.vue will re-mount or we watch)
watch(() => props.currentSessionId, async (newId) => {
  messages.value = []
  if (!newId) { initMessages(); return }
  try {
    const res = await fetch(`/api/sessions/${newId}/history`)
    const data = await res.json()
    if (data.messages?.length > 0) {
      messages.value = data.messages
    } else {
      initMessages()
    }
  } catch {
    initMessages()
  }
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

/* Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--space-6);
  height: 52px;
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.hamburger {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hamburger:hover { background: var(--bg-elevated); color: var(--text-primary); }

.header-title h2 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-right {
  display: flex;
  gap: var(--space-1);
}

.header-btn {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.header-btn:hover:not(:disabled) { background: var(--bg-elevated); color: var(--text-primary); }
.header-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* KB drawer */
.kb-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 300;
  display: flex;
  justify-content: flex-end;
}

.kb-drawer {
  width: 420px;
  max-width: 92vw;
  height: 100dvh;
  overflow-y: auto;
  background: var(--bg-surface);
  box-shadow: var(--shadow-lg);
  padding: var(--space-6);
  position: relative;
}

.kb-close-btn {
  position: absolute;
  top: var(--space-4);
  right: var(--space-4);
  width: 32px;
  height: 32px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--bg-surface);
  color: var(--text-tertiary);
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kb-close-btn:hover { background: var(--bg-elevated); }

@media (max-width: 768px) {
  .chat-header { padding: 0 var(--space-4); }
}
</style>
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 5`

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ChatView.vue
git commit -m "feat: add ChatView — SSE streaming orchestrator, i18n, suggestions

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: Rewrite App.vue as layout shell

**Files:**
- Modify: `frontend/src/App.vue`

- [ ] **Step 1: Rewrite App.vue**

Delete the old single-component App.vue, replace with sidebar + chat layout:

```vue
<script setup lang="ts">
import { ref, provide } from 'vue'
import AppSidebar from './components/AppSidebar.vue'
import ChatView from './components/ChatView.vue'
import type { Session } from './types'

const locale = ref<'zh' | 'en'>('zh')
provide('locale', locale)

const sidebarRef = ref<InstanceType<typeof AppSidebar>>()
provide('toggleSidebar', () => sidebarRef.value?.toggleMobile())

const sessions = ref<Session[]>([])
const currentSessionId = ref<string | null>(null)

const loadSessions = () => {
  try {
    const saved = localStorage.getItem('ai-chat-sessions')
    if (saved) sessions.value = JSON.parse(saved)
    const cur = localStorage.getItem('ai-chat-current-session')
    if (cur) currentSessionId.value = cur
  } catch { /* ignore */ }
}

const saveSessions = () => {
  localStorage.setItem('ai-chat-sessions', JSON.stringify(sessions.value))
  if (currentSessionId.value) localStorage.setItem('ai-chat-current-session', currentSessionId.value)
}

const generateId = () => crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
  const r = Math.random() * 16 | 0
  return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
})

// --- Session CRUD ---
const onCreateSession = () => {
  const now = new Date().toISOString()
  const s: Session = { id: generateId(), name: '新会话', message_count: 0, created_at: now, updated_at: now }
  sessions.value.unshift(s)
  saveSessions()
  currentSessionId.value = s.id
}

const onSelectSession = (id: string) => {
  currentSessionId.value = id
  localStorage.setItem('ai-chat-current-session', id)
}

const onRenameSession = async (id: string, name: string) => {
  const s = sessions.value.find(x => x.id === id)
  if (!s) return
  s.name = name
  s.updated_at = new Date().toISOString()
  saveSessions()
  try { await fetch(`/api/sessions/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) }) } catch { /* silent */ }
}

const onDeleteSession = async (id: string) => {
  sessions.value = sessions.value.filter(x => x.id !== id)
  saveSessions()
  try { await fetch(`/api/sessions/${id}`, { method: 'DELETE' }) } catch { /* silent */ }
  if (currentSessionId.value === id) {
    currentSessionId.value = sessions.value[0]?.id || null
    if (currentSessionId.value) localStorage.setItem('ai-chat-current-session', currentSessionId.value)
  }
}

// Init
loadSessions()
if (!currentSessionId.value && sessions.value.length === 0) {
  onCreateSession()
}
</script>

<template>
  <div class="app-root">
    <AppSidebar
      ref="sidebarRef"
      :sessions="sessions"
      :current-session-id="currentSessionId"
      @select="onSelectSession"
      @create="onCreateSession"
      @rename="onRenameSession"
      @delete="onDeleteSession"
    />
    <ChatView
      :sessions="sessions"
      :current-session-id="currentSessionId"
      :locale="locale"
    />
  </div>
</template>

<style>
.app-root {
  display: flex;
  height: 100dvh;
  overflow: hidden;
  background: var(--bg-primary);
}
</style>
```

- [ ] **Step 2: Verify Vite compiles**

Run: `docker logs ai-proj-frontend-1 --tail 5`

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.vue
git commit -m "feat: rewrite App.vue as layout shell — sidebar + chat view

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: Remove ChatAssistant.vue and update dependent components

**Files:**
- Delete: `frontend/src/components/ChatAssistant.vue`
- Delete: `frontend/src/components/HelloWorld.vue`
- Modify: `frontend/src/components/KnowledgePanel.vue` — update CSS variables
- Modify: `frontend/src/components/SettingsModal.vue` — update CSS variables

- [ ] **Step 1: Delete ChatAssistant.vue**

```bash
rm frontend/src/components/ChatAssistant.vue
rm frontend/src/components/HelloWorld.vue
```

- [ ] **Step 2: Verify everything compiles**

Run: `docker logs ai-proj-frontend-1 --tail 10`

Expected: Vite running, no import errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/
git commit -m "refactor: remove ChatAssistant.vue, replaced by component split

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 10: Smoke test the app

- [ ] **Step 1: Open the app in browser and verify**

Expected behavior:
- Sidebar visible on desktop (260px), hidden on mobile
- Click "新对话" creates a new session
- Type a message and send — SSE streaming works
- Dark theme by default
- Mobile hamburger menu opens sidebar drawer
- Settings modal opens
- Knowledge panel opens

- [ ] **Step 2: Verify all containers healthy**

Run: `docker ps --filter "name=ai-proj" --format "table {{.Names}}\t{{.Status}}"`

Expected: all 3 containers Up.

- [ ] **Step 3: Commit any final fixups**

```bash
git add -A
git commit -m "chore: final cleanup after frontend refactor

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```
