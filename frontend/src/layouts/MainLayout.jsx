import PropTypes from 'prop-types'
import Sidebar from '../components/Sidebar'
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'
import { useSidebar } from '../context/SidebarContext'

function MainLayout({ children }) {
  const { collapsed } = useSidebar()

  return (
    <div className="app-shell">
      <Sidebar />
      <div className={`app-content ${collapsed ? 'app-content--collapsed' : ''}`}>
        <Navbar />
        <main className="app-main">{children}</main>
        <Footer />
      </div>
    </div>
  )
}

MainLayout.propTypes = {
  children: PropTypes.node.isRequired,
}

export default MainLayout
