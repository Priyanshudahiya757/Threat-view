import { useState, useEffect, useCallback } from 'react'
import { getThreats } from '../services/threatService'

export function useThreats({ page = 1, perPage = 20, sortBy = 'created_at', order = 'desc', filters = {} } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const filtersKey = JSON.stringify(filters)

  const fetchThreats = useCallback(() => {
    setLoading(true)
    setError(null)

    return getThreats({ page, per_page: perPage, sort_by: sortBy, order, ...filters })
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
    // filters is captured via filtersKey since object identity changes every render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, perPage, sortBy, order, filtersKey])

  useEffect(() => {
    fetchThreats()
  }, [fetchThreats])

  return { data, loading, error, refetch: fetchThreats }
}
