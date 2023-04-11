from prefect_gcp import GcpCredentials
from prefect_gcp.cloud_storage import GcsBucket


# replace this PLACEHOLDER dict with your own service account info
service_account_info = {
  "type": "service_account",
  "project_id": "PROJECT_ID",
  "private_key_id": "KEY_ID",
  "private_key": "-----BEGIN PRIVATE KEY-----\nPRIVATE_KEY\n-----END PRIVATE KEY-----\n",
  "client_email": "SERVICE_ACCOUNT_EMAIL",
  "client_id": "CLIENT_ID",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/SERVICE_ACCOUNT_EMAIL"
}

GcpCredentials(
    service_account_info=service_account_info
).save("BLOCK-NAME-PLACEHOLDER")



gcp_credentials = GcpCredentials.load("BLOCK-NAME-PLACEHOLDER")

gcs_bucket = GcsBucket(
        bucket="BUCKET-NAME-PLACEHOLDER",
        gcp_credentials=gcp_credentials
    )

bucket_block.save("BUCKET-NAME-PLACEHOLDER")