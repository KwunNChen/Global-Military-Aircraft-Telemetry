import { useEffect, useState } from 'react'
import { getRecentActivity } from '../api'
import { AIRCRAFT_TYPE_COLORS } from '../constants'

const POLL_INTERVAL_MS = 30000

function ActivityTicker() {
  const [rows, setRows] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchActivity = () => {
      getRecentActivity()
        .then(setRows)
        .catch((err) => setError(err.message))
    }

    fetchActivity()
    const id = setInterval(fetchActivity, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  if (error) return <p>Error loading activity: {error}</p>
  if (rows.length === 0) return <p>Loading...</p>

  return (
    <div className="ticker-wrap">
      <table className="activity-ticker">
        <thead>
          <tr>
            <th>Aircraft</th>
            <th>Type</th>
            <th>Region</th>
            <th>Altitude</th>
            <th>Speed</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={`${r.aircraft_id}-${r.timestamp}`}>
              <td>{r.aircraft_id}</td>
              <td>
                <span
                  className="type-dot"
                  style={{ background: AIRCRAFT_TYPE_COLORS[r.aircraft_type] ?? '#8fa3b8' }}
                />
                {r.aircraft_type}
              </td>
              <td>{r.region}</td>
              <td>{r.altitude?.toFixed(0) ?? '—'}</td>
              <td>{r.speed?.toFixed(0) ?? '—'}</td>
              <td>{new Date(r.timestamp).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ActivityTicker
