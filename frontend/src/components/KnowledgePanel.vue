<template>
  <div class="knowledge-panel">
    <!-- 知识库摘要 -->
    <div class="kb-summary" v-if="kbStatus">
      <div class="summary-item">
        <span class="summary-icon">📚</span>
        <span class="summary-label">文档数</span>
        <span class="summary-value">{{ kbStatus.document_count }}</span>
      </div>
      <div class="summary-divider"></div>
      <div class="summary-item">
        <span class="summary-icon">🧩</span>
        <span class="summary-label">总片段数</span>
        <span class="summary-value">{{ kbStatus.total_chunks }}</span>
      </div>
    </div>

    <!-- 拖拽上传区域 -->
    <div
      class="drop-zone"
      :class="{ 'drop-zone--active': isDragging }"
      @dragenter.prevent="onDragEnter"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".txt,.pdf,.docx"
        class="file-input"
        @change="onFileSelected"
      />
      <div class="drop-zone__icon">📤</div>
      <div class="drop-zone__text">
        <p class="drop-zone__primary">拖拽文件到此处上传，或点击选择文件</p>
        <p class="drop-zone__secondary">支持 PDF / Word / TXT 格式</p>
      </div>
    </div>

    <!-- 上传进度条 -->
    <div v-if="uploadState.status === 'uploading'" class="upload-progress">
      <div class="upload-progress__header">
        <span class="upload-progress__name">📄 {{ uploadState.fileName }}</span>
        <span class="upload-progress__percent">{{ uploadState.progress }}%</span>
      </div>
      <div class="upload-progress__bar">
        <div
          class="upload-progress__fill"
          :style="{ width: uploadState.progress + '%' }"
        ></div>
      </div>
      <div class="upload-progress__footer">
        <span class="upload-progress__size">{{ formatFileSize(uploadState.fileSize) }}</span>
      </div>
    </div>

    <!-- 上传错误提示 -->
    <div v-if="uploadState.status === 'error'" class="upload-error">
      ⚠️ {{ uploadState.errorMessage }}
    </div>

    <!-- 文档列表 -->
    <div class="doc-list-section">
      <h3 class="section-title">已上传文档</h3>

      <!-- 加载中 -->
      <div v-if="docListState === 'loading'" class="loading-state">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <!-- 错误 -->
      <div v-else-if="docListState === 'error'" class="error-state">
        ⚠️ 加载失败，请
        <button class="retry-btn" @click="fetchDocuments">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="documents.length === 0" class="empty-state">
        <div class="empty-state__icon">📂</div>
        <p>暂无文档，上传文件开始构建知识库</p>
      </div>

      <!-- 文档列表 -->
      <ul v-else class="doc-list">
        <li
          v-for="doc in documents"
          :key="doc.id"
          class="doc-item"
          :class="{ 'doc-item--deleting': deletingId === doc.id }"
        >
          <div class="doc-item__icon">📄</div>
          <div class="doc-item__info">
            <div class="doc-item__name" :title="doc.filename">{{ doc.filename }}</div>
            <div class="doc-item__meta">
              <span v-if="doc.chunk_count !== undefined" class="doc-item__chunks">
                {{ doc.chunk_count }} 个片段
              </span>
              <span class="doc-item__size" v-if="doc.file_size">
                {{ formatFileSize(doc.file_size) }}
              </span>
            </div>
          </div>
          <div class="doc-item__right">
            <span
              class="index-badge"
              :class="'index-badge--' + getIndexStatus(doc)"
            >
              {{ getIndexStatusText(doc) }}
            </span>
            <button
              class="doc-item__delete"
              @click.stop="confirmDelete(doc)"
              :disabled="deletingId === doc.id"
              title="删除文档"
            >
              {{ deletingId === doc.id ? '...' : '✕' }}
            </button>
          </div>
        </li>
      </ul>
    </div>

    <!-- 删除确认弹窗 -->
    <Teleport to="body">
      <div
        v-if="showDeleteModal"
        class="modal-overlay"
        @click.self="cancelDelete"
      >
        <div class="modal">
          <h3>确认删除</h3>
          <p>确定要删除文档 <strong>{{ deleteTarget?.filename }}</strong> 吗？此操作不可撤销。</p>
          <div class="modal-actions">
            <button class="modal-btn modal-btn--cancel" @click="cancelDelete">取消</button>
            <button class="modal-btn modal-btn--confirm" @click="executeDelete">确认删除</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

/* ========== 类型定义 ========== */

interface Document {
  id: string
  filename: string
  chunk_count?: number
  index_status?: string
  file_size?: number
  uploaded_at?: string
}

interface KnowledgeBaseStatus {
  document_count: number
  total_chunks: number
}

type UploadStatus = 'idle' | 'uploading' | 'error'

interface UploadState {
  status: UploadStatus
  fileName: string
  fileSize: number
  progress: number
  errorMessage: string
}

type DocListState = 'loading' | 'loaded' | 'error'

/* ========== Props & Emits ========== */

