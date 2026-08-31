import { useEffect, useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts'
import { getSpeedByAircraftType } from '../api'
import { sortByAircraftType } from '../constants'

function SpeedByTypeChart() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getSpeedByAircraftType()
      .then((rows) => setData(sortByAircraftType(rows.filter((r) => r.avg_speed !== null))))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading chart: {error}</p>
  if (data.length === 0) return <p>Loading...</p>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data}>
        <CartesianGrid stroke="var(--border)" />
        <XAxis dataKey="aircraft_type" stroke="var(--text-muted)" />
        <YAxis stroke="var(--text-muted)" />
        <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)' }} />
        <Legend />
        <Bar dataKey="min_speed" fill="var(--accent)" />
        <Bar dataKey="avg_speed" fill="var(--accent-2)" />
        <Bar dataKey="max_speed" fill="#fbbf24" />
      </BarChart>
    </ResponsiveContainer>
  )
}

export default SpeedByTypeChart