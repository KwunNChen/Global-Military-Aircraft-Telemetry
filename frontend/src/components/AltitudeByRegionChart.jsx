import { useEffect, useState } from 'react'
import { BarChart, Bar, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { getAltitudeByRegion } from '../api'
import { colorForRegion } from '../constants'

function AltitudeByRegionChart() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getAltitudeByRegion()
      .then(setData)
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading chart: {error}</p>
  if (data.length === 0) return <p>Loading...</p>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} layout="vertical" margin={{ left: 20 }}>
        <CartesianGrid stroke="var(--border)" horizontal={false} />
        <XAxis type="number" stroke="var(--text-muted)" />
        <YAxis type="category" dataKey="region" stroke="var(--text-muted)" width={100} />
        <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)' }} />
        <Bar dataKey="avg_altitude">
          {data.map((entry) => (
            <Cell key={entry.region} fill={colorForRegion(entry.region)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default AltitudeByRegionChart