<template>
  <Transition name="modal">
    <div
      v-if="visible"
      class="modal-overlay"
      @click.self="$emit('close')"
    >
      <div class="modal-card" role="dialog" aria-modal="true" aria-label="设置">
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
          <!-- ============ LLM Provider ============ -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">🧠</span>
              <h4>LLM 大语言模型</h4>
              <span v-if="activeLlm" class="active-badge">已激活</span>
            </div>
            <div class="section-content">
              <!-- Provider selector -->
              <div class="field">
                <label class="field-label">选择服务商</label>
                <select v-model="selectedLlmId" class="select-input" @change="onLlmSelect">
                  <option value="">-- 请选择 --</option>
                  <option
                    v-for="p in providers.llm"
                    :key="p.id"
                    :value="p.id"
                  >
                    {{ p.name }} ({{ p.model_name }}){{ p.is_active ? ' ✓' : '' }}
                  </option>
                  <option disabled>──────────</option>
                  <option value="__custom_llm__">+ 自定义...</option>
                </select>
              </div>

              <!-- Existing provider detail panel -->
              <template v-if="selectedLlm && selectedLlmId !== '__custom_llm__'">
                <div class="field">
                  <label class="field-label">名称</label>
                  <div class="readonly-value">{{ selectedLlm.name }}</div>
                </div>
                <div class="field">
                  <label class="field-label">Base URL</label>
                  <input
                    v-if="selectedLlm.is_preset === false"
                    v-model="editLlm.base_url"
                    class="text-input"
                    placeholder="https://api.example.com/v1"
                  />
                  <div v-else class="readonly-value">{{ selectedLlm.base_url }}</div>
                </div>
                <div class="field">
                  <label class="field-label">模型</label>
                  <input
                    v-if="selectedLlm.is_preset === false"
                    v-model="editLlm.model_name"
                    class="text-input"
                    placeholder="model-name"
                  />
                  <div v-else class="readonly-value">{{ selectedLlm.model_name }}</div>
                </div>
                <div class="field">
                  <label class="field-label">API Key</label>
                  <input
                    type="password"
                    v-model="editLlm.api_key"
                    class="text-input"
                    placeholder="输入 API Key"
                    autocomplete="off"
                  />
                </div>

                <!-- Test result -->
                <div v-if="llmTestResult" class="test-result" :class="llmTestResult.success ? 'success' : 'error'">
                  {{ llmTestResult.message }}
                </div>

                <!-- Actions -->
                <div class="provider-actions">
                  <button
                    class="action-btn test-btn"
                    :disabled="testingLlm"
                    @click="testConnection('llm')"
                  >
                    {{ testingLlm ? '测试中...' : '测试连接' }}
                  </button>
                  <button
                    class="action-btn primary-btn"
                    :disabled="activatingLlm"
                    @click="activateProvider('llm')"
                  >
                    {{ activatingLlm ? '激活中...' : '激活' }}
                  </button>
                  <button
                    v-if="selectedLlm.is_preset === false"
                    class="action-btn delete-btn"
                    @click="deleteProvider('llm')"
                  >
                    删除
                  </button>
                </div>
              </template>

              <!-- Custom provider creation form -->
              <template v-if="selectedLlmId === '__custom_llm__'">
                <div class="custom-divider">新建自定义 LLM 服务商</div>
                <div class="field">
                  <label class="field-label">ID</label>
                  <input v-model="customLlm.id" class="text-input" placeholder="唯一标识，如 my-llm" />
                </div>
                <div class="field">
                  <label class="field-label">名称</label>
                  <input v-model="customLlm.name" class="text-input" placeholder="显示名称" />
                </div>
                <div class="field">
                  <label class="field-label">Base URL</label>
                  <input v-model="customLlm.base_url" class="text-input" placeholder="https://api.example.com/v1" />
                </div>
                <div class="field">
                  <label class="field-label">模型</label>
                  <input v-model="customLlm.model_name" class="text-input" placeholder="model-name" />
                </div>
                <div class="field">
                  <label class="field-label">API Key</label>
                  <input type="password" v-model="customLlm.api_key" class="text-input" placeholder="输入 API Key" />
                </div>

                <!-- Test result -->
                <div v-if="llmTestResult" class="test-result" :class="llmTestResult.success ? 'success' : 'error'">
                  {{ llmTestResult.message }}
                </div>

                <div class="provider-actions">
                  <button
                    class="action-btn test-btn"
                    :disabled="testingLlm"
                    @click="testCustom('llm')"
                  >
                    {{ testingLlm ? '测试中...' : '测试连接' }}
                  </button>
                  <button
                    class="action-btn primary-btn"
                    :disabled="creatingLlm"
                    @click="createCustom('llm')"
                  >
                    {{ creatingLlm ? '创建中...' : '创建服务商' }}
                  </button>
                </div>
              </template>
            </div>
          </div>

          <!-- ============ Embedding Provider ============ -->
          <div class="section">
            <div class="section-header">
              <span class="section-icon">🧩</span>
              <h4>Embedding 嵌入模型</h4>
              <span v-if="activeEmbedding" class="active-badge">已激活</span>
            </div>
            <div class="section-content">
              <!-- Provider selector -->
              <div class="field">
                <label class="field-label">选择服务商</label>
                <select v-model="selectedEmbeddingId" class="select-input" @change="onEmbeddingSelect">
                  <option value="">-- 请选择 --</option>
                  <option
                    v-for="p in providers.embedding"
                    :key="p.id"
                    :value="p.id"
                  >
                    {{ p.name }} ({{ p.model_name }}){{ p.is_active ? ' ✓' : '' }}
                  </option>
                  <option disabled>──────────</option>
                  <option value="__custom_emb__">+ 自定义...</option>
                </select>
              </div>

              <!-- Existing provider detail panel -->
              <template v-if="selectedEmbedding && selectedEmbeddingId !== '__custom_emb__'">
                <div class="field">
                  <label class="field-label">名称</label>
                  <div class="readonly-value">{{ selectedEmbedding.name }}</div>
                </div>
                <div class="field">
                  <label class="field-label">Base URL</label>
                  <input
                    v-if="selectedEmbedding.is_preset === false"
                    v-model="editEmbedding.base_url"
                    class="text-input"
                    placeholder="https://api.example.com/v1"
                  />
                  <div v-else class="readonly-value">{{ selectedEmbedding.base_url }}</div>
                </div>
                <div class="field">
                  <label class="field-label">模型</label>
                  <input
                    v-if="selectedEmbedding.is_preset === false"
                    v-model="editEmbedding.model_name"
                    class="text-input"
                    placeholder="model-name"
                  />
                  <div v-else class="readonly-value">{{ selectedEmbedding.model_name }}</div>
                </div>
                <div class="field">
                  <label class="field-label">API Key</label>
                  <input
                    type="password"
                    v-model="editEmbedding.api_key"
                    class="text-input"
                    placeholder="输入 API Key"
                  />
                </div>

                <!-- Test result -->
                <div v-if="embTestResult" class="test-result" :class="embTestResult.success ? 'success' : 'error'">
                  {{ embTestResult.message }}
                </div>

                <!-- Actions -->
                <div class="provider-actions">
                  <button
                    class="action-btn test-btn"
                    :disabled="testingEmbedding"
                    @click="testConnection('embedding')"
                  >
                    {{ testingEmbedding ? '测试中...' : '测试连接' }}
                  </button>
                  <button
                    class="action-btn primary-btn"
                    :disabled="activatingEmbedding"
                    @click="activateProvider('embedding')"
                  >
                    {{ activatingEmbedding ? '激活中...' : '激活' }}
                  </button>
                  <button
                    v-if="selectedEmbedding.is_preset === false"
                    class="action-btn delete-btn"
                    @click="deleteProvider('embedding')"
                  >
                    删除
                  </button>
                </div>
              </template>

              <!-- Custom provider creation form -->
              <template v-if="selectedEmbeddingId === '__custom_emb__'">
                <div class="custom-divider">新建自定义 Embedding 服务商</div>
                <div class="field">
                  <label class="field-label">ID</label>
                  <input v-model="customEmbedding.id" class="text-input" placeholder="唯一标识，如 my-emb" />
                </div>
                <div class="field">
                  <label class="field-label">名称</label>
                  <input v-model="customEmbedding.name" class="text-input" placeholder="显示名称" />
                </div>
                <div class="field">
                  <label class="field-label">Base URL</label>
                  <input v-model="customEmbedding.base_url" class="text-input" placeholder="https://api.example.com/v1" />
                </div>
                <div class="field">
                  <label class="field-label">模型</label>
                  <input v-model="customEmbedding.model_name" class="text-input" placeholder="model-name" />
                </div>
                <div class="field">
                  <label class="field-label">API Key</label>
                  <input type="password" v-model="customEmbedding.api_key" class="text-input" placeholder="输入 API Key" />
                </div>

                <!-- Test result -->
                <div v-if="embTestResult" class="test-result" :class="embTestResult.success ? 'success' : 'error'">
                  {{ embTestResult.message }}
                </div>

                <div class="provider-actions">
                  <button
                    class="action-btn test-btn"
                    :disabled="testingEmbedding"
                    @click="testCustom('embedding')"
                  >
                    {{ testingEmbedding ? '测试中...' : '测试连接' }}
                  </button>
                  <button
                    class="action-btn primary-btn"
                    :disabled="creatingEmbedding"
                    @click="createCustom('embedding')"
                  >
                    {{ creatingEmbedding ? '创建中...' : '创建服务商' }}
                  </button>
                </div>
              </template>
            </div>
          </div>

          <!-- ============ 文档分块 ============ -->
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

          <!-- ============ 检索设置 ============ -->
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
import { reactive, ref, computed, onMounted, onUnmounted, watch } from 'vue'
import api from '../api'

