<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="modal-overlay"
      @click.self="$emit('close')"
      @keydown.escape="$emit('close')"
    >
      <div class="modal-card" role="dialog" aria-modal="true" aria-label="RAG 设置">
        <!-- 头部 -->
        <div class="modal-header">
          <h3 class="modal-title">⚙️ 设置</h3>
          <button class="close-btn" @click="$emit('close')" aria-label="关闭">
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M4.5 4.5L13.5 13.5M13.5 4.5L4.5 13.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="modal-body">
          <!-- LLM Provider -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">🧠</span>
              <h4>LLM 大语言模型</h4>
            </div>
            <div class="section-content">
              <div class="field">
                <label class="field-label">服务商</label>
                <select v-model="settings.llm_provider" class="select-input">
                  <option value="zhipu">智谱 AI (glm-4-flash)</option>
                  <option value="ollama">Ollama 本地</option>
                  <option value="siliconflow">SiliconFlow (DeepSeek)</option>
                </select>
              </div>
              <p class="help-text">
                默认使用智谱 AI 的 glm-4-flash 免费模型，云端推理零等待
              </p>
            </div>
          </div>

          <!-- Embedding Provider -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">🧩</span>
              <h4>Embedding 嵌入模型</h4>
            </div>
            <div class="section-content">
              <div class="field">
                <label class="field-label">服务商</label>
                <select v-model="settings.embedding_provider" class="select-input">
                  <option value="zhipu">智谱 AI (embedding-2 · 1024维 · 云端)</option>
                  <option value="local">本地 text2vec (768维 · CPU)</option>
                  <option value="siliconflow">SiliconFlow (bge-large · 1024维 · 云端)</option>
                </select>
              </div>
              <p class="help-text" v-if="settings.embedding_provider === 'zhipu'">
                云端 API，首次上传文档无需等待，即时响应。约 ¥0.0005/千tokens
              </p>
              <p class="help-text" v-else-if="settings.embedding_provider === 'local'">
                本地 text2vec-base-chinese 模型，需下载 409MB（首次约 20 分钟），支持离线使用
              </p>
              <p class="help-text" v-else>
                云端 API，通过 SiliconFlow 调用 BAAI/bge-large-zh-v1.5
              </p>
            </div>
          </div>

          <!-- 文档分块 -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">📐</span>
              <h4>文档分块</h4>
            </div>
            <div class="section-content">
              <div class="field">
                <div class="slider-label">
                  <label class="field-label">分块大小</label>
                  <span class="slider-value">{{ settings.chunk_size }}</span>
                </div>
                <input
                  v-model.number="settings.chunk_size"
                  type="range"
                  :min="128"
                  :max="1024"
                  :step="32"
                  class="range-slider"
                />
                <div class="range-ticks">
                  <span>128</span>
                  <span>1024</span>
                </div>
              </div>
              <div class="field">
                <div class="slider-label">
                  <label class="field-label">分块重叠</label>
                  <span class="slider-value">{{ settings.chunk_overlap }}</span>
                </div>
                <input
                  v-model.number="settings.chunk_overlap"
                  type="range"
                  :min="0"
                  :max="256"
                  :step="16"
                  class="range-slider"
                />
                <div class="range-ticks">
                  <span>0</span>
                  <span>256</span>
                </div>
              </div>
              <p class="help-text">
                较大的块保留更多上下文，较小的块检索更精确
              </p>
            </div>
          </div>

          <!-- 检索设置 -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">🔍</span>
              <h4>检索设置</h4>
            </div>
            <div class="section-content">
              <div class="field">
                <div class="slider-label">
                  <label class="field-label">检索数量 (K)</label>
                  <span class="slider-value">{{ settings.retrieval_k }}</span>
                </div>
                <input
                  v-model.number="settings.retrieval_k"
                  type="range"
                  :min="1"
                  :max="20"
                  :step="1"
                  class="range-slider"
                />
                <div class="range-ticks">
                  <span>1</span>
                  <span>20</span>
                </div>
              </div>
              <p class="help-text">
                每次检索返回的相关文档片段数量
              </p>
            </div>
          </div>

          <!-- 重启提示 -->
          <div class="section notice-section">
            <div class="section-header">
              <span class="section-icon">⚠️</span>
              <h4>提示</h4>
            </div>
            <div class="section-content">
              <p class="notice-text">
                Provider 切换后需<b>重启后端服务</b>才能生效。当前已索引的文档不受影响。
              </p>
            </div>
          </div>
        </div>

        <!-- 底部按钮 -->
        <div class="modal-footer">
          <button class="footer-btn secondary" @click="resetDefaults">
            恢复默认
          </button>
          <button class="footer-btn primary" @click="saveSettings">
            保存设置
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { reactive, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

// ── 类型定义 ──────────────────────────────────────────
interface RagSettings {
  llm_provider: string
  embedding_provider: string
  chunk_size: number
  chunk_overlap: number
  retrieval_k: number
}

// ── Props / Emits ─────────────────────────────────────
defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
  saved: [settings: RagSettings]
}>()

