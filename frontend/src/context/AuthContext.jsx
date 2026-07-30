import { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react'
import PropTypes from 'prop-types'
import { login as apiLogin, register as apiRegister, refreshToken as apiRefresh, getMe } from '../services/authService'

const AuthContext = createContext(null)

const STORAGE_KEY_ACCESS  = 'tv_access_token'
const STORAGE_KEY_REFRESH = 'tv_refresh_token'

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [token,   setToken]   = useState(() => localStorage.getItem(STORAGE_KEY_ACCESS) || null)
  const [loading, setLoading] = useState(true)   // initial auth check

  // ── Persist tokens ──────────────────────────────────────────────────────────
  const saveTokens = useCallback((access, refresh) => {
    localStorage.setItem(STORAGE_KEY_ACCESS, access)
    if (refresh) localStorage.setItem(STORAGE_KEY_REFRESH, refresh)
    setToken(access)
  }, [])

  const clearTokens = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY_ACCESS)
    localStorage.removeItem(STORAGE_KEY_REFRESH)
    setToken(null)
    setUser(null)
  }, [])

  // ── Bootstrap: verify stored token on mount ─────────────────────────────────
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY_ACCESS)
    if (!stored) { setLoading(false); return }

    const timer = setTimeout(() => setLoading(false), 3000)

    getMe()
      .then(setUser)
      .catch(() => {
        const refresh = localStorage.getItem(STORAGE_KEY_REFRESH)
        if (!refresh) { clearTokens(); return }
        return apiRefresh(refresh)
          .then(({ access_token }) => {
            saveTokens(access_token, null)
            return getMe().then(setUser)
          })
          .catch(clearTokens)
      })
      .finally(() => {
        clearTimeout(timer)
        setLoading(false)
      })
  }, [clearTokens, saveTokens])

  // ── Actions ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password)
    saveTokens(data.access_token, data.refresh_token)
    setUser(data.user)
    return data.user
  }, [saveTokens])

  const register = useCallback(async (payload) => {
    const data = await apiRegister(payload)
    saveTokens(data.access_token, data.refresh_token)
    setUser(data.user)
    return data.user
  }, [saveTokens])

  const logout = useCallback(() => {
    clearTokens()
  }, [clearTokens])

  const value = useMemo(
    () => ({ user, token, loading, login, register, logout, isAdmin: user?.role === 'admin' }),
    [user, token, loading, login, register, logout]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

AuthProvider.propTypes = { children: PropTypes.node.isRequired }

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
