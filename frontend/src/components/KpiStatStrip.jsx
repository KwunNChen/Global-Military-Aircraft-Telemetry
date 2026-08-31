import { useEffect, useState } from 'react'
import { getAircraftByType, getAltitudeByRegion, getLatestPositions } from '../api'

function KpiStatStrip() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    Promise.all([getAircraftByType(), getAltitudeByRegion(), getLatestPositions()])
      .then(([byType, byRegion, positions]) => {
        setStats({
          totalAircraft: byType.reduce((sum, row) => sum + row.count, 0),
          regionCount: byRegion.length,
          activeNow: positions.length,
        })
      })
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading stats: {error}</p>
  if (!stats) return <p>Loading...</p>

  return (
    <div className="kpi-strip">
      <div className="kpi-tile">
        <div className="kpi-value">{stats.totalAircraft}</div>
        <div className="kpi-label">Aircraft Tracked</div>
      </div>
      <div className="kpi-tile">
        <div className="kpi-value">{stats.regionCount}</div>
        <div className="kpi-label">Regions Active</div>
      </div>
      <div className="kpi-tile">
        <div className="kpi-value">{stats.activeNow}</div>
        <div className="kpi-label">Currently Airborne</div>
      </div>
    </div>
  )
}

export default KpiStatStrip
