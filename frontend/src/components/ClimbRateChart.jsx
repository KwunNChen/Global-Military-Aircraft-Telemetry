import { useEffect, useState } from 'react'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { getClimbRateBreakdown } from '../api'
import { sortByClimbRate, CLIMB_RATE_COLORS } from '../constants'

function ClimbRateChart() {
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    getClimbRateBreakdown()
      .then((rows) => setData(sortByClimbRate(rows)))
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <p>Error loading chart: {error}</p>
  if (data.length === 0) return <p>Loading...</p>

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={data} dataKey="count" nameKey="bucket" outerRadius={100} label>
          {data.map((entry) => (
            <Cell key={entry.bucket} fill={CLIMB_RATE_COLORS[entry.bucket]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default ClimbRateChart
