# Transport for London Cycling Data Engineering Project


## Overview?
Transport for London (TfL) is the organization responsible for managing and operating London's transportation system, including the London Underground, buses, trams, river services, and taxis. Its mission is to provide a safe, efficient, and sustainable transportation system that connects Londoners to jobs, services, and communities. TfL plans, invests in, manages, and maintains the transport infrastructure in Greater London while regulating and licensing transport services.


This project aims to build an end-to-end orchestrated data pipeline. The pipeline will fetch cycling data from https://cycling.data.tfl.gov.uk and export it to Google Cloud Storage. Then, the data will be filtered, transformed to the desired data types, and uploaded to BigQuery. In BigQuery, DBT will be used to transform the data. Finally, the data will be visualised in a dashboard.

## Questions to answer 
1. What is the average cycling duration?
2. What are the top start stations
3. what are the top 4  end stations


## What technologies are being used?
- Cloud: `Google Cloud`
- Infrastructure: `Terraform`
- Orchestration: `Prefect`
- Data lake: `Google Cloud Storage`
- Data transformation: `DBT`
- Data warehouse: `BigQuery`
- Data visualization: `Google Looker Studio`

## Dashboard example
[Click here](https://lookerstudio.google.com/u/3/reporting/fbadcee0-64bf-4771-8187-960e6ad0f0fa/page/6g7MD) to see my Looker dashboard.

<p align="center">
<img src="images/dashboard.png" width="800">
</p>

<!-- ## What is the structure of the production table?
| Column | Description | 
|--------|-------------|
| primary_key | Unique surrogate key from card_id and released_at data points |
| card_id | Card ID in database, IDs can be repeated due to reprintings |
| name | The name of this card |
| released_at | The date this card was first released |
| color_identity | This card’s color identity |
| color_category | Based on the color_identity: Black, Blue, White, Green, Red, Colorless or Mixed |
| set_name | This card’s full set name |
| artist | The name of the illustrator of this card face |
| price | Price information of this card in US Dollar |
| data_update | Timestamp when the data was updated in the database |

- Here the dbt lineage graph <img src="images/dbt_lineage.png" width="400">
- Partitioned on the `released_at` column - in favor of question 1 and 3 - assuming that in most cases, cards with the same release date are from the same set
- Clustered on the `color_category` column - in favor of question 2 - assuming that within one set the number of colors is lower than the numbers of unique prices and artists

<p align="center">
<img src="images/lotus.png">
</p>

## How to make it work?
1. Setup your Google Cloud environment
- Create a [Google Cloud Platform project](https://console.cloud.google.com/cloud-resource-manager)
- Configure Identity and Access Management (IAM) for the service account, giving it the following privileges: BigQuery Admin, Storage Admin and Storage Object Admin
- Download the JSON credentials and save it, e.g. to `~/.gc/<credentials>`
- Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install-sdk)
- Let the [environment variable point to your GCP key](https://cloud.google.com/docs/authentication/application-default-credentials#GAC), authenticate it and refresh the session token
```bash
export GOOGLE_APPLICATION_CREDENTIALS=<path_to_your_credentials>.json
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
gcloud auth application-default login
```
2. Install all required dependencies into your environment
```bash
pip install -r requirements.txt
```
3. Setup your infrastructure
- Assuming you are using Linux AMD64 run the following commands to install Terraform - if you are using a different OS please choose the correct version [here](https://developer.hashicorp.com/terraform/downloads) and exchange the download link and zip file name

```bash
sudo apt-get install unzip
cd ~/bin
wget https://releases.hashicorp.com/terraform/1.4.1/terraform_1.4.1_linux_amd64.zip
unzip terraform_1.4.1_linux_amd64.zip
rm terraform_1.4.1_linux_amd64.zip
```
- To initiate, plan and apply the infrastructure, adjust and run the following Terraform commands
```bash
cd terraform/
terraform init
terraform plan -var="project=<your-gcp-project-id>"
terraform apply -var="project=<your-gcp-project-id>"
```
4. Setup your orchestration
- If you do not have a prefect workspace, sign-up for the prefect cloud and create a workspace [here](https://app.prefect.cloud/auth/login)
- Create the [prefect blocks](https://docs.prefect.io/concepts/blocks/) via the cloud UI or adjust the variables in `/prefect/prefect_blocks.py` and run
```bash
python magic-the-gathering/prefect/prefect_blocks.py
```
- Adjust the keyfile location at `dbt/profiles.yml` to the path of your Google Cloud credentials JSON
- To execute the flow, run the following commands in two different CL terminals
```bash
prefect agent start -q 'default'
```
```bash
python prefect/api_to_gcs_to_bq.py
```
5. Data deep dive
- The data will be available in BigQuery at `mtg_card_data_dbt.dbt_mtg_latest_data` 
- Query the data in-place or build a dashboard

<p align="center">
<img src="images/mana_black.png">
<img src="images/mana_red.png">
<img src="images/mana_green.png">
<img src="images/mana_blue.png">
<img src="images/mana_white.png">
</p>

## Potential next steps
With a growing database, I would be able to further explore the following:
- What is the color distribution over time?
- What is the price development of specific cards / colors / sets over time?

<p align="center">
<img src="images/black_wizard.png" height="300">
</p> -->
