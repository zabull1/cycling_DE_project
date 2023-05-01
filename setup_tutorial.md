## Set up your GCP Environment  
In this section, we cover how to setup our GCP environment.

- **Sign up**
  - If you don't already have a Google account, create one. Then, visit [this page](https://cloud.google.com/) and authorize access to the Google Cloud Platform.
  - **Note** that all Google users are eligible for a free $250 credit for three months of usage on their cloud services, but a credit card is required to sign up.
  
- **Create a new project**
  - Steps:
    1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and sign into your account.
    2. In the top navigation bar, select the project drop-down list and click on the "New Project" button.
     3. Enter a unique name for your project and select the billing account that you want to associate with the project.
    4. Select a location for your project. This location determines the default region for your resources. You can change this later if needed.
    5. Click on the "Create" button to create your project.
  - Notes:
    -  Make sure to keep track of your **projectID** and the **location** for your project
    - You can use an existing project but we strongly recommend for everyone to create a new project. If you decide to use an existing project make sure your project has the same exact setup/authorization as us.
    - Once you have created your project, you can access it from the Google Cloud Console by clicking navigational bar and selecting your project. From now on, we are assuming your project is selected.

 - **Create a service account**
    - Steps:
      1. Go to GCP main page
      2. In the left-hand menu, click on "IAM & Admin" and then select "Service accounts".
      3. Click on the "Create Service Account" button at the top of the page.
      4. Enter a name for the service account and an optional description.
      5. Select the Viewer role and click continue and done. 
   - Notes:
      - A service account is a special type of account that is used to authenticate applications and services to access GCP resources programmatically. 
      - In GCP A Viewer role grants read-only access to specific GCP resources.
  
  
 - **Generate SSH key**

[Reference link](https://cloud.google.com/compute/docs/connect/create-ssh-keys)

We need to generate an ssh key, which we'll upload to our Google Cloud project and this will be used for ssh'ing into a VM

On your local computer, open your terminal and run the below command:
`ssh-keygen -t rsa -f ~/.ssh/cycling_vm -C cycling -b 2048`

ssh-keygen -t rsa -f ~/.ssh/KEY_FILENAME -C USERNAME -b 2048

This will generate an 2048 bit rsa ssh keypair, named `cycling_vm` and a comment of `cycling`.  The comment will end up being the user on your VM.

Do a `cat cycling_vm.pub` to see the contents of the public key, and copy the contents.

Back in Google Cloud Console, navigate to Compute Engine > Metadata.

On the SSH keys tab, you can click Add SSH key and paste in the contents you copied, and hit save.

    
  - **Create a VM**

In Google Cloud Console, navigate to Compute Engine > VM instances.  You may have to activate the APi for the Compute Engine when you first come here.

Click the `Create Instance` action towards the top.  On the next screen, you'll want to set the following information:

    * Name = whatever name you would like to call this VM
    * Region, Zone = select a region near you, same with Zone
    * Machine Type = Standard, 4vCPu, 16 GB Memory (e2-standard-4)
    * Boot Disk section, change the following settings:
        * Select Ubuntu and Ubuntu 20.04 LTS (x86/64) as the Operating System and Version
        * Size = 20 GB should be plenty for this project.

Hit Create.  Once the VM is finished getting created, note the external IP address. (if you cant see the externel ip, click the triple dots and select view network details)

In your terminal window, you should now be able to ssh into the VM via the command below, inputing the external IP address of your VM
`ssh -i ~/.ssh/cycling_vm cycling@[external-ip-address]`

You can also update or create a `config` file in your `~/.ssh` folder with the block below, inputing the external IP address of your VM.  This will allow you to just do `ssh gcpvm` to login to your VM

```
Host gcpvm
    Hostname [external IP address]
    User cycling
    IdentityFile ~/.ssh/cycling_vm
```

> **Important note: When you're not using your VM, make sure to stop it in your VM Instances screen in Google Cloud Console.  This way it's not up and running, and using up your credits.**


- **Authenticate local environment to cloud**
  - steps:
    1. Go to GCP main page
    2.  In the left navigation menu, click on "IAM & Admin" and then "Service accounts".
    3. Click on the three verticals dots under the action section for the service name you just created. 
    4. Then click Manage keys, Add key, Create new key. Select JSON option and click Create.
    5. Go to your download folder and find the json file. 
    6. Rename the json file to google_credentials.json
        ```bash
          mv ~/Downloads/<xxxxxx.json> ~/Downloads/google_credentials.json
        ```
    7. Create the following path .google/credentials/ in your HOME directory. You can use the command below in a terminal.
          ```bash
         mkdir -p $HOME/.google/credentials/ 
          ```
    8. Move the google_credentials.json file to the directory above
        ```bash
        mv ~/Downloads/google_credentials.json ~/.google/credentials/ 
        ```
        
        or you can create a new file in $HOME/.google/credentials/ with the name google_credentials.json
        
        - `touch google_credentials.json`
        -  `nano google_credentials.json` and then copy the content of google_credentials.json from download and paste in the newly created json file
        -  `control O` to save the file
        -  `Enter` to confirm
        -  `control X` to close the file
     
