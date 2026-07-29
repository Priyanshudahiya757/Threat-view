import PropTypes from 'prop-types'
import { FiAlertTriangle } from 'react-icons/fi'

function ErrorState({ message = 'Something went wrong.', onRetry }) {
  return (
    <div className="error-state">
      <FiAlertTriangle size={26} />
      <p className="error-state__message">{message}</p>
      {onRetry && (
        <button type="button" className="btn btn-outline-light btn-sm" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}

ErrorState.propTypes = {
  message: PropTypes.string,
  onRetry: PropTypes.func,
}

export default ErrorState
