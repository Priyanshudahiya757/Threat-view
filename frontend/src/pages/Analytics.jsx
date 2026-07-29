import { useState } from 'react'
import { FiRefreshCw } from 'react-icons/fi'
import ChartCard from '../components/ChartCard'
import SeverityPieChart from '../components/charts/SeverityPieChart'
import CategoryBarChart from '../components/charts/CategoryBarChart'
import CountryDistributionChart from '../components/charts/CountryDistributionChart'
import TopSourcesChart from '../components/charts/TopSourcesChart'
import ThreatTrendChart from '../components/charts/ThreatTrendChart'
import MalwareTrendChart from '../components/charts/MalwareTrendChart'
import { useStats } from '../hooks/useStats'
import { useThreats } from '../hooks/useThreats'
import { useThreatAggregates } from '../hooks/useThreatAggregates'
import { useMalwareTrends } from '../hooks/useMalwareTrends'

const DAY_OPTIONS = [
  { label: '7d',  value: 7  },
  { label: '14d', value: 14 },
  { label: '30d', value: 30 },
  { label: '90d', value: 90 },
]

function Analytics() {
  const [malwareDays, setMalwareDays] = useState(14)

  const { data: stats, loading: statsLoading, error: statsError, refetch: refetchStats } = useStats()
  const {
    data: sample,
    loading: sampleLoading,
    error: sampleError,
  } = useThreats({ page: 1, perPage: 100, sortBy: 'created_at', order: 'desc' })
  const { data: malwareTrends, loading: malwareLoading, error: malwareError } = useMalwareTrends(malwareDays, 6)

  const { sourceCounts, dailyTrend } = useThreatAggregates(sample?.items)

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Analytics</h1>
          <p className="page__subtitle">Aggregate patterns across every ingested indicator</p>
        </div>
        <button type="button" className="btn btn-outline-light btn-sm d-flex align-items-center gap-1" onClick={refetchStats}>
          <FiRefreshCw size={13} /> Refresh
        </button>
      </div>

      <div className="row g-3">
        {/* ── Malware Trends (full width, prominent) ── */}
        <div className="col-12">
          <ChartCard
            title="Malware Family Trends"
            subtitle={`Daily activity by top malware families — last ${malwareDays} days`}
            loading={malwareLoading}
            error={malwareError}
            isEmpty={!malwareLoading && !(malwareTrends?.families?.length)}
            headerRight={
              <div className="analytics-day-selector">
                {DAY_OPTIONS.map(({ label, value }) => (
                  <button
                    key={value}
                    className={`analytics-day-btn ${malwareDays === value ? 'analytics-day-btn--active' : ''}`}
                    onClick={() => setMalwareDays(value)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            }
          >
            <MalwareTrendChart
              data={malwareTrends?.series}
              families={malwareTrends?.families}
            />
          </ChartCard>
        </div>

        {/* ── Severity + Categories ── */}
        <div className="col-lg-6">
          <ChartCard
            title="Threat Severity"
            loading={statsLoading}
            error={statsError}
            isEmpty={!statsLoading && Object.keys(stats?.severity_distribution || {}).length === 0}
          >
            <SeverityPieChart data={stats?.severity_distribution} />
          </ChartCard>
        </div>
        <div className="col-lg-6">
          <ChartCard
            title="Top Categories"
            loading={statsLoading}
            error={statsError}
            isEmpty={!statsLoading && (stats?.top_categories || []).length === 0}
          >
            <CategoryBarChart data={stats?.top_categories} />
          </ChartCard>
        </div>

        {/* ── Countries + Sources ── */}
        <div className="col-lg-6">
          <ChartCard
            title="Country Distribution"
            loading={statsLoading}
            error={statsError}
            isEmpty={!statsLoading && (stats?.top_countries || []).length === 0}
          >
            <CountryDistributionChart data={stats?.top_countries} />
          </ChartCard>
        </div>
        <div className="col-lg-6">
          <ChartCard
            title="Top Sources"
            subtitle="Based on the 100 most recently ingested indicators"
            loading={sampleLoading}
            error={sampleError}
            isEmpty={!sampleLoading && sourceCounts.length === 0}
          >
            <TopSourcesChart data={sourceCounts} />
          </ChartCard>
        </div>

        {/* ── Ingestion trend ── */}
        <div className="col-12">
          <ChartCard
            title="Ingestion Trend"
            subtitle="Based on the 100 most recently ingested indicators"
            loading={sampleLoading}
            error={sampleError}
            isEmpty={!sampleLoading && dailyTrend.length === 0}
          >
            <ThreatTrendChart data={dailyTrend} />
          </ChartCard>
        </div>
      </div>
    </div>
  )
}

export default Analytics