const props = defineProps<{
  sessionId: string
}>()

const emit = defineEmits<{
  documentChanged: []
}>()

/* ========== 响应式状态 ========== */

const fileInputRef = ref<HTMLInputElement>()
const isDragging = ref(false)
const dragCounter = ref(0)

const documents = ref<Document[]>([])
const kbStatus = ref<KnowledgeBaseStatus | null>(null)
const docListState = ref<DocListState>('loading')

const uploadState = ref<UploadState>({
  status: 'idle',
  fileName: '',
  fileSize: 0,
  progress: 0,
  errorMessage: '',
})

const showDeleteModal = ref(false)
const deleteTarget = ref<Document | null>(null)
const deletingId = ref<string | null>(null)

/* ========== 工具函数 ========== */

function formatFileSize(bytes: number): string {
  if (bytes === 0 || bytes == null) return '0 B'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getIndexStatus(doc: Document): string {
  if (doc.index_status === 'failed') return 'failed'
  if (doc.chunk_count !== undefined && doc.chunk_count > 0) return 'ready'
  return 'indexing'
}

function getIndexStatusText(doc: Document): string {
  const status = getIndexStatus(doc)
  if (status === 'failed') return '索引失败 ✗'
  if (status === 'ready') return '已索引 ✓'
  return '索引中...'
}

/* ========== API 调用 ========== */

async function fetchKnowledgeBaseStatus() {
  try {
    const res = await axios.get<KnowledgeBaseStatus>(
      `http://localhost:8000/rag/status?session_id=${encodeURIComponent(props.sessionId)}`
    )
    kbStatus.value = res.data
  } catch {
    kbStatus.value = null
  }
}

async function fetchDocuments() {
  docListState.value = 'loading'
  try {
    const res = await axios.get<{ documents: Document[] }>('http://localhost:8000/documents')
    documents.value = res.data.documents || []
    docListState.value = 'loaded'
  } catch {
    documents.value = []
    docListState.value = 'error'
  }
}

async function uploadFile(file: File) {
  uploadState.value = {
    status: 'uploading',
    fileName: file.name,
    fileSize: file.size,
    progress: 0,
    errorMessage: '',
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post('http://localhost:8000/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && event.total > 0) {
          uploadState.value.progress = Math.round((event.loaded / event.total) * 100)
        }
      },
    })

    uploadState.value.status = 'idle'
  } catch (err: any) {
    uploadState.value.status = 'error'
    uploadState.value.errorMessage = err?.response?.data?.detail || err?.message || '上传失败'
  }

  // 刷新数据
  await fetchDocuments()
  await fetchKnowledgeBaseStatus()
  emit('documentChanged')
}

async function deleteDocument(docId: string) {
  deletingId.value = docId
  try {
    await axios.delete(`http://localhost:8000/documents/${docId}`)
    documents.value = documents.value.filter((d) => d.id !== docId)
  } catch {
    // 即使后端失败，前端也先移除（乐观更新）
    documents.value = documents.value.filter((d) => d.id !== docId)
  } finally {
    deletingId.value = null
  }

  await fetchKnowledgeBaseStatus()
  emit('documentChanged')
}

/* ========== 事件处理 ========== */

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    uploadFile(file)
  }
  // 重置 input 以便可以重新选择同一文件
  target.value = ''
}

function onDragEnter(_e: DragEvent) {
  dragCounter.value++
  isDragging.value = true
}

function onDragOver(_e: DragEvent) {
  isDragging.value = true
}

function onDragLeave(_e: DragEvent) {
  dragCounter.value--
  if (dragCounter.value <= 0) {
    dragCounter.value = 0
    isDragging.value = false
  }
}

function onDrop(event: DragEvent) {
  dragCounter.value = 0
  isDragging.value = false

  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext && ['txt', 'pdf', 'docx'].includes(ext)) {
      uploadFile(file)
    } else {
      uploadState.value = {
        status: 'error',
        fileName: '',
        fileSize: 0,
        progress: 0,
        errorMessage: '不支持的文件格式，请上传 PDF / Word / TXT 文件',
      }
    }
  }
}

function confirmDelete(doc: Document) {
  deleteTarget.value = doc
  showDeleteModal.value = true
}

function cancelDelete() {
  showDeleteModal.value = false
  deleteTarget.value = null
}

async function executeDelete() {
  if (!deleteTarget.value) return
  const docId = deleteTarget.value.id
  showDeleteModal.value = false
  deleteTarget.value = null
  await deleteDocument(docId)
}

/* ========== 生命周期 ========== */

onMounted(async () => {
  await Promise.all([fetchDocuments(), fetchKnowledgeBaseStatus()])
})

watch(() => props.sessionId, () => {
  fetchKnowledgeBaseStatus()
})
</script>

<style scoped>
/* ============================================
   KnowledgePanel — 文档上传与知识库管理面板
   使用 style.css 的 CSS 变量作为设计令牌
   ============================================ */

