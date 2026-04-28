<template>
  <div class="app-layout">
    <!-- 侧边栏切换按钮 (移动端) -->
    <button class="sidebar-toggle" @click="showSidebar = !showSidebar">
      {{ showSidebar ? '✕' : '☰' }}
    </button>

    <!-- 会话列表侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: !showSidebar }">
      <div class="sidebar-header">
        <h2>{{ t('sessionList') }}</h2>
        <button class="new-session-btn" @click="createNewSession" :disabled="isLoading">
          + {{ t('newChat') }}
        </button>
      </div>
      <div class="session-list">
        <div
          v-for="session in sortedSessions"
          :key="session.id"
          class="session-item"
          :class="{ active: session.id === currentSessionId }"
          @click="switchSession(session.id)"
        >
          <div class="session-info">
            <div class="session-name">{{ session.name || t('newChat') }}</div>
            <div class="session-preview">{{ session.preview || '...' }}</div>
            <div class="session-meta">
              <span>{{ session.message_count }} {{ t('messages') }}</span>
              <span>{{ formatTime(session.updated_at) }}</span>
            </div>
          </div>
          <div class="session-actions" @click.stop>
            <button class="action-icon" @click="openRenameModal(session)" :title="t('rename')">✏️</button>
            <button class="action-icon delete" @click="openDeleteModal(session)" :title="t('delete')">🗑️</button>
          </div>
        </div>
        <div v-if="sessions.length === 0" class="empty-state">
          <p>{{ t('noSessions') }}</p>
        </div>
      </div>
    </aside>

    <!-- 主聊天区域 -->
    <section class="chat-container">
      <!-- 顶部栏 -->
      <header class="chat-header">
      <div class="header-left">
        <h1>{{ t('title') }}</h1>
        <p>{{ t('description') }}</p>
      </div>
      <div class="header-right">
        <div class="language-switcher">
          <button
            v-for="item in locales"
            :key="item.value"
            :class="['lang-btn', { active: locale === item.value }]"
            @click="locale = item.value"
          >
            {{ item.label }}
          </button>
        </div>
      </div>
    </header>

    <!-- 消息区域 -->
    <div class="messages-area" ref="messagesAreaRef">
      <div
        v-for="(message, idx) in messages"
        :key="idx"
        class="message-wrapper"
        :class="message.role"
      >
        <!-- 头像 -->
        <div class="message-avatar">
          {{ message.role === 'user' ? '👤' : '🤖' }}
        </div>

        <!-- 消息内容 -->
        <div class="message-content">
          <!-- 意图标签 -->
          <div v-if="message.role === 'assistant' && message.intent" class="intent-badge">
            {{ intentLabel(message.intent) }}
          </div>

          <!-- Agent 步骤 (可折叠) - 支持流式更新 -->
          <div v-if="message.role === 'assistant' && message.steps && message.steps.length > 0" class="agent-steps">
            <div
              v-for="(step, si) in message.steps"
              :key="si"
              class="step-item streaming"
              :class="{ expanded: expandedSteps[idx]?.[si] }"
            >
              <div class="step-header" @click="toggleStep(idx, si)">
                <span class="step-icon">{{ expandedSteps[idx]?.[si] ? '▼' : '▶' }}</span>
                <span class="step-tool">{{ formatToolName(step.tool) }}</span>
                <span v-if="step.observation" class="step-check">✓</span>
                <span v-else class="step-spinner">⏳</span>
              </div>
              <div v-if="expandedSteps[idx]?.[si]" class="step-detail">
                <div class="step-input"><strong>{{ t('input') }}:</strong> {{ step.tool_input }}</div>
                <div class="step-output"><strong>{{ t('output') }}:</strong> {{ step.observation || t('streamingStep') + '...' }}</div>
              </div>
            </div>
          </div>

          <!-- 消息文本 (支持 Markdown) -->
          <div
            class="message-bubble"
            :class="{ streaming: isLoading && idx === messages.length - 1 && message.role === 'assistant' }"
            v-html="renderMarkdown(message.content)"
          ></div>
          <!-- 流式光标 -->
          <span v-if="isLoading && idx === messages.length - 1 && message.role === 'assistant'" class="streaming-cursor">▊</span>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="message-wrapper assistant">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <div ref="messagesEndRef"></div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <textarea
        v-model="userInput"
        :placeholder="t('placeholder')"
        rows="2"
        @keydown.enter.ctrl="sendMessage"
        @keydown.enter.meta="sendMessage"
        :disabled="isLoading"
      ></textarea>
      <button class="send-btn" @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        <span v-if="isLoading">{{ t('sending') }}</span>
        <span v-else>{{ t('send') }}</span>
      </button>
    </div>

