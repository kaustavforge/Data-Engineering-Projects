import dlt
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import DecimalType


# ============================================================
# SILVER LAYER
# Cleaning + Data Quality + SCD Type 1
# ============================================================


# ============================================================
# BOOKINGS
# ============================================================

booking_rules = {
    "valid_booking_id": "booking_id IS NOT NULL",
    "valid_passenger_id": "passenger_id IS NOT NULL",
    "valid_flight_id": "flight_id IS NOT NULL",
    "valid_airport_id": "airport_id IS NOT NULL",
    "valid_amount": "amount IS NOT NULL AND amount >= 0",
    "valid_booking_date": "booking_date IS NOT NULL"
}


@dlt.view(
    name="trans_bookings",
    comment="Cleaned booking stream."
)
def trans_bookings():
    df = spark.readStream.table("bronze.bronze_bookings")
    df = df.withColumn("amount", col("amount").cast(DecimalType(18, 2))).withColumn("booking_date", to_date(col("booking_date"))).drop("_rescued_data")
    return df


@dlt.table(
    name="silver.silver_bookings",
    comment="Validated and standardized booking data.",
    table_properties={"quality": "silver"}
)
@dlt.expect_all_or_drop(booking_rules)
def silver_bookings():
    df = spark.readStream.table("trans_bookings")
    return df


# ============================================================
# FLIGHTS - SCD TYPE 1
# ============================================================

@dlt.view(
    name="trans_flights",
    comment="Clean flight change stream used by Silver SCD1 and Gold SCD2."
)
def trans_flights():
    df = spark.readStream.table("bronze.bronze_flights")
    df = df.withColumn("flight_date", to_date(col("flight_date"))).drop("_rescued_data")
    return df


dlt.create_streaming_table(
    name="silver.silver_flights",
    comment="Current/latest flight state using SCD Type 1.",
    table_properties={"quality": "silver"}
)

dlt.create_auto_cdc_flow(
    target="silver.silver_flights",
    source="trans_flights",
    keys=["flight_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=1
)


# ============================================================
# PASSENGERS - SCD TYPE 1
# ============================================================

@dlt.view(
    name="trans_passengers",
    comment="Clean passenger change stream used by Silver SCD1 and Gold SCD2."
)
def trans_passengers():
    df = spark.readStream.table("bronze.bronze_customers")
    df = df.drop("_rescued_data")
    return df


dlt.create_streaming_table(
    name="silver.silver_passengers",
    comment="Current/latest passenger state using SCD Type 1.",
    table_properties={"quality": "silver"}
)

dlt.create_auto_cdc_flow(
    target="silver.silver_passengers",
    source="trans_passengers",
    keys=["passenger_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=1
)


# ============================================================
# AIRPORTS - SCD TYPE 1
# ============================================================

@dlt.view(
    name="trans_airports",
    comment="Clean airport change stream used by Silver SCD1 and Gold SCD2."
)
def trans_airports():
    df = spark.readStream.table("bronze.bronze_airports")
    df = df.drop("_rescued_data")
    return df


dlt.create_streaming_table(
    name="silver.silver_airports",
    comment="Current/latest airport state using SCD Type 1.",
    table_properties={"quality": "silver"}
)

dlt.create_auto_cdc_flow(
    target="silver.silver_airports",
    source="trans_airports",
    keys=["airport_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=1
)