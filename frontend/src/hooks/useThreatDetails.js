import { useState, useEffect, useCallback } from 'react'
import { getThreatById } from '../services/threatService'

export function useThreatDetails(id) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchThreat = useCallback(() => {
    if (!id) return undefined
    setLoading(true)
    setError(null)
    return getThreatById(id)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => {
    fetchThreat()
  }, [fetchThreat])

  return { data, loading, error, refetch: fetchThreat }
}
