import duckdb
import logging
from pathlib import Path
from schema import CREATE_DIM_AIRCRAFT, CREATE_DIM_LOCATION, CREATE_FACT_AIRCRAFT_ACTIVITY
from prefect import task

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def get_connection():
    logging.info("Connecting to DuckDB database...")
    return duckdb.connect(str(BASE_DIR / "pipeline.duckdb"))

def create_tables(con):
    con.execute(CREATE_DIM_AIRCRAFT)
    con.execute(CREATE_DIM_LOCATION)
    con.execute(CREATE_FACT_AIRCRAFT_ACTIVITY)
    logging.info("Tables created successfully.")

def get_new_files():
    return sorted((DATA_DIR / "processed").glob("clean_aircraft_*.parquet"))

def archive_files(files):
    if not files:
        return
    archive_dir = files[0].parent / "clean_archive"
    archive_dir.mkdir(exist_ok=True)
    for f in files:
        f.rename(archive_dir / f.name)

def load_batch(con, files):
    paths = [str(f) for f in files]
    con.execute("""
        INSERT INTO dim_aircraft
        SELECT DISTINCT acft_ID AS aircraft_id, registration, type_code, aircraft_type, owner AS operator
        FROM read_parquet(?)
        ON CONFLICT (aircraft_id) DO UPDATE SET operator = excluded.operator
        WHERE excluded.operator IS NOT NULL
    """, [paths])
    con.execute("""
        INSERT INTO dim_location (region)
        SELECT DISTINCT region
        FROM read_parquet(?)
        ON CONFLICT DO NOTHING""", [paths])
    con.execute("""
        INSERT INTO fact_aircraft_activity
        (aircraft_id, region, timestamp, altitude_change, speed_variability, lat, lon, altitude, speed, climb_rate, acceleration, heading_change, on_ground)
        SELECT acft_ID, region, timestamp, altitude_change, speed_variability, lat, lon, alt_baro, speed_mph, computed_climb_rate_fpm, acceleration_kts_per_s, heading_change_deg, on_ground
        FROM read_parquet(?)
        ON CONFLICT DO NOTHING""", [paths])

def run_test_queries(con):
    result = con.execute("SELECT aircraft_type, COUNT(*) FROM dim_aircraft GROUP BY aircraft_type").fetchall()
    logging.info(f"Aircraft by type: {result}")
    result = con.execute("SELECT region, AVG(altitude) FROM fact_aircraft_activity GROUP BY region").fetchall()
    logging.info(f"Average altitude by region: {result}")
    result = con.execute("SELECT aircraft_type, MIN(speed), MAX(speed), AVG(speed) FROM fact_aircraft_activity JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id GROUP BY aircraft_type").fetchall()
    logging.info(f"Speed statistics by aircraft type: {result}")

@task
def run_load():
    files = get_new_files()
    with get_connection() as con:
        create_tables(con)
        if not files:
            logging.info("Load: no new clean files to process")
        else:
            load_batch(con, files)
            logging.info(f"Data loaded into DuckDB successfully from {len(files)} files.")
            archive_files(files)
        run_test_queries(con)

if __name__ == "__main__":
    run_load()
