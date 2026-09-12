import dlt
from pyspark.sql.functions import col, lower, when, lit, to_timestamp


# ============================================================
# BRONZE LAYER
# Auto Loader -> Bronze Streaming Tables
# ============================================================

RAW_BASE = "/Volumes/airlines_project/raw/rawvolume/rawdata"
BRONZE_SCHEMA_BASE = "/Volumes/airlines_project/bronze/bronzevolume/_schemas"


def bronze_autoloader(src: str):
    df = (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("cloudFiles.schemaLocation", f"{BRONZE_SCHEMA_BASE}/{src}")
        .option("cloudFiles.schemaEvolutionMode", "rescue")
        .load(f"{RAW_BASE}/{src}/")
    )

    # The supplied training CSVs do not contain a real source
    # update timestamp. We therefore create a deterministic
    # demo sequence from the file name:
    #
    # base file       -> 1
    # *_increment.csv -> 2
    # *_scd.csv       -> 3
    #
    # In production, use the source system's real updated_at /
    # event timestamp / CDC sequence instead.

    source_file = lower(col("_metadata.file_name"))
    source_sequence = when(source_file.contains("_scd"), lit(3)).when(source_file.contains("_increment"), lit(2)).otherwise(lit(1))
    modified_date = when(source_sequence == 1, to_timestamp(lit("2025-05-01 00:00:00"))).when(source_sequence == 2, to_timestamp(lit("2025-06-01 00:00:00"))).otherwise(to_timestamp(lit("2025-07-01 00:00:00")))

    df = df.withColumn("modifiedDate", modified_date)
    return df


# ============================================================
# BOOKINGS
# ============================================================

@dlt.table(
    name="bronze.bronze_bookings",
    comment="Raw booking data ingested incrementally using Auto Loader.",
    table_properties={"quality": "bronze"}
)
def bronze_bookings():
    df = bronze_autoloader("bookings")
    return df


# ============================================================
# FLIGHTS
# ============================================================

@dlt.table(
    name="bronze.bronze_flights",
    comment="Raw flight data ingested incrementally using Auto Loader.",
    table_properties={"quality": "bronze"}
)
def bronze_flights():
    df = bronze_autoloader("flights")
    return df


# ============================================================
# PASSENGERS
# ============================================================

@dlt.table(
    name="bronze.bronze_customers",
    comment="Raw passenger data ingested incrementally using Auto Loader.",
    table_properties={"quality": "bronze"}
)
def bronze_customers():
    df = bronze_autoloader("customers")
    return df


# ============================================================
# AIRPORTS
# ============================================================

@dlt.table(
    name="bronze.bronze_airports",
    comment="Raw airport data ingested incrementally using Auto Loader.",
    table_properties={"quality": "bronze"}
)
def bronze_airports():
    df = bronze_autoloader("airports")
    return df