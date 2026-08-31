export const AIRCRAFT_TYPE_ORDER = ['helicopter', 'isr', 'tanker', 'trainer', 'transport', 'unknown']

export const AIRCRAFT_TYPE_COLORS = {
  helicopter: '#34d399',
  isr: '#60a5fa',
  tanker: '#f472b6',
  trainer: '#fbbf24',
  transport: '#22d3ee',
  unknown: '#64748b',
}

export function sortByAircraftType(rows) {
  return [...rows].sort(
    (a, b) => AIRCRAFT_TYPE_ORDER.indexOf(a.aircraft_type) - AIRCRAFT_TYPE_ORDER.indexOf(b.aircraft_type)
  )
}

export const REGION_COLORS = {
  CONUS: '#22d3ee',
  Europe: '#34d399',
  'Indo-Pacific': '#f472b6',
  'Middle East': '#fbbf24',
  other: '#64748b',
}

export function colorForRegion(region) {
  return REGION_COLORS[region] ?? '#8fa3b8'
}

export const CLIMB_RATE_ORDER = ['climbing', 'cruising', 'descending']

export const CLIMB_RATE_COLORS = {
  climbing: '#34d399',
  cruising: '#64748b',
  descending: '#fbbf24',
}

export function sortByClimbRate(rows) {
  return [...rows].sort(
    (a, b) => CLIMB_RATE_ORDER.indexOf(a.bucket) - CLIMB_RATE_ORDER.indexOf(b.bucket)
  )
}
