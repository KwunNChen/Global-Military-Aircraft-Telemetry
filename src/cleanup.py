from prefect import task
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def list_aircraft_files(directory):
    # Walks subfolders too (e.g. raw/archive, processed/validated_archive,
    # processed/clean_archive) so archived files still get pruned after 30 days.
    # Matches both aircraft_* files and features.py's ml_features_* snapshots,
    # which aren't archived by any stage and would otherwise grow unbounded.
    matches = []
    for root, _dirs, files in os.walk(directory):
        for file in files:
            if "aircraft_" in file or "ml_features_" in file:
                matches.append(os.path.join(root, file))
    return matches if matches else None

def get_all_raw_files(directory=None):
    if directory is None:
        directory = DATA_DIR / "raw"
    return list_aircraft_files(directory)

def get_all_processed_files(directory=None):
    if directory is None:
        directory = DATA_DIR / "processed"
    return list_aircraft_files(directory)

def cuttoff_removal(filepath):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    try:

        content = Path(filepath).name.split("_")[2].split(".")[0]
        clean_raw = datetime.strptime(content, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        if clean_raw <= cutoff:
            os.remove(filepath)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


@task
def cleanup_monthly():
    raws = get_all_raw_files()
    processedes = get_all_processed_files()
    if raws is not None:
        for raw in raws:
            cuttoff_removal(raw)
    if processedes is not None:
        for processed in processedes:
            cuttoff_removal(processed)