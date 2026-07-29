import { createContext, useContext, useState, useEffect } from 'react'
import PropTypes from 'prop-types'

const PreferencesContext = createContext(undefined)

const KEYS = {
  pageSize: 'threatview:default-page-size',
  toastsEnabled: 'threatview:toasts-enabled',
}

function readNumber(key, fallback) {
  try {
    const stored = localStorage.getItem(key)
    return stored ? Number(stored) : fallback
  } catch {
    return fallback
  }
}

function readBoolean(key, fallback) {
  try {
    const stored = localStorage.getItem(key)
    return stored === null ? fallback : stored === 'true'
  } catch {
    return fallback
  }
}

export function PreferencesProvider({ children }) {
  const [pageSize, setPageSize] = useState(() => readNumber(KEYS.pageSize, 20))
  const [toastsEnabled, setToastsEnabled] = useState(() => readBoolean(KEYS.toastsEnabled, true))

  useEffect(() => {
    try {
      localStorage.setItem(KEYS.pageSize, String(pageSize))
    } catch {
      // ignore -- localStorage may be unavailable
    }
  }, [pageSize])

  useEffect(() => {
    try {
      localStorage.setItem(KEYS.toastsEnabled, String(toastsEnabled))
    } catch {
      // ignore -- localStorage may be unavailable
    }
  }, [toastsEnabled])

  return (
    <PreferencesContext.Provider value={{ pageSize, setPageSize, toastsEnabled, setToastsEnabled }}>
      {children}
    </PreferencesContext.Provider>
  )
}

PreferencesProvider.propTypes = {
  children: PropTypes.node.isRequired,
}

export function usePreferences() {
  const context = useContext(PreferencesContext)
  if (context === undefined) {
    throw new Error('usePreferences must be used within a PreferencesProvider')
  }
  return context
}