<!-- 快捷操作栏 -->
      <div class="quick-actions">
        <div class="action-left">
          <button class="action-btn" @click="clearHistory" :disabled="isLoading">
            {{ t('clearHistory') }}
          </button>
          <button class="action-btn" @click="toggleDocuments" :disabled="isLoading">
            {{ t('uploadDocumentLabel') }}
          </button>
        </div>

        <div class="action-right">
          <button
            v-for="example in examples[locale]"
            :key="example.key"
            class="example-btn"
            @click="quickAsk(example.query)"
          >
            {{ example.label }}
          </button>
        </div>
      </div>

      <!-- 文档上传面板 (可折叠) -->
      <div v-if="showDocuments" class="documents-panel">
        <div class="panel-header">
          <h3>{{ t('uploadDocumentLabel') }}</h3>
          <button class="close-btn" @click="showDocuments = false">×</button>
        </div>
        <div class="panel-content">
          <input type="file" accept=".txt,.pdf,.docx" @change="handleFileChange" />
          <button class="upload-btn" @click="uploadDocument" :disabled="!documentFile || isLoading">
            {{ t('uploadButton') }}
          </button>
          <span class="upload-status">{{ uploadStatus }}</span>
        </div>
        <div v-if="documents.length > 0" class="document-list">
          <h4>{{ t('docsLoaded') }}</h4>
          <ul>
            <li v-for="doc in documents" :key="doc.id">
              <span class="doc-name">{{ doc.filename }}</span>
              <button class="remove-btn" @click="removeDocument(doc.id)">×</button>
            </li>
          </ul>
          <button class="clear-docs-btn" @click="clearDocuments">
            {{ t('clearDocuments') }}
          </button>
        </div>
      </div>
    </section>

    <!-- 重命名弹窗 -->
    <div v-if="showRenameModal" class="modal-overlay" @click.self="showRenameModal = false">
      <div class="modal">
        <h3>{{ t('renameSession') }}</h3>
        <input
          v-model="renameInput"
          type="text"
          :placeholder="t('sessionNamePlaceholder')"
          @keydown.enter="confirmRename"
          ref="renameInputRef"
        />
        <div class="modal-actions">
          <button class="cancel-btn" @click="showRenameModal = false">{{ t('cancel') }}</button>
          <button class="confirm-btn" @click="confirmRename">{{ t('confirm') }}</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <h3>{{ t('deleteSession') }}</h3>
        <p>{{ t('confirmDelete') }}</p>
        <div class="modal-actions">
          <button class="cancel-btn" @click="showDeleteModal = false">{{ t('cancel') }}</button>
          <button class="confirm-btn danger" @click="confirmDelete">{{ t('delete') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted, computed } from 'vue'
import { marked } from 'marked'
import axios from 'axios'

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

interface Message {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  steps?: AgentStep[]
}

interface AgentStep {
  thought: string
  tool: string
  tool_input: string
  observation: string
}

interface Session {
  id: string
  name: string
  preview: string
  message_count: number
  created_at: string
  updated_at: string
}

// 生成 UUID
const generateId = () => {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

// 格式化相对时间
const formatTime = (dateStr: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (minutes < 1) return locale.value === 'zh' ? '刚刚' : 'Just now'
  if (minutes < 60) return `${minutes}m`
  if (hours < 24) return `${hours}h`
  if (days < 7) return `${days}d`
  return date.toLocaleDateString()
}

const locale = ref<'zh' | 'en'>('zh')
const locales = [
  { value: 'zh' as const, label: '中文' },
  { value: 'en' as const, label: 'English' },
]

// 国际化
const translations: Record<string, Record<string, string>> = {
  zh: {
    title: 'AI 智能助手',
    description: '支持天气查询、问答、总结、翻译和代码解释',
    placeholder: '输入您的问题...',
    send: '发送',
    sending: '处理中...',
    clearHistory: '清空聊天',
    uploadDocumentLabel: '上传文档',
    uploadButton: '上传',
    clearDocuments: '清空',
    docsLoaded: '已加载：',
    noDocuments: '未上传文档',
    welcomeMessage:
      '👋 欢迎使用 AI 智能助手！\n\n我支持以下功能：\n- **天气查询**：询问天气和穿衣建议\n- **问答**：回答各类问题\n- **总结**：总结长文本内容\n- **翻译**：多语言翻译\n- **代码解释**：解释代码逻辑\n\n请直接输入您的问题！',
    // 会话相关
    sessionList: '会话列表',
    newChat: '新会话',
    noSessions: '暂无会话',
    messages: '条消息',
    rename: '重命名',
    delete: '删除',
    renameSession: '重命名会话',
    deleteSession: '删除会话',
    confirmDelete: '确定要删除这个会话吗？此操作不可撤销。',
    cancel: '取消',
    confirm: '确认',
    deleteLastSession: '无法删除最后一个会话',
    sessionNamePlaceholder: '输入会话名称...',
    // Agent 相关
    input: '输入',
    output: '输出',
    agentThinking: '正在思考...',
    agentCallingTool: '调用工具...',
    streamingStep: '正在执行',
    streamingDone: '完成',
    errorDefault: '请求失败，请稍后重试。',
  },
  en: {
    title: 'AI Assistant',
    description: 'Supports weather, Q&A, summarize, translate and code explanation',
    placeholder: 'Type your question...',
    send: 'Send',
    sending: 'Processing...',
    clearHistory: 'Clear',
    uploadDocumentLabel: 'Upload',
    uploadButton: 'Upload',
    clearDocuments: 'Clear',
    docsLoaded: 'Loaded:',
    noDocuments: 'No documents',
    welcomeMessage:
      '👋 Welcome to AI Assistant!\n\nI support:\n- **Weather**: weather and clothing advice\n- **Q&A**: answer questions\n- **Summarize**: summarize text\n- **Translate**: multilingual translation\n- **Code**: explain code\n\nAsk me anything!',
    sessionList: 'Sessions',
    newChat: 'New Chat',
    noSessions: 'No sessions',
    messages: 'messages',
    rename: 'Rename',
    delete: 'Delete',
    renameSession: 'Rename Session',
    deleteSession: 'Delete Session',
    confirmDelete: 'Are you sure you want to delete this session? This cannot be undone.',
    cancel: 'Cancel',
    confirm: 'Confirm',
    deleteLastSession: 'Cannot delete the last session',
    sessionNamePlaceholder: 'Enter session name...',
    input: 'Input',
    output: 'Output',
    agentThinking: 'Thinking...',
    agentCallingTool: 'Calling tool...',
    streamingStep: 'Running',
    streamingDone: 'Done',
    errorDefault: 'Request failed. Please try again.',
  },
}

// 意图标签
const intentLabels: Record<string, Record<string, string>> = {
  zh: {
    '天气查询': '🌤️ 天气',
    '问答': '💬 问答',
    '总结': '📝 总结',
    '翻译': '🌐 翻译',
    '代码解释': '💻 代码',
    '文档问答': '📄 文档',
    '错误': '❌ 错误',
  },
  en: {
    '天气查询': '🌤️ Weather',
    '问答': '💬 Q&A',
    '总结': '📝 Summary',
    '翻译': '🌐 Translate',
    '代码解释': '💻 Code',
    '文档问答': '📄 Document',
    '错误': '❌ Error',
  },
}

// 快捷示例
const examples = computed(() => ({
  zh: [
    { key: 'weather', label: '🌤️ 天气', query: '今天合肥天气如何？' },
    { key: 'qa', label: '💬 问答', query: '什么是人工智能？' },
    { key: 'translate', label: '🌐 翻译', query: '请翻译：Hello world' },
    { key: 'summarize', label: '📝 总结', query: '请总结：人工智能是模拟人类智能的技术。' },
  ],
  en: [
    { key: 'weather', label: '🌤️ Weather', query: 'How is the weather today?' },
    { key: 'qa', label: '💬 Q&A', query: 'What is AI?' },
    { key: 'translate', label: '🌐 Translate', query: 'Translate: Hello world' },
    { key: 'summarize', label: '📝 Summary', query: 'Summarize: Artificial intelligence is...' },
  ],
}))

// 状态
const userInput = ref('')
const messages = ref<Message[]>([])
const isLoading = ref(false)
const documentFile = ref<File | null>(null)
const documents = ref<Array<{ id: string; filename: string; uploaded_at: string }>>([])
const uploadStatus = ref('')
const messagesEndRef = ref<HTMLElement>()
const showDocuments = ref(false)

// 会话状态
const sessions = ref<Session[]>([])
const currentSessionId = ref<string | null>(null)
const showSidebar = ref(true)
const showRenameModal = ref(false)
const showDeleteModal = ref(false)
const renameInput = ref('')
const renameTargetId = ref<string | null>(null)
const deleteTargetId = ref<string | null>(null)
const renameInputRef = ref<HTMLInputElement>()

// Agent 步骤展开状态 (messageIndex → {stepIndex → boolean})
const expandedSteps = ref<Record<number, Record<number, boolean>>>({})

// 格式化工具名称
const formatToolName = (tool: string): string => {
  const names: Record<string, string> = {
    get_weather: '🌤️ ' + (locale.value === 'zh' ? '查询天气' : 'Weather'),
    web_search: '🔍 ' + (locale.value === 'zh' ? '网页搜索' : 'Web Search'),
    summarize_text: '📝 ' + (locale.value === 'zh' ? '文本总结' : 'Summarize'),
    translate_text: '🌐 ' + (locale.value === 'zh' ? '文本翻译' : 'Translate'),
    explain_code: '💻 ' + (locale.value === 'zh' ? '代码解释' : 'Code'),
    calculator: '🧮 ' + (locale.value === 'zh' ? '计算器' : 'Calculator'),
  }
  return names[tool] || tool
}

// 切换步骤展开/收起
const toggleStep = (msgIdx: number, stepIdx: number) => {
  if (!expandedSteps.value[msgIdx]) {
    expandedSteps.value[msgIdx] = {}
  }
  expandedSteps.value[msgIdx][stepIdx] = !expandedSteps.value[msgIdx][stepIdx]
}

// 会话排序 (按更新时间倒序)
const sortedSessions = computed(() => {
  return [...sessions.value].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  )
})

// Markdown 渲染
const renderMarkdown = (content: string) => {
  try {
    return marked.parse(content) as string
  } catch {
    return content
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
}

watch(messages, scrollToBottom, { deep: true })

// 初始化欢迎消息
const initWelcome = () => {
  if (messages.value.length === 0) {
    messages.value.push({
      role: 'assistant',
      content: t('welcomeMessage'),
    })
  }
}

const t = (key: string) => translations[locale.value]?.[key] || translations.zh[key] || key
const intentLabel = (intent: string) => intentLabels[locale.value]?.[intent] || intentLabels.zh[intent] || intent

// 加载会话列表
const loadSessions = () => {
  try {
    const saved = localStorage.getItem('ai-chat-sessions')
    if (saved) {
      sessions.value = JSON.parse(saved)
    }
    const currentId = localStorage.getItem('ai-chat-current-session')
    if (currentId) {
      currentSessionId.value = currentId
    }
  } catch {
    sessions.value = []
  }
}

// 保存会话列表
const saveSessions = () => {
  localStorage.setItem('ai-chat-sessions', JSON.stringify(sessions.value))
  if (currentSessionId.value) {
    localStorage.setItem('ai-chat-current-session', currentSessionId.value)
  }
}

// 创建新会话
const createNewSession = () => {
  const newSession: Session = {
    id: generateId(),
    name: '',
    preview: '',
    message_count: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  sessions.value.unshift(newSession)
  saveSessions()
  switchSession(newSession.id)
}

// 切换会话
const switchSession = async (sessionId: string) => {
  currentSessionId.value = sessionId
  localStorage.setItem('ai-chat-current-session', sessionId)
  messages.value = []

  try {
    const res = await axios.get(`http://localhost:8000/sessions/${sessionId}/history`)
    const history = res.data.messages || []
    if (history.length === 0) {
      initWelcome()
    } else {
      messages.value = history
    }

    // 同步更新 session metadata (message_count)
    const session = sessions.value.find((s) => s.id === sessionId)
    if (session) {
      session.message_count = history.length
      if (history.length > 0) {
        const firstUser = history.find((m: Message) => m.role === 'user')
        if (firstUser) {
          session.preview = firstUser.content.length > 30
            ? firstUser.content.substring(0, 30) + '...'
            : firstUser.content
        }
      }
      session.updated_at = new Date().toISOString()
      saveSessions()
    }
  } catch (err) {
    console.error('加载会话历史失败:', err)
    initWelcome()
  }

  await nextTick()
  scrollToBottom()
}

// 重命名会话
const openRenameModal = (session: Session) => {
  renameTargetId.value = session.id
  renameInput.value = session.name || ''
  showRenameModal.value = true
  nextTick(() => renameInputRef.value?.focus())
}

const confirmRename = async () => {
  if (!renameTargetId.value || !renameInput.value.trim()) return

  const session = sessions.value.find((s) => s.id === renameTargetId.value)
  if (session) {
    session.name = renameInput.value.trim()
    session.updated_at = new Date().toISOString()
    saveSessions()
    try {
      await axios.patch(`http://localhost:8000/sessions/${renameTargetId.value}`, {
        name: renameInput.value.trim(),
      })
    } catch {
      // 静默失败，前端已更新
    }
  }

  showRenameModal.value = false
  renameTargetId.value = null
  renameInput.value = ''
}

// 删除会话
const openDeleteModal = (session: Session) => {
  deleteTargetId.value = session.id
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  if (!deleteTargetId.value) return

  // 检查是否是最后一个会话
  if (sessions.value.length <= 1) {
    alert(t('deleteLastSession'))
    showDeleteModal.value = false
    deleteTargetId.value = null
    return
  }

  const wasCurrent = currentSessionId.value === deleteTargetId.value
  sessions.value = sessions.value.filter((s) => s.id !== deleteTargetId.value)
  saveSessions()

  try {
    await axios.delete(`http://localhost:8000/sessions/${deleteTargetId.value}`)
  } catch {
    // 静默失败
  }

  if (wasCurrent) {
    // 切换到第一个会话
    const nextSession = sortedSessions.value[0]
    if (nextSession) {
      await switchSession(nextSession.id)
    }
  }

  showDeleteModal.value = false
  deleteTargetId.value = null
}

// 发送消息
const sendMessageStream = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const query = userInput.value.trim()
  userInput.value = ''

  messages.value.push({ role: 'user', content: query })
  isLoading.value = true

  // 创建占位的 assistant 消息
  const assistantMsg: Message = { role: 'assistant', content: '', steps: [] }
  messages.value.push(assistantMsg)
  const msgIndex = messages.value.length - 1

  // 更新会话 preview
  if (currentSessionId.value) {
    const session = sessions.value.find((s) => s.id === currentSessionId.value)
    if (session) {
      session.preview = query.length > 30 ? query.substring(0, 30) + '...' : query
      session.updated_at = new Date().toISOString()
    }
  }

  try {
    const response = await fetch(`http://localhost:8000/ask?stream=true`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: currentSessionId.value }),
    })

    if (!response.ok) throw new Error(`HTTP ${response.status}`)

    const reader = response.body!.getReader()
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
            handleSSEEvent(msgIndex, eventType, data)
          } catch {
            // 纯文本 token
            if (eventType === 'token') {
              messages.value[msgIndex].content += dataStr
              await nextTick()
            }
          }
          eventType = ''
        }
      }
    }
  } catch (error: any) {
    messages.value[msgIndex].content = error.message || t('errorDefault')
  } finally {
    isLoading.value = false
    messages.value[msgIndex].steps = [...streamingSteps.value]
    streamingSteps.value = []

    // 更新会话计数
    if (currentSessionId.value) {
      const session = sessions.value.find((s) => s.id === currentSessionId.value)
      if (session) {
        session.message_count = messages.value.length
        session.updated_at = new Date().toISOString()
        saveSessions()
      }
    }
  }
}

