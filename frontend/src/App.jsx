import AircraftTypeChart from './components/AircraftTypeChart'
import AltitudeByRegionChart from './components/AltitudeByRegionChart'
import SpeedByTypeChart from './components/SpeedByTypeChart'
import AircraftMap from './components/AircraftMap'
import KpiStatStrip from './components/KpiStatStrip'
import ActivityTicker from './components/ActivityTicker'
import SpeedAltitudeScatter from './components/SpeedAltitudeScatter'

function App() {
  return (
    <>
      <header>
        <h1> Automatic Dependent Surveillance Broadcasting Military Aircrafts</h1>
      </header>
      <KpiStatStrip />
      <div className="dashboard-main">
        <div className="card">
          <h2>Live Positions</h2>
          <AircraftMap />
        </div>
        <div className="card">
          <h2>Recent Activity</h2>
          <ActivityTicker />
        </div>
      </div>
      <div className="dashboard-grid">
        <div className="card">
          <h2>Aircraft by Type</h2>
          <AircraftTypeChart />
        </div>
        <div className="card">
          <h2>Altitude by Region</h2>
          <AltitudeByRegionChart />
        </div>
        <div className="card card-wide">
          <h2>Speed by Type</h2>
          <SpeedByTypeChart />
        </div>
        <div className="card card-wide">
          <h2>Speed vs. Altitude</h2>
          <SpeedAltitudeScatter />
        </div>
      </div>
    </>
  )
}

export default App
