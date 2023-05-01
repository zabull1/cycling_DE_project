## Tutorial

## Introduction:
In this tutorial, we will walk through the process of reproducing the Transport for London (TFL) cycling data engineering project. This project involves extracting cycling data from the TFL website (https://cycling.data.tfl.gov.uk), transforming and cleaning it, and loading it into Google Cloud Storage and BigQuery. Later, we used dbt to transform the data in Big Query.

## Prerequisites:
- Basic knowledge of Python programming
- Familiarity with data engineering concepts
- Access to a Google Cloud Platform (GCP) account

## Step 1: Setup

1. Please see [Setup](/setup_tutorial.md)  if you need to set up a GCP Environment, including a VM, GCP account with the service account and project. 
2. Clone on your VM, ```git clone https://github.com/zabull1/cycling_DE_project.git```
3. Change the directory to the repo folder using `cd`
4. 4. To install Google Cloud CLI, Terraform and Anaconda run `bash ./setup.sh`

	- (Note) This may take a little time to process and if you see any prompts from updates, you can hit OK on the prompts and f for the MORE prompt 	   for the Anaconda setup
	- After installation, run the following command to see if you installed GCP SDK correctly:
        ```bash
        gcloud -v
        ``` 
5. Setup virtual environment by running the below commands	
	- `python -m venv env`
	- `source env/bin/activate`
	- `pip install -r ./requirements.txt`

6. Execute Terraform code
    - Change the directory to terraform folder containing the terraform configuration filester
      `cd terraform`
    
    - update the variable.tf file
    	- update the project ID
    	   
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
   
7. 
