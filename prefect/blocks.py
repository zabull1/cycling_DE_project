from prefect_gcp import GcpCredentials, BigQueryWarehouse
from prefect_gcp.cloud_storage import GcsBucket
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation
from pathlib import Path


# This is an alternative to creating GCP blocks in the UI

# Insert your own service_account_file path or service_account_info dictionary from the json file
# IMPORTANT - do not store credentials in a publicly available repository!

bucket_name = "" #insert your gcp bucket name here
service_account_file = Path("~/.google/credentials/google_credentials.json")

credentials_block = GcpCredentials(service_account_file= service_account_file)

credentials_block.save("gcs-credentials", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load("gcs-credentials"),
    bucket= bucket_name,
)

bucket_block.save("gcs-bucket", overwrite=True)

gcp_credentials = GcpCredentials.load("gcs-credentials")

# Creating BQ Bucket Block

BigQueryWarehouse(gcp_credentials=gcp_credentials).save("bq-block", overwrite=True)

credentials = GcpCredentials.load("gcs-credentials")
target_configs = BigQueryTargetConfigs(
    schema="cycling_data_all", 
    credentials=credentials,
)
target_configs.save("bq-block-dbt", overwrite=True)

dbt_cli_profile = DbtCliProfile(
    name="default",
    target="dev",
    target_configs=target_configs,
)
dbt_cli_profile.save("cycling-dbt-cli-profile", overwrite=True)
