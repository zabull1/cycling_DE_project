from pathlib import Path
import pandas as pd
import pandas_gbq
import io
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials
from prefect_gcp.bigquery import bigquery_create_table
from google.cloud.bigquery import SchemaField
from chardet.universaldetector import UniversalDetector
from prefect_gcp.bigquery import bigquery_load_file

@task(retries=3)
def extract_from_gcs(year: str) -> Path:
    """Download trip data from GCS"""
    gcs_path = Path(f"trips/{year}/raw_/*.csv")
    gcs_block = GcsBucket.load("gcs-bucket")
    contents = gcs_block.list_blobs(f"trips/{year}/")
    return contents

@task
def get_dataframe(storage_path: str) -> pd.DataFrame:
    gcs = GcsBucket.load('gcs-bucket')
    temp_file = io.BytesIO()
    gcs.download_object_to_file_object(
        from_path=storage_path, 
        to_file_object=temp_file
    )

    temp_file.seek(0)
    df = pd.read_parquet((temp_file))
  
    return df    



@task()
def transform(df) -> pd.DataFrame:
    """Data cleaning example"""

    df['Rental Id']= df['Rental Id'].astype("STRING")
    df['Bike Id']= df['Bike Id'].astype("STRING")
    df['End Date'] = pd.to_datetime(df['End Date'])
    df['EndStation Id']= df['EndStation Id'].astype("STRING")
    df['EndStation Name']= df['EndStation Name'].astype("STRING")
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['StartStation Id']= df['StartStation Id'].astype("STRING")
    df['StartStation Name']= df['StartStation Name'].astype("STRING") 
    df['Duration']= df['Duration'].astype("int")

      df['Rental Id']= df['Rental Id'].astype("string")
        df['Bike Id']= df['Bike Id'].astype("string")
        df['End Date'] = pd.to_datetime(df['End Date'])
        df['EndStation Id']= df['EndStation Id'].astype("string")
        df['EndStation Name']= df['EndStation Name'].astype("string")
        df['Start Date'] = pd.to_datetime(df['Start Date'])
        df['StartStation Id']= df['StartStation Id'].astype("string")
        df['StartStation Name']= df['StartStation Name'].astype("string") 
        df['Duration']= df['Duration'].astype("int")

    df = df[df['Duration'] > 1]
    
    df = df.astype('str')

    # dataframes = []
    # #for content in contents[]:
    # # df = pd.read_csv(io.STRINGIO(contents[1].download_as_STRING().decode('utf-8')))
    # df = pd.read_csv(io.STRINGIO(contents[0].download_as_text(encoding='ISO-8859-1')))

    # df = df.astype(str)
    # df.fillna(" ", inplace=True)
    #df["EndStation Name"].dropna()
    # ,dtype={
    #         'Rental Id': 'str',
    #         'Duration': 'int',
    #         'Bike Id': 'str',
    #         'End Date': 'str',
    #         'EndStation Id': 'str',
    #         'EndStation Name': 'str',
    #         'Start Date': 'str',
    #         'StartStation Id': 'str',
    #         'StartStation Name': 'str'
    #         }, parse_dates=['Start Date','End Date' ])
    # df.info()

    df = df.rename(columns={ 'Rental Id': 'Rental_Id',
                'Bike Id': 'Bike_Id',
                'End Date': 'End_Date',
                'Start Date': 'Start_Date',
                'EndStation Id': 'EndStation_Id',
                'EndStation Name': 'EndStation_Name',
                'StartStation Id': 'StartStation_Id',
                'StartStation Name': 'StartStation_Name',
                })
    
    # df['Rental Id']= df['Rental Id'].astype("object")
    # df['Bike Id']= df['Bike Id'].astype("object")
    # # df['End Date'] = pd.to_datetime(df['End Date'])
    # df['End Date'] = df['End Date'].astype('object')
    # df['Start Date'] =   df['Start Date'].astype('object')
    # df['EndStation Id']= df['EndStation Id'].astype("object")
    # df['EndStation Name']= df['EndStation Name'].astype("object")
    # # df['Start Date'] = pd.to_datetime(df['Start Date'])
    # df['StartStation Id']= df['StartStation Id'].astype("object")
    # df['StartStation Name']= df['StartStation Name'].astype("object") 
    # df['Duration']= df['Duration'].astype("object") 

    # df['Rental Id'].dropna()
    # df['Rental Id']= df['Rental Id'].astype("object")
    # df['Bike Id']= df['Bike Id'].astype("object")
    # # df['End Date'] = pd.to_datetime(df['End Date'])
    # df['End Date'] = df['End Date'].astype('object')
    # df['Start Date'] =   df['Start Date'].astype('object')
    # df['EndStation Id']= df['EndStation Id'].astype("object")
    # df['EndStation Name']= df['EndStation Name'].astype("object")
    # # df['Start Date'] = pd.to_datetime(df['Start Date'])
    # df['StartStation Id']= df['StartStation Id'].astype("object")
    # df['StartStation Name']= df['StartStation Name'].astype("object") 
    # df['Duration']= df['Duration'].astype("object") 

    # df['Rental Id']= df['Rental Id'].astype("object")
    # df['Bike Id']= df['Bike Id'].astype("object")
    # df['End Date'] = pd.to_datetime(df['End Date'])
    # df['EndStation Id']= df['EndStation Id'].astype("object")
    # df['EndStation Name']= df['EndStation Name'].astype("object")
    # df['Start Date'] = pd.to_datetime(df['Start Date'])
    # df['StartStation Id']= df['StartStation Id'].astype("object")
    # df['StartStation Name']= df['StartStation Name'].astype("object") 
    # print(df.isna().sum())
    # dataframes.append(df)
    return df


