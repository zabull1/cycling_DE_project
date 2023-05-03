## Tutorial

## Introduction:
In this tutorial, we will walk through the process of reproducing the Transport for London (TFL) cycling data engineering project. This project involves extracting cycling data from the TFL website (https://cycling.data.tfl.gov.uk), transforming and cleaning it, and loading it into Google Cloud Storage and BigQuery. Later, we used dbt to transform the data in Big Query.

## Prerequisites:
- Basic knowledge of Python programming
- Familiarity with data engineering concepts
- Access to a Google Cloud Platform (GCP) account

## Setup

1. Please see [Setup](/setup_tutorial.md)  if you need to set up a GCP Environment, including a VM, GCP account with the service account and project. 
2. Clone on your VM home directory, ```git clone https://github.com/zabull1/cycling_DE_project.git```
3. Change the directory to the repo folder using `cd`
4. 4. To install Google Cloud CLI, Terraform and Anaconda run `bash ./setup.sh`

	- (Note) This may take a little time to process and if you see any prompts from updates, you can hit OK on the prompts and f for the MORE prompt 	   for the Anaconda setup
	- After installation, run the following command to see if you installed GCP SDK correctly:
        ```bash
        gcloud -v
        ``` 
5. Setup virtual environment by running the below commands	
	- `python3 -m venv env` or `python -m venv env`
	- `source env/bin/activate`
	- `pip install -r ./requirements.txt`

6. Execute Terraform code
    - Change the directory to terraform folder containing the terraform configuration filester
      `cd terraform`
    
    - update the variable.tf file
    	- update the project ID to your chosen ID
    	- update the region to your chosen region
    		- `nano variables.tf`
    		- make changes
    		- `control O`
    		- press the Enter key
    		- `control X` to exit
    	   
    - Initialize 
      ```bash
      terraform init
      ```
    - Stage
      ```bash
      terraform plan
      ```
    - Deploy
      ```bash
      terraform apply
      ```
   
7. Setup your orchestration
	- sign-up for the prefect cloud and create a workspace [here](https://app.prefect.cloud/auth/login)
	-  Generate a new API key (if you dont have any) and keep it safe 
		- click the icon at the bottom left corner
		- click on the profile (your name)
		- click on API Keys
		- click on Create API Key
		- enter API key name and click on Create
		- copy the API key and keep it safe
	- change the directory to prefect folder using `cd`
	- Log in to the Prefect Cloud dashboard		
		- `prefect cloud login -k [api_key]`
	- Edit `blocks.py` by inserting bucket name
	- Edit `web_to_gcs_to_bq.py` with your project and bucket name
	- Edit `profiles.yml` file in dbt folder with location of your gcp resources (for example: europe-west1)
	- Create the prefect blocks
		- `python blocks.py` or  via the cloud UI [prefect blocks](https://docs.prefect.io/concepts/blocks/)
	- Deploy the pipeline (Please note this takes around one and a half hour to complete)
		- `python deploy_web_to_gcs_to_bq.py`
		- in Cloud UI, goto Deployment and a start a quick run
		- in terminal, run below command
			- `prefect agent start --pool default-agent-pool`
	
