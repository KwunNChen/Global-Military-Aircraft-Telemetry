# Military Aircraft Activity Pipeline

A reproducible data engineering pipeline that ingests open-source military aircraft telemetry, validates it, transforms it, stores it in an analytical database, and produces ML-ready datasets for defense activity analysis.

> Status: **Phase 7 — Orchestration (Prefect)** (in progress). See [ROADMAP.md](ROADMAP.md) for full phase tracking.

## Overview

This project pulls real-time global military aircraft telemetry from the [adsb.fi](https://adsb.fi/) API (a free, community-run feed carrying the same ADS-B Exchange-lineage data format), enforces a strict data schema, engineers activity features (climb rate, acceleration, heading change), and lands the result in a queryable OLAP warehouse — with the whole pipeline orchestrated and automatable end to end.

It's built to demonstrate the core skill set of a data engineer working on defense/telemetry analytics: ingestion, schema validation, transformation, dimensional modeling, storage, and orchestration — with an ML-ready output layer as the payoff.

If you're auditing this code, please beware that I comment a lot because I'm one of those people that look at my own code after a week and go, "How the heck does this work?"

## Architecture

```
adsb.fi API
        │
        ▼
  [1] Ingestion         raw JSON  →  /data/raw
        │
        ▼
  [2] Validation         Pydantic models  →  validated parquet
        │
        ▼
  [3] Transformation      Polars (clean, enrich, feature-engineer)
        │
        ▼
  [4] Star Schema         fact_aircraft_activity, dim_aircraft, dim_location
        │
        ▼
  [5] Storage              DuckDB (OLAP)
        │
        ▼
  [6] ML Feature Output    /data/processed/ml_features_<timestamp>.parquet

  Orchestrated end-to-end by Prefect flows, with logging, retries, and scheduling.
```

## Tech Stack

| Layer | Tool |
|---|---|
| Ingestion | Python, `requests` |
| Validation | Pydantic |
| Transformation | Polars |
| Storage | DuckDB |
| Orchestration | Prefect |
| Data source | adsb.fi API (free, global military feed) |

**Planned enhancements:** GeoPandas (geospatial validation), DVC (data versioning), MLflow (experiment tracking).

## Data Scope

Global military-tagged aircraft, pulled from adsb.fi's `/v2/mil` endpoint — not limited to US assets. adsb.fi carries the same unfiltered, independent-receiver-network data as ADS-B Exchange, so this captures military traffic worldwide as it's broadcast. See `ROADMAP.md` for how region-scoping (e.g. CONUS vs. overseas) fits into the schema.

Note: this is a free, volunteer-run community API, not a paid contract. It's a known tradeoff worth stating plainly — uptime and terms aren't guaranteed the way a commercial API's would be.

## Project Structure

```
├── src/
│   ├── ingest.py        # Phase 2 — API ingestion
│   ├── validate.py      # Phase 3 — Pydantic validation
│   ├── transform.py     # Phase 4 — Polars transforms
│   ├── schema.py         # Phase 5 — star schema definitions
│   ├── load.py            # Phase 6 — DuckDB loading
│   ├── features.py        # Phase 8 — ML feature generation
│   └── flows.py            # Phase 7 — Prefect orchestration
├── data/
│   ├── raw/                 # untouched API dumps (gitignored)
│   └── processed/           # parquet outputs (gitignored)
├── tests/
├── requirements.txt
├── pipeline.duckdb           # local OLAP database (gitignored)
└── README.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

No API key required (adsb.fi is open access). The `.env` file is still gitignored and reserved for future keys if additional data sources are added.

## Example Queries

Run against a live snapshot of 656 validated observations across 512 aircraft.

**Aircraft count by type**
```sql
SELECT aircraft_type, COUNT(*) FROM dim_aircraft GROUP BY aircraft_type
```
transport: 120, unknown: 238, helicopter: 93, trainer: 42, tanker: 13, isr: 6

**Average altitude by region**
```sql
SELECT region, AVG(altitude) FROM fact_aircraft_activity GROUP BY region
```
Europe: 25,083 ft, Middle East: 11,839 ft, other: 11,188 ft, Indo-Pacific: 10,758 ft, CONUS: 9,268 ft

**Speed distribution by aircraft class**
```sql
SELECT aircraft_type, MIN(speed), MAX(speed), AVG(speed)
FROM fact_aircraft_activity
JOIN dim_aircraft ON fact_aircraft_activity.aircraft_id = dim_aircraft.aircraft_id
GROUP BY aircraft_type
```
Tankers average fastest (437 mph), helicopters slowest (98 mph), consistent with their real-world roles. Minimum speeds bottom out at 0 mph across most classes, aircraft caught on the ground between snapshots.

## Roadmap

Full 9-phase build plan with status tracking lives in [ROADMAP.md](ROADMAP.md).

## Future Work

- GeoPandas for geospatial validation and region-boundary analysis
- DVC for raw data versioning
- MLflow for tracking anomaly-detection model experiments built on top of the ML feature output
- Additional open telemetry sources beyond adsb.fi
