import duckdb
import polars
import logging
from datetime import datetime, timezone
from pathlib import Path
from prefect import task
from load import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def get_ml_features(con):
    query = """
        SELECT fact_aircraft_activity.aircraft_id,timestamp,climb_rate,acceleration,heading_change,altitude_change, speed_variability, aircraft_type,region
        FROM fact_aircraft_activity
        JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
    """
    return con.sql(query).pl()

def retrieve_clean():
    unclean = get_ml_features(get_connection())
    logging.info("Clean data retrieved; null data dropped")
    return unclean.drop_nulls(subset=["climb_rate", "acceleration", "heading_change", "altitude_change", "speed_variability"])

def save(clean_data):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = DATA_DIR / "processed" / f"ml_features_{timestamp}.parquet"
    clean_data.write_parquet(path)
    return path

@task
def run_features():
    save(retrieve_clean())
    logging.info("ML Features saved sucessfully")

if __name__ == "__main__": 
    run_features()