import duckdb
import logging
from schema import CREATE_DIM_AIRCRAFT, CREATE_DIM_LOCATION, CREATE_FACT_AIRCRAFT_ACTIVITY

logging.basicConfig(level=logging.INFO, filename="data/pipeline.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

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
        SELECT acft_ID AS aircraft_id, region, timestamp, lat, lon, alt_baro AS altitude, speed_mph AS speed, computed_climb_rate_fpm AS climb_rate, acceleration_kts_per_s AS acceleration, heading_change_deg AS heading_change, on_ground
        FROM read_parquet('data/processed/clean_aircraft_*.parquet')
        ON CONFLICT DO NOTHING""")


if __name__ == "__main__":
    with get_connection() as con:
        create_tables(con)
        load_batch(con)
        logging.info("Data loaded into DuckDB successfully.")
