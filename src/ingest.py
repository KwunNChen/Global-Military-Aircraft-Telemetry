import requests
import time
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from prefect import task

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

@task
def fetch_data():
    for i in range(3):
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        try:
            filepath = DATA_DIR / "raw" / f"raw_aircraft_{timestamp}.json"
            logging.info("Starting request to adsb.fi")
            response = None
            headers = {"User-Agent": "MilitaryAircraftPipeline/1.0"}
            response = requests.get("https://opendata.adsb.fi/api/v2/mil", headers=headers, timeout=10)
            response.raise_for_status() #Except triggers 
            data = response.json()
            with open(filepath, "w") as file:
                json.dump(data, file)
            logging.info(f"Request successful. Status code: {response.status_code}: {response.reason}. Aircraft count: {len(data['ac'])}. File saved to {filepath}.")
            return True
        except requests.exceptions.RequestException as e:
            logging.warning(f"Request failed: {e}. Retrying in {2**i} seconds...")
            if response != None:
                logging.error(f"Request failed. Status code: {response.status_code}: {response.reason}.")
            else:
                logging.error("Request failed. No response received. Potential API fetch error.")
            time.sleep(2**i) #Exponential backoff
    return False

if __name__ == "__main__": #Blocks running if not called directly
    success = fetch_data()
    if success:
        logging.info("Data ingestion completed successfully.")
    else:
        logging.critical("Data ingestion failed after multiple attempts.")