// SSE 事件处理
const streamingSteps = ref<AgentStep[]>([])

const handleSSEEvent = (msgIndex: number, eventType: string, data: any) => {
  switch (eventType) {
    case 'token':
      messages.value[msgIndex].content += data
      break
    case 'step':
      streamingSteps.value.push({
        thought: '',
        tool: data.tool || 'unknown',
        tool_input: data.input || '',
        observation: '',
      })
      messages.value[msgIndex].steps = [...streamingSteps.value]
      break
    case 'step_done':
      const last = streamingSteps.value[streamingSteps.value.length - 1]
      if (last) {
        last.observation = data.output || ''
      }
      messages.value[msgIndex].steps = [...streamingSteps.value]
      break
    case 'error':
      messages.value[msgIndex].content += `\n\n[${t('errorDefault')}: ${data.message || ''}]`
      break
  }
}

// 发送消息 (入口)
const sendMessage = () => sendMessageStream()

// 加载文档
const fetchDocuments = async () => {
  try {
    const res = await axios.get('http://localhost:8000/documents')
    documents.value = res.data.documents || []
  } catch {
    documents.value = []
  }
}

// 清空历史
const clearHistory = async () => {
  try {
    await axios.delete('http://localhost:8000/history')
    messages.value = []
    initWelcome()
  } catch (error) {
    console.error('清除历史失败：', error)
  }
}

