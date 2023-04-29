from prefect.deployments import Deployment

from web_to_gcs_to_bq import web_to_gcs_to_bq


# Deployment for Loading data to GCS from the web
local_dep = Deployment.build_from_flow(
    flow = web_to_gcs_to_bq, 
    name='Deploy3', 
    # work_queue_name="development", 
    entrypoint="web_to_gcs_to_bq.py:web_to_gcs_to_bq", 
    parameters={"year": 2014})

# , schedule =(CronSchedule(cron="5 0 1 * *", timezone="America/Chicago")

if __name__=="__main__":
    """Builds the Deployment and Applies the Deployment by parameterizing the flow"""
    local_dep.apply()

# Optional CLI
# Build & Schedule & Apply in 1 step
# `prefect deployment build ingest.py:etl_parent_flow -n "web_to_gcp_etl" --cron "5 0 1 * ?" --timezone "UTC" -a`

# Run this script & and deploy the flow on Prefect Cloud(make sure you are logged into prefect cloud)
# python flows/deploy_ingest.py
# Check the UI if deployment is available
# Start the prefect agent in detaches mode
# screen -A -m -d -S prefectagent prefect agent start --work-queue "development"
# Force run the deployment
# prefect deployment run ParentFlow/etl_web_to_gcp