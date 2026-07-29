import axios from 'axios'

const STORAGE_KEY_ACCESS  = 'tv_access_token'
const STORAGE_KEY_REFRESH = 'tv_refresh_token'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// ── Request: inject Bearer token ─────────────────────────────────────────────
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(STORAGE_KEY_ACCESS)
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ── Response: normalize errors + silent token refresh on 401 ─────────────────
let _refreshing = false
let _queue = []

const processQueue = (error, token = null) => {
  _queue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve(token)))
  _queue = []
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    // 401 on a non-auth endpoint → try silent refresh once
    if (
      error.response?.status === 401 &&
      !original._retry &&
      !original.url?.includes('/auth/')
    ) {
      if (_refreshing) {
        return new Promise((resolve, reject) => _queue.push({ resolve, reject }))
          .then((token) => {
            original.headers.Authorization = `Bearer ${token}`
            return apiClient(original)
          })
      }

      original._retry = true
      _refreshing = true

      const refresh = localStorage.getItem(STORAGE_KEY_REFRESH)
      if (refresh) {
        try {
          const { data } = await axios.post(
            `${apiClient.defaults.baseURL}/auth/refresh`,
            {},
            { headers: { Authorization: `Bearer ${refresh}` } }
          )
          localStorage.setItem(STORAGE_KEY_ACCESS, data.access_token)
          apiClient.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
          processQueue(null, data.access_token)
          original.headers.Authorization = `Bearer ${data.access_token}`
          return apiClient(original)
        } catch (refreshError) {
          processQueue(refreshError)
          localStorage.removeItem(STORAGE_KEY_ACCESS)
          localStorage.removeItem(STORAGE_KEY_REFRESH)
          window.location.href = '/login'
          return Promise.reject(refreshError)
        } finally {
          _refreshing = false
        }
      } else {
        _refreshing = false
        window.location.href = '/login'
      }
    }

    // Normalize errors into plain Error objects
    if (error.response) {
      const message = error.response.data?.error || `Request failed with status ${error.response.status}`
      return Promise.reject(new Error(message))
    }
    if (error.request) {
      return Promise.reject(
        new Error('Could not reach the ThreatView backend. Check that it is running and VITE_API_URL is correct.')
      )
    }
    return Promise.reject(new Error(error.message || 'Something went wrong.'))
  }
)

export default apiClient