// ── 类型定义 ──────────────────────────────────────────

interface Provider {
  id: string
  name: string
  provider_type: string
  base_url: string
  model_name: string
  api_key: string
  is_active: boolean
  is_preset: boolean
  is_local: boolean
}

interface ProvidersData {
  llm: Provider[]
  embedding: Provider[]
}

interface ProviderForm {
  id: string
  name: string
  base_url: string
  model_name: string
  api_key: string
}

interface RagSettings {
  chunk_size: number
  chunk_overlap: number
  retrieval_k: number
}

interface TestResult {
  success: boolean
  message: string
}

// ── Props / Emits ─────────────────────────────────────
const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
  saved: [settings: RagSettings]
}>()

// ── 默认值 ────────────────────────────────────────────
const DEFAULTS: RagSettings = {
  chunk_size: 384,
  chunk_overlap: 64,
  retrieval_k: 4,
}

const STORAGE_KEY = 'ai-rag-settings'

// ── Provider 状态 ─────────────────────────────────────
const providers = reactive<ProvidersData>({
  llm: [],
  embedding: [],
})

const selectedLlmId = ref('')
const selectedEmbeddingId = ref('')

const editLlm = reactive<ProviderForm>({ id: '', name: '', base_url: '', model_name: '', api_key: '' })
const editEmbedding = reactive<ProviderForm>({ id: '', name: '', base_url: '', model_name: '', api_key: '' })

