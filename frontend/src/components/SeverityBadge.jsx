import PropTypes from 'prop-types'

const LABELS = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
}

function SeverityBadge({ severity }) {
  const key = (severity || '').toLowerCase()
  const label = LABELS[key] || severity || 'Unknown'
  const className = `severity-badge severity-badge--${key || 'medium'}`

  return <span className={className}>{label}</span>
}

SeverityBadge.propTypes = {
  severity: PropTypes.string,
}

export default SeverityBadge
