import { useState } from 'react'
import type { ChatMessage, AgentStep } from '../types'

interface MessageBubbleProps {
  message: ChatMessage
  isStreaming?: boolean
  streamSteps?: AgentStep[]
}

export default function MessageBubble({ message, isStreaming, streamSteps }: MessageBubbleProps) {
  const [stepsOpen, setStepsOpen] = useState(false)
  const isUser = message.role === 'user'
  const steps = message.steps || streamSteps

  return (
    <div className={`message ${isUser ? 'message--user' : 'message--assistant'}`}>
      {message.intent && (
        <span className="message-intent">{message.intent}</span>
      )}
      <div className={`message-bubble ${isUser ? 'message-bubble--user' : 'message-bubble--assistant'} ${isStreaming ? 'message-bubble--streaming' : ''}`}>
        <div className="message-content" dangerouslySetInnerHTML={{ __html: formatContent(message.content) }} />
        {isStreaming && <span className="cursor-blink">|</span>}
      </div>
      {steps && steps.length > 0 && (
        <div className="message-steps">
          <button className="btn-steps-toggle" onClick={() => setStepsOpen(!stepsOpen)}>
            {stepsOpen ? '▼' : '▶'} Agent Steps ({steps.length})
          </button>
          {stepsOpen && (
            <div className="steps-panel">
              {steps.map((s, i) => (
                <div key={i} className="step-item">
                  <div className="step-header">
                    <span className="step-tool">{s.tool}</span>
                    <span className="step-input">{s.tool_input}</span>
                  </div>
                  {s.observation && <div className="step-output">{s.observation}</div>}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function formatContent(text: string): string {
  if (!text) return ''
  // Basic markdown: code blocks, bold, links, line breaks
  let html = text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/```(\w*)\n?([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    .replace(/\n/g, '<br/>')
  return html
}