const customLlm = reactive<ProviderForm>({ id: '', name: '', base_url: '', model_name: '', api_key: '' })
const customEmbedding = reactive<ProviderForm>({ id: '', name: '', base_url: '', model_name: '', api_key: '' })

const testingLlm = ref(false)
const testingEmbedding = ref(false)
const activatingLlm = ref(false)
const activatingEmbedding = ref(false)
const creatingLlm = ref(false)
const creatingEmbedding = ref(false)

const llmTestResult = ref<TestResult | null>(null)
const embTestResult = ref<TestResult | null>(null)

// ── RAG 状态 ──────────────────────────────────────────
const settings = reactive<RagSettings>({ ...DEFAULTS })

// ── Selected providers (ref instead of computed for reactivity) ─
const selectedLlm = ref<Provider | null>(null)
const selectedEmbedding = ref<Provider | null>(null)

const activeLlm = computed(() =>
  providers.llm.find(p => p.is_active) ?? null
)

const activeEmbedding = computed(() =>
  providers.embedding.find(p => p.is_active) ?? null
)

// ── Helpers ───────────────────────────────────────────
const blankForm = (): ProviderForm => ({ id: '', name: '', base_url: '', model_name: '', api_key: '' })

const resetCustomForms = (): void => {
  Object.assign(customLlm, blankForm())
  Object.assign(customEmbedding, blankForm())
}

const isMaskedKey = (key: string): boolean => {
  return !key || key === '***' || /^\*+$/.test(key) || key.includes('...')
}

