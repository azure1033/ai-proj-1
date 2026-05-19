<template>
  <!-- Mobile drawer -->
  <Teleport to="body" v-if="isMobile">
    <Transition name="drawer">
      <div v-if="showMobile" class="drawer-overlay" @click.self="showMobile = false">
        <aside class="sidebar sidebar-drawer" @click.stop>
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
            <div v-for="s in filtered" :key="s.id" class="session-item" :class="{ active: s.id === currentSessionId }" @click="emit('select', s.id)">
              <template v-if="renamingId === s.id">
                <input v-model="renameInput" class="rename-input" @keydown.enter="confirmRename(s.id)" @keydown.escape="renamingId = null" @click.stop @blur="confirmRename(s.id)" autofocus />
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
            <div v-if="filtered.length === 0" class="empty-list">{{ searchQuery ? '无匹配会话' : '暂无会话' }}</div>
          </div>
          <div class="sidebar-footer">
            <button class="new-chat-btn" @click="emit('create')">+ 新对话</button>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>

  <!-- Desktop sidebar -->
  <aside v-if="!isMobile" class="sidebar sidebar-desktop">
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
      <div v-for="s in filtered" :key="s.id" class="session-item" :class="{ active: s.id === currentSessionId }" @click="emit('select', s.id)">
        <template v-if="renamingId === s.id">
          <input v-model="renameInput" class="rename-input" @keydown.enter="confirmRename(s.id)" @keydown.escape="renamingId = null" @click.stop @blur="confirmRename(s.id)" autofocus />
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
      <div v-if="filtered.length === 0" class="empty-list">{{ searchQuery ? '无匹配会话' : '暂无会话' }}</div>
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
import type { Session } from '../types'

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
  [...props.sessions].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
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

// Time
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
.session-actions { display: none; gap: 2px; flex-shrink: 0; }
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
.modal-card h3 { margin-bottom: var(--space-3); font-size: 16px; color: var(--text-primary); }
.modal-card p { margin-bottom: var(--space-5); font-size: 13px; color: var(--text-tertiary); line-height: 1.5; }
.modal-btns { display: flex; gap: var(--space-3); justify-content: flex-end; }
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