// 切换文档面板
const toggleDocuments = () => {
  showDocuments.value = !showDocuments.value
}

// 文件选择
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    documentFile.value = target.files[0]
  }
}

// 上传文档
const uploadDocument = async () => {
  if (!documentFile.value) return
  const formData = new FormData()
  formData.append('file', documentFile.value)
  uploadStatus.value = '上传中...'
  try {
    await axios.post('http://localhost:8000/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    uploadStatus.value = '✓ 上传成功'
    documentFile.value = null
    await fetchDocuments()
  } catch (error: any) {
    uploadStatus.value = error?.response?.data?.detail || '上传失败'
  }
}

// 移除文档 (后端暂不支持单个删除)
const removeDocument = async (_id: string) => {
  // TODO: 后端支持后实现
}

// 清空文档
const clearDocuments = async () => {
  try {
    await axios.delete('http://localhost:8000/documents')
    documents.value = []
  } catch (error) {
    console.error('清除文档失败：', error)
  }
}

// 快捷提问
const quickAsk = (query: string) => {
  userInput.value = query
  nextTick(() => sendMessage())
}

onMounted(async () => {
  loadSessions()

  // 如果有保存的会话，加载其历史；否则创建新会话
  if (currentSessionId.value) {
    await switchSession(currentSessionId.value)
  } else if (sessions.value.length === 0) {
    // 创建第一个会话
    createNewSession()
  } else {
    // 切换到第一个会话
    const firstSession = sortedSessions.value[0]
    if (firstSession) {
      await switchSession(firstSession.id)
    }
  }

  await fetchDocuments()
})
</script>

<style scoped>
/* 容器 */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

/* 顶部栏 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.header-left p {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: #6b7280;
}

.language-switcher {
  display: flex;
  gap: 4px;
}

.lang-btn {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #ffffff;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.lang-btn.active {
  background: #f3f4f6;
  color: #1f2937;
  border-color: #d1d5db;
}

.lang-btn:hover {
  background: #f9fafb;
}

/* 消息区域 */
.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f8f9fa;
}

