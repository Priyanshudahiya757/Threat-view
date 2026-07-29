import { useState, useEffect, useCallback } from 'react'
import {
  listRules,
  createRule,
  updateRule,
  deleteRule,
  listEvents,
  markEventRead,
  markAllRead,
  getUnreadCount,
} from '../services/alertService'

// ── Rules ─────────────────────────────────────────────────────────────────────

export function useAlertRules() {
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(() => {
    setLoading(true)
    setError(null)
    return listRules()
      .then(setRules)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const add = useCallback(
    (payload) => createRule(payload).then((rule) => { setRules((prev) => [rule, ...prev]); return rule }),
    []
  )

  const edit = useCallback(
    (id, payload) =>
      updateRule(id, payload).then((updated) => {
        setRules((prev) => prev.map((r) => (r.id === id ? updated : r)))
        return updated
      }),
    []
  )

  const remove = useCallback(
    (id) => deleteRule(id).then(() => setRules((prev) => prev.filter((r) => r.id !== id))),
    []
  )

  return { rules, loading, error, refetch: fetch, add, edit, remove }
}

// ── Events ────────────────────────────────────────────────────────────────────

export function useAlertEvents({ page = 1, perPage = 20, unreadOnly = false } = {}) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(() => {
    setLoading(true)
    setError(null)
    return listEvents({ page, perPage, unreadOnly })
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false))
  }, [page, perPage, unreadOnly])

  useEffect(() => { fetch() }, [fetch])

  const markRead = useCallback(
    (id) =>
      markEventRead(id).then(() => {
        setData((prev) =>
          prev
            ? {
                ...prev,
                items: prev.items.map((e) => (e.id === id ? { ...e, is_read: true } : e)),
              }
            : prev
        )
      }),
    []
  )

  const markAll = useCallback(
    () => markAllRead().then(fetch),
    [fetch]
  )

  return { data, loading, error, refetch: fetch, markRead, markAll }
}

// ── Unread count ──────────────────────────────────────────────────────────────

export function useUnreadCount(pollIntervalMs = 30000) {
  const [count, setCount] = useState(0)

  const fetch = useCallback(() => {
    getUnreadCount().then(setCount).catch(() => {})
  }, [])

  useEffect(() => {
    fetch()
    const timer = setInterval(fetch, pollIntervalMs)
    return () => clearInterval(timer)
  }, [fetch, pollIntervalMs])

  return count
}
