const BASE_URL = import.meta.env.VITE_API_BASE_URL

export async function getAircraftByType() {
  const res = await fetch(`${BASE_URL}/aircraft-by-type`)
  if (!res.ok) throw new Error(`Failed to fetch aircraft-by-type: ${res.status}`)
  return res.json()
}

export async function getAltitudeByRegion() {
  const res = await fetch(`${BASE_URL}/altitude-by-region`)
  if (!res.ok) throw new Error(`Failed to fetch altitude-by-region: ${res.status}`)
  return res.json()
}

export async function getSpeedByAircraftType() {
  const res = await fetch(`${BASE_URL}/speed-by-aircraft-type`)
  if (!res.ok) throw new Error(`Failed to fetch speed-by-aircraft-type: ${res.status}`)
  return res.json()
}

export async function getLatestPositions() {
  const res = await fetch(`${BASE_URL}/latest-positions`)
  if (!res.ok) throw new Error(`Failed to fetch latest-positions: ${res.status}`)
  return res.json()
}

export async function getClimbRateBreakdown() {
  const res = await fetch(`${BASE_URL}/climb-rate-breakdown`)
  if (!res.ok) throw new Error(`Failed to fetch climb-rate-breakdown: ${res.status}`)
  return res.json()
}

export async function getRecentActivity() {
  const res = await fetch(`${BASE_URL}/recent-activity`)
  if (!res.ok) throw new Error(`Failed to fetch recent-activity: ${res.status}`)
  return res.json()
}

export async function getSpeedAltitudeSample() {
  const res = await fetch(`${BASE_URL}/speed-altitude-sample`)
  if (!res.ok) throw new Error(`Failed to fetch speed-altitude-sample: ${res.status}`)
  return res.json()
}