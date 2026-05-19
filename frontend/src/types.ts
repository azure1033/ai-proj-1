export interface Session {
  id: string
  name: string
  preview?: string
  message_count: number
  created_at: string
  updated_at: string
}

export interface AgentStep {
  thought?: string
  tool: string
  tool_input: string
  observation: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  intent?: string
  steps?: AgentStep[]
}