// ── 默认值 ────────────────────────────────────────────
const DEFAULTS: RagSettings = {
  llm_provider: 'zhipu',
  embedding_provider: 'zhipu',
  chunk_size: 384,
  chunk_overlap: 64,
  retrieval_k: 4,
}

const STORAGE_KEY = 'ai-rag-settings'

// ── 响应式状态 ────────────────────────────────────────
const settings = reactive<RagSettings>({ ...DEFAULTS })

// ── 从 localStorage 加载 ──────────────────────────────
const loadFromStorage = (): void => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<RagSettings>
      if (parsed.llm_provider !== undefined) settings.llm_provider = parsed.llm_provider
      if (parsed.embedding_provider !== undefined) settings.embedding_provider = parsed.embedding_provider
      if (parsed.chunk_size !== undefined) settings.chunk_size = parsed.chunk_size
      if (parsed.chunk_overlap !== undefined) settings.chunk_overlap = parsed.chunk_overlap
      if (parsed.retrieval_k !== undefined) settings.retrieval_k = parsed.retrieval_k
    }
  } catch {
    // 解析失败，使用默认值
  }
}

// ── 保存到 localStorage ───────────────────────────────
const persistToStorage = (): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...settings }))
}

// ── 同步到后端 ────────────────────────────────────────
const syncToBackend = async (): Promise<void> => {
  try {
    await axios.post('http://localhost:8000/rag/settings', { ...settings })
  } catch (err) {
    console.error('同步 RAG 设置到后端失败:', err)
  }
}

// ── 保存设置 ──────────────────────────────────────────
const saveSettings = async (): Promise<void> => {
  persistToStorage()
  await syncToBackend()
  emit('saved', { ...settings })
}

// ── 恢复默认 ──────────────────────────────────────────
const resetDefaults = (): void => {
  Object.assign(settings, JSON.parse(JSON.stringify(DEFAULTS)))
}

// ── Esc 键关闭 ────────────────────────────────────────
const handleKeydown = (e: KeyboardEvent): void => {
  if (e.key === 'Escape') {
    emit('close')
  }
}

