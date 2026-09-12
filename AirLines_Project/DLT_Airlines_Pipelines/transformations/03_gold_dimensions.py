import dlt
from pyspark.sql.functions import col


# ============================================================
# GOLD DIMENSIONS
# SCD TYPE 2 - Full history
#
# Gold consumes the cleaned trans_* streams directly.
# Silver SCD1 contains only the latest state, so it must not
# be used as the source for Gold history.
# ============================================================


# ============================================================
# PASSENGERS
# ============================================================

dlt.create_streaming_table(
    name="gold.DimPassengers",
    comment="Passenger dimension with generated surrogate key and full SCD Type 2 history.",
    schema="""
        DimPassengersKey BIGINT GENERATED ALWAYS AS IDENTITY,
        passenger_id STRING,
        name STRING,
        gender STRING,
        nationality STRING,
        modifiedDate TIMESTAMP,
        __START_AT TIMESTAMP,
        __END_AT TIMESTAMP
    """
)

dlt.create_auto_cdc_flow(
    target="gold.DimPassengers",
    source="trans_passengers",
    keys=["passenger_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=2
)


# ============================================================
# FLIGHTS
# ============================================================

dlt.create_streaming_table(
    name="gold.DimFlights",
    comment="Flight dimension with generated surrogate key and full SCD Type 2 history.",
    schema="""
        DimFlightsKey BIGINT GENERATED ALWAYS AS IDENTITY,
        flight_id STRING,
        airline STRING,
        origin STRING,
        destination STRING,
        flight_date DATE,
        modifiedDate TIMESTAMP,
        __START_AT TIMESTAMP,
        __END_AT TIMESTAMP
    """
)

dlt.create_auto_cdc_flow(
    target="gold.DimFlights",
    source="trans_flights",
    keys=["flight_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=2
)


# ============================================================
# AIRPORTS
# ============================================================

dlt.create_streaming_table(
    name="gold.DimAirports",
    comment="Airport dimension with generated surrogate key and full SCD Type 2 history.",
    schema="""
        DimAirportsKey BIGINT GENERATED ALWAYS AS IDENTITY,
        airport_id STRING,
        airport_name STRING,
        city STRING,
        country STRING,
        modifiedDate TIMESTAMP,
        __START_AT TIMESTAMP,
        __END_AT TIMESTAMP
    """
)

dlt.create_auto_cdc_flow(
    target="gold.DimAirports",
    source="trans_airports",
    keys=["airport_id"],
    sequence_by=col("modifiedDate"),
    stored_as_scd_type=2
)