import { useState, useEffect, useCallback } from 'react'
import { listMonitors, createMonitor, deleteMonitor } from '../services/brandMonitorService'

export function useBrandMonitors() {
  const [monitors, setMonitors] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(() => {
    setLoading(true)
    setError(null)
    return listMonitors()
      .then(setMonitors)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const add = useCallback(
    (payload) =>
      createMonitor(payload).then((monitor) => {
        setMonitors((prev) => [monitor, ...prev])
        return monitor
      }),
    []
  )

  const remove = useCallback(
    (id) => deleteMonitor(id).then(() => setMonitors((prev) => prev.filter((m) => m.id !== id))),
    []
  )

  return { monitors, loading, error, refetch: fetch, add, remove }
}
