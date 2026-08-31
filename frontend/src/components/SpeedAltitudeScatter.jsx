import { useEffect, useState } from 'react'
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getSpeedAltitudeSample } from '../api'
import { AIRCRAFT_TYPE_ORDER, AIRCRAFT_TYPE_COLORS } from '../constants'

function SpeedAltitudeScatter() {
  const [byType, setByType] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSpeedAltitudeSample()
      .then((rows) => {
        const grouped = {}
        for (const row of rows) {
          if (!grouped[row.aircraft_type]) grouped[row.aircraft_type] = []
          grouped[row.aircraft_type].push({ speed: row.speed, altitude: row.altitude })
        }
        setByType(grouped)
      })
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading chart: {error}</p>
  if (!byType) return <p>Loading...</p>

  return (
    <ResponsiveContainer width="100%" height={280}>
      <ScatterChart margin={{ left: 10, right: 20, bottom: 10 }}>
        <CartesianGrid stroke="var(--border)" />
        <XAxis type="number" dataKey="speed" name="Speed" unit=" kt" stroke="var(--text-muted)" />
        <YAxis type="number" dataKey="altitude" name="Altitude" unit=" ft" stroke="var(--text-muted)" />
        <ZAxis range={[40, 40]} />
        <Tooltip
          cursor={{ strokeDasharray: '3 3', stroke: 'var(--border)' }}
          contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)' }}
        />
        <Legend />
        {AIRCRAFT_TYPE_ORDER.filter((type) => byType[type]?.length).map((type) => (
          <Scatter key={type} name={type} data={byType[type]} fill={AIRCRAFT_TYPE_COLORS[type]} opacity={0.7} />
        ))}
      </ScatterChart>
    </ResponsiveContainer>
  )
}

export default SpeedAltitudeScatter