/* --- 容器 --- */
.knowledge-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  background: var(--bg);
  color: var(--text);
  font-family: var(--sans);
  border-radius: 12px;
  border: 1px solid var(--border);
}

/* ============================================
   1. 知识库摘要
   ============================================ */
.kb-summary {
  display: flex;
  align-items: center;
  gap: 0;
  padding: 16px 20px;
  background: var(--accent-bg);
  border: 1px solid var(--accent-border);
  border-radius: 10px;
}

.summary-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.summary-label {
  font-size: 13px;
  color: var(--text);
  flex-shrink: 0;
}

.summary-value {
  font-family: var(--mono);
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
  margin-left: auto;
}

.summary-divider {
  width: 1px;
  height: 32px;
  background: var(--accent-border);
  margin: 0 16px;
  flex-shrink: 0;
}

/* ============================================
   2. 拖拽上传区域
   ============================================ */
.drop-zone {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  min-height: 140px;
  padding: 24px;
  border: 2px dashed var(--border);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.25s ease;
  background: var(--bg);
}

.drop-zone:hover {
  border-color: var(--accent-border);
  background: var(--accent-bg);
}

.drop-zone--active {
  border-color: var(--accent);
  background: var(--accent-bg);
  transform: scale(1.01);
}

.file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  clip-path: inset(50%);
}

.drop-zone__icon {
  font-size: 32px;
  opacity: 0.7;
  transition: transform 0.25s ease;
}

.drop-zone--active .drop-zone__icon {
  transform: translateY(-2px);
  opacity: 1;
}

.drop-zone__text {
  text-align: center;
}

.drop-zone__primary {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-h);
}

.drop-zone__secondary {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text);
  opacity: 0.7;
}

/* ============================================
   3. 上传进度条
   ============================================ */
.upload-progress {
  padding: 14px 16px;
  background: var(--code-bg);
  border: 1px solid var(--border);
  border-radius: 10px;
}

.upload-progress__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.upload-progress__name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-h);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 12px;
}

.upload-progress__percent {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
  flex-shrink: 0;
}

.upload-progress__bar {
  width: 100%;
  height: 6px;
  background: var(--border);
  border-radius: 3px;
  overflow: hidden;
}

.upload-progress__fill {
  height: 100%;
  background: var(--accent);
  border-radius: 3px;
  transition: width 0.15s ease;
}

.upload-progress__footer {
  margin-top: 6px;
}

.upload-progress__size {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text);
  opacity: 0.7;
}

/* 上传错误 */
.upload-error {
  padding: 12px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  font-size: 13px;
  color: #ef4444;
}

/* ============================================
   4. 文档列表
   ============================================ */
.doc-list-section {
  display: flex;
  flex-direction: column;
}

.section-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-h);
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 24px;
  justify-content: center;
  font-size: 13px;
  color: var(--text);
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  padding: 16px;
  text-align: center;
  font-size: 13px;
  color: #ef4444;
}

.retry-btn {
  background: none;
  border: none;
  color: var(--accent);
  cursor: pointer;
  text-decoration: underline;
  font-size: 13px;
  padding: 0;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 20px;
  text-align: center;
  color: var(--text);
  opacity: 0.6;
  border: 1px dashed var(--border);
  border-radius: 10px;
}

.empty-state__icon {
  font-size: 36px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

/* 文档列表项 */
.doc-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  transition: all 0.2s ease;
}

.doc-item:hover {
  box-shadow: var(--shadow);
  border-color: var(--accent-border);
}

.doc-item--deleting {
  opacity: 0.5;
  pointer-events: none;
}

.doc-item__icon {
  font-size: 24px;
  flex-shrink: 0;
}

.doc-item__info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doc-item__name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-h);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.doc-item__meta {
  display: flex;
  gap: 10px;
  font-size: 12px;
  color: var(--text);
  opacity: 0.7;
}

.doc-item__chunks {
  font-family: var(--mono);
}

.doc-item__size {
  font-family: var(--mono);
}

.doc-item__right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* 索引状态徽章 */
.index-badge {
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
}

.index-badge--indexing {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.index-badge--ready {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.index-badge--failed {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* 删除按钮 */
.doc-item__delete {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.08);
  color: #ef4444;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.doc-item__delete:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
}

.doc-item__delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ============================================
   5. 删除确认弹窗
   ============================================ */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  width: 90%;
  max-width: 420px;
  box-shadow:
    rgba(0, 0, 0, 0.15) 0 20px 60px -10px,
    rgba(0, 0, 0, 0.08) 0 8px 24px -8px;
}

.modal h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-h);
}

.modal p {
  margin: 0 0 24px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
}

.modal p strong {
  color: var(--text-h);
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.modal-btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.modal-btn--cancel {
  background: var(--code-bg);
  color: var(--text);
  border: 1px solid var(--border);
}

.modal-btn--cancel:hover {
  background: var(--border);
}

.modal-btn--confirm {
  background: #ef4444;
  color: #fff;
}

.modal-btn--confirm:hover {
  background: #dc2626;
}
</style>