// ── Fetch providers from backend ──────────────────────
const fetchProviders = async (): Promise<void> => {
  try {
    const { data } = await api.get('/providers')
    if (data.llm) providers.llm = data.llm
    if (data.embedding) providers.embedding = data.embedding

    // Auto-select active providers (only on first load, don't overwrite user selection)
    const activeL = providers.llm.find(p => p.is_active)
    if (activeL && !selectedLlmId.value) {
      selectedLlmId.value = activeL.id
      selectedLlm.value = activeL
      initEditForm('llm', activeL)
    }

    const activeE = providers.embedding.find(p => p.is_active)
    if (activeE && !selectedEmbeddingId.value) {
      selectedEmbeddingId.value = activeE.id
      selectedEmbedding.value = activeE
      initEditForm('embedding', activeE)
    }
  } catch (err) {
    console.error('获取服务商列表失败:', err)
  }
}

// ── Init edit form from a provider ────────────────────
const initEditForm = (type: 'llm' | 'embedding', p: Provider): void => {
  const form = type === 'llm' ? editLlm : editEmbedding
  form.id = p.id
  form.name = p.name
  form.base_url = p.base_url
  form.model_name = p.model_name
  form.api_key = isMaskedKey(p.api_key) ? '' : p.api_key
}

// ── Dropdown handlers ─────────────────────────────────
const onLlmSelect = (): void => {
  llmTestResult.value = null
  if (selectedLlmId.value === '__custom_llm__') {
    Object.assign(editLlm, blankForm())
    selectedLlm.value = null
    return
  }
  const p = providers.llm.find(x => x.id === selectedLlmId.value) ?? null
  selectedLlm.value = p
  if (p) initEditForm('llm', p)
  else Object.assign(editLlm, blankForm())
}

const onEmbeddingSelect = (): void => {
  embTestResult.value = null
  if (selectedEmbeddingId.value === '__custom_emb__') {
    Object.assign(editEmbedding, blankForm())
    selectedEmbedding.value = null
    return
  }
  const p = providers.embedding.find(x => x.id === selectedEmbeddingId.value) ?? null
  selectedEmbedding.value = p
  if (p) initEditForm('embedding', p)
  else Object.assign(editEmbedding, blankForm())
}

// ── Test connection ───────────────────────────────────
const testConnection = async (type: 'llm' | 'embedding'): Promise<void> => {
  const id = type === 'llm' ? selectedLlmId.value : selectedEmbeddingId.value
  const setTesting = type === 'llm' ? (v: boolean) => { testingLlm.value = v } : (v: boolean) => { testingEmbedding.value = v }
  const setResult = type === 'llm' ? (r: TestResult | null) => { llmTestResult.value = r } : (r: TestResult | null) => { embTestResult.value = r }
  const form = type === 'llm' ? editLlm : editEmbedding

  if (!id || id.startsWith('__custom_')) return

  setTesting(true)
  setResult(null)
  try {
    const body: Record<string, string> = {}
    if (form.api_key) body.api_key = form.api_key
    const { data } = await api.post(`/providers/${id}/test`, body)
    if (data.success !== false) {
      setResult({ success: true, message: data.message ?? '连接成功' })
    } else {
      setResult({ success: false, message: data.error ?? '连接失败' })
    }
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? err?.message ?? '连接失败'
    setResult({ success: false, message: `连接失败: ${msg}` })
  } finally {
    setTesting(false)
  }
}

const testCustom = async (type: 'llm' | 'embedding'): Promise<void> => {
  const setTesting = type === 'llm' ? (v: boolean) => { testingLlm.value = v } : (v: boolean) => { testingEmbedding.value = v }
  const setResult = type === 'llm' ? (r: TestResult | null) => { llmTestResult.value = r } : (r: TestResult | null) => { embTestResult.value = r }
  const form = type === 'llm' ? customLlm : customEmbedding

  if (!form.base_url || !form.model_name) {
    setResult({ success: false, message: '请填写 Base URL 和模型名称' })
    return
  }

  setTesting(true)
  setResult(null)
  try {
    const body: Record<string, string> = {
      base_url: form.base_url,
      model_name: form.model_name,
    }
    if (form.api_key) body.api_key = form.api_key
    // Test custom provider without an ID yet - use a temporary test endpoint or simulate
    const { data } = await api.post('/providers/test-custom', body)
    setResult({ success: true, message: data.message ?? '连接成功' })
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? err?.message ?? '连接失败'
    setResult({ success: false, message: `连接失败: ${msg}` })
  } finally {
    setTesting(false)
  }
}

