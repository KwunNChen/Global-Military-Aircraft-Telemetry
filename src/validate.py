from pathlib import Path
import json

def load_file(filepath):
    try:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        content = path.read_text(encoding="utf-8")
        return content
    except (FileNotFoundError, IsADirectoryError) as e:
        print(f"Error: {e}")
    except UnicodeDecodeError:
        print("Error: Could not decode file. Check encoding.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def build_models(loadeddata):
    #Metadata
    loadeddata = json.loads(loadeddata)
    totalAC = len(loadeddata['ac'])
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
        timestamp =  now - aircraft['seen']
        one_acft_model = {"acft_ID": acft_ID,"callsign": callsign,"registration": registration,"type_code": type_code,"desc": desc,"owner": owner,"category": category}

        #PositionModel
        coordinates = (aircraft['lat'], aircraft['lon']) if 'lat' in aircraft and 'lon' in aircraft else (None, None)
        rounded_fallback = (aircraft['rr_lat'], aircraft['rr_lon']) if 'rr_lat' in aircraft and 'rr_lon' in aircraft else (None, None)
        last_known_loc = (aircraft['lastPosition']['lat'], aircraft['lastPosition']['lon']) if 'lastPosition' in aircraft and 'lat' in aircraft['lastPosition'] and 'lon' in aircraft['lastPosition'] else (None, None)
        baro_alt = aircraft['alt_baro'] if 'alt_baro' in aircraft else None
        geom_alt = aircraft['alt_geom'] if 'alt_geom' in aircraft else None
        heading = aircraft['track'] if 'track' in aircraft else None
        one_pos_model = {"coordinates": coordinates, "rounded_fallback": rounded_fallback, "last_known_loc": last_known_loc, "baro_alt": baro_alt, "geom_alt": geom_alt, "heading": heading}

        #TelemetryRecord
        one_telemetry_record = {
            **one_acft_model, #btw ** unpacks dictionaries into the new dictionary
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
   #Empty space here that I'm going to work in models.py validation code, once the code validation completes I will be able to sub in the code

    for record in telemetry_record:
        if record['acft_ID'] is None:
            continue
        else:
            valid_records.append(record)
    return valid_records

if __name__ == "__main__":
    file_content = load_file("the file path to file here")
    if file_content is not None:
        print("File loaded successfully:")
        saved_telemetry = build_models(file_content)
        #Pretend Im saving the validated data into processed or something