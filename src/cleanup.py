from prefect import task
from pathlib import Path
from datetime import datetime, timezone, timedelta
import logging
import os

def get_all_raw_files(directory="data/raw"):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    acceptable_raw_filepath = []
    for file in files:
        if "aircraft_" in file:
            acceptable_raw_filepath.append(os.path.join(directory, file))   
    return acceptable_raw_filepath

def get_all_processed_files(directory="data/processed"):
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if not files:
        return None
    acceptable_processed_filepath = []
    for file in files:
        if "aircraft_" in file:
            acceptable_processed_filepath.append(os.path.join(directory, file))   
    return acceptable_processed_filepath

def cuttoff_removal(filepath):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    try:

        content = str(filepath).split("_")[2].split(".")[0]
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