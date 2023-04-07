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

        storage_path_parquet = f'trips/parquet_/{year}/journey_Data_Extract_{year}-{index:02}.parquet'
       
        #decode content encoding
        detector = UniversalDetector()
        detector.feed(content[1])
        detector.close()
        encoding = detector.result["encoding"]

        print(encoding)

        df = pd.read_csv(BytesIO(content[1]), encoding=encoding)

        df =df.astype(str)
        
        buffer = BytesIO()
        df.to_parquet(buffer, engine='auto', compression='snappy')
        buffer.seek(0)
        gcs.upload_from_file_object(buffer, storage_path_parquet)

        print(f"Successfully save {storage_path_parquet} to Google Cloud Storage.")


@task(log_prints=True, name= "Get parquet from Google Cloud Storage", retries=3)
def get_dataframe(storage_path: str) -> pd.DataFrame:
    """Gets the parquet file from GCS and converts it to a dataframe"""
    gcs = GcsBucket.load('gcs-bucket')
    temp_file = BytesIO()
    gcs.download_object_to_file_object(
        from_path=storage_path, 
        to_file_object=temp_file
    )

    temp_file.seek(0)
    df = pd.read_parquet((temp_file))
  
    return df  

@task(log_prints =True, name= "enforce column names and datatypes")
def transform(df) -> pd.DataFrame:
    """Data cleaning: enforcing column names and datatypes"""

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
                'Rental Id': 'Rental_Id',
                'Bike Id': 'Bike_Id',
                'End Date': 'End_Date',
                'Start Date': 'Start_Date',
                'EndStation Id': 'EndStation_Id',
                'EndStation Name': 'EndStation_Name',
                'StartStation Id': 'StartStation_Id',
                'StartStation Name': 'StartStation_Name',
                })

    df = df[
        [
        'Rental_Id',
        'Bike_Id',
        'End_Date',
        'Start_Date',
        'EndStation_Id',
        'EndStation_Name',
        'StartStation_Id',
        'StartStation_Name',
        'Duration'
        ] 
    ]            

    print("Successfully enforced column names and data types.")
    return df




@task(log_prints=True, name="Write to BigQuery")
def write_bq(df) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("gcs-credentials")
   
    df.to_gbq(
            destination_table="cycling_data_all.test",
            project_id="balmy-component-381417",
            credentials=gcp_credentials_block.get_credentials_from_service_account(),
            chunksize=10000,
            if_exists="append",
        )

    print("Succesfully uploaded data to BiqQuery")


@flow(name='Save from web to Cloud Storage to bigQuery')
def web_to_gcs_to_bq() -> None:
    """Orchestrates the flow of cycling data from web to BigQuery via Google Cloud Storage"""
    year = 2014
    num = 20  #number of files in the directory
    url = f"https://cycling.data.tfl.gov.uk/usage-stats/cyclehireusagestats-{year}.zip"
    
    # content = extract_from_web(url)
    # unzipped_content = unzip_file(content)
    # save_as_parquet(unzipped_content, year)

    for index in list(range(1,num+1)):
        storage_path = f'trips/parquet/{year}/journey_Data_Extract-{index:02}.parquet'
        df = get_dataframe(storage_path)
        transformed_df = transform(df)
        write_bq(transformed_df)

    print("Succesfully orchestrated cycling data from web to BiqQuery  via Google Cloud Storage")

if __name__ == "__main__":
 web_to_gcs_to_bq()