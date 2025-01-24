

Enable the Cloud Storage API
Cloud Run API: Ensure the Cloud Run API is enabled. Follow the same steps as for Cloud Functions API in the original guide, but search for and enable "Cloud Run API".
Artifact Registry API or Container Registry API: You'll need to push your container image. Enable either:
Artifact Registry API (Recommended, newer): Search for and enable "Artifact Registry API".


### Step 1:  Setting up Google Cloud Storage (GCS) Bucket

1. Go to the Google Cloud Console in your web browser: https://console.cloud.google.com/
If you're not already logged in, log in with your Google account associated with your GCP account.
create a new project, click on the project dropdown and then **NEW PROJECT**. Follow the prompts to create a new project, giving it a name and billing account.

2. In the Navigation menu, scroll down to "Storage" and click on "Cloud Storage".
3. Click on "Buckets" in the left-hand menu.
4. Click on the "+ CREATE" button at the top.
5. Configure your bucket (Important settings):
    **bucket name**: Choose a globally unique name for your bucket. Bucket names must be globally unique across all of Google Cloud Storage. Use lowercase letters, numbers, dashes (-), underscores (_), and dots (.). A good practice is to include your project ID or a part of it in the bucket name to ensure uniqueness. For example, my-project-file-upload-bucket.
    **region**: Select the `us-central1` region.
    **Storage class**: "Standard". Standard is suitable for frequently accessed data.
    **Access control**: Leave the default "Uniform access control" selected. This provides consistent, bucket-level access control.
    **Advanced options**: For this tutorial, the default settings are usually sufficient.
6. Click the **CREATE** button to create your bucket.

You will now see your newly created bucket in the Buckets list. Note down your bucket name; you'll need it later.

###  Step 2: Setting up Google Cloud Run Function to Listen to Bucket Events

**Google Cloud Shell** provides a browser-based IDE that's very convenient for developing and managing your cloud resources.

1. Open Cloud Shell: In the Google Cloud Console, look for the "Activate Cloud Shell" button in the top right toolbar (it looks like a terminal prompt icon: >_). Click on it.
Cloud Shell will open in a pane at the bottom of your browser window. It might take a moment to provision the environment.

2. Navigate to the working directory **legal-eagle-loader**: By default, Cloud Shell starts in your home directory (/home/your-username). Use cd command in the Cloud Shell terminal create the file.
```
cd legal-eagle-loader
```

3. Create `main.py`,`requirements.txt`, and `Dockerfile` files. In the Cloud Shell terminal, use the touch command to create the files:
```
touch main.py requirements.txt Dockerfile
```

4. Open the Cloud Shell Code Editor. In the Cloud Shell toolbar (the top of the Cloud Shell pane), click on the "Open Editor" button (it looks like an open folder with a pencil).
This will open the Cloud Shell Code Editor in a new browser tab or window. You'll see a file explorer on the left side. 

5. Enable Gemini Code Assist in Cloud Shell IDE
    - Click on the **Cloud Code, sign i**n** button in the bottom status bar as shown. Authorize the plugin as instructed. If you see **Cloud Code - no project** in the status bar, select that and then select the specific Google Cloud Project from the list of projects that you plan to work with.
    - Click on the Code Assist button in the bottom right corner as shown and select one last time the correct Google Cloud project. If you are asked to enable the Cloud AI Companion API, please do so and move forward. Once you've selected your Google Cloud project, ensure that you are able to see that in the Cloud Code status message in the status bar and that you also have Code Assist enabled on the right, in the status bar as shown below:

6. Edit `main.py`. In the file explorer on the left, navigate to the directory where you created the files and double-click on main.py to open it in the editor.
Paste the following Python code into `main.py`:

```
from google.cloud import storage
import functions_framework

@functions_framework.cloud_event
def process_file(cloud_event):
    """Triggered by a Cloud Storage event.
       Args:
            cloud_event (functions_framework.CloudEvent): The CloudEvent
                containing the Cloud Storage event data.
    """
    bucket_name = cloud_event.data['bucket']
    file_name = cloud_event.data['name']

    print(f"CloudEvent received: {cloud_event}") # Log the entire CloudEvent for inspection
    print(f"New file detected in bucket: {bucket_name}, file: {file_name}")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        # Download the file content as bytes
        file_content_bytes = blob.download_as_bytes()
        file_content_string = file_content_bytes.decode('utf-8') # Assuming text file, decode to string

        print(f"File content:")
        print("---------------------")
        print(file_content_string)
        print("---------------------")

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
```
7. Edit requirements.txt. In the file explorer, double-click on requirements.txt. Paste the following lines into the file:
```
google-cloud-storage
functions-framework
```

