import { useState, useEffect, useCallback } from 'react'
import { getRecentThreats } from '../services/threatService'

export function useRecentThreats(limit = 10) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRecent = useCallback(() => {
    setLoading(true)
    setError(null)
    return getRecentThreats(limit)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [limit])

  useEffect(() => {
    fetchRecent()
  }, [fetchRecent])

  return { data, loading, error, refetch: fetchRecent }
}
