import { useState, useCallback, useEffect } from 'react'
import { LocaleProvider } from './context/LocaleContext'
import AppSidebar from './components/AppSidebar'
import ChatView from './components/ChatView'
import Dashboard from './components/Dashboard'
import type { Session } from './types'
import api from './api'

function generateId(): string {
  return crypto.randomUUID?.() || 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
    const r = (Math.random() * 16) | 0
    return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16)
  })
}

export default function App() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [showDashboard, setShowDashboard] = useState(false)

  // ── Load sessions from backend on mount ──────────────────
  useEffect(() => {
    const savedId = localStorage.getItem('ai-chat-current-session')

    api.get('/sessions')
      .then(res => {
        const serverSessions: Session[] = res.data.sessions || []
        setSessions(serverSessions)

        // Determine current session
        if (savedId && serverSessions.some(s => s.id === savedId)) {
          setCurrentSessionId(savedId)
        } else if (serverSessions.length > 0) {
          setCurrentSessionId(serverSessions[0].id)
        } else {
          // No sessions at all — create one
          createSession().then(id => setCurrentSessionId(id))
        }
      })
      .catch(() => {
        // Backend unavailable — fallback to localStorage
        try {
          const saved = localStorage.getItem('ai-chat-sessions')
          const local: Session[] = saved ? JSON.parse(saved) : []
          setSessions(local)
          setCurrentSessionId(savedId || local[0]?.id || null)
        } catch { setCurrentSessionId(null) }
      })
      .finally(() => setLoading(false))
  }, [])

  // ── Persist current session ID to localStorage ──────────
  const saveCurrentId = useCallback((id: string | null) => {
    setCurrentSessionId(id)
    if (id) localStorage.setItem('ai-chat-current-session', id)
    else localStorage.removeItem('ai-chat-current-session')
  }, [])

  // ── Helper: create session on backend ────────────────────
  const createSession = async (name?: string): Promise<string> => {
    try {
      const res = await api.post('/sessions', { name: name || '新会话' })
      return res.data.session.id
    } catch {
      return generateId()
    }
  }

  // ── CRUD handlers ───────────────────────────────────────

  const onCreateSession = useCallback(async () => {
    const id = await createSession()
    // Reload session list from backend
    try {
      const res = await api.get('/sessions')
      setSessions(res.data.sessions || [])
    } catch { /* ignore */ }
    saveCurrentId(id)
  }, [saveCurrentId])

  const onSelectSession = useCallback((id: string) => {
    saveCurrentId(id)
  }, [saveCurrentId])

  const onRenameSession = useCallback(async (id: string, name: string) => {
    // Update locally first (instant feedback)
    setSessions(prev => prev.map(s => s.id === id ? { ...s, name, updated_at: new Date().toISOString() } : s))
    // Sync to backend
    try {
      await api.patch(`/sessions/${id}`, { name })
    } catch { /* silent */ }
  }, [])

  const onDeleteSession = useCallback(async (id: string) => {
    // Remove locally first
    const updated = sessions.filter(s => s.id !== id)
    setSessions(updated)
    // Sync to backend
    try {
      await api.delete(`/sessions/${id}`)
    } catch { /* silent */ }
    // Switch to next session
    if (currentSessionId === id) {
      const nextId = updated[0]?.id || null
      if (nextId) {
        saveCurrentId(nextId)
      } else {
        // No sessions left — create one
        const newId = await createSession()
        try {
          const res = await api.get('/sessions')
          setSessions(res.data.sessions || [])
        } catch { /* ignore */ }
        saveCurrentId(newId)
      }
    }
  }, [sessions, currentSessionId, saveCurrentId])

  // ── After sending a message, refresh session metadata ────
  const onMessageSent = useCallback(async () => {
    try {
      const res = await api.get('/sessions')
      setSessions(res.data.sessions || [])
    } catch { /* ignore */ }
  }, [])

  if (loading) {
    return <div className="app-root" style={{ alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ color: 'var(--text-tertiary)', fontSize: '14px' }}>加载中...</div>
    </div>
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
          onToggleDashboard={() => setShowDashboard(!showDashboard)}
        />
        {showDashboard ? (
          <Dashboard />
        ) : (
          <ChatView
            currentSessionId={currentSessionId}
            onMessageSent={onMessageSent}
          />
        )}
      </div>
    </LocaleProvider>
  )
}
