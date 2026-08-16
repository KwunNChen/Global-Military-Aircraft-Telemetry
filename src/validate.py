from pathlib import Path
from models import AircraftModel, PositionModel
from pydantic import BaseModel, ValidationError
from datetime import datetime, timezone
import polars as pl
import os
import logging
import json

logging.basicConfig(level=logging.INFO, filename ="data/pipeline.log",filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

def get_all_files(directory="data/raw"):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    acceptable_filepath = []
    for file in files:
        if "aircraft_" in file:
            acceptable_filepath.append(os.path.join(directory, file))   
    return acceptable_filepath

def load_file(filepath):
    try:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        content = path.read_text(encoding="utf-8")
        return content
    except (FileNotFoundError, IsADirectoryError) as e:
        logging.error(f"Error: {e}")
    except UnicodeDecodeError:
        logging.error("Error: Could not decode file. Check encoding.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def build_models(loadeddata):
    #Metadata
    loadeddata = json.loads(loadeddata)
    totalacft = len(loadeddata['ac'])
    now = loadeddata['now']

    telemetry_record = []
    
    for aircraft in loadeddata['ac']:
        #AircraftModel
        acft_ID = aircraft['hex']
        callsign = aircraft['flight'].strip() if 'flight' in aircraft else None
        registration = aircraft['r'] if 'r' in aircraft else None
        type_code = aircraft['t'] if 't' in aircraft else None
        desc = aircraft['desc'] if 'desc' in aircraft else None
        owner = aircraft['ownOp'] if 'ownOp' in aircraft else None
        category = aircraft['category'] if 'category' in aircraft else None
        timestamp =  now - (aircraft['seen'] * 1000)
        one_acft_model = {"acft_ID": acft_ID,"callsign": callsign,"registration": registration,"type_code": type_code,"desc": desc,"owner": owner,"category": category}

        #PositionModel
        lat = aircraft['lat'] if 'lat' in aircraft else None
        lon = aircraft['lon'] if 'lon' in aircraft else None
        rr_lat = aircraft['rr_lat'] if 'rr_lat' in aircraft else None
        rr_lon = aircraft['rr_lon'] if 'rr_lon' in aircraft else None
        last_position = aircraft['lastPosition'] if 'lastPosition' in aircraft else None
        alt_baro = aircraft['alt_baro'] if 'alt_baro' in aircraft else None
        geom_alt = aircraft['alt_geom'] if 'alt_geom' in aircraft else None
        heading = aircraft['track'] if 'track' in aircraft else None
        one_pos_model = {"lat": lat, "lon": lon, "rr_lat": rr_lat, "rr_lon": rr_lon, "lastPosition": last_position, "alt_baro": alt_baro, "geom_alt": geom_alt, "heading": heading}

        #TelemetryRecord
        one_telemetry_record = {
            **one_acft_model, #** unpacks dictionaries into the new dictionary
            **one_pos_model,
            "timestamp": timestamp,
            "gs": aircraft['gs'] if 'gs' in aircraft else None,
            "climb_rate": aircraft['baro_rate'] if 'baro_rate' in aircraft else (aircraft['geom_rate'] if 'geom_rate' in aircraft else None),
            "seen": aircraft['seen'] if 'seen' in aircraft else None,
            "seen_pos": aircraft['seen_pos'] if 'seen_pos' in aircraft else None,
            "squawk": aircraft['squawk'] if 'squawk' in aircraft else None,
            "emergency": aircraft['emergency'] if 'emergency' in aircraft else None,
        }
        telemetry_record.append(one_telemetry_record)
    return telemetry_record 

def validate_models(telemetry_record):
    valid_records = []
    for record in telemetry_record:
        if record['acft_ID'] is None:
            continue
        try:
            pos = PositionModel(**record)
            AircraftModel(**record)
            valid_records.append(pos.model_dump())
        except ValidationError as e:
            logging.warning(f"Validation failed for record {record.get('acft_ID')}: {e}")
    return valid_records

if __name__ == "__main__":
    filepaths = get_all_files()
    all_telemetry = []
    loaded = 0
    error = 0

    for file in filepaths:
        content = load_file(file)
        if content is not None:
            all_telemetry.extend(build_models(content))
            loaded += 1
        else:
            error += 1

    validated_data = validate_models(all_telemetry)
    df = pl.DataFrame(validated_data)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    df.write_parquet(f"data/processed/validated_aircraft_{timestamp}.parquet")
    logging.info(f"Validation: processed {loaded} files ({error} failed), wrote {len(validated_data)} rows")