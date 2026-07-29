import { useState } from 'react'
import { Link } from 'react-router-dom'
import ThreatTable from '../components/ThreatTable'
import Pagination from '../components/Pagination'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import Modal from '../components/Modal'
import SeverityBadge from '../components/SeverityBadge'
import { useThreats } from '../hooks/useThreats'
import { usePreferences } from '../context/PreferencesContext'

const SEVERITIES = ['low', 'medium', 'high', 'critical']
const INDICATOR_TYPES = ['IP', 'Domain', 'URL', 'Hash']
const SOURCES = ['AlienVault OTX', 'PhishTank', 'URLhaus']

function ThreatFeed() {
  const { pageSize } = usePreferences()
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('created_at')
  const [order, setOrder] = useState('desc')
  const [filters, setFilters] = useState({ severity: '', indicator_type: '', source: '' })
  const [quickView, setQuickView] = useState(null)

  const activeFilters = Object.fromEntries(Object.entries(filters).filter(([, value]) => value))

  const { data, loading, error, refetch } = useThreats({
    page,
    perPage: pageSize,
    sortBy,
    order,
    filters: activeFilters,
  })

  const handleSort = (field) => {
    if (sortBy === field) {
      setOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(field)
      setOrder('desc')
    }
    setPage(1)
  }

  const handleFilterChange = (field, value) => {
    setFilters((prev) => ({ ...prev, [field]: value }))
    setPage(1)
  }

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Threat Feed</h1>
          <p className="page__subtitle">
            {loading ? 'Loading...' : `${data?.total_items ?? 0} indicators across all sources`}
          </p>
        </div>
      </div>

      <div className="panel mb-3">
        <div className="row g-2 align-items-end">
          <div className="col-6 col-md-3">
            <label className="form-label small text-secondary" htmlFor="severity-filter">
              Severity
            </label>
            <select
              id="severity-filter"
              className="form-select form-select-sm bg-dark text-light border-secondary"
              value={filters.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
            >
              <option value="">All</option>
              {SEVERITIES.map((s) => (
                <option key={s} value={s}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </option>
              ))}
            </select>
          </div>
          <div className="col-6 col-md-3">
            <label className="form-label small text-secondary" htmlFor="type-filter">
              Indicator Type
            </label>
            <select
              id="type-filter"
              className="form-select form-select-sm bg-dark text-light border-secondary"
              value={filters.indicator_type}
              onChange={(e) => handleFilterChange('indicator_type', e.target.value)}
            >
              <option value="">All</option>
              {INDICATOR_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
          <div className="col-6 col-md-3">
            <label className="form-label small text-secondary" htmlFor="source-filter">
              Source
            </label>
            <select
              id="source-filter"
              className="form-select form-select-sm bg-dark text-light border-secondary"
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
            >
              <option value="">All</option>
              {SOURCES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="col-6 col-md-3">
            <button type="button" className="btn btn-sm btn-outline-light w-100" onClick={refetch}>
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="panel">
        {loading && <LoadingSpinner label="Loading threats..." />}
        {!loading && error && <ErrorState message={error.message} onRetry={refetch} />}
        {!loading && !error && (
          <>
            <ThreatTable
              threats={data?.items}
              sortBy={sortBy}
              order={order}
              onSort={handleSort}
              onQuickView={setQuickView}
            />
            <div className="mt-3">
              <Pagination page={data?.page || 1} totalPages={data?.total_pages || 1} onPageChange={setPage} />
            </div>
          </>
        )}
      </div>

      <Modal title="Threat Snapshot" isOpen={Boolean(quickView)} onClose={() => setQuickView(null)}>
        {quickView && (
          <div className="threat-snapshot">
            <p className="threat-snapshot__indicator">{quickView.indicator}</p>
            <div className="d-flex gap-2 mb-3">
              <SeverityBadge severity={quickView.severity} />
              <span className="badge bg-secondary">{quickView.indicator_type}</span>
            </div>
            <dl className="threat-snapshot__meta">
              <dt>Category</dt>
              <dd>{quickView.category || '—'}</dd>
              <dt>Source</dt>
              <dd>{quickView.source}</dd>
              <dt>Country</dt>
              <dd>{quickView.country || '—'}</dd>
              <dt>Confidence</dt>
              <dd>{quickView.confidence != null ? `${quickView.confidence}/100` : '—'}</dd>
            </dl>
            <Link to={`/threats/${quickView.id}`} className="btn btn-sm btn-primary">
              View full details
            </Link>
          </div>
        )}
      </Modal>
    </div>
  )
}

export default ThreatFeed