// ── 生命周期 ──────────────────────────────────────────
onMounted(() => {
  loadFromStorage()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
/* ── 过渡动画 ─────────────────────────────────────── */
.modal-enter-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .modal-card {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-leave-active .modal-card {
  transition: opacity 0.2s ease, transform 0.15s ease;
}

.modal-enter-from {
  opacity: 0;
}
.modal-enter-from .modal-card {
  opacity: 0;
  transform: scale(0.92) translateY(12px);
}

.modal-leave-to {
  opacity: 0;
}
.modal-leave-to .modal-card {
  opacity: 0;
  transform: scale(0.95) translateY(4px);
}

/* ── 遮罩层 ──────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  padding: 20px;
}

/* ── 卡片主体 ────────────────────────────────────── */
.modal-card {
  background: var(--bg, #fff);
  border-radius: 16px;
  box-shadow:
    0 0 0 1px var(--border, #e5e4e7),
    0 20px 60px rgba(0, 0, 0, 0.15),
    0 8px 20px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 520px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── 头部 ────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border, #e5e4e7);
  flex-shrink: 0;
}

.modal-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h, #08060d);
  letter-spacing: -0.2px;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text, #6b6375);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.close-btn:hover {
  background: var(--code-bg, #f4f3ec);
  color: var(--text-h, #08060d);
}

/* ── 可滚动内容 ──────────────────────────────────── */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.modal-body::-webkit-scrollbar {
  width: 4px;
}
.modal-body::-webkit-scrollbar-thumb {
  background: var(--border, #e5e4e7);
  border-radius: 2px;
}

/* ── 分区卡片 ────────────────────────────────────── */
.section {
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--code-bg, #f4f3ec);
  border-bottom: 1px solid var(--border, #e5e4e7);
}

.section-icon {
  font-size: 16px;
  line-height: 1;
}

.section-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h, #08060d);
}

.section-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── 表单字段 ────────────────────────────────────── */
.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-h, #08060d);
}

.readonly-value {
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--code-bg, #f4f3ec);
  font-family: var(--mono, ui-monospace, Consolas, monospace);
  font-size: 13px;
  color: var(--text, #6b6375);
  border: 1px solid var(--border, #e5e4e7);
  user-select: all;
}

/* ── 帮助文本 ────────────────────────────────────── */
.help-text {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text, #6b6375);
}

/* ── 下拉选择 ────────────────────────────────────── */
.select-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 8px;
  background: var(--bg, #fff);
  color: var(--text-h, #08060d);
  font-size: 14px;
  font-family: inherit;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%236b6375' stroke-width='1.5' stroke-linecap='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 40px;
}

.select-input:focus {
  border-color: var(--accent, #aa3bff);
}

/* ── 提示区块 ────────────────────────────────────── */
.notice-section {
  background: var(--accent-bg, rgba(170, 59, 255, 0.05));
  border: 1px solid var(--accent-border, rgba(170, 59, 255, 0.2));
  border-radius: 8px;
  padding: 16px;
}

.notice-text {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text, #6b6375);
}

/* ── 单选按钮组 ──────────────────────────────────── */
.radio-group {
  display: flex;
  gap: 8px;
}

.radio-group.vertical {
  flex-direction: column;
  gap: 6px;
}

.radio-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border: 1.5px solid var(--border, #e5e4e7);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.18s ease;
  flex: 1;
}

.radio-group.vertical .radio-item {
  align-items: flex-start;
}

.radio-item:hover {
  border-color: var(--accent-border, rgba(170, 59, 255, 0.5));
}

.radio-item.checked {
  border-color: var(--accent, #aa3bff);
  background: var(--accent-bg, rgba(170, 59, 255, 0.1));
}

.radio-item input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
  pointer-events: none;
}

.radio-mark {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1.5px solid var(--border, #e5e4e7);
  flex-shrink: 0;
  transition: all 0.18s ease;
  position: relative;
}

.radio-item.checked .radio-mark {
  border-color: var(--accent, #aa3bff);
  background: var(--accent, #aa3bff);
  box-shadow: 0 0 0 3px var(--accent-bg, rgba(170, 59, 255, 0.1));
}

.radio-item.checked .radio-mark::after {
  content: '';
  position: absolute;
  inset: 3px;
  border-radius: 50%;
  background: #fff;
}

.radio-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-h, #08060d);
}

.radio-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.radio-hint {
  margin: 0;
  font-size: 11px;
  line-height: 1.45;
  color: var(--text, #6b6375);
}

/* ── 滑块样式 ────────────────────────────────────── */
.slider-label {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.slider-value {
  font-family: var(--mono, ui-monospace, Consolas, monospace);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent, #aa3bff);
  background: var(--accent-bg, rgba(170, 59, 255, 0.1));
  padding: 2px 8px;
  border-radius: 6px;
  min-width: 36px;
  text-align: center;
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--border, #e5e4e7);
  outline: none;
  margin: 4px 0;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent, #aa3bff);
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.range-slider::-webkit-slider-thumb:active {
  transform: scale(1.05);
}

.range-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--accent, #aa3bff);
  border: 2px solid #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15);
  cursor: pointer;
}

.range-ticks {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text, #6b6375);
  padding: 0 2px;
}

/* ── 底部按钮栏 ──────────────────────────────────── */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 24px;
  border-top: 1px solid var(--border, #e5e4e7);
  flex-shrink: 0;
}

.footer-btn {
  padding: 10px 22px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: none;
  letter-spacing: 0.2px;
}

.footer-btn.secondary {
  background: transparent;
  color: var(--text, #6b6375);
  border: 1.5px solid var(--border, #e5e4e7);
}

.footer-btn.secondary:hover {
  background: var(--code-bg, #f4f3ec);
  color: var(--text-h, #08060d);
  border-color: var(--text, #6b6375);
}

.footer-btn.primary {
  background: var(--accent, #aa3bff);
  color: #fff;
  box-shadow: 0 2px 8px rgba(170, 59, 255, 0.3);
}

.footer-btn.primary:hover {
  background: color-mix(in srgb, var(--accent, #aa3bff) 85%, #000);
  box-shadow: 0 4px 14px rgba(170, 59, 255, 0.4);
  transform: translateY(-1px);
}

.footer-btn.primary:active {
  transform: translateY(0);
}

/* ── 响应式 ──────────────────────────────────────── */
@media (max-width: 560px) {
  .modal-card {
    max-width: 100%;
    max-height: 92vh;
    border-radius: 14px;
  }

  .modal-header {
    padding: 16px 18px;
  }

  .modal-body {
    padding: 16px 18px;
    gap: 18px;
  }

  .modal-footer {
    padding: 14px 18px;
  }

  .radio-group {
    flex-direction: column;
  }
}
</style>
