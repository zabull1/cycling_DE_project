import os
import zipfile
import requests
import pandas as pd
import datetime as dt
from io import BytesIO
from pathlib import Path
from random import randint
from prefect import task, flow
from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp.bigquery import BigQueryWarehouse
from prefect_dbt.cli.commands import DbtCoreOperation
from chardet.universaldetector import UniversalDetector


@task(log_prints=True, name="Read cycling data", retries=3)
def extract_from_web(url: str) -> bytes:
    """Read cycling data from web"""
    response = requests.get(url, timeout=4)
    if response.status_code == 200:
        return response.content
        print("Successfully fetched data from web.")
    else:
        print(f"ERROR: {response.status_code}")  



@task(log_prints=True, name="Unzip cycling data", retries=3)
def unzip_file(content: bytes, retries=3)-> list:
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



@task(log_prints=True, name= "save cycling data to Google Cloud Storage in parquet format", retries=3)
def save_as_parquet(unzipped_files: list, year: str) -> None:
    """save cycling data to Google Cloud Storage in parquet format"""

    gcs = GcsBucket.load('gcs-bucket')
    
    for index , content in enumerate(unzipped_files, start=1):

        storage_path_parquet = f'trips/parquet/{year}/journey_Data_Extract_{year}-{index:02}.parquet'
       
        #decode content encoding
        detector = UniversalDetector()
        detector.feed(content[1])
        detector.close()
        encoding = detector.result["encoding"]

        print(encoding)

        df = pd.read_csv(BytesIO(content[1]), encoding=encoding)

        df['Rental Id']= df['Rental Id'].astype("string")
        df['Bike Id']= df['Bike Id'].astype("string")
        df['End Date'] = pd.to_datetime(df['End Date'])
        df['EndStation Id']= df['EndStation Id'].astype("string")
        df['EndStation Name']= df['EndStation Name'].astype("string")
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['StartStation Id']= df['StartStation Id'].astype("string")
        df['StartStation Name']= df['StartStation Name'].astype("string") 
        df['Duration']= df['Duration'].astype("float")

        df['Duration'].fillna(0)
    

        df = df.rename(columns={ 
                    'Rental Id': 'rental_id',
                    'Bike Id': 'bike_id',
                    'End Date': 'end_date',
                    'Start Date': 'start_date',
                    'EndStation Id': 'endstation_id',
                    'EndStation Name': 'endstation_name',
                    'StartStation Id': 'startstation_id',
                    'StartStation Name': 'startstation_name',
                    'Duration': 'duration'
                    })

        df = df[
            [
            'rental_id',
            'bike_id',
            'end_date',
            'start_date',
            'endstation_id',
            'endstation_name',
            'startstation_id',
            'startstation_name',
            'duration'
            ] 
        ]            

            
        buffer = BytesIO()
        df.to_parquet(buffer, engine='auto', compression='snappy')
        buffer.seek(0)
        gcs.upload_from_file_object(buffer, storage_path_parquet)

        print(f"Successfully save {storage_path_parquet} to Google Cloud Storage.")




@task(name="Stage GCS to BQ")
def stage_bq():
    """Stage data in BigQuery"""

    bq_ext_tbl = f"""
            CREATE OR REPLACE EXTERNAL TABLE `balmy-component-381417.cycling_data_all.external_cycling_data`
            OPTIONS (
                format = 'PARQUET',
                uris = ['gs://dtc_data_lake_balmy-component-381417/trips/parquet/2014/journey_*.parquet']
            )
        """

    with BigQueryWarehouse.load("bq-block") as warehouse:
        operation = bq_ext_tbl
        warehouse.execute(operation)

    bq_part_tbl = f"""
            CREATE OR REPLACE TABLE `balmy-component-381417.cycling_data_all.external_cycling_data_partitioned_clustered`
            PARTITION BY DATE(start_date)
            CLUSTER BY startstation_id, endstation_name AS (
            SELECT * FROM `balmy-component-381417.cycling_data_all.external_cycling_data`);
        """

    with BigQueryWarehouse.load("bq-block") as warehouse:
        operation = bq_part_tbl
        warehouse.execute(operation)

@task(name="dbt modelling")
def dbt_model():
    """Run dbt models"""

    dbt_path = Path(f"../dbt/")

    dbt_run = DbtCoreOperation(
                    commands=["dbt deps", 
                              "dbt seed -t prod", 
                              "dbt build -t prod"],
                    project_dir=dbt_path,
                    profiles_dir=dbt_path,
    )

    dbt_run.run()

    return


@flow(name='Save from web to Cloud Storage to bigQuery')
def web_to_gcs_to_bq(year : int) -> None:
    """Orchestrates the flow of cycling data from web to BigQuery via Google Cloud Storage"""

    url = f"https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-{year}.zip"
    
    content = extract_from_web(url)
    unzipped_content = unzip_file(content)
    save_as_parquet(unzipped_content, year)


    stage_bq()

    dbt_model()

    print("Succesfully orchestrated cycling data from web to BiqQuery  via Google Cloud Storage")

if __name__ == "__main__":
 year = 2014
 web_to_gcs_to_bq(year)