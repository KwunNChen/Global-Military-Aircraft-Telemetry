# Roadmap

**Repo:** https://github.com/KwunNChen/Global-Military-Aircraft-Telemetry
**Live site:** https://mil-aircraft-telemetry.pages.dev/
**Live API (quick tunnel, temporary):** https://starting-ict-providing-give.trycloudflare.com/docs

## Phase 1 — Project Setup
- [x] Virtual environment created (`.venv`)
- [x] Libraries installed *into* the venv (not global)
- [x] Directory structure created (`/src`, `/data/raw`, `/data/processed`)
- [x] README skeleton
- [x] GitHub repository created and pushed: https://github.com/KwunNChen/Global-Military-Aircraft-Telemetry
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
- [x] `ingest_flow`
- [x] `validate_flow`
- [x] `transform_flow`
- [x] `load_flow`
- [x] `full_pipeline_flow` (chains the above, verified end-to-end run)
- [x] Logging, retries added
- [x] Scheduling added — originally `.serve()`, replaced with a systemd-driven hourly loop (see Phase 10) because `.serve()` on an ephemeral Prefect server never created scheduled runs

## Phase 8 — ML-Ready Feature Generation
- [x] Feature set finalized (climb_rate, acceleration, heading_change, altitude_change, speed_variability, aircraft_type, region)
- [x] Output: `ml_features_<timestamp>.parquet`

## Phase 9 — Documentation
- [x] README fully populated (overview, architecture, tech stack, pipeline steps, example queries, future work)
- [ ] Recruiter/lab-ready polish pass

## Phase 10 — Frontend & Live Hosting (extension beyond original blueprint)

Decisions locked in: FastAPI + a real (React) frontend, deployed on a small always-on VM.

**Backend (FastAPI)**
- [x] Endpoints for the three existing OLAP queries (count by type, avg altitude by region, speed distribution by class) — `src/api.py`, verified locally against real `pipeline.duckdb` data via `/docs`
- [x] Endpoint for latest known position per aircraft (map view) — `/latest-positions`, uses `ROW_NUMBER() ... QUALIFY` to get each aircraft's newest row, verified working (global spread of real positions)
- [x] Endpoint for a single aircraft's history (time series of altitude/speed/climb rate) — `/aircraft-history/{aircraft_id}`
- [x] DuckDB connections opened `read_only=True`, since Prefect's `load_flow` writes to the same file periodically
- [x] CORS configured (`allow_origins=["*"]`, appropriate since all endpoints are public read-only data, no auth)
- [x] Pydantic response models for all five endpoints — verified real typed schemas showing in `/docs` (`AircraftTypeCount`, `RegionAltitude`, `SpeedStats`, `AircraftPosition`, `AircraftHistoryPoint`)

**Backend deployed and verified live:** all 5 endpoints (with CORS + Pydantic response models) confirmed reachable at `https://starting-ict-providing-give.trycloudflare.com/docs` via the Cloudflare Tunnel workaround, deployed as systemd services (`mil-pipeline`, `mil-api`, `nginx`, `mil-tunnel`) — all confirmed surviving disconnects and staying `active` for 4+ hours unattended.

**Frontend (React)**
- [ ] Dashboard view: the three OLAP results as charts/tables
- [ ] Map view: latest aircraft positions (react-leaflet or similar)
- [ ] Aircraft detail view: time series for one aircraft — nice-to-have, pairs with the optional history endpoint above
- [ ] Decide build/serve strategy: simplest v1 is a built React static bundle served directly by FastAPI (`StaticFiles`), one deployable unit instead of two

**VM & deployment**
- [x] Provision a small always-on VM (Oracle Cloud Always Free, `VM.Standard.E2.1.Micro`, Ubuntu 24.04)
- [x] Full pipeline (ingest → validate → transform → load → features) verified running end-to-end on the VM itself, not just locally — cross-platform path bugs (Windows-relative paths breaking on Linux) found and fixed across `ingest.py`, `validate.py`, `transform.py`, `load.py`, `features.py`, `cleanup.py`
- [x] Run the pipeline as a systemd service (`mil-pipeline.service`) that runs the full flow once per hour as a fresh process — survives reboot/crash, `Restart=always`. Verified 2026-10-05: ingestion had silently not run since 2026-08-27 under `.serve()`; after the switch, fresh rows (04:28 UTC) appear in the live API. Also required rebuilding the VM's `pipeline.duckdb` (old file backed up as `pipeline.duckdb.bak`) because `dim_aircraft` gained an `operator` column and `CREATE TABLE IF NOT EXISTS` doesn't migrate existing tables.
- [x] Run the FastAPI app (via uvicorn) as a systemd service (`mil-api.service`)
- [x] Reverse proxy: nginx in front of FastAPI on port 80 (`mil-api-nginx.conf`)
- [x] Firewall opened correctly at every layer (ufw → replaced by direct iptables ACCEPT rules, both Security Lists, no NSGs) — **but inbound traffic to this instance is still blocked externally regardless**, confirmed via port scanner on ports 80, 443, and 8000 with every layer verified correct. Matches a documented, known Oracle Always Free tier issue (see forum thread linked in session), not a misconfiguration on our end.
- [x] **Workaround: Cloudflare Tunnel** (`cloudflared`) — VM makes an outbound connection to Cloudflare instead of accepting inbound traffic, sidestepping the Oracle block entirely. Quick tunnel verified working end-to-end (`/docs` reachable over a public HTTPS URL).
- [x] Make the tunnel persistent: `mil-tunnel.service`, systemd-managed, `Restart=always`, verified working end-to-end at a live public URL
- [ ] Upgrade from a random `trycloudflare.com` quick-tunnel URL to a permanent named tunnel (requires a free Cloudflare account + a domain) for a stable link worth putting on a resume

**Known limitation to document, not solve**
- [ ] DuckDB single-writer conflict: a request landing during the nightly write window can fail. Acceptable at this scale — note it in the README rather than over-engineering a fix (e.g. migrating to Postgres) for a portfolio project.
- [x] Oracle Always Free inbound networking issue — documented above, worked around via Cloudflare Tunnel rather than continuing to debug infrastructure outside our control

---

**Data scope decision:** Global military-tagged aircraft via airplanes.live `/v2/mil` (free, ADS-B Exchange-lineage data, same response format), not US-only. `region` field in the schema allows slicing to CONUS vs. overseas later without re-ingesting.

**Data source decision:** Switched from ADS-B Exchange's paid RapidAPI tier ($10/mo) to airplanes.live, a free community-run API with matching schema and a dedicated military endpoint.
