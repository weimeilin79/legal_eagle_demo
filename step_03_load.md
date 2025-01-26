
Now that we understand RAG and our trusty Firestore vector store, it's time to build the engine that populates our legal library!

So, how do we make legal documents 'searchable by meaning'? The magic is in embeddings! Think of embeddings as converting words, sentences, or even whole documents into numerical vectors – lists of numbers that capture their semantic meaning. Similar concepts get vectors that are 'close' to each other in vector space. We use powerful models (like those from Vertex AI) to perform this conversion. It's like creating a secret numerical code for each piece of legal text, allowing our system to understand and compare them based on what they mean, not just the words they use.

And to automate our document loading, we'll use Cloud Run Functions and Eventarc. Cloud Run Function is a lightweight, serverless container that runs your code only when needed. We'll package our document processing Python script into a container and deploy it as a Cloud Run Function. But how does it know when to run? That's where Eventarc comes in! Eventarc lets us set up triggers that react to events happening in Google Cloud. We'll create an Eventarc trigger that 'listens' to our GCS bucket. Whenever a new legal document is uploaded to the bucket, Eventarc will automatically wake up our Cloud Run Function and tell it to start processing that new file – completely hands-free document indexing!


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
cd legal-eagle
mkdir loader
cd loader
```

3. Create `main.py`,`requirements.txt`, and `Dockerfile` files. In the Cloud Shell terminal, use the touch command to create the files:
```
touch main.py requirements.txt Dockerfile
```

4. Open the Cloud Shell Code Editor. You'll see the newly created folder called `*loader` and the three files. 

6. Edit `main.py`. In the file explorer on the left, navigate to the directory where you created the files and double-click on main.py to open it in the editor.
Paste the following Python code into `main.py`:

```
from google.cloud import storage
import functions_framework
from google.cloud import firestore
from vertexai.language_models import TextEmbeddingModel
from langchain.text_splitter import RecursiveCharacterTextSplitter
import vertexai

# Initialize Vertex AI and Embedding Model (adjust project and location if needed)
PROJECT_ID = "<YOUR_PROJECT_ID>" # Replace with your GCP Project ID
LOCATION = "us-central1"       # Or the location where Vertex AI embeddings are available
vertexai.init(project=PROJECT_ID, location=LOCATION)
embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001") # Or your preferred model

# Initialize Firestore client
db = firestore.Client()
collection_ref = db.collection("legal_documents") # Replace with your collection name if different

def process_file(cloud_event):
    """Triggered by a Cloud Storage event.
       Args:
            cloud_event (functions_framework.CloudEvent): The CloudEvent
                containing the Cloud Storage event data.
    """
    bucket_name = cloud_event.data['bucket']
    file_name = cloud_event.data['name']

    print(f"CloudEvent received: {cloud_event}")
    print(f"New file detected in bucket: {bucket_name}, file: {file_name}")

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    try:
        # Download the file content as string (assuming UTF-8 encoded text file)
        file_content_string = blob.download_as_string().decode("utf-8")

        print(f"File content downloaded. Processing...")

        # Split text into chunks using RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            length_function=len,
        )
        text_chunks = text_splitter.split_text(file_content_string)

        print(f"Text split into {len(text_chunks)} chunks.")

        # Generate embeddings for each text chunk
        embeddings = embedding_model.get_embeddings(text_chunks)
        embedding_vectors = [embedding.values.tolist() for embedding in embeddings] # Convert to list of lists

        print(f"Embeddings generated for {len(embedding_vectors)} chunks.")

        # Prepare Firestore document data
        for i, chunk in enumerate(text_chunks):
            doc_id = f"{file_name}_chunk_{i+1}" # Create a unique document ID for each chunk
            doc_data = {
                "file": file_name,
                "original_text_chunk": chunk,
                "embedding_vector": embedding_vectors[i],
                "chunk_number": i + 1, # Optional: chunk number for ordering
                "total_chunks": len(text_chunks) # Optional: total chunks for the file
            }

            # Upsert document to Firestore (create or update if doc_id exists)
            doc_ref = collection_ref.document(doc_id)
            doc_ref.set(doc_data)
            print(f"Document '{doc_id}' upserted to Firestore.")

        print(f"File processing and Firestore upsert complete for file: {file_name}")


    except Exception as e:
        print(f"Error processing file {file_name}: {e}")
```
7. Edit requirements.txt. In the file explorer, double-click on requirements.txt. Paste the following lines into the file:
```
google-cloud-storage
functions-framework
google-cloud-vertexai
google-cloud-firestore
langchain
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

## Grant permission to the loader service:
Your Cloud Run service needs permission to read files from various components. We need to grant the service's service account the "Storage Object Viewer" role on your bucket.

1. Get the Cloud Run Service Account Email Address: As you did in the console instructions, you first need to get the service account email address associated with your Cloud Run service. Go to "Cloud Run" in the Google Cloud Console.
2. Click on your Cloud Run service name and go to the "Permissions" tab.
3. Copy the email address of the service account listed there. It will likely be in the format your-project-id-run@developer.gserviceaccount.com or similar. Let's say you copy this email and it is <CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>.

4. Grant "GCS Bucket Viewer" Role:
Run the gcloud iam policy add-binding command: Open your terminal or Cloud Shell and execute the following gcloud command:

```
gcloud storage buckets iam-policy add-binding gs://<YOUR_GCS_BUCKET_NAME> \
    --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>" \
    --role="roles/storage.objectViewer"
```

Replace the placeholders:
<YOUR_GCS_BUCKET_NAME>: Replace this with the actual name of your GCS bucket (e.g., my-project-file-upload-bucket).
<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>: Replace this with the service account email address you copied in Step 1.


5.  Grant "Vertex AI User" Role using gcloud:
```
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
    --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>" \
    --role="roles/aiplatform.user"
```

6. Grant "Firestore User" Role

```
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
    --member="serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>" \
    --role="roles/datastore.user"
```

7. Verify TODO, use a script to print the section needed.

gcloud storage buckets iam-policy get gs://<YOUR_GCS_BUCKET_NAME>

```
- members:
  - serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>
  role: roles/storage.objectViewer
```

gcloud projects get-iam-policy <YOUR_PROJECT_ID>

```
- members:
  - serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>
  role: roles/aiplatform.user
  - serviceAccount:<CLOUD_RUN_SERVICE_ACCOUNT_EMAIL>
  role: roles/datastore.user
```

### Test by Uploading a New File in GCS bucket

1. Upload the court case file to your GCS bucket.

```
gcloud storage cp court_case.md gs://<YOUR_GCS_BUCKET_NAME>/court_case.md
```


2. Monitor Cloud Run Service Logs, go to "Cloud Run" -> your service `legal-eagle-loader` -> "Logs". And check the logs for successful processing messages, including:
```
    "CloudEvent received:"
    "New file detected in bucket:"
    "File content downloaded. Processing..."
    "Text split into ... chunks."
    "Embeddings generated for ... chunks."
    "Document '...chunk...' upserted to Firestore."
    "File processing and Firestore upsert complete..."
```
Look for any error messages in the logs and troubleshoot if necessary.

3. Verify Data in Firestore. Go to "Databases" -> "Firestore" -> "Data" in the Cloud Console and open your legal_documents collection.
You should see new documents created in your collection. Each document will represent a chunk of the text from the file you uploaded and will contain:
```
file: The filename.
original_text_chunk: The text chunk content.
embedding_vector: A list of floating-point numbers (the Vertex AI embedding).
chunk_number, total_chunks.
```