import { useState, useCallback, useRef } from 'react'
import { LocaleProvider, useLocale } from './context/LocaleContext'
import AppSidebar from './components/AppSidebar'
import ChatView from './components/ChatView'
import type { Session } from './types'

function generateId(): string {
  return crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
}

function loadSessions(): Session[] {
  try {
    const saved = localStorage.getItem('ai-chat-sessions')
    return saved ? JSON.parse(saved) : []
  } catch { return [] }
}

function loadCurrentId(): string | null {
  return localStorage.getItem('ai-chat-current-session')
}

export default function App() {
  const [sessions, setSessions] = useState<Session[]>(loadSessions)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(loadCurrentId)

  const saveSessions = useCallback((updated: Session[]) => {
    setSessions(updated)
    localStorage.setItem('ai-chat-sessions', JSON.stringify(updated))
  }, [])

  const saveCurrentId = useCallback((id: string | null) => {
    setCurrentSessionId(id)
    if (id) localStorage.setItem('ai-chat-current-session', id)
    else localStorage.removeItem('ai-chat-current-session')
  }, [])

  const onCreateSession = useCallback(() => {
    const now = new Date().toISOString()
    const s: Session = { id: generateId(), name: '新会话', message_count: 0, created_at: now, updated_at: now }
    const updated = [s, ...sessions]
    saveSessions(updated)
    saveCurrentId(s.id)
  }, [sessions, saveSessions, saveCurrentId])

  const onSelectSession = useCallback((id: string) => {
    saveCurrentId(id)
  }, [saveCurrentId])

  const onRenameSession = useCallback(async (id: string, name: string) => {
    const updated = sessions.map(s => s.id === id ? { ...s, name, updated_at: new Date().toISOString() } : s)
    saveSessions(updated)
    try { await fetch(`/api/sessions/${id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name }) }) } catch { /* silent */ }
  }, [sessions, saveSessions])

  const onDeleteSession = useCallback(async (id: string) => {
    const updated = sessions.filter(s => s.id !== id)
    saveSessions(updated)
    try { await fetch(`/api/sessions/${id}`, { method: 'DELETE' }) } catch { /* silent */ }
    if (currentSessionId === id) {
      const nextId = updated[0]?.id || null
      saveCurrentId(nextId)
    }
  }, [sessions, saveSessions, currentSessionId, saveCurrentId])

  // Init: create default session if none exist
  const initialized = useRef(false)
  if (!initialized.current) {
    initialized.current = true
    if (!currentSessionId && sessions.length === 0) {
      const now = new Date().toISOString()
      const s: Session = { id: generateId(), name: '新会话', message_count: 0, created_at: now, updated_at: now }
      saveSessions([s])
      saveCurrentId(s.id)
    }
  }

  return (
    <LocaleProvider>
      <div className="app-root">
        <AppSidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelect={onSelectSession}
          onCreate={onCreateSession}
          onRename={onRenameSession}
          onDelete={onDeleteSession}
        />
        <ChatView
          currentSessionId={currentSessionId}
        />
      </div>
    </LocaleProvider>
  )
}
