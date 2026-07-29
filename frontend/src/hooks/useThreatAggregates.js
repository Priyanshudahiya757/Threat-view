import { useMemo } from 'react'

/**
 * Derives "top sources" and "threats per day" from a raw list of threat
 * rows. The backend's /api/stats endpoint exposes severity/country/category
 * breakdowns directly but not these two, so we compute them client-side
 * from whatever batch of recent threats the caller already fetched.
 *
 * This is a sample-based approximation, not a full-dataset aggregation --
 * callers should label charts built from it accordingly (see Analytics.jsx).
 */
export function useThreatAggregates(threats) {
  return useMemo(() => {
    const list = threats || []

    const sourceTally = new Map()
    const dayTally = new Map()

    list.forEach((threat) => {
      sourceTally.set(threat.source, (sourceTally.get(threat.source) || 0) + 1)

      const day = (threat.created_at || '').slice(0, 10) // YYYY-MM-DD
      if (day) dayTally.set(day, (dayTally.get(day) || 0) + 1)
    })

    const sourceCounts = Array.from(sourceTally, ([name, count]) => ({ name, count })).sort(
      (a, b) => b.count - a.count
    )

    const dailyTrend = Array.from(dayTally, ([date, count]) => ({ date, count })).sort((a, b) =>
      a.date.localeCompare(b.date)
    )

    return { sourceCounts, dailyTrend }
  }, [threats])
}
