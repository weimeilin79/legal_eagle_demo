1. The legal.py file needs to be updated to include the RAG implementation. 

    - Import `FirestoreVectorStore` and other required modules from langchain and vertexai.
    - Initialize the Vertex AI and the embedding model.You'll be using `text-embedding-004`.
    - Create a FirestoreVectorStore pointing to the legal_documents collection, using the initialized embedding model and specifying the content and embedding fields.
        - The content field is 1original_text1 
        - embedding field is 1embedding1.
    - Define a function called `search_resource` that takes a query, performs a similarity search using vector_store.similarity_search, and returns the combined results.
    - Modifying ask_llm function and use the `search_resource` function to retrieve relevant context based on the user's query.     
        - The retrieved context is then included in the SystemMessage within the ChatPromptTemplate.

```
import os
import signal
import sys
import vertexai
import random
from langchain_google_vertexai import VertexAI, VertexAIEmbeddings
from langchain_google_firestore import FirestoreVectorStore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate

PROJECT_ID = "pure-album-446616-n3" 
LOCATION = "us-central1"      
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Connect to resourse needed from Google Cloud
llm = VertexAI(model_name="gemini-1.5-flash-002")

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

def search_resource(query):
    results = []
    results = vector_store.similarity_search(query, k=5)
    
    combined_results = "\n".join([result.page_content for result in results])
    print(f"==>{combined_results}")
    return combined_results


def ask_llm(query):
    try:
        query_message = {
            "type": "text",
            "text": query,
        }

        relevant_resource = search_resource(query)
       
        input_msg = HumanMessage(content=[query_message])
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are a helpful assistant, and you are with the attorney in a courtroom, you are helping him to win the case by providing the information he needs "
                        "Don't answer if you don't know the answer, just say sorry in a funny way possible"
                        "Use high engergy tone, don't use more than 100 words to answer"
                        f"Here are some contenxt that is relavant to the question {relevant_resource} that you might use"
                    )
                ),
                input_msg,
            ]
        )

        prompt = prompt_template.format()
        
        response = llm.invoke(prompt)
        print(f"response: {response}")

        return response
    except Exception as e:
        print(f"Error sending message to chatbot: {e}") # Log this error too!
        return f"Unable to process your request at this time. Due to the following reason: {str(e)}"

```

To deploy the web application to Cloud Run, follow these step-by-step instructions, based on the provided sources:

1: Containerize the Application
Create a `Dockerfile` in `webapp` project directory that specifies how to build a Docker image, run the following line to create the file.
```
```

2: Build, tag and push the Docker image to the Artifact Registry:
```
docker build -t gcr.io/<YOUR_PROJECT_ID>/legal-eagle-webapp .
docker tag gcr.io/<YOUR_PROJECT_ID>/legal-eagle-webapp us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/my-repository/legal-eagle-webapp
docker push us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/my-repository/legal-eagle-webapp
```

3. Navigate to "Cloud Run" in the Google Cloud Console, Click on **CREATE SERVICE** and configure the Cloud Run service
    - Container image: Select "us-central1-docker.pkg.dev/<YOUR_PROJECT_ID>/my-repository/legal-eagle-webapp".
    - Service name: `legal-eagle-webapp`
    - Region: `us-central1`
    - Authentication: For workshop purposes, allow "Allow unauthenticated invocations" but for production, you'll want to restrict access.
    - Other Settings: Leave the default settings for "Container, Networking, Security".
Click CREATE to deploy the service

4.  Grant permissions to the service account



Now we're going to have it anaylsis the court case for us. we're going to add another textarea as input to let us put in case related info. Change the index.html. css. and main.js in webapp and the legalrag.py

1. Add another textarea in index.html
2. Update webapp/main.js and webapp/legal.js
Try and use Code Assist to help you. 

