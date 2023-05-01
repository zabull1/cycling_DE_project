from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket
from prefect_dbt.cli import BigQueryTargetConfigs, DbtCliProfile, DbtCoreOperation

# This is an alternative to creating GCP blocks in the UI

# Insert your own service_account_file path or service_account_info dictionary from the json file
# IMPORTANT - do not store credentials in a publicly available repository!


credentials_block = GcpCredentials(
    service_account_info={}  enter your credentials info here
)

credentials_block.save("gcs-credentials", overwrite=True)


bucket_block = GcsBucket(
    gcp_credentials=GcpCredentials.load("gcs-credentials"),
    bucket= "gcs-bucket",
)

bucket_block.save("gcs-bucket", overwrite=True)


credentials = GcpCredentials.load("gcs-credentials")
target_configs = BigQueryTargetConfigs(
    schema="cycling_data_all", 
    credentials=credentials,
)
target_configs.save("bq-block", overwrite=True)

dbt_cli_profile = DbtCliProfile(
    name="cycling-dbt-cli-profile",
    target="dev",
    target_configs=target_configs,
)
dbt_cli_profile.save("cycling-dbt-cli-profile", overwrite=True)
