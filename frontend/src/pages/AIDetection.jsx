import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { FiCpu, FiAlertTriangle, FiRefreshCw, FiSliders, FiShield, FiExternalLink } from 'react-icons/fi'
import apiClient from '../services/api'
import ChartCard from '../components/ChartCard'
import AnomalyDistributionChart from '../components/charts/AnomalyDistributionChart'

function AIDetection() {
  const [data, setData]               = useState(null)
  const [loading, setLoading]         = useState(true)
  const [error, setError]             = useState(null)
  const [contamination, setContamination] = useState(0.1)
  const [topN, setTopN]               = useState(50)

  const fetchAnomalies = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.get('/ai/anomalies', {
        params: { contamination, top_n: topN }
      })
      setData(res.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to analyze anomalies')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAnomalies()
  }, [contamination, topN])

  const getScoreColor = (score) => {
    if (score >= 80) return 'var(--color-critical)'
    if (score >= 60) return 'var(--color-high)'
    if (score >= 40) return 'var(--color-medium)'
    return 'var(--color-accent)'
  }

  return (
    <div className="tv-page">
      <header className="tv-page__header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FiCpu style={{ color: 'var(--color-accent)' }} /> AI Anomaly Detection
          </h1>
          <p className="tv-page__subtitle">
            Unsupervised ML (IsolationForest) scoring abnormal threat behavior & suspicious pattern deviations
          </p>
        </div>
        <button className="tv-btn tv-btn--secondary" onClick={fetchAnomalies} disabled={loading}>
          <FiRefreshCw className={loading ? 'tv-spin' : ''} /> {loading ? 'Analyzing…' : 'Re-run Model'}
        </button>
      </header>

      {/* ── Controls Bar ── */}
      <div className="tv-card" style={{ marginBottom: '1.5rem', padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <FiSliders style={{ color: 'var(--color-text-muted)' }} />
            <label style={{ fontSize: '0.875rem', fontWeight: 500 }}>Sensitivity (Contamination):</label>
            <select
              className="tv-select"
              value={contamination}
              onChange={(e) => setContamination(parseFloat(e.target.value))}
              style={{ width: '130px' }}
            >
              <option value={0.05}>5% (Strict)</option>
              <option value={0.10}>10% (Balanced)</option>
              <option value={0.20}>20% (Broad)</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <label style={{ fontSize: '0.875rem', fontWeight: 500 }}>Limit Results:</label>
            <select
              className="tv-select"
              value={topN}
              onChange={(e) => setTopN(parseInt(e.target.value))}
              style={{ width: '110px' }}
            >
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
              <option value={100}>Top 100</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="tv-card" style={{ padding: '1.5rem', color: 'var(--color-critical)', marginBottom: '1.5rem' }}>
          <FiAlertTriangle /> {error}
        </div>
      )}

      {loading && !data && (
        <div className="tv-card" style={{ padding: '3rem', textAlign: 'center', color: 'var(--color-text-muted)' }}>
          <FiRefreshCw className="tv-spin" size={32} style={{ marginBottom: '1rem', color: 'var(--color-accent)' }} />
          <p>Training IsolationForest on threat dataset…</p>
        </div>
      )}

      {data && (
        <>
          {/* ── Summary Stats Row ── */}
          <div className="tv-grid tv-grid--3" style={{ marginBottom: '1.5rem' }}>
            <div className="tv-stat-card">
              <span className="tv-stat-card__label">Total Analyzed</span>
              <span className="tv-stat-card__value">{data.total_analyzed?.toLocaleString() || 0}</span>
            </div>
            <div className="tv-stat-card">
              <span className="tv-stat-card__label">Detected Anomalies</span>
              <span className="tv-stat-card__value" style={{ color: 'var(--color-critical)' }}>
                {data.total_anomalies?.toLocaleString() || 0}
              </span>
            </div>
            <div className="tv-stat-card">
              <span className="tv-stat-card__label">Highest Anomaly Score</span>
              <span className="tv-stat-card__value" style={{ color: 'var(--color-high)' }}>
                {data.anomalies?.[0]?.anomaly_score ?? 'N/A'}
              </span>
            </div>
          </div>

          {/* ── Score Distribution Chart ── */}
          <div style={{ marginBottom: '1.5rem' }}>
            <ChartCard
              title="Anomaly Score Distribution"
              subtitle="Indicators grouped into 10 score buckets (0 = Normal, 100 = Critical Anomaly)"
              loading={loading}
              isEmpty={!data?.score_distribution?.length}
            >
              <AnomalyDistributionChart data={data.score_distribution} />
            </ChartCard>
          </div>

          {/* ── Anomalies Ranked Table ── */}
          <div className="tv-card" style={{ padding: '1.25rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>
              Ranked Anomalous Indicators ({data.anomalies?.length || 0})
            </h3>
            <div className="tv-table-wrapper">
              <table className="tv-table">
                <thead>
                  <tr>
                    <th>Score</th>
                    <th>Indicator</th>
                    <th>Type</th>
                    <th>Severity</th>
                    <th>Reputation</th>
                    <th>Malware Family</th>
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.anomalies?.map((item) => (
                    <tr key={item.id}>
                      <td>
                        <span
                          className="tv-badge"
                          style={{
                            backgroundColor: getScoreColor(item.anomaly_score),
                            color: '#fff',
                            fontWeight: 700,
                            padding: '0.25rem 0.6rem'
                          }}
                        >
                          {item.anomaly_score}
                        </span>
                      </td>
                      <td style={{ fontFamily: 'monospace', fontWeight: 600 }}>{item.indicator}</td>
                      <td>
                        <span className="tv-pill">{item.indicator_type}</span>
                      </td>
                      <td>
                        <span className={`tv-sev-tag tv-sev-tag--${(item.severity || 'low').toLowerCase()}`}>
                          {item.severity || 'Low'}
                        </span>
                      </td>
                      <td>
                        <span className={`tv-rep-tag tv-rep-tag--${(item.reputation || 'unknown').toLowerCase()}`}>
                          {item.reputation || 'Unknown'}
                        </span>
                      </td>
                      <td>{item.malware_family || '—'}</td>
                      <td>{item.source || '—'}</td>
                      <td>
                        <Link to={`/threats/${item.id}`} className="tv-btn tv-btn--sm tv-btn--ghost" title="View details">
                          <FiExternalLink />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default AIDetection
