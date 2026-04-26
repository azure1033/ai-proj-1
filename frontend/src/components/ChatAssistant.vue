<template>
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

          <!-- 消息文本 (支持 Markdown) -->
          <div class="message-bubble" v-html="renderMarkdown(message.content)"></div>
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

// 加载历史
const loadHistory = async () => {
  try {
    const res = await axios.get('http://localhost:8000/history')
    messages.value = res.data.history || []
    if (messages.value.length === 0) {
      initWelcome()
    }
  } catch {
    initWelcome()
  }
}

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

onMounted(async () => {
  await loadHistory()
  await fetchDocuments()
})

// 发送消息
const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const query = userInput.value.trim()
  userInput.value = ''

  messages.value.push({ role: 'user', content: query })
  isLoading.value = true

  try {
    const res = await axios.post('http://localhost:8000/ask', { query })
    const { intent, response } = res.data
    messages.value.push({ role: 'assistant', content: response, intent })
  } catch (error: any) {
    const errorMsg = error?.response?.data?.detail || error.message || '请求失败，请稍后重试。'
    messages.value.push({ role: 'assistant', content: errorMsg, intent: '错误' })
  } finally {
    isLoading.value = false
  }
}

// 快捷提问
const quickAsk = (query: string) => {
  userInput.value = query
  nextTick(() => sendMessage())
}
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
}
</style>