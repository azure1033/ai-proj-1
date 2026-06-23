import { useState, useRef, useEffect } from 'react'
import { useLocale } from '../context/LocaleContext'
import type { Session } from '../types'

interface AppSidebarProps {
  sessions: Session[]
  currentSessionId: string | null
  onSelect: (id: string) => void
  onCreate: () => void
  onRename: (id: string, name: string) => void
  onDelete: (id: string) => void
}

export default function AppSidebar({ sessions, currentSessionId, onSelect, onCreate, onRename, onDelete }: AppSidebarProps) {
  const { t, locale, toggleLocale } = useLocale()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [showKnowledge, setShowKnowledge] = useState(false)

  const handleDoubleClick = (s: Session) => {
    setEditingId(s.id)
    setEditName(s.name)
  }

  const handleRenameConfirm = () => {
    if (editingId && editName.trim()) {
      onRename(editingId, editName.trim())
    }
    setEditingId(null)
    setEditName('')
  }

  return (
    <>
      <button className="sidebar-toggle" onClick={() => setMobileOpen(!mobileOpen)}>☰</button>
      <aside className={`sidebar ${mobileOpen ? 'sidebar--open' : ''}`}>
        <div className="sidebar-header">
          <h2>{t('appTitle')}</h2>
          <div className="sidebar-header-actions">
            <button className="btn-icon" onClick={() => setShowKnowledge(!showKnowledge)} title={t('knowledgePanel')}>📚</button>
            <button className="btn-icon" onClick={() => setShowSettings(!showSettings)} title={t('settings')}>⚙</button>
            <button className="btn-icon" onClick={toggleLocale} title={t('language')}>{locale === 'zh' ? 'EN' : '中文'}</button>
          </div>
        </div>
        <button className="btn-new-session" onClick={() => { onCreate(); setMobileOpen(false) }}>+ {t('newSession')}</button>
        <div className="session-list">
          {sessions.map(s => (
            <div
              key={s.id}
              className={`session-item ${s.id === currentSessionId ? 'session-item--active' : ''}`}
              onClick={() => { onSelect(s.id); setMobileOpen(false) }}
              onDoubleClick={() => handleDoubleClick(s)}
            >
              {editingId === s.id ? (
                <input
                  className="session-edit-input"
                  value={editName}
                  onChange={e => setEditName(e.target.value)}
                  onBlur={handleRenameConfirm}
                  onKeyDown={e => e.key === 'Enter' && handleRenameConfirm()}
                  autoFocus
                  onClick={e => e.stopPropagation()}
                />
              ) : (
                <>
                  <span className="session-name">{s.name}</span>
                  <span className="session-count">{s.message_count}</span>
                  <button
                    className="btn-delete-session"
                    onClick={e => { e.stopPropagation(); if (confirm(t('confirmDelete'))) onDelete(s.id) }}
                    title={t('deleteSession')}
                  >🗑</button>
                </>
              )}
            </div>
          ))}
        </div>
      </aside>
      {mobileOpen && <div className="sidebar-overlay" onClick={() => setMobileOpen(false)} />}
      {showSettings && <SettingsModal onClose={() => setShowSettings(false)} />}
      {showKnowledge && <KnowledgePanel onClose={() => setShowKnowledge(false)} />}
    </>
  )
}

// ── Settings Modal ─────────────────────────────────────────

import api from '../api'

function SettingsModal({ onClose }: { onClose: () => void }) {
  const { t } = useLocale()
  const [llmProviders, setLlmProviders] = useState<any[]>([])
  const [embProviders, setEmbProviders] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')

  const loadProviders = async () => {
    setLoading(true)
    try {
      const res = await api.get('/providers')
      setLlmProviders(res.data.llm || [])
      setEmbProviders(res.data.embedding || [])
    } catch { setMessage(t('error')) }
    setLoading(false)
  }

  useEffect(() => { loadProviders() }, [])

  const handleActivate = async (id: string) => {
    try {
      await api.post(`/providers/${id}/activate`)
      setMessage('已激活')
      loadProviders()
    } catch (err: any) {
      setMessage(err.response?.data?.detail || t('error'))
    }
  }

  if (loading) return <div className="modal-overlay"><div className="modal"><div className="modal-body">{t('thinking')}</div></div></div>

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('settings')}</h3>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {message && <div className="settings-message">{message}</div>}
          <h4>{t('llmProvider')}</h4>
          <div className="provider-grid">
            {llmProviders.map((p: any) => (
              <div key={p.id} className={`provider-card ${p.is_active ? 'provider-card--active' : ''}`}>
                <div className="provider-name">{p.name}</div>
                <div className="provider-model">{p.model_name}</div>
                {p.is_active
                  ? <span className="provider-badge provider-badge--active">{t('active')}</span>
                  : <button className="btn-sm" onClick={() => handleActivate(p.id)}>{t('activate')}</button>
                }
              </div>
            ))}
          </div>
          <h4>{t('embeddingProvider')}</h4>
          <div className="provider-grid">
            {embProviders.map((p: any) => (
              <div key={p.id} className={`provider-card ${p.is_active ? 'provider-card--active' : ''}`}>
                <div className="provider-name">{p.name}</div>
                <div className="provider-model">{p.model_name}</div>
                {p.is_active
                  ? <span className="provider-badge provider-badge--active">{t('active')}</span>
                  : <button className="btn-sm" onClick={() => handleActivate(p.id)}>{t('activate')}</button>
                }
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Knowledge Panel ────────────────────────────────────────

function KnowledgePanel({ onClose }: { onClose: () => void }) {
  const { t } = useLocale()
  const [documents, setDocuments] = useState<any[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadDocs = async () => {
    try {
      const res = await api.get('/documents')
      setDocuments(res.data.documents || [])
    } catch { /* ignore */ }
  }

  useEffect(() => { loadDocs() }, [])

  const handleUpload = async (file: File) => {
    if (!file) return
    setUploading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      await api.post('/documents/upload', form)
      loadDocs()
    } catch { /* ignore */ }
    setUploading(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleUpload(file)
  }

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/documents/${id}`)
      loadDocs()
    } catch { /* ignore */ }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal knowledge-panel" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{t('knowledgePanel')}</h3>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div
            className={`drop-zone ${dragOver ? 'drop-zone--active' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? <p>{t('uploading')}</p> : <p>{t('dragDrop')}</p>}
            <p className="drop-hint">{t('supportedFormats')}</p>
            <input ref={fileInputRef} type="file" accept=".txt,.pdf,.docx" className="file-input-hidden" onChange={e => { const f = e.target.files?.[0]; if (f) handleUpload(f) }} />
          </div>
          <div className="doc-list">
            {documents.map((d: any) => (
              <div key={d.id} className="doc-item">
                <span className="doc-name">{d.filename}</span>
                <span className="doc-meta">{d.chunks} {t('chunks')}</span>
                <span className={`doc-status ${d.indexed ? 'doc-status--ok' : ''}`}>{d.indexed ? t('indexed') : t('notIndexed')}</span>
                <button className="btn-delete-doc" onClick={() => handleDelete(d.id)} title={t('deleteDoc')}>🗑</button>
              </div>
            ))}
            {documents.length === 0 && <p className="doc-empty">{t('dragDrop')}</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
