# Roadmap

## Phase 1 — Project Setup
- [x] Virtual environment created (`.venv`)
- [x] Libraries installed *into* the venv (not global)
- [x] Directory structure created (`/src`, `/data/raw`, `/data/processed`)
- [x] README skeleton
- [x] GitHub repository created (local only — never pushed without explicit go-ahead)
- [x] Architecture description added to README

## Phase 2 — Data Ingestion
- [x] `src/ingest.py` written
- [x] Queries airplanes.live `/v2/mil` endpoint (free, no key, 1 req/sec limit) — note: no trailing slash, that returns 400
- [x] Saves raw JSON to `/data/raw/raw_aircraft_<timestamp>.json`
- [x] Logs ingestion timestamps
- [x] Error handling + retries implemented (verified against a real timeout + real bad-status failure)

## Phase 3 — Data Validation (Pydantic)
- [x] `AircraftModel` defined
- [x] `PositionModel` defined
- [x] `TelemetryRecord` defined
- [x] Lat/lon range validation
- [x] Altitude/speed numeric validation
- [x] ICAO hex format validation (6 chars)
- [x] Timestamp parsing
    -- fair doubt, but this source never gives you a timestamp string to parse in the first place, just a snapshot epoch (`now`) and a per-aircraft offset (`seen`). Computing + range/future-checking it is the correct equivalent here, that counts.
- [x] Output: `validated_aircraft_<timestamp>.parquet`

## Phase 4 — Transformation (Polars)
- [x] Timestamp normalization
- [x] Speed unit conversion (knots → mph)
- [x] Climb rate computed
- [x] Acceleration computed
- [x] Heading change computed
- [x] Aircraft type classification
- [x] Duplicates removed, sorted by timestamp
- [x] Output: `clean_aircraft_<timestamp>.parquet`

**Data source note:** switched from airplanes.live to adsb.fi (`opendata.adsb.fi/api/v2/mil`) mid-Phase-4 — airplanes.live and adsb.one both started returning 403s (shared infra, airplanes.live's own error pointed to contacting them directly). adsb.fi is free, same ADSBX-lineage schema, no code changes needed beyond the URL. README/ROADMAP data-source references still say airplanes.live and need updating.

## Phase 5 — Schema Design (Star Schema)
- [x] `fact_aircraft_activity` designed
- [x] `dim_aircraft` designed
- [x] `dim_location` designed
- [x] Field list finalized (aircraft_id, timestamp, lat, lon, altitude, speed, climb_rate, aircraft_type, region)

## Phase 6 — Storage (DuckDB)
- [x] DuckDB file initialized (`pipeline.duckdb`)
- [x] Schema tables created
- [x] Transformed data loaded
- [x] Test OLAP queries run (count by type, avg altitude by region, speed distribution by class)

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

**Data scope decision:** Global military-tagged aircraft via airplanes.live `/v2/mil` (free, ADS-B Exchange-lineage data, same response format), not US-only. `region` field in the schema allows slicing to CONUS vs. overseas later without re-ingesting.

**Data source decision:** Switched from ADS-B Exchange's paid RapidAPI tier ($10/mo) to airplanes.live, a free community-run API with matching schema and a dedicated military endpoint.
