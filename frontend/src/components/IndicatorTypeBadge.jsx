import PropTypes from 'prop-types'
import { FiGlobe, FiLink, FiHash, FiServer } from 'react-icons/fi'

const TYPE_ICONS = {
  IP: FiServer,
  Domain: FiGlobe,
  URL: FiLink,
  Hash: FiHash,
}

function IndicatorTypeBadge({ type }) {
  const Icon = TYPE_ICONS[type] || FiGlobe
  return (
    <span className="indicator-type-badge">
      <Icon size={12} className="me-1" />
      {type}
    </span>
  )
}

IndicatorTypeBadge.propTypes = {
  type: PropTypes.string,
}

export default IndicatorTypeBadge
