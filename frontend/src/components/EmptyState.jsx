import PropTypes from 'prop-types'
import { FiInbox } from 'react-icons/fi'

function EmptyState({ message = 'Nothing to show yet.' }) {
  return (
    <div className="empty-state">
      <FiInbox size={26} />
      <p className="mb-0">{message}</p>
    </div>
  )
}

EmptyState.propTypes = {
  message: PropTypes.string,
}

export default EmptyState
