import { FiAlertTriangle, FiShield, FiActivity, FiTrendingUp } from 'react-icons/fi'
import StatCard from '../components/StatCard'
import ChartCard from '../components/ChartCard'
import ThreatTable from '../components/ThreatTable'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
import SeverityPieChart from '../components/charts/SeverityPieChart'
import ThreatTrendChart from '../components/charts/ThreatTrendChart'
import { useStats } from '../hooks/useStats'
import { useRecentThreats } from '../hooks/useRecentThreats'
import { useThreatAggregates } from '../hooks/useThreatAggregates'

function relativeTime(value) {
  if (!value) return ''
  const diffMs = Date.now() - new Date(value).getTime()
  const minutes = Math.round(diffMs / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.round(hours / 24)}d ago`
}

function Dashboard() {
  const { data: stats, loading: statsLoading, error: statsError, refetch: refetchStats } = useStats()
  const { data: recent, loading: recentLoading, error: recentError } = useRecentThreats(8)
  const { dailyTrend } = useThreatAggregates(recent)

  const handleDownloadWeeklyReport = () => {
    const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'
    window.open(`${apiBase}/report/weekly`, '_blank', 'noopener,noreferrer')
  }

  const severity = stats?.severity_distribution || {}
  const highAndCritical = (severity.high || 0) + (severity.critical || 0)

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Dashboard</h1>
          <p className="page__subtitle">Live overview of ingested threat intelligence</p>
        </div>
        <div>
          <button type="button" className="btn btn-outline-light btn-sm" onClick={handleDownloadWeeklyReport}>
            Download Weekly Report
          </button>
        </div>
      </div>

      {statsError && <ErrorState message={statsError.message} onRetry={refetchStats} />}

      {!statsError && (
        <div className="row g-3 mb-4">
          <div className="col-6 col-xl-3">
            <StatCard label="Total Threats" value={statsLoading ? '—' : stats.total_threats} icon={FiShield} accent="blue" />
          </div>
          <div className="col-6 col-xl-3">
            <StatCard label="High Severity" value={statsLoading ? '—' : highAndCritical} icon={FiAlertTriangle} accent="red" />
          </div>
          <div className="col-6 col-xl-3">
            <StatCard label="Medium Severity" value={statsLoading ? '—' : severity.medium || 0} icon={FiActivity} accent="amber" />
          </div>
          <div className="col-6 col-xl-3">
            <StatCard label="Low Severity" value={statsLoading ? '—' : severity.low || 0} icon={FiTrendingUp} accent="purple" />
          </div>
        </div>
      )}

      <div className="row g-3 mb-4">
        <div className="col-lg-5">
          <ChartCard
            title="Severity Breakdown"
            loading={statsLoading}
            error={statsError}
            isEmpty={!statsLoading && Object.keys(severity).length === 0}
          >
            <SeverityPieChart data={severity} />
          </ChartCard>
        </div>
        <div className="col-lg-7">
          <ChartCard
            title="Threat Timeline"
            subtitle="Based on the most recently ingested indicators"
            loading={recentLoading}
            error={recentError}
            isEmpty={!recentLoading && dailyTrend.length === 0}
          >
            <ThreatTrendChart data={dailyTrend} />
          </ChartCard>
        </div>
      </div>

      <div className="row g-3">
        <div className="col-lg-7">
          <div className="panel">
            <div className="panel__header">
              <h3 className="panel__title">Latest Threats</h3>
            </div>
            {recentLoading && <LoadingSpinner label="Loading latest threats..." />}
            {!recentLoading && recentError && <ErrorState message={recentError.message} />}
            {!recentLoading && !recentError && <ThreatTable threats={(recent || []).slice(0, 6)} compact />}
          </div>
        </div>
        <div className="col-lg-5">
          <div className="panel">
            <div className="panel__header">
              <h3 className="panel__title">Recent Activity</h3>
            </div>
            {recentLoading && <LoadingSpinner label="Loading activity..." />}
            {!recentLoading && recentError && <ErrorState message={recentError.message} />}
            {!recentLoading && !recentError && (!recent || recent.length === 0) && (
              <EmptyState message="No ingestion activity yet." />
            )}
            {!recentLoading && !recentError && recent && recent.length > 0 && (
              <ul className="activity-feed">
                {recent.map((threat) => (
                  <li key={threat.id} className={`activity-feed__item activity-feed__item--${threat.severity}`}>
                    <div>
                      <p className="activity-feed__text">
                        New <strong>{threat.severity}</strong>-severity {threat.indicator_type.toLowerCase()} from{' '}
                        <strong>{threat.source}</strong>
                      </p>
                      <span className="activity-feed__time">{relativeTime(threat.created_at)}</span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
