import { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getLatestPositions } from '../api'
import { AIRCRAFT_TYPE_COLORS } from '../constants'

const POLL_INTERVAL_MS = 60000

function AircraftMap() {
  const [positions, setPositions] = useState([])
  const [error, setError] = useState(null)
  const mapRef = useRef(null)

  useEffect(() => {
    const fetchPositions = () => {
      getLatestPositions()
        .then(setPositions)
        .catch((err) => setError(err.message))
    }

    fetchPositions()
    const id = setInterval(fetchPositions, POLL_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  // Leaflet can measure its container before the page's flex layout settles,
  // leaving the map undersized until a resize recalculation is forced.
  useEffect(() => {
    const id = setTimeout(() => mapRef.current?.invalidateSize(), 100)
    return () => clearTimeout(id)
  }, [])

  if (error) return <p>Error loading map: {error}</p>

  return (
    <MapContainer ref={mapRef} center={[20, 0]} zoom={2} style={{ height: '100%', width: '100%' }}>
      <TileLayer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        attribution="Tiles &copy; Esri"
      />
      {positions.map((p) => (
        <CircleMarker
          key={p.aircraft_id}
          center={[p.lat, p.lon]}
          radius={5}
          pathOptions={{
            color: AIRCRAFT_TYPE_COLORS[p.aircraft_type] ?? '#8fa3b8',
            fillColor: AIRCRAFT_TYPE_COLORS[p.aircraft_type] ?? '#8fa3b8',
            fillOpacity: 0.8,
          }}
        >
          <Tooltip>
            <strong>{p.aircraft_id}</strong> — {p.aircraft_type}
            <br />
            {p.operator ?? 'Unknown operator'}
          </Tooltip>
        </CircleMarker>
      ))}
    </MapContainer>
  )
}

export default AircraftMap
