# Roadmap

## Phase 1 — Project Setup
- [x] Virtual environment created (`.venv`)
- [ ] Libraries installed *into* the venv (not global)
- [ ] Directory structure created (`/src`, `/data/raw`, `/data/processed`)
- [x] README skeleton
- [ ] GitHub repository created (local only — never pushed without explicit go-ahead)
- [x] Architecture description added to README

## Phase 2 — Data Ingestion
- [ ] `src/ingest.py` written
- [ ] Queries ADS-B Exchange `/v2/mil` endpoint
- [ ] Saves raw JSON to `/data/raw/raw_aircraft_<timestamp>.json`
- [ ] Logs ingestion timestamps
- [ ] Error handling + retries implemented

## Phase 3 — Data Validation (Pydantic)
- [ ] `AircraftModel` defined
- [ ] `PositionModel` defined
- [ ] `TelemetryRecord` defined
- [ ] Lat/lon range validation
- [ ] Altitude/speed numeric validation
- [ ] ICAO hex format validation (6 chars)
- [ ] Timestamp parsing
- [ ] Output: `validated_aircraft_<timestamp>.parquet`

## Phase 4 — Transformation (Polars)
- [ ] Timestamp normalization
- [ ] Speed unit conversion (knots → mph)
- [ ] Climb rate computed
- [ ] Acceleration computed
- [ ] Heading change computed
- [ ] Aircraft type classification
- [ ] Duplicates removed, sorted by timestamp
- [ ] Output: `clean_aircraft_<timestamp>.parquet`

## Phase 5 — Schema Design (Star Schema)
- [ ] `fact_aircraft_activity` designed
- [ ] `dim_aircraft` designed
- [ ] `dim_location` designed
- [ ] Field list finalized (aircraft_id, timestamp, lat, lon, altitude, speed, climb_rate, aircraft_type, region)

## Phase 6 — Storage (DuckDB)
- [ ] DuckDB file initialized (`pipeline.duckdb`)
- [ ] Schema tables created
- [ ] Transformed data loaded
- [ ] Test OLAP queries run (count by type, avg altitude by region, speed distribution by class)

## Phase 7 — Orchestration (Prefect)
- [ ] `ingest_flow`
- [ ] `validate_flow`
- [ ] `transform_flow`
- [ ] `load_flow`
- [ ] `full_pipeline_flow` (chains the above)
- [ ] Logging, retries, scheduling added

## Phase 8 — ML-Ready Feature Generation
- [ ] Feature set finalized (climb_rate, acceleration, heading_change, altitude_change, speed_variability, aircraft_type, region)
- [ ] Output: `ml_features_<timestamp>.parquet`

## Phase 9 — Documentation
- [ ] README fully populated (overview, architecture, tech stack, pipeline steps, example queries, future work)
- [ ] Recruiter/lab-ready polish pass

---

**Data scope decision:** Global military-tagged aircraft via ADS-B Exchange `/v2/mil`, not US-only. `region` field in the schema allows slicing to CONUS vs. overseas later without re-ingesting.
