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
from chardet.universaldetector import UniversalDetector

@task()
def extract_from_web(url: str) -> bytes:
    r = requests.get(url)
    return r.content

@task()
def unzip_file(content: bytes, retries=3)-> list:
    zipfile_obj = zipfile.ZipFile(BytesIO(content))
    unzipped_files = []
    for file_name in zipfile_obj.namelist():
        # Extract each file in memory
        file_content = zipfile_obj.read(file_name)
        unzipped_files.append((file_name, file_content))
    return unzipped_files    

@task(log_prints=True, retries=3)
def save_as_raw(unzipped_files: list, year: str) -> None:
    gcs = GcsBucket.load('gcs-bucket')

    for index, content in enumerate(unzipped_files, start=1):
        gcs.upload_from_file_object(BytesIO(content[1]), f'trips/raw/{year}/journey_Data_Extract-{index:02}.csv')
        

@task(log_prints=True, retries=3)
def save_as_parquet(unzipped_files: list, year: str) -> None:
    gcs = GcsBucket.load('gcs-bucket')
    
    for index , content in enumerate(unzipped_files, start=1):
        storage_path_parquet = f'trips/parquet_/{year}/journey_Data_Extract_{year}-{index:02}.parquet'
       
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
        df['Duration']= df['Duration'].astype("int")
        
        
        buffer = BytesIO()
        df.to_parquet(buffer, engine='auto', compression='snappy')
        buffer.seek(0)
        gcs.upload_from_file_object(buffer, storage_path_parquet)
  



@flow(name='Save from web to Cloud Storage')
def load_to_gcs(years : list) -> None:
    
    for year in years:
        url = f"https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-{year}.zip"

        content = extract_from_web(url)
        unzipped_content = unzip_file(content)
        # save_as_raw(unzipped_content, year)
        save_as_parquet(unzipped_content, year)
 

if __name__ == "__main__":
 years = [2012,2013,2014]
 load_to_gcs(years)
 







#@task(log_prints=True, name="fetch data", retries=3)
# def fetch(url: str) -> pd.DataFrame:
#     """Fetches the API and returns the latest card data as a pandas dataframe"""
#     response = requests.get(url, timeout=5)
#     if response.status_code == 200:
#         json = response.content
       
#         # df = pd.read_json(json)
#         # print("Successfully fetched data from API.")
#         # return df, update_ts
#         return json
#     else:
#         print(f"[ERROR] {response.status_code}.")

# def fetch(url: str) -> pd.DataFrame:
#     """Fetches the API and returns the latest card data as a pandas dataframe"""
#     df = pd.read_csv(url)
#     print("Successfully fetched data from API.")
#     return df
       
        
    

# @task()
# def write_gcs(path: Path) -> None:
#     """Upload local parquet file to GCS"""
#     gcs_block = GcsBucket.load("zoom-gcs")
#     gcs_block.upload_from_path(from_path=path, to_path=path)
#     return

# @flow(log_prints=True, name="[Magic: The Gathering] API to BigQuery")
# # def api_to_bq_orchestration(
# #     dataset: str, download_parquet: bool = False, update_prod_table: bool = True
# # ) -> None:
# def api_to_bq_orchestration() -> None:
#     #url = "https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-2014.zip"
#     url = "https://cycling.data.tfl.gov.uk/usage-stats/97JourneyDataExtract14Feb2018-20Feb2018.csv"
#     df = fetch(url)
#     write_gcs(from_path=file, to_path="A")

#       df = fetch(dataset_url)
#     df_clean = clean(df)
#     path = write_local(df_clean, color, dataset_file)
#     # write_gcs(path)







# @task(log_prints=True)
# def save_as_parquet(content: bytes, url: str, storage_path_parquet: str) -> pd.DataFrame:
#     gcs = GcsBucket.load('gcs-creds')
#     if url.endswith('.csv'):
#         df = pd.read_csv(BytesIO(content))
#     if url.endswith('.csv.gz'):
#         df = pd.read_csv(BytesIO(content), compression='gzip')
#     df.columns = [c.lower() for c in df.columns]
#     print(df.head())
#     print('Rows loaded:', len(df))
#     buffer = BytesIO()
#     df.to_parquet(buffer, engine='auto', compression='snappy')
#     buffer.seek(0)
#     gcs.upload_from_file_object(buffer, storage_path_parquet)

# if __name__ == '__main__':
#     color = 'yellow'
#     year = 2021
#     month = 1
    
#     load_to_gcs(color, year, month)


# # Unzip the file in memory
# zipfile_obj = zipfile.ZipFile(io.BytesIO(content))
# unzipped_files = []
# for file_name in zipfile_obj.namelist():
#     # Extract each file in memory
#     file_content = zipfile_obj.read(file_name)
#     unzipped_files.append((file_name, file_content))

# Upload the unzipped files to GCS
# for file_name, file_content in unzipped_files:
#     new_blob = bucket.blob(file_name)
#     new_blob.upload_from_string(file_content)

    #url = "https://cycling.data.tfl.gov.uk/usage-stats/97JourneyDataExtract14Feb2018-20Feb2018.csv"
    #storage_path = f'trips/zip/cyclehireusagestats-2014.zip'
    #storage_path_parquet = f'trips/parquet/{color}_tripdata_{year}-{month:02}.parquet'

   #save_as_parquet(content, url, storage_path_parquet)