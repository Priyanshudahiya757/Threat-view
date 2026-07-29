import PropTypes from 'prop-types'
import { useNavigate } from 'react-router-dom'
import { FiEye, FiCopy } from 'react-icons/fi'
import { toast } from 'react-toastify'
import SeverityBadge from './SeverityBadge'
import IndicatorTypeBadge from './IndicatorTypeBadge'
import EmptyState from './EmptyState'
import { usePreferences } from '../context/PreferencesContext'

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString()
}

function ThreatTable({ threats, sortBy, order, onSort, onQuickView, compact = false }) {
  const navigate = useNavigate()
  const { toastsEnabled } = usePreferences()

  const handleCopy = async (indicator) => {
    try {
      await navigator.clipboard.writeText(indicator)
      if (toastsEnabled) toast.success('Indicator copied to clipboard')
    } catch {
      if (toastsEnabled) toast.error('Could not copy to clipboard')
    }
  }

  const renderHeader = (field, label) => {
    if (!onSort) return <th>{label}</th>
    const isActive = sortBy === field
    return (
      <th role="button" tabIndex={0} onClick={() => onSort(field)} className={isActive ? 'is-sorted' : ''}>
        {label} {isActive && (order === 'asc' ? '▲' : '▼')}
      </th>
    )
  }

  if (!threats || threats.length === 0) {
    return <EmptyState message="No threats match the current filters." />
  }

  return (
    <div className="table-responsive threat-table-wrapper">
      <table className="table table-dark table-hover align-middle threat-table">
        <thead>
          <tr>
            <th>Indicator</th>
            <th>Type</th>
            {renderHeader('severity', 'Severity')}
            <th>Category</th>
            <th>Country</th>
            <th>Source</th>
            {renderHeader('last_seen', 'Last Seen')}
            <th className="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          {threats.map((threat) => (
            <tr key={threat.id}>
              <td className="threat-table__indicator" title={threat.indicator}>
                {threat.indicator}
              </td>
              <td>
                <IndicatorTypeBadge type={threat.indicator_type} />
              </td>
              <td>
                <SeverityBadge severity={threat.severity} />
              </td>
              <td>{threat.category || '—'}</td>
              <td>{threat.country || '—'}</td>
              <td>{threat.source}</td>
              <td>{formatDate(threat.last_seen)}</td>
              <td className="text-end">
                <div className="d-flex gap-1 justify-content-end">
                  <button
                    type="button"
                    className="btn btn-sm btn-outline-light"
                    onClick={() => (onQuickView ? onQuickView(threat) : navigate(`/threats/${threat.id}`))}
                    aria-label={`View details for ${threat.indicator}`}
                  >
                    <FiEye size={14} />
                  </button>
                  {!compact && (
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-light"
                      onClick={() => handleCopy(threat.indicator)}
                      aria-label={`Copy ${threat.indicator}`}
                    >
                      <FiCopy size={14} />
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

ThreatTable.propTypes = {
  // eslint-disable-next-line react/forbid-prop-types
  threats: PropTypes.array,
  sortBy: PropTypes.string,
  order: PropTypes.oneOf(['asc', 'desc']),
  onSort: PropTypes.func,
  onQuickView: PropTypes.func,
  compact: PropTypes.bool,
}

export default ThreatTable
