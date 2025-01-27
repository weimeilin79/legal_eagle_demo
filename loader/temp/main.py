from google.cloud import storage
import functions_framework
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_google_firestore import FirestoreVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
import vertexai

PROJECT_ID = "pure-album-446616-n3" 
LOCATION = "us-central1"      
vertexai.init(project=PROJECT_ID, location=LOCATION)
embedding_model = VertexAIEmbeddings(
    model_name="text-embedding-004" ,
    project=PROJECT_ID,)

COLLECTION_NAME = "legal_documents"

# Create a vector store
vector_store = FirestoreVectorStore(
    collection="legal_documents",
    embedding_service=embedding_model,
    content_field="original_text",
    embedding_field="embedding",

)

def process_file(cloud_event):
    print(cloud_event)  
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
 

        # Add the docs to the vector store
        vector_store.add_texts(text_chunks)    

        print(f"File processing and Firestore upsert complete for file: {file_name}")


    except Exception as e:
        print(f"Error processing file {file_name}: {e}")