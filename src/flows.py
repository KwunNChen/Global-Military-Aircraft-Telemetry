from prefect import flow, serve
from ingest import fetch_data
from validate import run_validation
from transform import run_transform
from load import run_load
from cleanup import cleanup_monthly
from features import run_features
import logging
from datetime import timedelta

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
def features_flow():
    run_features()

@flow
def full_pipeline_flow():
    ingest_flow()
    validation_flow()
    transformation_flow()
    loading_flow()
    features_flow()
    cleanup_monthly() #btw if you're auditing the code, this doesn't run monthly. It checks if something is past the monthly cutoff
    logging.info("Full Pipeline ran sucessfully")

if __name__ == "__main__":
    full_pipeline_flow.serve(name="mil-aircraft-pipeline",interval=timedelta(days = 1))