.message-wrapper {
  display: flex;
  gap: 12px;
  max-width: 100%;
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-wrapper.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
}

.message-wrapper.assistant .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-content {
  max-width: 75%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-wrapper.user .message-content {
  align-items: flex-end;
}

/* 意图标签 */
.intent-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  background: #f3f4f6;
  color: #6b7280;
  width: fit-content;
}

/* 消息气泡 */
.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
  background: #ffffff;
  color: #1f2937;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-wrapper.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #ffffff;
}

/* Markdown 样式 */
.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bullet {
  font-size: 15px;
  font-weight: 600;
  margin: 12px 0 8px 0;
}

.message-bubble :deep(h1:first-child),
.message-bubble :deep(h2:first-child) {
  margin-top: 0;
}

.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-bubble :deep(li) {
  margin: 4px 0;
}

.message-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 13px;
}

.message-wrapper.user .message-bubble :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.message-bubble :deep(pre) {
  background: #f1f3f5;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-bubble :deep(pre code) {
  background: none;
  padding: 0;
}

.message-bubble :deep(strong) {
  font-weight: 600;
}

.message-bubble :deep(a) {
  color: #667eea;
  text-decoration: underline;
}

/* 加载动画 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
  30% { opacity: 1; transform: translateY(-4px); }
}

/* 输入区域 */
.input-area {
  display: flex;
  gap: 12px;
  padding: 16px 24px;
  background: #ffffff;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.input-area textarea {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: none;
  min-height: 44px;
  max-height: 120px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-area textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-area textarea:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

.send-btn {
  padding: 12px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.send-btn:hover:not(:disabled) {
  background: #5a6fd6;
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 快捷操作栏 */
.quick-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.action-left,
.action-right {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover:not(:disabled) {
  background: #f3f4f6;
  color: #1f2937;
}

.example-btn {
  padding: 6px 12px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  font-size: 12px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.example-btn:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* 文档面板 */
.documents-panel {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: 320px;
  background: #ffffff;
  border-left: 1px solid #e5e7eb;
  padding: 20px;
  overflow-y: auto;
  z-index: 100;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #1f2937;
}

.close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-content input[type="file"] {
  font-size: 13px;
}

.upload-btn {
  padding: 10px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.upload-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-status {
  font-size: 12px;
  color: #6b7280;
}

.document-list {
  margin-top: 20px;
}

.document-list h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #1f2937;
}

.document-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.document-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.doc-name {
  font-size: 13px;
  color: #1f2937;
}

.remove-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 50%;
  font-size: 14px;
  cursor: pointer;
}

.clear-docs-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background: #fee2e2;
  color: #dc2626;
  border: none;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
}

/* 响应式 */
@media (max-width: 768px) {
  .chat-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }

  .header-left p {
    display: none;
  }

  .message-content {
    max-width: 85%;
  }

  .quick-actions {
    flex-direction: column;
    gap: 8px;
  }

  .action-right {
    flex-wrap: wrap;
    justify-content: center;
  }

  .documents-panel {
    width: 100%;
  }

  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 200;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }

  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }

  .sidebar-toggle {
    display: flex;
  }
}

