import { useState, useEffect, useCallback } from 'react'
import { getHealth } from '../services/threatService'

const POLL_INTERVAL_MS = 30000

/**
 * Polls GET /api/health so the "API Online / Degraded / Offline" indicator
 * shown in the navbar and on the Settings page reflects the real backend,
 * not a decorative status dot.
 */
export function useApiHealth() {
  const [status, setStatus] = useState('checking') // 'ok' | 'degraded' | 'offline' | 'checking'

  const check = useCallback(() => {
    getHealth()
      .then((data) => setStatus(data.status === 'ok' ? 'ok' : 'degraded'))
      .catch(() => setStatus('offline'))
  }, [])

  useEffect(() => {
    check()
    const interval = setInterval(check, POLL_INTERVAL_MS)
    return () => clearInterval(interval)
  }, [check])

  return status
}
