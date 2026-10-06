import { useEffect, useState } from 'react'
import { getRecentActivity } from '../api'

const POLL_INTERVAL_MS = 60000
// Pipeline runs hourly, so one missed run is normal; two means something is wrong.
const STALE_AFTER_MINUTES = 120

// The API sends UTC timestamps without a timezone marker, so add one if missing.
function parseUtc(timestamp) {
  const hasZone = /(Z|[+-]\d\d:?\d\d)$/.test(timestamp)
  return new Date(hasZone ? timestamp : `${timestamp}Z`)
}

function formatAge(minutes) {
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes} min ago`
  if (minutes < 1440) return `${Math.floor(minutes / 60)} h ${minutes % 60} min ago`
  const days = Math.floor(minutes / 1440)
  return `${days} day${days === 1 ? '' : 's'} ago`
}

function LastUpdated() {
  const [latest, setLatest] = useState(null)
  const [now, setNow] = useState(() => Date.now())
  const [error, setError] = useState(null)

  useEffect(() => {
    const refresh = () => {
      getRecentActivity()
        .then((rows) => {
          setLatest(rows[0]?.timestamp ?? null)
          setNow(Date.now())
          setError(null)
        })
        .catch((err) => setError(err.message))
    }

    refresh()
    const id = setInterval(refresh, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  if (error) return <p className="last-updated stale">Last updated: unavailable</p>
  if (!latest) return <p className="last-updated">Checking data freshness...</p>

  const date = parseUtc(latest)
  const minutes = Math.max(0, Math.floor((now - date.getTime()) / 60000))
  const stale = minutes > STALE_AFTER_MINUTES

  return (
    <p className={`last-updated${stale ? ' stale' : ''}`} title={date.toLocaleString()}>
      Data updated {formatAge(minutes)} · refreshes hourly
    </p>
  )
}

export default LastUpdated
