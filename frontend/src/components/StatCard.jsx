import PropTypes from 'prop-types'

function StatCard({ label, value, icon: Icon, accent = 'blue' }) {
  return (
    <div className={`stat-card stat-card--${accent}`}>
      <div className="stat-card__icon">
        <Icon size={20} />
      </div>
      <div className="stat-card__body">
        <p className="stat-card__label">{label}</p>
        <h3 className="stat-card__value">{value}</h3>
      </div>
    </div>
  )
}

StatCard.propTypes = {
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  icon: PropTypes.elementType.isRequired,
  accent: PropTypes.oneOf(['blue', 'purple', 'red', 'amber', 'green']),
}

export default StatCard
