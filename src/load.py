import duckdb
import logging
from schema import CREATE_DIM_AIRCRAFT, CREATE_DIM_LOCATION, CREATE_FACT_AIRCRAFT_ACTIVITY
from prefect import task

def get_connection():
    logging.info("Connecting to DuckDB database...")
    return duckdb.connect("pipeline.duckdb")

def create_tables(con):
    con.execute(CREATE_DIM_AIRCRAFT)
    con.execute(CREATE_DIM_LOCATION)
    con.execute(CREATE_FACT_AIRCRAFT_ACTIVITY)
    logging.info("Tables created successfully.")

def load_batch(con):
    con.execute("""
        INSERT INTO dim_aircraft
        SELECT DISTINCT acft_ID AS aircraft_id, registration, type_code, aircraft_type
        FROM read_parquet('data/processed/clean_aircraft_*.parquet')
        ON CONFLICT DO NOTHING
    """)
    con.execute("""
        INSERT INTO dim_location (region)
        SELECT DISTINCT region
        FROM read_parquet('data/processed/clean_aircraft_*.parquet')
        ON CONFLICT DO NOTHING""")
    con.execute("""
        INSERT INTO fact_aircraft_activity
        (aircraft_id, region, timestamp, altitude_change, speed_variability, lat, lon, altitude, speed, climb_rate, acceleration, heading_change, on_ground)
        SELECT acft_ID, region, timestamp, altitude_change, speed_variability, lat, lon, alt_baro, speed_mph, computed_climb_rate_fpm, acceleration_kts_per_s, heading_change_deg, on_ground
        FROM read_parquet('data/processed/clean_aircraft_*.parquet')
        ON CONFLICT DO NOTHING""")

def run_test_queries(con):
    result = con.execute("SELECT aircraft_type, COUNT(*) FROM dim_aircraft GROUP BY aircraft_type").fetchall()
    logging.info(f"Aircraft by type: {result}")
    result = con.execute("SELECT region, AVG(altitude) FROM fact_aircraft_activity GROUP BY region").fetchall()
    logging.info(f"Average altitude by region: {result}")
    result = con.execute("SELECT aircraft_type, MIN(speed), MAX(speed), AVG(speed) FROM fact_aircraft_activity JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id GROUP BY aircraft_type").fetchall()
    logging.info(f"Speed statistics by aircraft type: {result}")

@task
def run_load():
    with get_connection() as con:
        create_tables(con)
        load_batch(con)
        logging.info("Data loaded into DuckDB successfully.")
        run_test_queries(con)

if __name__ == "__main__":
    run_load()