/* 应用布局 */
.app-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* 侧边栏切换按钮 */
.sidebar-toggle {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 201;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: #667eea;
  color: white;
  font-size: 18px;
  cursor: pointer;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  overflow: hidden;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header h2 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1f2937;
}

.new-session-btn {
  width: 100%;
  padding: 10px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.new-session-btn:hover:not(:disabled) {
  background: #5a6fd6;
}

.new-session-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 会话列表 */
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.session-item {
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  margin-bottom: 4px;
}

.session-item:hover {
  background: #f3f4f6;
}

.session-item.active {
  background: #eef2ff;
  border: 1px solid #667eea;
}

.session-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-preview {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.session-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #9ca3af;
}

.session-actions {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  display: none;
  gap: 4px;
}

.session-item:hover .session-actions {
  display: flex;
}

.action-icon {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 6px;
  background: #ffffff;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-icon:hover {
  background: #f3f4f6;
}

.action-icon.delete:hover {
  background: #fee2e2;
}

.empty-state {
  text-align: center;
  padding: 32px 16px;
  color: #9ca3af;
  font-size: 14px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 300;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
}

.modal h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #1f2937;
}

.modal p {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #6b7280;
}

.modal input[type="text"] {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  margin-bottom: 16px;
  box-sizing: border-box;
}

