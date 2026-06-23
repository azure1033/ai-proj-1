import { useState, useRef, useEffect } from 'react'
import { useLocale } from '../context/LocaleContext'

interface ChatInputProps {
  onSend: (text: string) => void
  onStop: () => void
  streaming: boolean
}

export default function ChatInput({ onSend, onStop, streaming }: ChatInputProps) {
  const { t } = useLocale()
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [text])

  const handleSubmit = () => {
    if (text.trim() && !streaming) {
      onSend(text.trim())
      setText('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="chat-input-container">
      <div className="chat-input-wrapper">
        <textarea
          ref={textareaRef}
          className="chat-input"
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('inputPlaceholder')}
          rows={1}
          disabled={streaming}
        />
        <div className="chat-input-actions">
          {streaming ? (
            <button className="btn-stop" onClick={onStop}>■</button>
          ) : (
            <button className="btn-send" onClick={handleSubmit} disabled={!text.trim()}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
