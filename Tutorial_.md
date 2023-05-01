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
4. To install Google Cloud CLI, Terraform and Anaconda run `bash ./setup.sh`

	- (Note) This may take a little time to process and if you see any prompts from updates, you can hit OK on the prompts and f for the MORE prompt 	   for the Anaconda setup
	- After installation, run the following command to see if you installed GCP SDK correctly:
        ```bash
        gcloud -v
        ``` 
        - Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of the json file. Use the command bellow:
        ``` bash
        export GOOGLE_APPLICATION_CREDENTIALS="~/.google/credentials/google_credentials.json"
        ```
	 (run export GOOGLE_APPLICATION_CREDENTIALS="<absolute path to the json file in the ./creds folder>" to set environment variable for your service account file.)
        - Run the command bellow - it will make you sign into your google account and verify the authentication. If all goes well your a google browser will open with the following message displayed: **You are now authenticated with the gcloud CLI!**
            ```bash
            gcloud auth application-default login
            ```
       - Notes:
       - In above(export GOOGLE_APP....), We're telling Google Cloud SDK and API client libraries to use the JSON file specified by the path as the    default location for authentication credentials. This means that we can access Google Cloud Platform services without having to explicitly provide authentication keys in our code. Thus, that's what allows us to automatically sign in into our google account wth the command in step 12. 
       - We changed the name and location of our credentials file for future purpose but ideally we could ran the export command from step 11 when our credential file was located in the downloads folder with its default name. We just had to provide the correct path. 

- **Add additional Roles and permission (i.e services)**
  - steps:
    1. Go to GCP main page
    2. In the left-hand menu, click on "IAM & Admin" and then select "IAM". You should see the service account we created in the previous steps and our Viewer role.
    3. On the same row we see our Service account name, click 'edit principal' button which is located in the last column.
    4. Then add the BigQuery Admin, Storage Admin, Storage Object Admin as roles for our service account and click the save button. 
    5. Enable IAM APIs by clicking the following links:
        - [IAM-API](https://console.cloud.google.com/apis/library/iam.googleapis.com)
        - [IAM-credential-API](https://console.cloud.google.com/apis/library/iamcredentials.googleapis.com)

  - Notes:
    - In Google Cloud Platform (GCP), the Identity and Access Management (IAM) API and the IAM Credentials API are used to manage and control access to GCP resources.
    - The IAM API provides the ability to manage access control policies for GCP resources such as projects, buckets, and instances. It enables you to create and manage IAM roles, which define a set of permissions for specific actions on resources, and grant those roles to members or groups.
    - The IAM Credentials API is used to create, manage, and exchange temporary credentials such as access tokens, identity tokens, and service account keys. These temporary credentials can be used to authenticate requests to GCP APIs and services.
    - Enabling the IAM API and the IAM Credentials API is required in order to use and manage IAM roles and policies, as well as to create and manage temporary credentials.
    - These APIs are required for Terraform (SEE IN NEXT SECTION)
