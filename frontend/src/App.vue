<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const query = ref('')
const response = ref('')
const intent = ref('')
const isLoading = ref(false)

const ask = async () => {
  if (!query.value.trim()) {
    response.value = '请输入问题或文本内容。'
    intent.value = ''
    return
  }

  isLoading.value = true
  response.value = ''
  intent.value = ''

  try {
    const res = await axios.post('http://localhost:8000/ask', { query: query.value })
    intent.value = res.data.intent
    response.value = res.data.response
  } catch (error: any) {
    response.value = error?.response?.data?.detail || error.message || '请求失败，请稍后重试。'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="page-shell">
    <header class="hero-panel">
      <div>
        <p class="eyebrow">智能助手 · 多技能</p>
        <h1>AI 智能问答助手</h1>
        <p class="hero-description">支持问答、总结、翻译、代码解释，自动识别意图并返回专业回答。</p>
      </div>
      <div class="hero-badge">Instant AI</div>
    </header>

    <main class="layout-grid">
      <section class="card input-card">
        <div class="card-header">
          <div>
            <h2>开始提问</h2>
            <p>请输入您的问题或文本，系统会自动识别最合适的技能。</p>
          </div>
          <span class="status-chip" :class="{ loading: isLoading }">
            {{ isLoading ? '处理中...' : '准备就绪' }}
          </span>
        </div>

        <textarea
          v-model="query"
          rows="6"
          placeholder="例如：请帮我总结以下内容，或解释这段代码..."
        />

        <button class="action-btn" @click="ask" :disabled="isLoading">
          {{ isLoading ? '生成中...' : '提交请求' }}
        </button>
      </section>

      <section class="card result-card" v-if="response || intent">
        <div class="result-meta">
          <div>
            <p class="result-label">意图识别</p>
            <h3>{{ intent || '未识别' }}</h3>
          </div>
          <div class="result-badge">AI 回复</div>
        </div>

        <div class="response-panel">
          <pre>{{ response || '回答将在这里展示。' }}</pre>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.page-shell {
  min-height: 100vh;
  padding: 32px 24px;
  background: radial-gradient(circle at top, rgba(112, 75, 255, 0.16), transparent 28%),
    radial-gradient(circle at bottom right, rgba(34, 202, 255, 0.14), transparent 22%),
    #080b18;
  color: #ffffff;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.hero-panel {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr auto;
  align-items: center;
  max-width: 1100px;
  margin: 0 auto 28px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.04);
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.28);
}

.eyebrow {
  margin: 0 0 12px;
  color: #8f8fff;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 0.86rem;
}

.hero-panel h1 {
  margin: 0;
  font-size: clamp(2rem, 4vw, 3.4rem);
  line-height: 1.05;
}

.hero-description {
  margin: 16px 0 0;
  max-width: 680px;
  color: #d9d9ff;
  font-size: 1rem;
  line-height: 1.75;
}

.hero-badge {
  align-self: start;
  background: linear-gradient(135deg, #7263ff, #39d4ff);
  color: #0b1220;
  padding: 12px 20px;
  border-radius: 999px;
  font-weight: 700;
  letter-spacing: 0.02em;
  box-shadow: 0 16px 32px rgba(56, 88, 255, 0.25);
}

.layout-grid {
  display: grid;
  gap: 24px;
  max-width: 1100px;
  margin: 0 auto;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.75fr);
}

@media (max-width: 900px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  border-radius: 28px;
  padding: 28px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(18px);
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.18);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.card-header h2 {
  margin: 0;
  font-size: 1.5rem;
}

.card-header p {
  margin: 8px 0 0;
  color: #bec4ff;
  font-size: 0.96rem;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 16px;
  border-radius: 999px;
  color: #e4e8ff;
  background: rgba(69, 61, 255, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 0.95rem;
}

.status-chip.loading {
  background: rgba(255, 255, 255, 0.14);
}

textarea {
  width: 100%;
  min-height: 180px;
  border: none;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.05);
  color: #f8f9ff;
  resize: vertical;
  padding: 20px;
  font-size: 1rem;
  line-height: 1.7;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
}

textarea:focus {
  outline: none;
  box-shadow: inset 0 0 0 1px rgba(113, 99, 255, 0.9), 0 0 0 4px rgba(113, 99, 255, 0.12);
}

.action-btn {
  margin-top: 18px;
  width: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 18px;
  padding: 16px 24px;
  font-size: 1rem;
  font-weight: 700;
  color: #0b1220;
  background: linear-gradient(135deg, #7f66ff, #40d9ff);
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 18px 35px rgba(63, 162, 255, 0.25);
}

.action-btn:hover {
  transform: translateY(-1px);
}

.action-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.result-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.result-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.result-label {
  margin: 0;
  color: #8f94ff;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.8rem;
}

.result-meta h3 {
  margin: 8px 0 0;
  font-size: 1.4rem;
}

.result-badge {
  align-self: start;
  background: rgba(255, 255, 255, 0.08);
  color: #d0d1ff;
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.95rem;
}

.response-panel {
  border-radius: 24px;
  min-height: 280px;
  background: rgba(3, 11, 35, 0.65);
  padding: 24px;
  overflow-wrap: anywhere;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.05);
}

.response-panel pre {
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.96rem;
  line-height: 1.8;
  white-space: pre-wrap;
  color: #f4f5ff;
}
</style>
