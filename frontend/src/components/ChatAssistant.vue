<template>
  <section class="chat-container">
    <div class="chat-header">
      <h1>🤖 AI 智能助手</h1>
      <p>支持天气查询、问答、总结、翻译和代码解释</p>
    </div>

    <!-- 聊天消息区域 -->
    <div class="messages-area">
      <div
        v-for="(message, idx) in messages"
        :key="idx"
        class="message"
        :class="{ user: message.role === 'user', assistant: message.role === 'assistant' }"
      >
        <div class="message-icon">{{ message.role === 'user' ? '👤' : '🤖' }}</div>
        <div class="message-content">
          <div v-if="message.role === 'assistant' && message.intent" class="intent-badge">
            {{ message.intent }}
          </div>
          <div class="message-text">{{ message.content }}</div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="isLoading" class="message assistant loading-message">
        <div class="message-icon">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>

      <!-- 消息容器末尾 -->
      <div ref="messagesEndRef"></div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <textarea
        v-model="userInput"
        placeholder="输入您的问题...（支持天气查询、问答、总结、翻译、代码解释）"
        rows="3"
        @keydown.enter.ctrl="sendMessage"
        @keydown.enter.meta="sendMessage"
        :disabled="isLoading"
      />
      <button class="send-btn" @click="sendMessage" :disabled="isLoading || !userInput.trim()">
        {{ isLoading ? '处理中...' : '发送' }}
      </button>
    </div>

    <!-- 快速命令提示 -->
    <div class="quick-tips">
      <p>💡 快速示例：</p>
      <div class="tips-grid">
        <button @click="quickAsk('今天合肥热不热，需要穿外套吗？')">天气查询</button>
        <button @click="quickAsk('请解释什么是API')">问答</button>
        <button @click="quickAsk('请翻译：Hello, how are you doing today?')">翻译</button>
        <button @click="quickAsk('请总结：人工智能是模拟人类智能的技术。')">总结</button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import axios from 'axios'

interface Message {
  role: 'user' | 'assistant'
  content: string
  intent?: string
}

const userInput = ref('')
const messages = ref<Message[]>([])
const isLoading = ref(false)
const messagesEndRef = ref<HTMLElement>()

// 自动滚动到底部
const scrollToBottom = async () => {
  await nextTick()
  messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' })
}

// 监听消息变化，自动滚动
watch(messages, scrollToBottom, { deep: true })

const sendMessage = async () => {
  if (!userInput.value.trim() || isLoading.value) return

  const query = userInput.value.trim()
  userInput.value = ''

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: query,
  })

  isLoading.value = true

  try {
    const res = await axios.post('http://localhost:8000/ask', { query })
    const { intent, response } = res.data

    // 添加助手回复
    messages.value.push({
      role: 'assistant',
      content: response,
      intent,
    })
  } catch (error: any) {
    const errorMsg =
      error?.response?.data?.detail ||
      error.message ||
      '请求失败，请稍后重试。'

    messages.value.push({
      role: 'assistant',
      content: errorMsg,
      intent: '错误',
    })
  } finally {
    isLoading.value = false
  }
}

const quickAsk = (query: string) => {
  userInput.value = query
  // 使用 nextTick 确保输入框已更新
  nextTick(() => {
    sendMessage()
  })
}

// 初始欢迎消息
messages.value.push({
  role: 'assistant',
  content:
    '👋 欢迎使用 AI 智能助手！我支持多种技能：\n\n• 天气查询：询问天气状况和穿衣建议\n• 问答：回答您的问题\n• 总结：总结长篇文本\n• 翻译：翻译不同语言的文本\n• 代码解释：解释代码逻辑\n\n请输入您的问题开始吧！',
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  gap: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, sans-serif;
}

.chat-header {
  text-align: center;
  color: white;
  padding: 20px 0;
}

.chat-header h1 {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.chat-header p {
  margin: 8px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.message {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-icon {
  font-size: 24px;
  min-width: 32px;
  text-align: center;
}

.message.user .message-icon {
  order: 2;
}

.message-content {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.message.user .message-content {
  align-items: flex-end;
}

.intent-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  width: fit-content;
}

.message-text {
  background: #f0f0f0;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 14px;
}

.message.user .message-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.loading-message .message-text {
  background: transparent;
  padding: 8px 0;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%,
  60%,
  100% {
    opacity: 0.3;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-10px);
  }
}

.input-area {
  display: flex;
  gap: 12px;
  background: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

textarea {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 60px;
  max-height: 120px;
  transition: border-color 0.3s;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
}

textarea:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
  align-self: flex-end;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.quick-tips {
  background: white;
  padding: 16px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.quick-tips p {
  margin: 0 0 12px 0;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.tips-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 8px;
}

.tips-grid button {
  padding: 8px 12px;
  background: #f0f0f0;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.tips-grid button:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    padding: 10px;
  }

  .message-content {
    max-width: 85%;
  }

  .chat-header h1 {
    font-size: 24px;
  }

  .tips-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
