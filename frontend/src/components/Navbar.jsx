import { FiMenu, FiShield, FiLogOut, FiUser } from 'react-icons/fi'
import { useNavigate } from 'react-router-dom'
import { useSidebar } from '../context/SidebarContext'
import { useAuth } from '../context/AuthContext'
import { useApiHealth } from '../hooks/useApiHealth'

const STATUS_LABEL = {
  ok:       'API Online',
  degraded: 'API Degraded',
  offline:  'API Offline',
  checking: 'Checking...',
}

function Navbar() {
  const { toggle }   = useSidebar()
  const { user, logout } = useAuth()
  const apiStatus    = useApiHealth()
  const navigate     = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="tv-navbar">
      <button type="button" className="tv-navbar__menu-btn" onClick={toggle} aria-label="Toggle sidebar">
        <FiMenu size={20} />
      </button>

      <div className="tv-navbar__brand d-lg-none">
        <FiShield size={18} className="me-2" />
        ThreatView
      </div>

      <div className="tv-navbar__right">
        <span className={`tv-navbar__status tv-navbar__status--${apiStatus}`}>
          <span className="status-dot" />
          {STATUS_LABEL[apiStatus]}
        </span>

        {user && (
          <div className="tv-navbar__user">
            <div className="tv-navbar__user-avatar" title={user.email}>
              <FiUser size={14} />
            </div>
            <div className="tv-navbar__user-info">
              <span className="tv-navbar__user-email">{user.email}</span>
              <span className="tv-navbar__user-role">{user.role}</span>
            </div>
            <button
              type="button"
              className="tv-navbar__icon-btn"
              onClick={handleLogout}
              title="Sign out"
              aria-label="Sign out"
            >
              <FiLogOut size={16} />
            </button>
          </div>
        )}
      </div>
    </header>
  )
}

export default Navbar

