import { createContext, useContext, useState, useEffect } from 'react'
import PropTypes from 'prop-types'

const SidebarContext = createContext(undefined)
const STORAGE_KEY = 'threatview:sidebar-collapsed'

export function SidebarProvider({ children }) {
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) === 'true'
    } catch {
      return false
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, String(collapsed))
    } catch {
      // localStorage may be unavailable (private browsing, etc.) -- not fatal
    }
  }, [collapsed])

  const toggle = () => setCollapsed((prev) => !prev)

  return <SidebarContext.Provider value={{ collapsed, toggle }}>{children}</SidebarContext.Provider>
}

SidebarProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export function useSidebar() {
  const context = useContext(SidebarContext)
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider')
  }
  return context
}