@flow
def bigquery_create_table_flow():
    # gcp_credentials = GcpCredentials(project="project")
    gcp_credentials_block = GcpCredentials.load("gcs-credentials")
    # schema = [
    #     SchemaField('Rental Id', field_type="INTEGER"),
    #     SchemaField('Bike Id', field_type="INTEGER"),
    #     SchemaField('End Date', field_type="TIMESTAMP", mode="REQUIRED"),
    #     SchemaField('EndStation Id', field_type="INTEGER", mode="REQUIRED"),
    #     SchemaField('EndStation Name', field_type="STRING", mode="REQUIRED"),
    #     SchemaField('Start Date', field_type="TIMESTAMP", mode="REQUIRED"),
    #     SchemaField('StartStation Id', field_type="INTEGER", mode="REQUIRED"),
    #     SchemaField('StartStation Name', field_type="STRING"),
    #     SchemaField('Duration', field_type="INTEGER", mode="REQUIRED"),
    #     # SchemaField('Bike Id', field_type="STRING", mode="REQUIRED"),
    #     # SchemaField('Bike Id', field_type="STRING", mode="REQUIRED"),
    # ]
    schema = [
        SchemaField('Rental_Id', field_type="STRING"),
        SchemaField('Bike_Id', field_type="STRING"),
        SchemaField('End_Date', field_type="STRING"),
        SchemaField('EndStation_Id', field_type="STRING"),
        SchemaField('EndStation_Name', field_type="STRING"),
        SchemaField('Start_Date', field_type="STRING"),
        SchemaField('StartStation_Id', field_type="STRING"),
        SchemaField('StartStation_Name', field_type="STRING"),
        SchemaField('Duration', field_type="STRING" )
    ]
    result = bigquery_create_table(
        dataset="cycling_data_all",
        table="data",
        schema= schema,
        gcp_credentials=gcp_credentials_block
    )
    return result

@flow()
def example_bigquery_load_file_flow(df):
   gcp_credentials_block = GcpCredentials.load("gcs-credentials")
   result = bigquery_load_file(
        dataset="cycling_data_all",
        table="test_table",
        path=df,
         schema= schema,
        gcp_credentials=gcp_credentials_block,
       
    )
   return result

# @task(log_prints=True, retries=3)
# def save_as_raw(unzipped_files: list, year: str) -> None:
#     gcs = GcsBucket.load('gcs-bucket')

#     for index, content in enumerate(unzipped_files, start=1):
#         gcs.upload_from_file_object(BytesIO(content[1]), f'trips/raw/{year}/journey_Data_Extract-{index:02}.csv')

@task()
def write_bq(df) -> None:
    """Write DataFrame to BiqQuery"""

    gcp_credentials_block = GcpCredentials.load("gcs-credentials")

    # print(df.head(10))
    # print(df.dtypes)
    # for df in dataframes:
   
    df.to_gbq(
            destination_table="cycling_data_all.data",
            project_id="balmy-component-381417",
            credentials=gcp_credentials_block.get_credentials_from_service_account(),
            chunksize=10000,
            if_exists="append",
        )

    # from google.cloud import bigquery
    # import pandas as pd

    # client = bigquery.Client()

    # define project, dataset, and table_name variables
    # project, dataset, table_name = "balmy-component-381417", "cycling_data_all", "cycling"
    # table_id = f"{project}.{dataset}.{table_name}"

    # job_config = bigquery.job.LoadJobConfig()

    # # set write_disposition parameter as WRITE_APPEND for appending to table
    # job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND

    # job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

    # job.result()  # Wait for the job to complete.

    # table = client.get_table(table_id)  # Make an API request.
    # print(
    #     f"Loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}"
    # )


@flow()
def etl_gcs_to_bq():
    bigquery_create_table_flow()
    # """Main ETL flow to load data into Big Query"""
  
    #years = [(2012, 18 ),(2013, 14 ), (2014, 20)]
  

    # for year, num in years:
    #     for index in list(range(1,num+1)): 
    #         storage_path = f'trips/parquet/{year}/journey_Data_Extract-{index:02}.parquet'
    #         df = get_dataframe(storage_path)
    #         transformed_df = transform(df)
    #         write_bq(transformed_df)
    #         # example_bigquery_load_file_flow(df)

    year = 2012
    index = 9
    storage_path = f'trips/parquet/{year}/journey_Data_Extract-{index:02}.parquet'
    df = get_dataframe(storage_path)
    transformed_df = transform(df)

    write_bq(transformed_df)
    # example_bigquery_load_file_flow(df)
   


if __name__ == "__main__":
 
    etl_gcs_to_bq()