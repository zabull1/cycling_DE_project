## Introduction:
In this tutorial, we will walk through the process of reproducing the Transport for London (TFL) cycling data engineering project. This project involves extracting cycling data from the TFL website (https://cycling.data.tfl.gov.uk), transforming and cleaning it, and loading it into Google Cloud Storage and BigQuery. Later, we used dbt to transform the data in Big Query.

## Prerequisites:
- Basic knowledge of Python programming
- Familiarity with data engineering concepts
- Access to a Google Cloud Platform (GCP) account

## Step 1: Setup

1. Please see GCP Setup  if you need to set up a GCP Environment, including a VM, GCP account with the service account and project.
2. Clone on your VM, `git clone https://github.com/zabull1/cycling_DE_project.git`
3. Change to the directory to the repo folder using `cd`
4. To install Google Cloud CLI, Terraform and Anaconda run `bash ./setup/setup.sh` 
5. Setup virtual environment by running the below commands5	- source ~/.bashrc
	- conda create -n mpls311 python=3.9 -y
	- conda activate mpls311
	- pip install -r ./setup/conda_requirements.txt
6. Save your Google Cloud Account .json file to the .credentials folder.
7. run export GOOGLE_APPLICATION_CREDENTIALS="<absolute path to the json file in the ./creds folder>" to set environment variable for your service account file.
