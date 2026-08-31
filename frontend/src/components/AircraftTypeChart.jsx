import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getAircraftByType } from '../api'
import { sortByAircraftType, AIRCRAFT_TYPE_COLORS } from '../constants'

function AircraftTypeChart() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getAircraftByType()
      .then((rows) => setData(sortByAircraftType(rows)))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading chart: {error}</p>
  if (data.length === 0) return <p>Loading...</p>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="aircraft_type" outerRadius={100} label>
          {data.map((entry) => (
            <Cell key={entry.aircraft_type} fill={AIRCRAFT_TYPE_COLORS[entry.aircraft_type]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default AircraftTypeChart