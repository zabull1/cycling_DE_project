from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date
from pyspark.sql.types import StringType, FloatType
import requests
import zipfile
from io import BytesIO
from chardet.universaldetector import UniversalDetector

spark = SparkSession.builder.appName("CyclingDataPipeline").getOrCreate()

# Step 1: Extract cycling data from the web
def extract_from_web(url):
    response = requests.get(url, timeout=4)
    if response.status_code == 200:
        return response.content

url = "https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-2014.zip"
content = extract_from_web(url)

# Step 2: Unzip cycling data
def unzip_file(content):
    zipfile_obj = zipfile.ZipFile(BytesIO(content))
    unzipped_files = []
    for file_name in zipfile_obj.namelist():
        file_content = zipfile_obj.read(file_name)
        unzipped_files.append((file_name, file_content))
    return unzipped_files

unzipped_content = unzip_file(content)

# Step 3: Save cycling data to Google Cloud Storage in Parquet format
def save_as_parquet(unzipped_files, year):
    for index, content in enumerate(unzipped_files, start=1):
        storage_path_parquet = f'gs://your-bucket-name/trips/parquet_test_1/{year}/journey_Data_Extract_{year}-{index:02}.parquet'
        encoding = detect_encoding(content[1])
        df = spark.read.csv(BytesIO(content[1]), header=True, encoding=encoding)
        df = df.withColumn("Duration", df["Duration"].cast(FloatType()))
        df = df.withColumn("End Date", to_date(df["End Date"]))
        df = df.withColumn("Start Date", to_date(df["Start Date"]))
        df = df.withColumnRenamed("Rental Id", "rental_id") \
            .withColumnRenamed("Bike Id", "bike_id") \
            .withColumnRenamed("End Date", "end_date") \
            .withColumnRenamed("Start Date", "start_date") \
            .withColumnRenamed("EndStation Id", "endstation_id") \
            .withColumnRenamed("EndStation Name", "endstation_name") \
            .withColumnRenamed("StartStation Id", "startstation_id") \
            .withColumnRenamed("StartStation Name", "startstation_name") \
            .withColumnRenamed("Duration", "duration")
        df.write.parquet(storage_path_parquet, mode="overwrite")

year = 2014
save_as_parquet(unzipped_content, year)

# Step 4: Stage data in BigQuery
def stage_bq():
    bq_ext_tbl = f"""
        CREATE OR REPLACE EXTERNAL TABLE `project.dataset.external_cycling_data`
        OPTIONS (
            format = 'parquet',
            path = 'gs://your-bucket-name/trips/parquet_test_1/2014/'
        )
    """
    spark.sql(bq_ext_tbl)

stage_bq()

# Step 5: Run dbt models
def dbt_model():
    dbt_path = Path("../dbt/")
    subprocess.run(["dbt", "deps"], cwd=dbt_path)
    subprocess.run(["dbt", "seed", "-t", "prod"], cwd=dbt_path)
    subprocess.run(["dbt", "run", "-t", "prod"], cwd=dbt_path)

dbt_model()

spark.stop




import os
import zipfile
import requests
import pandas as pd
import datetime as dt
from io import BytesIO
from pathlib import Path
from random import randint
from prefect import task, Flow
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_dbt.cli.commands import DbtCoreOperation
from chardet.universaldetector import UniversalDetector
from pyspark.sql import SparkSession

@task(log_stdout=True, name="Read cycling data")
def extract_from_web(url: str) -> bytes:
    """Read cycling data from web"""
    response = requests.get(url, timeout=4)
    if response.status_code == 200:
        return response.content
        print("Successfully fetched data from web.")
    else:
        print(f"ERROR: {response.status_code}")  

@task(log_stdout=True, name="Unzip cycling data")
def unzip_file(content: bytes) -> list:
    """Unzip cycling data"""
    print("unzipping........")
    zipfile_obj = zipfile.ZipFile(BytesIO(content))
    unzipped_files = []
    for file_name in zipfile_obj.namelist():
        # Extract each file in memory
        file_content = zipfile_obj.read(file_name)
        unzipped_files.append((file_name, file_content))
    print("Successfully unzip data.")
    return unzipped_files    

@task(log_stdout=True, name="Save cycling data to Google Cloud Storage in parquet format")
def save_as_parquet(spark, unzipped_files: list, year: str, path: str) -> None:
    """Save cycling data to Google Cloud Storage in parquet format"""

    for index, content in enumerate(unzipped_files, start=1):
        storage_path_parquet = f'{path}/{year}/journey_Data_Extract_{year}-{index:02}.parquet'
        
        # Decode content encoding
        detector = UniversalDetector()
        detector.feed(content[1])
        detector.close()
        encoding = detector.result["encoding"]

        df = spark.read.csv(BytesIO(content[1]), header=True, encoding=encoding)

        # Perform necessary transformations on the DataFrame
        
        df.write.parquet(storage_path_parquet, mode="overwrite")
        print(f"Successfully saved {storage_path_parquet} to Google Cloud Storage.")

@task(log_stdout=True, name="Stage GCS to BQ")
def stage_bq():
    """Stage data in BigQuery"""

    bq_ext_tbl = f"""
        CREATE OR REPLACE EXTERNAL TABLE `balmy-component-381417.cycling_data_all.external_cycling_data`
        OPTIONS (
            format = 'PARQUET',
            uris = ['gs://dtc_data_lake_balmy-component-381417/trips/parquet_test_1/2014/journey_*.parquet']
        )
    """

    with BigQueryWarehouse.load("bq-block") as warehouse:
        operation = bq_ext_tbl
        warehouse.execute(operation)

    bq_part_tbl = f"""
        CREATE OR REPLACE TABLE `balmy-component-381417.cycling_data_all.external_cycling_data_partitioned_clustered`
        PARTITION BY DATE(start_date)
        CLUSTER BY startstation_id, endstation_name AS (
        SELECT *
            FROM balmy-component-381417.cycling_data_all.external_cycling_data);
            """



    with BigQueryWarehouse.load("bq-block") as warehouse:
    operation = bq_part_tbl
    warehouse.execute(operation)

    @task(log_stdout=True, name="Dbt modelling")
    def dbt_model():
"""Run dbt models"""

dbt_path = Path(f"../dbt/")

dbt_run = DbtCoreOperation(
    commands=["dbt deps", "dbt seed -t prod", "dbt build -t prod"],
    project_dir=dbt_path,
    profiles_dir=dbt_path,
)

dbt_run.run()


@task(log_stdout=True, name="Orchestrate cycling data pipeline")
def orchestrate_pipeline(year: str, url: str, path: str):
"""Orchestrates the flow of cycling data from web to BigQuery via Google Cloud Storage"""

scss
Copy code
content = extract_from_web(url)
unzipped_content = unzip_file(content)

spark = SparkSession.builder.getOrCreate()

save_as_parquet(spark, unzipped_content, year, path)
stage_bq()
dbt_model()

print("Successfully orchestrated cycling data from web to BigQuery via Google Cloud Storage")
Define the flow

with Flow("Cycling Data Pipeline") as flow:
year = "2014"
url = "https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-2014.zip"
path = "gs://dtc_data_lake_balmy-component-381417/trips/parquet_test_1"

scss
Copy code
orchestrate_pipeline(year, url, path)
Run the flow

flow.run()