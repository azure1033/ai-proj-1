import { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import type { ChatMessage, AgentStep } from '../types'

interface MessageListProps {
  messages: ChatMessage[]
  streamingText: string
  agentSteps: { tool: string; input: string; output: string }[]
}

export default function MessageList({ messages, streamingText, agentSteps }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  return (
    <div className="message-list">
      {messages.map((msg, i) => (
        <MessageBubble key={i} message={msg} />
      ))}
      {streamingText && (
        <MessageBubble
          message={{ role: 'assistant', content: streamingText }}
          isStreaming
          streamSteps={agentSteps.map(s => ({
            tool: s.tool, tool_input: s.input, observation: s.output, thought: ''
          }))}
        />
      )}
      <div ref={bottomRef} />
    </div>
  )
}
