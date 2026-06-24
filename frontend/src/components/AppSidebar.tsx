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
  onToggleDashboard: () => void
}

export default function AppSidebar({ sessions, currentSessionId, onSelect, onCreate, onRename, onDelete, onToggleDashboard }: AppSidebarProps) {
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
            <button className="btn-icon" onClick={onToggleDashboard} title="Dashboard">📊</button>
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
                  >✕</button>
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
  const [testResult, setTestResult] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [form, setForm] = useState({ id: '', name: '', provider_type: 'llm', base_url: '', api_key: '', model_name: '' })
  const [editingKeyId, setEditingKeyId] = useState<string | null>(null)
  const [editingKeyValue, setEditingKeyValue] = useState('')

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

  const handleTestConnection = async (providerId: string) => {
    setTestResult('')
    try {
      const res = await api.post(`/providers/${providerId}/test`)
      setTestResult(res.data.message || '连接成功')
    } catch (err: any) {
      setTestResult(err.response?.data?.detail || '连接失败')
    }
  }

  const handleSaveApiKey = async (providerId: string) => {
    if (!editingKeyValue.trim()) return
    try {
      await api.put(`/providers/${providerId}`, { api_key: editingKeyValue })
      setMessage('API Key 已保存')
      setEditingKeyId(null)
      setEditingKeyValue('')
      loadProviders()
    } catch (err: any) {
      setMessage(err.response?.data?.detail || '保存失败')
    }
  }

  const handleAddProvider = async () => {
    if (!form.id || !form.name || !form.base_url || !form.model_name) {
      setMessage('请填写所有必填字段')
      return
    }
    try {
      await api.post('/providers', form)
      setMessage('添加成功')
      setShowAddForm(false)
      setForm({ id: '', name: '', provider_type: 'llm', base_url: '', api_key: '', model_name: '' })
      loadProviders()
    } catch (err: any) {
      setMessage(err.response?.data?.detail || '添加失败')
    }
  }

  if (loading) return <div className="modal-overlay"><div className="modal"><div className="modal-body">{t('thinking')}</div></div></div>

  const ProviderCard = ({ p }: { p: any }) => (
    <div className={`provider-card ${p.is_active ? 'provider-card--active' : ''}`}>
      <div className="provider-name">{p.name}</div>
      <div className="provider-model">{p.model_name}</div>
      <div className="provider-url">{p.base_url}</div>
      {editingKeyId === p.id ? (
        <div style={{ display: 'flex', gap: '4px', marginTop: '4px' }}>
          <input className="session-edit-input" type="password" placeholder="API Key"
            value={editingKeyValue} onChange={e => setEditingKeyValue(e.target.value)}
            style={{ flex: 1, fontSize: '12px' }} autoFocus
            onKeyDown={e => e.key === 'Enter' && handleSaveApiKey(p.id)} />
          <button className="btn-sm" onClick={() => handleSaveApiKey(p.id)}>保存</button>
          <button className="btn-sm" style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
            onClick={() => setEditingKeyId(null)}>取消</button>
        </div>
      ) : (
        <div style={{ display: 'flex', gap: '4px', marginTop: '6px' }}>
          {p.is_active
            ? <span className="provider-badge provider-badge--active">{t('active')}</span>
            : <button className="btn-sm" onClick={() => handleActivate(p.id)}>{t('activate')}</button>
          }
          <button className="btn-sm" style={{ background: 'var(--bg-elevated)', color: 'var(--text-secondary)', border: '1px solid var(--border-default)' }}
            onClick={() => handleTestConnection(p.id)}>{t('testConnection')}</button>
          <button className="btn-sm" style={{ background: 'var(--bg-elevated)', color: 'var(--accent-cyan)', border: '1px solid var(--border-default)', fontSize: '11px' }}
            onClick={() => { setEditingKeyId(p.id); setEditingKeyValue('') }}
            title="Set API Key">🔑</button>
        </div>
      )}
    </div>
  )

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()} style={{ minWidth: '520px' }}>
        <div className="modal-header">
          <h3>{t('settings')}</h3>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {message && <div className="settings-message" onClick={() => setMessage('')}>{message}</div>}
          {testResult && <div className="settings-message" onClick={() => setTestResult('')}>{testResult}</div>}

          {/* ── Add Provider Form ── */}
          <button className="btn-new-session" style={{ width: '100%', margin: '0 0 12px 0' }}
            onClick={() => setShowAddForm(!showAddForm)}>
            + {t('addProvider')}
          </button>
          {showAddForm && (
            <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-md)', padding: '12px', marginBottom: '12px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '8px' }}>
                <input className="session-edit-input" placeholder="ID (e.g. my-provider)" value={form.id}
                  onChange={e => setForm({ ...form, id: e.target.value })} />
                <input className="session-edit-input" placeholder="Name" value={form.name}
                  onChange={e => setForm({ ...form, name: e.target.value })} />
              </div>
              <select style={{ width: '100%', marginBottom: '8px', padding: '4px 8px', background: 'var(--bg-input)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', fontSize: '13px' }}
                value={form.provider_type} onChange={e => setForm({ ...form, provider_type: e.target.value })}>
                <option value="llm">LLM Provider</option>
                <option value="embedding">Embedding Provider</option>
              </select>
              <input className="session-edit-input" placeholder="Base URL (https://api.deepseek.com/v1)" value={form.base_url}
                onChange={e => setForm({ ...form, base_url: e.target.value })} style={{ width: '100%', marginBottom: '8px' }} />
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '8px' }}>
                <input className="session-edit-input" type="password" placeholder="API Key" value={form.api_key}
                  onChange={e => setForm({ ...form, api_key: e.target.value })} />
                <input className="session-edit-input" placeholder="Model Name (deepseek-v4-pro)" value={form.model_name}
                  onChange={e => setForm({ ...form, model_name: e.target.value })} />
              </div>
              <button className="btn-sm" onClick={handleAddProvider} style={{ width: '100%', padding: '8px' }}>
                {t('addProvider')}
              </button>
            </div>
          )}

          <h4>{t('llmProvider')}</h4>
          <div className="provider-grid">
            {llmProviders.map((p: any) => <ProviderCard key={p.id} p={p} />)}
          </div>
          <h4>{t('embeddingProvider')}</h4>
          <div className="provider-grid">
            {embProviders.map((p: any) => <ProviderCard key={p.id} p={p} />)}
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
