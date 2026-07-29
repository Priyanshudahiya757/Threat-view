import { useState, useCallback } from 'react'
import { searchThreats } from '../services/threatService'

export function useSearch() {
  const [data,       setData]       = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)
  const [hasSearched, setHasSearched] = useState(false)

  const search = useCallback((term, filters = {}) => {
    if (!term || !term.trim()) return undefined
    setLoading(true)
    setError(null)
    setHasSearched(true)
    return searchThreats(term.trim(), filters)
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error, hasSearched, search }
}