.modal input[type="text"]:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 10px 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: white;
  color: #6b7280;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f3f4f6;
}

.confirm-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: #667eea;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover {
  background: #5a6fd6;
}

.confirm-btn.danger {
  background: #dc2626;
}

.confirm-btn.danger:hover {
  background: #b91c1c;
}

/* Agent 步骤面板 */
.agent-steps {
  margin-bottom: 8px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background: #f9fafb;
}

.step-item {
  border-bottom: 1px solid #e5e7eb;
}

.step-item:last-child {
  border-bottom: none;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.15s;
}

.step-header:hover {
  background: #f3f4f6;
}

.step-icon {
  font-size: 10px;
  width: 12px;
  color: #6b7280;
  flex-shrink: 0;
}

.step-tool {
  flex: 1;
  color: #374151;
  font-weight: 500;
}

.step-check {
  color: #10b981;
  font-size: 12px;
  flex-shrink: 0;
}

.step-detail {
  padding: 8px 12px 12px 32px;
  font-size: 12px;
  line-height: 1.5;
}

.step-input {
  color: #6b7280;
  margin-bottom: 4px;
  word-break: break-all;
}

.step-output {
  color: #1f2937;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 120px;
  overflow-y: auto;
}

/* 流式光标 */
.streaming-cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #667eea;
  font-size: 16px;
  margin-left: 1px;
  line-height: 1;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

/* 流式步骤旋转指示器 */
.step-spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
  font-size: 12px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>