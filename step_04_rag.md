Next Show how to implement RAG using RetrievalQA 
TODO: make an interesting intro

1. Open legal.py: In your Cloud Shell Editor, open main.py.

Example legal.py (Illustrative - Adapt to your existing legal.py):

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

Now we're going to have it anaylsis the court case for us. we're going to add another textarea as input to let us put in case related info. Change the index.html. css. and main.js in webapp and the legalrag.py