8. Edit Dockerfile. In the file explorer, double-click on Dockerfile. Ask Gemini to generate the dockerfile for you
```
Generate a Dockerfile for a Python 3.12 Cloud Run service that uses functions-framework. It needs to:
1. Use a Python 3.12 slim base image.
2. Set the working directory to /app.
3. Copy requirements.txt and install Python dependencies.
4. Copy main.py.
5. Set the command to run functions-framework, targeting the 'process_file' function on port 8080
```

9. Build the Docker Image: Open your terminal, navigate to the directory where you saved Dockerfile, main.py, and requirements.txt, and run the following command to build the Docker image. 

```
docker tag gcr.io/<YOUR_PROJECT_ID>/legal-eagle-loader us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/my-repository/legal-eagle-loader
docker push us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/my-repository/legal-eagle-loader
```

###  Step 3: Deploy the Cloud Run function and Set up Eventarc Trigger for GCS Events
1. In the Google Cloud Console, navigate to "Cloud Run". Click on **CREATE SERVICE**.
2. Configure your Cloud Run service:
    - **Container image**: Select "Select container image". Enter the image URL you pushed to Artifact Registry (e.g., us-central1-docker.pkg.dev/your-project-id/my-repository/legal-eagle-loader).
    - **Service name**: `legal-eagle-loader`
    - **Region**: Select the `us-central1` region.
    - **Authentication**: For the purpose of this workshop, you can allow "Allow unauthenticated invocations". For production, you'll likely want to restrict access.
    - **Container, Networking, Security** : default.
Click **CREATE**. Cloud Run will deploy your service.


To trigger your Cloud Run service when files are uploaded to your GCS bucket, we'll use Eventarc. Eventarc allows you to route events from various GCP services to Cloud Run, Cloud Functions, or other destinations.

3. In the Google Cloud Console, navigate to "Eventarc" -> "Triggers". Click on "+ CREATE TRIGGER".

4. Configure Eventarc Trigger:
    - Trigger name: `legal-eagle-upload-trigger`.
    - Event provider: Select "Cloud Storage".
    - Event: Choose "google.cloud.storage.object.v1.finalized" (Object Finalized - this is for file creation/upload completion).
    - Cloud Storage Bucket: Select your GCS bucket from the dropdown.
    - Destination:
        Destination type: "Cloud Run service".
    - Service: Select `legal-eagle-loader`.
    - Region: `us-central1`
    - Path: Leave this blank for now .
Click **CREATE**. Eventarc will now set up the trigger.


Your Cloud Run service needs permission to read files from your GCS bucket. We need to grant the service's service account the "Storage Object Viewer" role on your bucket.

5. Get the Cloud Run Service Account Email Address: As you did in the console instructions, you first need to get the service account email address associated with your Cloud Run service. Go to "Cloud Run" in the Google Cloud Console.
6. Click on your Cloud Run service name and go to the "Permissions" tab.
7. Copy the email address of the service account listed there. It will likely be in the format your-project-id-run@developer.gserviceaccount.com or similar. Let's say you copy this email and it is <CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>.
Get your GCS Bucket Name: You need to know the name of your GCS bucket where you want to grant the permission. Let's assume your bucket name is <YOUR_GCS_BUCKET_NAME>.

Run the gcloud iam policy add-binding command: Open your terminal or Cloud Shell and execute the following gcloud command:

```
gcloud storage buckets iam-policy add-binding gs://<YOUR_GCS_BUCKET_NAME> \
    --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>" \
    --role="roles/storage.objectViewer"
```

Replace the placeholders:
<YOUR_GCS_BUCKET_NAME>: Replace this with the actual name of your GCS bucket (e.g., my-project-file-upload-bucket).
<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>: Replace this with the service account email address you copied in Step 1.

8. You can verify that the role has been granted using the `gcloud iam policy` get command:
```
gcloud storage buckets iam-policy get gs://<YOUR_GCS_BUCKET_NAME>
```
This command will output the IAM policy for your bucket in JSON or YAML format. Look for the "bindings" section and verify that you see an entry similar to this (within the bindings array):

```
- members:
  - serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>
  role: roles/storage.objectViewer
```

