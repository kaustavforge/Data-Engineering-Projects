import dlt
from pyspark.sql.functions import col, count, sum as spark_sum, avg


# ============================================================
# GOLD FACT
#
# Grain:
#   ONE ROW = ONE BOOKING
#
# Fact columns:
#   booking_id
#   DimPassengersKey
#   DimFlightsKey
#   DimAirportsKey
#   amount
#   booking_date
#
# booking_id is the business key because it identifies the
# individual booking/fact row.
# ============================================================


fact_rules = {
    "passenger_dimension_found": "DimPassengersKey IS NOT NULL",
    "flight_dimension_found": "DimFlightsKey IS NOT NULL",
    "airport_dimension_found": "DimAirportsKey IS NOT NULL"
}


@dlt.table(
    name="gold.FactBookings",
    comment="Booking fact table at one-row-per-booking grain.",
    table_properties={"quality": "gold"}
)
@dlt.expect_all_or_drop(fact_rules)
def fact_bookings():

    bookings = spark.readStream.table("silver.silver_bookings").alias("b")
    passengers = spark.read.table("gold.DimPassengers").filter(col("__END_AT").isNull()).alias("p")
    flights = spark.read.table("gold.DimFlights").filter(col("__END_AT").isNull()).alias("f")
    airports = spark.read.table("gold.DimAirports").filter(col("__END_AT").isNull()).alias("a")

    df = bookings.join(passengers, col("b.passenger_id") == col("p.passenger_id"), "left").join(flights, col("b.flight_id") == col("f.flight_id"), "left").join(airports, col("b.airport_id") == col("a.airport_id"), "left")

    df = df.select(
        col("b.booking_id"),
        col("p.DimPassengersKey"),
        col("f.DimFlightsKey"),
        col("a.DimAirportsKey"),
        col("b.amount"),
        col("b.booking_date")
    )

    return df


# ============================================================
# BUSINESS MATERIALIZED VIEW
#
# With the legacy @dlt API, a batch @dlt.table is used for the
# materialized/derived result.
# ============================================================

@dlt.table(
    name="gold.daily_airline_revenue",
    comment="Daily booking count, revenue, and average booking amount by airline.",
    table_properties={"quality": "gold"}
)
def daily_airline_revenue():

    fact = spark.read.table("gold.FactBookings").alias("f")
    flights = spark.read.table("gold.DimFlights").filter(col("__END_AT").isNull()).select("DimFlightsKey", "airline").alias("d")

    df = fact.join(flights, col("f.DimFlightsKey") == col("d.DimFlightsKey"), "left")
    df = df.groupBy(col("f.booking_date"), col("d.airline")).agg(count("*").alias("total_bookings"), spark_sum(col("f.amount")).alias("total_revenue"), avg(col("f.amount")).alias("average_booking_amount"))

    return df