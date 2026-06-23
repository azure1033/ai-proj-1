import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

type Locale = 'zh' | 'en'

interface LocaleContextType {
  locale: Locale
  t: (key: string) => string
  toggleLocale: () => void
}

const translations: Record<Locale, Record<string, string>> = {
  zh: {
    appTitle: 'AI 智能问答助手',
    newSession: '新建会话',
    renameSession: '重命名',
    deleteSession: '删除',
    confirmDelete: '确认删除',
    cancel: '取消',
    send: '发送',
    inputPlaceholder: '输入您的问题...',
    thinking: '思考中...',
    agentSteps: '推理步骤',
    noMessages: '开始新对话',
    welcomeTitle: 'AI 智能问答助手',
    welcomeDesc: '我可以帮您回答问题、查询天气、搜索信息等',
    knowledgePanel: '知识库',
    uploadDoc: '上传文档',
    dragDrop: '拖拽文件到此处或点击上传',
    supportedFormats: '支持 .txt, .pdf, .docx',
    uploading: '上传中...',
    indexed: '已索引',
    notIndexed: '未索引',
    chunks: '分块',
    settings: '设置',
    llmProvider: 'LLM 提供商',
    embeddingProvider: 'Embedding 提供商',
    activate: '激活',
    active: '当前活跃',
    testConnection: '测试连接',
    addProvider: '添加提供商',
    chunkSize: '分块大小',
    chunkOverlap: '重叠大小',
    retrievalK: '检索数量',
    save: '保存',
    language: '语言',
    weather: '天气',
    history: '历史记录',
    clearHistory: '清空历史',
    deleteDoc: '删除文档',
    close: '关闭',
    error: '错误',
    retry: '重试',
  },
  en: {
    appTitle: 'AI Assistant',
    newSession: 'New Session',
    renameSession: 'Rename',
    deleteSession: 'Delete',
    confirmDelete: 'Confirm Delete',
    cancel: 'Cancel',
    send: 'Send',
    inputPlaceholder: 'Type your question...',
    thinking: 'Thinking...',
    agentSteps: 'Reasoning Steps',
    noMessages: 'Start a new conversation',
    welcomeTitle: 'AI Assistant',
    welcomeDesc: 'I can help you with questions, weather, search, and more',
    knowledgePanel: 'Knowledge Base',
    uploadDoc: 'Upload Document',
    dragDrop: 'Drag & drop files here or click to upload',
    supportedFormats: 'Supports .txt, .pdf, .docx',
    uploading: 'Uploading...',
    indexed: 'Indexed',
    notIndexed: 'Not indexed',
    chunks: 'chunks',
    settings: 'Settings',
    llmProvider: 'LLM Provider',
    embeddingProvider: 'Embedding Provider',
    activate: 'Activate',
    active: 'Active',
    testConnection: 'Test Connection',
    addProvider: 'Add Provider',
    chunkSize: 'Chunk Size',
    chunkOverlap: 'Chunk Overlap',
    retrievalK: 'Retrieval K',
    save: 'Save',
    language: 'Language',
    weather: 'Weather',
    history: 'History',
    clearHistory: 'Clear History',
    deleteDoc: 'Delete Document',
    close: 'Close',
    error: 'Error',
    retry: 'Retry',
  },
}

const LocaleContext = createContext<LocaleContextType>({
  locale: 'zh',
  t: (key: string) => key,
  toggleLocale: () => {},
})

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(() => {
    const saved = localStorage.getItem('ai-chat-locale')
    return (saved === 'en' ? 'en' : 'zh')
  })

  const t = useCallback((key: string): string => {
    return translations[locale][key] || key
  }, [locale])

  const toggleLocale = useCallback(() => {
    setLocale(prev => {
      const next = prev === 'zh' ? 'en' : 'zh'
      localStorage.setItem('ai-chat-locale', next)
      return next
    })
  }, [])

  return (
    <LocaleContext.Provider value={{ locale, t, toggleLocale }}>
      {children}
    </LocaleContext.Provider>
  )
}

export function useLocale() {
  return useContext(LocaleContext)
}