// ── Activate ──────────────────────────────────────────
const activateProvider = async (type: 'llm' | 'embedding'): Promise<void> => {
  const id = type === 'llm' ? selectedLlmId.value : selectedEmbeddingId.value
  const setActivating = type === 'llm' ? (v: boolean) => { activatingLlm.value = v } : (v: boolean) => { activatingEmbedding.value = v }
  const form = type === 'llm' ? editLlm : editEmbedding

  if (!id || id.startsWith('__custom_')) return

  setActivating(true)
  try {
    // Send changed fields before activating
    const p = type === 'llm' ? selectedLlm.value : selectedEmbedding.value
    const updateBody: Record<string, string> = {}

    if (form.api_key && !isMaskedKey(form.api_key)) {
      updateBody.api_key = form.api_key
    }

    if (p && p.is_preset === false) {
      if (form.base_url && form.base_url !== p.base_url) updateBody.base_url = form.base_url
      if (form.model_name && form.model_name !== p.model_name) updateBody.model_name = form.model_name
      if (form.name && form.name !== p.name) updateBody.name = form.name
    }

    if (Object.keys(updateBody).length > 0) {
      await api.put(`/providers/${id}`, updateBody)
    }
    // Activate
    await api.post(`/providers/${id}/activate`)
    await fetchProviders()

    // Re-select this provider in dropdown
    if (type === 'llm') { selectedLlmId.value = id; selectedLlm.value = providers.llm.find(p => p.id === id) ?? null }
    else { selectedEmbeddingId.value = id; selectedEmbedding.value = providers.embedding.find(p => p.id === id) ?? null }
    const refreshed = type === 'llm'
      ? providers.llm.find(p => p.id === id)
      : providers.embedding.find(p => p.id === id)
    if (refreshed) initEditForm(type, refreshed)
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? err?.message ?? '激活失败'
    alert(`激活失败: ${msg}`)
  } finally {
    setActivating(false)
  }
}

// ── Create custom provider ────────────────────────────
const createCustom = async (type: 'llm' | 'embedding'): Promise<void> => {
  const setCreating = type === 'llm' ? (v: boolean) => { creatingLlm.value = v } : (v: boolean) => { creatingEmbedding.value = v }
  const form = type === 'llm' ? customLlm : customEmbedding

  if (!form.id || !form.name || !form.base_url || !form.model_name) {
    alert('请填写所有必填字段（ID、名称、Base URL、模型）')
    return
  }

  setCreating(true)
  try {
    await api.post('/providers', {
      id: form.id,
      name: form.name,
      base_url: form.base_url,
      model_name: form.model_name,
      api_key: form.api_key,
      provider_type: type,
    })
    await fetchProviders()
    resetCustomForms()
    if (type === 'llm') selectedLlmId.value = form.id
    else selectedEmbeddingId.value = form.id
    const created = type === 'llm'
      ? providers.llm.find(p => p.id === form.id)
      : providers.embedding.find(p => p.id === form.id)
    if (created) initEditForm(type, created)
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? err?.message ?? '创建失败'
    alert(`创建失败: ${msg}`)
  } finally {
    setCreating(false)
  }
}

// ── Delete custom provider ────────────────────────────
const deleteProvider = async (type: 'llm' | 'embedding'): Promise<void> => {
  const id = type === 'llm' ? selectedLlmId.value : selectedEmbeddingId.value
  if (!id) return
  if (!confirm('确定要删除该服务商吗？此操作不可撤销。')) return

  try {
    await api.delete(`/providers/${id}`)
    if (type === 'llm') {
      selectedLlmId.value = ''
      Object.assign(editLlm, blankForm())
    } else {
      selectedEmbeddingId.value = ''
      Object.assign(editEmbedding, blankForm())
    }
    await fetchProviders()
  } catch (err: any) {
    const msg = err?.response?.data?.detail ?? err?.message ?? '删除失败'
    alert(`删除失败: ${msg}`)
  }
}

