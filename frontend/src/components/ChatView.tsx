import { useState, useCallback, useEffect, useRef } from 'react'
import { useLocale } from '../context/LocaleContext'
import ChatInput from './ChatInput'
import MessageList from './MessageList'
import WelcomeScreen from './WelcomeScreen'
import type { ChatMessage, AgentStep } from '../types'
import api from '../api'

interface ChatViewProps {
  currentSessionId: string | null
}

export default function ChatView({ currentSessionId }: ChatViewProps) {
  const { t } = useLocale()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [streaming, setStreaming] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([])
  const abortRef = useRef<AbortController | null>(null)
  // Ref to track agent steps during streaming, avoiding stale closure
  const stepsRef = useRef<AgentStep[]>([])

  // Sync ref with state
  useEffect(() => { stepsRef.current = agentSteps }, [agentSteps])

  // Load history when session changes
  useEffect(() => {
    if (!currentSessionId) { setMessages([]); return }
    api.get(`/sessions/${currentSessionId}/history`).then(res => {
      setMessages(res.data.messages || [])
    }).catch(() => setMessages([]))
  }, [currentSessionId])

  const handleSend = useCallback(async (text: string) => {
    if (!text.trim() || streaming) return

    const userMsg: ChatMessage = { role: 'user', content: text }
    setMessages(prev => [...prev, userMsg])
    setStreaming(true)
    setStreamingText('')
    setAgentSteps([])
    stepsRef.current = []

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const res = await fetch(`/api/ask?stream=true`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, session_id: currentSessionId }),
        signal: controller.signal,
      })

      const reader = res.body?.getReader()
      if (!reader) return

      const decoder = new TextDecoder()
      let buffer = ''
      let fullText = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let eventType = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            const data = line.slice(6)
            try {
              const parsed = JSON.parse(data)
              if (eventType === 'token') {
                fullText += parsed
                setStreamingText(fullText)
              } else if (eventType === 'step') {
                const step: AgentStep = { tool: parsed.tool, tool_input: parsed.input || '', observation: '', thought: '' }
                setAgentSteps(prev => [...prev, step])
              } else if (eventType === 'step_done') {
                setAgentSteps(prev => {
                  const updated = prev.map(s => ({ ...s }))
                  const last = updated[updated.length - 1]
                  if (last) last.observation = typeof parsed === 'string' ? parsed : (parsed.output || '')
                  return updated
                })
              }
            } catch { /* ignore */ }
          }
        }
      }

      // Use ref for accurate step state at completion time
      const finalSteps = stepsRef.current.filter(s => s.tool)
      if (fullText) {
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: fullText,
          steps: finalSteps.length > 0 ? finalSteps : undefined,
        }])
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setMessages(prev => [...prev, { role: 'assistant', content: t('error') + ': ' + err.message }])
      }
    } finally {
      setStreaming(false)
      setStreamingText('')
      setAgentSteps([])
      abortRef.current = null
    }
  }, [streaming, currentSessionId, t])

  const handleStop = useCallback(() => {
    abortRef.current?.abort()
  }, [])

  return (
    <div className="chat-view">
      {messages.length === 0 && !streaming ? (
        <WelcomeScreen onSend={handleSend} />
      ) : (
        <MessageList messages={messages} streamingText={streamingText} agentSteps={agentSteps} />
      )}
      <ChatInput onSend={handleSend} onStop={handleStop} streaming={streaming} />
    </div>
  )
}
