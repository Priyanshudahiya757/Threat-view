import { NavLink } from 'react-router-dom'
import { FiGrid, FiList, FiSearch, FiBarChart2, FiCpu, FiSettings, FiBell, FiGlobe } from 'react-icons/fi'
import { useSidebar } from '../context/SidebarContext'
import { useUnreadCount } from '../hooks/useAlerts'
import logo from '../assets/logo.svg'

const NAV_ITEMS = [
  { to: '/dashboard',      label: 'Dashboard',      icon: FiGrid },
  { to: '/threats',        label: 'Threat Feed',     icon: FiList },
  { to: '/search',         label: 'Search IOC',      icon: FiSearch },
  { to: '/analytics',      label: 'Analytics',       icon: FiBarChart2 },
  { to: '/ai-detection',   label: 'AI Detection',    icon: FiCpu },
  { to: '/alerts',         label: 'Alerts',          icon: FiBell,  badge: true },
  { to: '/brand-monitor',  label: 'Brand Monitor',   icon: FiGlobe },
  { to: '/settings',       label: 'Settings',        icon: FiSettings },
]

function Sidebar() {
  const { collapsed }  = useSidebar()
  const unreadCount    = useUnreadCount(30000)

  return (
    <aside className={`tv-sidebar ${collapsed ? 'tv-sidebar--collapsed' : ''}`}>
      <div className="tv-sidebar__brand">
        <img src={logo} width={26} height={26} alt="" className="tv-sidebar__brand-icon" />
        {!collapsed && <span className="tv-sidebar__brand-text">ThreatView</span>}
      </div>

      <nav className="tv-sidebar__nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, badge }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) => `tv-sidebar__link ${isActive ? 'tv-sidebar__link--active' : ''}`}
          >
            <Icon size={18} className="tv-sidebar__link-icon" />
            {!collapsed && <span>{label}</span>}
            {badge && unreadCount > 0 && (
              <span className="tv-sidebar__badge">{unreadCount > 99 ? '99+' : unreadCount}</span>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}

export default Sidebar
