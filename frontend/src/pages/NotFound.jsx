import { Link } from 'react-router-dom'
import { FiShieldOff } from 'react-icons/fi'

function NotFound() {
  return (
    <div className="not-found">
      <FiShieldOff size={44} />
      <h1>404</h1>
      <p>This page doesn&apos;t exist in the threat database either.</p>
      <Link to="/dashboard" className="btn btn-primary">
        Back to Dashboard
      </Link>
    </div>
  )
}

export default NotFound
