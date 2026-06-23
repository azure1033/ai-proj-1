import { useState } from 'react'
import { useLocale } from '../context/LocaleContext'

interface WelcomeScreenProps {
  onSend: (text: string) => void
}

export default function WelcomeScreen({ onSend }: WelcomeScreenProps) {
  const { t } = useLocale()

  const suggestions = [
    '今天北京天气如何？',
    '帮我解释一下这段代码',
    '搜索最新的AI新闻',
    '1+1等于几？',
  ]

  return (
    <div className="welcome-screen">
      <div className="welcome-icon">AI</div>
      <h1>{t('welcomeTitle')}</h1>
      <p>{t('welcomeDesc')}</p>
      <div className="welcome-suggestions">
        {suggestions.map((s, i) => (
          <button key={i} className="suggestion-chip" onClick={() => onSend(s)}>
            {s}
          </button>
        ))}
      </div>
    </div>
  )
}
