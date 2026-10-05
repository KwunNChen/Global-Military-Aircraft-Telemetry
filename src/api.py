from fastapi import FastAPI
from datetime import datetime
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
app = FastAPI()

class AircraftTypeCount(BaseModel):
    aircraft_type: str
    count: int
class RegionAltitude(BaseModel):
    region: str
    avg_altitude: float

class SpeedStats(BaseModel):
    aircraft_type: str
    min_speed: float | None
    max_speed: float | None
    avg_speed: float | None

class AircraftPosition(BaseModel):
    aircraft_id: str
    lat: float
    lon: float
    aircraft_type: str
    operator: str | None

class AircraftHistoryPoint(BaseModel):
    timestamp: datetime
    altitude: float | None
    speed: float | None
    climb_rate: float | None

class RegionTypeCount(BaseModel):
    region: str
    aircraft_type: str
    count: int

class ClimbRateBucket(BaseModel):
    bucket: str
    count: int

class ActivityRecord(BaseModel):
    aircraft_id: str
    aircraft_type: str
    timestamp: datetime
    region: str
    altitude: float | None
    speed: float | None

class SpeedAltitudePoint(BaseModel):
    aircraft_type: str
    speed: float
    altitude: float

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def get_readonly_connection():
    return duckdb.connect(str(BASE_DIR / "pipeline.duckdb"), read_only=True)

@app.get("/aircraft-by-type", response_model=list[AircraftTypeCount])
def get_aircraft_by_type():
    with get_readonly_connection() as con:
        result = con.execute("SELECT aircraft_type, COUNT(*) FROM dim_aircraft GROUP BY aircraft_type").fetchall()
    return [{"aircraft_type": row[0], "count": row[1]} for row in result]

@app.get("/altitude-by-region", response_model=list[RegionAltitude])
def get_avg_alt_by_region():
    with get_readonly_connection() as con:
        result = con.execute("SELECT region, AVG(altitude) FROM fact_aircraft_activity GROUP BY region").fetchall()
    return [{"region": row[0], "avg_altitude": row[1]} for row in result]

@app.get("/speed-by-aircraft-type", response_model=list[SpeedStats])
def get_spd_distribution_by_acft_class():
    with get_readonly_connection() as con:
        result = con.execute("SELECT aircraft_type, MIN(speed), MAX(speed), AVG(speed) FROM fact_aircraft_activity JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id GROUP BY aircraft_type").fetchall()
    return [{"aircraft_type": row[0], "min_speed": row[1], "max_speed": row[2], "avg_speed": row[3]} for row in result]

@app.get("/latest-positions", response_model=list[AircraftPosition])
def get_latest_positions():
    with get_readonly_connection() as con:
        result = con.execute("""
            SELECT fact_aircraft_activity.aircraft_id, lat, lon, aircraft_type, operator
            FROM fact_aircraft_activity
            JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
            QUALIFY ROW_NUMBER() OVER (PARTITION BY fact_aircraft_activity.aircraft_id ORDER BY timestamp DESC) = 1
        """).fetchall()
    return [{"aircraft_id": row[0], "lat": row[1], "lon": row[2], "aircraft_type": row[3], "operator": row[4]} for row in result]

@app.get("/aircraft-history/{aircraft_id}", response_model=list[AircraftHistoryPoint])
def get_aircraft_history(aircraft_id: str):
    with get_readonly_connection() as con:
        result = con.execute(
            "SELECT timestamp, altitude, speed, climb_rate FROM fact_aircraft_activity WHERE aircraft_id = ? ORDER BY timestamp",
            [aircraft_id]
        ).fetchall()
    return [{"timestamp": row[0], "altitude": row[1], "speed": row[2], "climb_rate": row[3]} for row in result]

@app.get("/aircraft-type-by-region", response_model=list[RegionTypeCount])
def get_aircraft_type_by_region():
    with get_readonly_connection() as con:
        result = con.execute("""
            SELECT region, aircraft_type, COUNT(DISTINCT fact_aircraft_activity.aircraft_id)
            FROM fact_aircraft_activity
            JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
            GROUP BY region, aircraft_type
        """).fetchall()
    return [{"region": row[0], "aircraft_type": row[1], "count": row[2]} for row in result]

@app.get("/climb-rate-breakdown", response_model=list[ClimbRateBucket])
def get_climb_rate_breakdown():
    with get_readonly_connection() as con:
        result = con.execute("""
            SELECT
                CASE
                    WHEN climb_rate > 500 THEN 'climbing'
                    WHEN climb_rate < -500 THEN 'descending'
                    ELSE 'cruising'
                END AS bucket,
                COUNT(*)
            FROM fact_aircraft_activity
            GROUP BY bucket
        """).fetchall()
    return [{"bucket": row[0], "count": row[1]} for row in result]

@app.get("/recent-activity", response_model=list[ActivityRecord])
def get_recent_activity(limit: int = 20):
    with get_readonly_connection() as con:
        result = con.execute("""
            SELECT fact_aircraft_activity.aircraft_id, aircraft_type, timestamp, region, altitude, speed
            FROM fact_aircraft_activity
            JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
            ORDER BY timestamp DESC
            LIMIT ?
        """, [limit]).fetchall()
    return [{"aircraft_id": r[0], "aircraft_type": r[1], "timestamp": r[2], "region": r[3], "altitude": r[4], "speed": r[5]} for r in result]

@app.get("/speed-altitude-sample", response_model=list[SpeedAltitudePoint])
def get_speed_altitude_sample(limit: int = 500):
    with get_readonly_connection() as con:
        result = con.execute("""
            SELECT aircraft_type, speed, altitude
            FROM fact_aircraft_activity
            JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
            WHERE speed IS NOT NULL AND altitude IS NOT NULL
            ORDER BY random()
            LIMIT ?
        """, [limit]).fetchall()
    return [{"aircraft_type": r[0], "speed": r[1], "altitude": r[2]} for r in result]