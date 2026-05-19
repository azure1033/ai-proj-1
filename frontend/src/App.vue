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

// --- Persistence ---
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

const generateId = () =>
  crypto.randomUUID?.() ||
  'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
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

// --- Init ---
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
