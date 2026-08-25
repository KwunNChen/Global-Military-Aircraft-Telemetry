from prefect import flow
from ingest import fetch_data
from validate import run_validation
from transform import run_transform
from load import run_load
import logging

logging.basicConfig(level=logging.INFO, filename="data/pipeline.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s", force = True)

@flow
def ingest_flow():
    fetch_data()

@flow
def validation_flow():
    run_validation()

@flow
def transformation_flow():
    run_transform()

@flow
def loading_flow():
    run_load()

@flow
def full_pipeline_flow():
    ingest_flow()
    validation_flow()
    transformation_flow()
    loading_flow()
    logging.info("Full Pipeline ran sucessfully")

if __name__ == "__main__":
    full_pipeline_flow()