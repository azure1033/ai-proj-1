import { useState, useEffect } from 'react'
import { useLocale } from '../context/LocaleContext'
import api from '../api'

interface Metrics {
  total_requests: number
  total_tokens: number
  avg_latency_ms: number
  error_rate: number
  by_provider: { provider_id: string; count: number; tokens: number; avg_latency: number }[]
  by_model: { model_name: string; count: number; tokens: number }[]
  daily: { date: string; count: number; tokens: number }[]
}

export default function Dashboard() {
  const { t } = useLocale()
  const [metrics, setMetrics] = useState<Metrics | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/metrics?days=7').then(res => {
      setMetrics(res.data)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="welcome-screen"><p>{t('thinking')}</p></div>
  if (!metrics) return <div className="welcome-screen"><p>Failed to load metrics</p></div>

  const maxTokens = Math.max(...metrics.by_provider.map(p => p.tokens), 1)

  return (
    <div className="dashboard">
      <h2 style={{ padding: '24px 24px 0', fontSize: '18px' }}>Dashboard</h2>

      {/* Metric Cards */}
      <div className="metrics-grid">
        <MetricCard label="Total Requests" value={metrics.total_requests.toLocaleString()} />
        <MetricCard label="Total Tokens" value={metrics.total_tokens.toLocaleString()} />
        <MetricCard label="Avg Latency" value={`${metrics.avg_latency_ms}ms`} />
        <MetricCard label="Error Rate" value={`${metrics.error_rate}%`} alert={metrics.error_rate > 5} />
      </div>

      {/* Provider Distribution */}
      <div className="dashboard-section">
        <h4>Provider Distribution (7 days)</h4>
        <div className="bar-chart">
          {metrics.by_provider.map(p => (
            <div key={p.provider_id} className="bar-row">
              <span className="bar-label">{p.provider_id || 'unknown'}</span>
              <div className="bar-track">
                <div className="bar-fill" style={{ width: `${(p.tokens / maxTokens) * 100}%` }} />
              </div>
              <span className="bar-value">{p.tokens.toLocaleString()} tokens</span>
            </div>
          ))}
        </div>
      </div>

      {/* Daily Trend */}
      <div className="dashboard-section">
        <h4>Daily Requests (7 days)</h4>
        <div className="trend-chart">
          {metrics.daily.map(d => {
            const maxCount = Math.max(...metrics.daily.map(x => x.count), 1)
            return (
              <div key={d.date} className="trend-bar-wrapper">
                <div className="trend-bar" style={{ height: `${(d.count / maxCount) * 100}%` }} title={`${d.date}: ${d.count} requests`} />
                <span className="trend-label">{d.date.slice(5)}</span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

function MetricCard({ label, value, alert }: { label: string; value: string; alert?: boolean }) {
  return (
    <div className={`metric-card ${alert ? 'metric-card--alert' : ''}`}>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
    </div>
  )
}
