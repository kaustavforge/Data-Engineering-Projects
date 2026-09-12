# Databricks notebook source
# MAGIC %sql
# MAGIC CREATE CATALOG IF NOT EXISTS airlines_project;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA IF NOT EXISTS airlines_project.raw;
# MAGIC CREATE SCHEMA IF NOT EXISTS airlines_project.bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS airlines_project.silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS airlines_project.gold;

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE VOLUME IF NOT EXISTS airlines_project.raw.rawvolume;
# MAGIC CREATE VOLUME IF NOT EXISTS airlines_project.bronze.bronzevolume;
# MAGIC CREATE VOLUME IF NOT EXISTS airlines_project.silver.silvervolume;
# MAGIC CREATE VOLUME IF NOT EXISTS airlines_project.gold.goldvolume;

# COMMAND ----------

landing_zones = [
    '/Volumes/airlines_project/raw/rawvolume/rawdata/bookings',
    '/Volumes/airlines_project/raw/rawvolume/rawdata/flights',
    '/Volumes/airlines_project/raw/rawvolume/rawdata/customers',
    '/Volumes/airlines_project/raw/rawvolume/rawdata/airports'
]

for path in landing_zones:
    dbutils.fs.mkdirs(path)

# COMMAND ----------



# COMMAND ----------



# COMMAND ----------

