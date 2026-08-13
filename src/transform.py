import polars as pl
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, filename="data/pipeline.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

TYPE_TO_CATEGORY = {
    "F15": "fighter", "F16": "fighter", "F22": "fighter", "F35": "fighter", "F18": "fighter",
    "KC135": "tanker", "KC10": "tanker", "KC46": "tanker",
    "C130": "transport", "C17": "transport", "C5": "transport", "C40": "transport",
    "E3TF": "isr", "RC135": "isr", "U2": "isr", "MQ9": "isr", "P8": "isr",
}


def load_data(pattern="data/processed/validated_aircraft_*.parquet"):
    return pl.read_parquet(pattern)


def normalize_timestamp(dataframe):
    return dataframe.with_columns(
        pl.from_epoch(pl.col("timestamp").cast(pl.Int64), time_unit="ms")
          .dt.replace_time_zone("UTC")
          .alias("timestamp")
    )


def dedupe_and_sort(dataframe):
    return (
        dataframe.unique(subset=["acft_ID", "timestamp"])
                 .sort(["acft_ID", "timestamp"])
    )


def add_deltas(dataframe):
    dataframe = dataframe.with_columns(
        pl.col("timestamp").diff().over("acft_ID").dt.total_seconds().alias("time_delta_s")
    )
    dataframe = dataframe.with_columns([
        (pl.col("alt_baro").diff().over("acft_ID") / (pl.col("time_delta_s") / 60)).alias("computed_climb_rate_fpm"),
        (pl.col("gs").diff().over("acft_ID") / pl.col("time_delta_s")).alias("acceleration_kts_per_s"),
        (((pl.col("heading").diff().over("acft_ID") + 180) % 360) - 180).alias("heading_change_deg"),
    ])
    return dataframe


def convert_units(dataframe):
    return dataframe.with_columns(
        (pl.col("gs") * 1.15078).alias("speed_mph")
    )


def classify_type(dataframe):
    return dataframe.with_columns(
        pl.col("type_code").replace(TYPE_TO_CATEGORY, default="unknown").alias("aircraft_type")
    )


def save(dataframe):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = f"data/processed/clean_aircraft_{timestamp}.parquet"
    dataframe.write_parquet(path)
    return path


if __name__ == "__main__":
    dataframe = load_data()
    logging.info(f"Transform: loaded {dataframe.height} raw validated rows")

    dataframe = normalize_timestamp(dataframe)
    dataframe = dedupe_and_sort(dataframe)
    dataframe = add_deltas(dataframe)
    dataframe = convert_units(dataframe)
    dataframe = classify_type(dataframe)

    path = save(dataframe)
    logging.info(f"Transform: wrote {dataframe.height} rows to {path}")
    print(f"Wrote {dataframe.height} rows to {path}")
