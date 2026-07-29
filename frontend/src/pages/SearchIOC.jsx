import { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { FiSearch } from 'react-icons/fi'
import SearchBar from '../components/SearchBar'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorState from '../components/ErrorState'
import EmptyState from '../components/EmptyState'
import SeverityBadge from '../components/SeverityBadge'
import IndicatorTypeBadge from '../components/IndicatorTypeBadge'
import { useSearch } from '../hooks/useSearch'

const REPUTATIONS = [
  { value: '',           label: 'All'         },
  { value: 'malicious',  label: '🔴 Malicious'  },
  { value: 'suspicious', label: '🟡 Suspicious' },
  { value: 'unknown',    label: '⚪ Unknown'    },
  { value: 'clean',      label: '🟢 Clean'      },
]

const IOC_TYPES = [
  { value: '',       label: 'All Types' },
  { value: 'IP',     label: 'IP'        },
  { value: 'Domain', label: 'Domain'    },
  { value: 'URL',    label: 'URL'       },
  { value: 'Hash',   label: 'Hash'      },
  { value: 'Email',  label: 'Email'     },
]

const REP_STYLE = {
  malicious:  { bg: 'var(--tv-accent-red-soft)',    color: '#fb7185' },
  suspicious: { bg: 'rgba(245,166,35,0.12)',         color: '#fbbf24' },
  unknown:    { bg: 'var(--tv-bg-base)',             color: 'var(--tv-text-muted)' },
  clean:      { bg: 'rgba(52,211,153,0.1)',          color: '#34d399' },
}

function ReputationBadge({ rep }) {
  if (!rep) return null
  const style = REP_STYLE[rep] || REP_STYLE.unknown
  return (
    <span
      style={{
        background: style.bg,
        color: style.color,
        fontSize: '0.7rem',
        fontWeight: 700,
        padding: '2px 8px',
        borderRadius: 999,
        letterSpacing: '0.03em',
        textTransform: 'capitalize',
        flexShrink: 0,
      }}
    >
      {rep}
    </span>
  )
}
ReputationBadge.propTypes = { rep: PropTypes.string }

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

function MetaItem({ label, value }) {
  return (
    <div className="ioc-result__meta-item">
      <span className="ioc-result__meta-label">{label}</span>
      <span className="ioc-result__meta-value">{value}</span>
    </div>
  )
}
MetaItem.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
}

function SearchIOC() {
  const { data, loading, error, hasSearched, search } = useSearch()
  const [reputation,  setReputation]  = useState('')
  const [iocType,     setIocType]     = useState('')
  const lastTermRef = useRef('')

  const runSearch = (term, rep, type) => {
    const filters = {}
    if (rep)  filters.reputation     = rep
    if (type) filters.indicator_type = type
    search(term, filters)
  }

  const handleSearch = (term) => {
    lastTermRef.current = term
    runSearch(term, reputation, iocType)
  }

  const handleRepChange = (val) => {
    setReputation(val)
    if (hasSearched && lastTermRef.current) runSearch(lastTermRef.current, val, iocType)
  }

  const handleTypeChange = (val) => {
    setIocType(val)
    if (hasSearched && lastTermRef.current) runSearch(lastTermRef.current, reputation, val)
  }

  return (
    <div className="page">
      <div className="page__header">
        <div>
          <h1 className="page__title">Search IOC</h1>
          <p className="page__subtitle">Look up an IP, domain, URL, or file hash across every ingested feed</p>
        </div>
      </div>

      {/* Search bar */}
      <div className="panel mb-3">
        <SearchBar onSearch={handleSearch} placeholder="e.g. 45.61.49.78, evil-domain.test, or a SHA-256 hash" />
      </div>

      {/* Filters */}
      <div className="ioc-filters mb-3">
        {/* Reputation pills */}
        <div className="ioc-filter-group">
          <span className="ioc-filter-label">Reputation</span>
          <div className="ioc-filter-pills">
            {REPUTATIONS.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                className={`ioc-filter-pill ${reputation === value ? 'ioc-filter-pill--active' : ''}`}
                onClick={() => handleRepChange(value)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Type pills */}
        <div className="ioc-filter-group">
          <span className="ioc-filter-label">Type</span>
          <div className="ioc-filter-pills">
            {IOC_TYPES.map(({ value, label }) => (
              <button
                key={value}
                type="button"
                className={`ioc-filter-pill ${iocType === value ? 'ioc-filter-pill--active' : ''}`}
                onClick={() => handleTypeChange(value)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && <LoadingSpinner label="Searching..." />}
      {!loading && error && <ErrorState message={error.message} />}

      {!loading && !error && hasSearched && (
        <div className="panel">
          <p className="text-secondary small mb-3 d-flex align-items-center gap-2">
            <FiSearch size={13} />
            <strong>{data?.total_items ?? 0}</strong> result{data?.total_items === 1 ? '' : 's'}
            {' '}for &ldquo;{data?.query}&rdquo;
            {reputation && <span className="ioc-active-filter">rep: {reputation}</span>}
            {iocType    && <span className="ioc-active-filter">type: {iocType}</span>}
          </p>

          {(!data || data.items.length === 0) && (
            <EmptyState message="No matching indicators found in the threat database." />
          )}

          <div className="row g-3">
            {(data?.items || []).map((threat) => (
              <div key={threat.id} className="col-12">
                <div className="ioc-result">
                  <div className="ioc-result__main">
                    <div className="d-flex gap-2 align-items-center mb-2 flex-wrap">
                      <SeverityBadge severity={threat.severity} />
                      <IndicatorTypeBadge type={threat.indicator_type} />
                      <ReputationBadge rep={threat.reputation} />
                    </div>
                    <p className="ioc-result__indicator">{threat.indicator}</p>
                    {threat.description && <p className="ioc-result__description">{threat.description}</p>}
                  </div>
                  <div className="ioc-result__meta">
                    <MetaItem label="Threat Score" value={threat.confidence != null ? `${threat.confidence}/100` : '—'} />
                    <MetaItem label="Country"      value={threat.country   || '—'} />
                    <MetaItem label="Category"     value={threat.category  || '—'} />
                    <MetaItem label="Source"       value={threat.source} />
                    <MetaItem label="First Seen"   value={formatDate(threat.first_seen)} />
                    <MetaItem label="Last Seen"    value={formatDate(threat.last_seen)} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!hasSearched && !loading && (
        <EmptyState message="Enter an indicator above to check it against the aggregated threat database." />
      )}
    </div>
  )
}

export default SearchIOC
