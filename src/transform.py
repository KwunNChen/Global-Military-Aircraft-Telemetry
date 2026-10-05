import polars as pl
import logging
from datetime import datetime, timezone
from pathlib import Path
from prefect import task

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

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


def get_new_files():
    return sorted((DATA_DIR / "processed").glob("validated_aircraft_*.parquet"))


def load_last_state():
    path = DATA_DIR / "processed" / "last_state.parquet"
    if path.exists():
        return pl.read_parquet(path)
    return None


def save_last_state(dataframe):
    dataframe.write_parquet(DATA_DIR / "processed" / "last_state.parquet")


def archive_files(files):
    if not files:
        return
    archive_dir = files[0].parent / "validated_archive"
    archive_dir.mkdir(exist_ok=True)
    for f in files:
        f.rename(archive_dir / f.name)


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
        (pl.col("alt_baro") - pl.col("alt_baro").shift(1).over("acft_ID")).alias("altitude_change"),
        (pl.col("gs").rolling_std(window_size=5).over("acft_ID")).alias("speed_variability"),
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
    path = DATA_DIR / "processed" / f"clean_aircraft_{timestamp}.parquet"
    dataframe.write_parquet(path)
    return path

@task
def run_transform():
    files = get_new_files()
    if not files:
        logging.info("Transform: no new validated files to process")
        return

    new_data = pl.read_parquet(files).with_columns(pl.lit(True).alias("is_new"))
    logging.info(f"Transform: loaded {new_data.height} new rows from {len(files)} files")

    # Seed with each aircraft's last known reading so delta calculations (climb
    # rate, acceleration, etc.) stay correct even though we only process new
    # files each run instead of the full history. last_state is kept in the
    # same raw (pre-normalize) schema as new_data so a single normalize_timestamp
    # pass handles both consistently — normalizing it twice across runs would
    # corrupt the timestamp.
    last_state = load_last_state()
    if last_state is not None:
        combined = pl.concat([last_state.with_columns(pl.lit(False).alias("is_new")), new_data], how="vertical_relaxed")
    else:
        combined = new_data
    combined = combined.unique(subset=["acft_ID", "timestamp"])

    # Snapshot the latest raw reading per aircraft to seed the next run.
    next_state = combined.sort("timestamp").unique(subset=["acft_ID"], keep="last").drop("is_new")

    combined = normalize_timestamp(combined)
    combined = dedupe_and_sort(combined)
    combined = add_deltas(combined)
    combined = convert_units(combined)
    combined = classify_type(combined)
    combined = make_region(combined)

    output = combined.filter(pl.col("is_new")).drop("is_new")
    path = save(output)
    logging.info(f"Transform: wrote {output.height} rows to {path}")

    save_last_state(next_state)
    archive_files(files)

if __name__ == "__main__":
    run_transform()
