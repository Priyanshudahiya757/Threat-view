import PropTypes from 'prop-types'

function LoadingSpinner({ label = 'Loading...' }) {
  return (
    <div className="loading-state" role="status">
      <div className="spinner-border" aria-hidden="true" />
      <span className="loading-state__label">{label}</span>
    </div>
  )
}

LoadingSpinner.propTypes = {
  label: PropTypes.string,
}

export default LoadingSpinner
