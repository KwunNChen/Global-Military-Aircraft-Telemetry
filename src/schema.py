CREATE_DIM_AIRCRAFT = """
CREATE TABLE dim_aircraft (
    aircraft_id VARCHAR PRIMARY KEY,
    registration VARCHAR,
    type_code VARCHAR,
    aircraft_type VARCHAR
);
"""

CREATE_DIM_LOCATION = """
    CREATE TABLE dim_location (
    region VARCHAR PRIMARY KEY
);
"""

CREATE_FACT_AIRCRAFT_ACTIVITY = """
CREATE TABLE fact_aircraft_activity (
    activity_id INTEGER PRIMARY KEY,
    aircraft_id VARCHAR,
    FOREIGN KEY (aircraft_id) REFERENCES dim_aircraft(aircraft_id),
    region VARCHAR,
    FOREIGN KEY (region) REFERENCES dim_location(region),
    timestamp TIMESTAMP,
    lat DOUBLE,
    lon DOUBLE,
    altitude DOUBLE,
    speed DOUBLE,
    climb_rate DOUBLE,
    acceleration DOUBLE,
    heading_change DOUBLE,
    on_ground BOOLEAN
);
"""