// ── RAG: 从 localStorage 加载 ─────────────────────────
const loadFromStorage = (): void => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<RagSettings>
      if (parsed.chunk_size !== undefined) settings.chunk_size = parsed.chunk_size
      if (parsed.chunk_overlap !== undefined) settings.chunk_overlap = parsed.chunk_overlap
      if (parsed.retrieval_k !== undefined) settings.retrieval_k = parsed.retrieval_k
    }
  } catch {
    // 解析失败，使用默认值
  }
}

// ── RAG: 持久化 ───────────────────────────────────────
const persistToStorage = (): void => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...settings }))
}

const syncToBackend = async (): Promise<void> => {
  try {
    await api.post('rag/settings', { ...settings })
  } catch (err) {
    console.error('同步 RAG 设置到后端失败:', err)
  }
}

// ── Save / Reset ──────────────────────────────────────
const saveSettings = async (): Promise<void> => {
  persistToStorage()
  await syncToBackend()
  emit('saved', { ...settings })
}

const resetDefaults = (): void => {
  Object.assign(settings, JSON.parse(JSON.stringify(DEFAULTS)))
}

// ── Esc key ───────────────────────────────────────────
const handleKeydown = (e: KeyboardEvent): void => {
  if (e.key === 'Escape') {
    emit('close')
  }
}

// ── Lifecycle ─────────────────────────────────────────
onMounted(() => {
  loadFromStorage()
  fetchProviders()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})

// 每次打开弹窗时刷新 provider 列表
watch(() => props.visible, (newVal) => {
  if (newVal) fetchProviders()
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

/* ── 激活徽章 ────────────────────────────────────── */
.active-badge {
  margin-left: auto;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  color: #16a34a;
  background: rgba(22, 163, 74, 0.1);
  border: 1px solid rgba(22, 163, 74, 0.25);
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

/* ── 文本输入 ────────────────────────────────────── */
.text-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border, #e5e4e7);
  border-radius: 8px;
  background: var(--bg, #fff);
  color: var(--text-h, #08060d);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
  box-sizing: border-box;
}

.text-input::placeholder {
  color: var(--text, #6b6375);
  opacity: 0.5;
}

.text-input:focus {
  border-color: var(--accent, #aa3bff);
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
  box-sizing: border-box;
}

.select-input:focus {
  border-color: var(--accent, #aa3bff);
}

/* ── 自定义分隔线 ────────────────────────────────── */
.custom-divider {
  padding: 6px 12px;
  border-radius: 6px;
  background: var(--accent-bg, rgba(170, 59, 255, 0.05));
  font-size: 12px;
  font-weight: 600;
  color: var(--accent, #aa3bff);
  text-align: center;
  border: 1px dashed var(--accent-border, rgba(170, 59, 255, 0.2));
}

/* ── Provider 操作按钮 ───────────────────────────── */
.provider-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 8px 18px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1.5px solid transparent;
  line-height: 1.4;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.test-btn {
  background: var(--code-bg, #f4f3ec);
  color: var(--text-h, #08060d);
  border-color: var(--border, #e5e4e7);
}

.test-btn:hover:not(:disabled) {
  background: var(--border, #e5e4e7);
}

.primary-btn {
  background: var(--accent, #aa3bff);
  color: #fff;
  box-shadow: 0 1px 4px rgba(170, 59, 255, 0.25);
}

.primary-btn:hover:not(:disabled) {
  background: color-mix(in srgb, var(--accent, #aa3bff) 85%, #000);
}

.delete-btn {
  background: transparent;
  color: #dc2626;
  border-color: rgba(220, 38, 38, 0.3);
}

.delete-btn:hover:not(:disabled) {
  background: rgba(220, 38, 38, 0.08);
  border-color: rgba(220, 38, 38, 0.5);
}

/* ── 测试结果 ────────────────────────────────────── */
.test-result {
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.5;
  font-weight: 500;
}

.test-result.success {
  background: rgba(22, 163, 74, 0.08);
  color: #15803d;
  border: 1px solid rgba(22, 163, 74, 0.2);
}

.test-result.error {
  background: rgba(220, 38, 38, 0.06);
  color: #b91c1c;
  border: 1px solid rgba(220, 38, 38, 0.15);
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

  .provider-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    text-align: center;
  }
}
</style>
