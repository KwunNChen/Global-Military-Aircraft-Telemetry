import polars as pl
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, filename="data/pipeline.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

TYPE_TO_CATEGORY = {
    "F15": "fighter", "F16": "fighter", "F22": "fighter", "F35": "fighter", "F18": "fighter",
    "KC135": "tanker", "KC10": "tanker", "KC46": "tanker", "K35R": "tanker",
    "C130": "transport", "C17": "transport", "C5": "transport", "C40": "transport",
    "C30J": "transport", "B350": "transport", "C560": "transport", "B762": "transport",
    "BE20": "transport", "A332": "transport", "C5M": "transport", "CN35": "transport",
    "C27J": "transport", "B748": "transport", "AT76": "transport", "LJ35": "transport",
    "B737": "transport", "BE9L": "transport", "B736": "transport", "E135": "transport",
    "B742": "transport", "AN12": "transport", "DH8C": "transport", "B738": "transport",
    "FA7X": "transport", "B190": "transport", "PC24": "transport", "B38M": "transport",
    "FA8X": "transport", "D328": "transport", "C208": "transport", "A319": "transport",
    "A320": "transport", "AT72": "transport", "GLF5": "transport", "IL76": "transport",
    "V22": "transport",
    "E3TF": "isr", "RC135": "isr", "U2": "isr", "MQ9": "isr", "P8": "isr",
    "E737": "isr", "E2": "isr",
    # rotary-wing, all roles (utility/attack/transport)
    "H60": "helicopter", "EC45": "helicopter", "H47": "helicopter", "AS65": "helicopter",
    "A119": "helicopter", "H64": "helicopter", "EC35": "helicopter", "H53S": "helicopter",
    "B212": "helicopter", "A169": "helicopter", "AS32": "helicopter", "NH90": "helicopter",
    "B429": "helicopter", "A139": "helicopter", "W3": "helicopter",
    "TEX2": "trainer", "PC21": "trainer", "F260": "trainer", "G120": "trainer",
    "DA40": "trainer", "T38": "trainer", "P28A": "trainer", "CT4": "trainer", "HAWK": "trainer",
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
        pl.col("type_code").replace_strict(TYPE_TO_CATEGORY, default="unknown").alias("aircraft_type")
    )

def make_region(dataframe):
    return dataframe.with_columns(
        pl.when(
            (pl.col("lat") >= 24) & (pl.col("lat") <= 50) & (pl.col("lon") >= -125) & (pl.col("lon") <= -66)
        ).then(pl.lit("CONUS")).when(
            (pl.col("lat") >= 35) & (pl.col("lat") <= 71) & (pl.col("lon") >= -25) & (pl.col("lon") <= 40)
        ).then(pl.lit("Europe")).when(
            (pl.col("lat") >= 12) & (pl.col("lat") <= 42) & (pl.col("lon") >= 34) & (pl.col("lon") <= 63)
        ).then(pl.lit("Middle East")).when(
            (pl.col("lat") >= -50) & (pl.col("lat") <= 55) & (pl.col("lon") >= 90) & (pl.col("lon") <= 180)
        ).then(pl.lit("Indo-Pacific")).otherwise(pl.lit("other")).alias("region")
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
    dataframe = make_region(dataframe)

    path = save(dataframe)
    logging.info(f"Transform: wrote {dataframe.height} rows to {path}")
    print(f"Wrote {dataframe.height} rows to {path}")
