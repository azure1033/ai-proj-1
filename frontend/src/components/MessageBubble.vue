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
