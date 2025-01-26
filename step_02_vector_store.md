Time to put an end to these LLM 'creative interpretations' of the law.That’s where Retrieval-Augmented Generation (RAG) comes to the rescue! Think of it like giving our LLM access to a super-powered legal library right before it answers your questions. Instead of relying solely on its general knowledge (which can be fuzzy or outdated depending on the model), RAG first fetches relevant information from a trusted source – in our case, legal documents – and then uses that context to generate a much more informed and accurate answer. It's like the LLM doing its homework before stepping into the courtroom!

Next, we'll use Firestore,

To build our RAG system, we need a place to store all those legal documents and, importantly, make them searchable by meaning. That's where Firestore comes in! Firestore is Google Cloud's super flexible, super scalable NoSQL document database. We're going to use Firestore as our vector store. We'll store chunks of our legal documents in Firestore, and for each chunk, we'll also store its embedding – that fancy numerical representation of its meaning. Then, when you ask our Legal Eagle a question, we'll use Firestore's vector search to find the chunks of legal text that are most relevant to your query. This retrieved context is what RAG uses to give you answers that are grounded in actual legal information, not just LLM imagination!

### Set up Firestore Database in Google Cloud
1. In the Navigation menu, scroll down to "Databases" and click on "Firestore".
2. Choose "Native mode". Important: Vector Search in Firestore is currently only supported in Native mode. Select "Native mode" and click "Select Native mode".
3. Select a location:  `us-central1` 
Click **Create Database**. Firestore will provision your database, which might take a few moments.

4. Enable Vector Search for your Firestore Database. Go to the "Indexes" tab.
    - Click on "Vector Search" (in the sub-navigation within the "Indexes" tab). You might see a banner prompting you to enable Vector Search.
    - Click "Enable Vector Search". Confirm if prompted. Enabling Vector Search might take a few minutes. You'll typically see a progress indicator or message.

5. Create a Firestore Collection. Go to the "Data" tab in your Firestore database.
    - Click on "+ Start collection".
    - Collection ID: Enter a name for your collection. For example, legal_documents. Click "Next".
    - Document ID: You can leave this as "Autogenerate ID" for now.

    - Field 1:
        - Field name: file
        - Data type: String
        - Value: (You can put a sample filename for now, e.g., case_one.md).
    Click "Add field".
    - Field 2:
        - Field name: original_text
        - Data type: String
        - Value: XXXXdfjksdjflsdkfjsdl.
     Click "Add field".
    - Field 3: embedding_vector (for vector embeddings)
        - Field name: embedding_vector
        - Data type: Array
        - Value: [0.1,3.0,6.6]
    Click "Save".
    You have now created a collection legal_documents and inserted a document with sample data, including a placeholder embedding_vector.

6. Create a Vector Index on the embedding_vector field, to enable vector search, you need to create a vector index on the embedding_vector field in your legal_documents collection.
    - Go back to the "Indexes" tab in your Firestore database.
    - Click on "Vector Search" (again, in the sub-navigation).
    - Click on "+ Create Index" with 
        Index name: Give your index a name, e.g., legal_doc_embedding_index.
        Collection ID: Select your collection, legal_documents.
    -Fields to index:
        - Field path: Select embedding_vector.
        - Index type: "Vector".
        - Dimensions: 768. For our workshop, the dimension is 768 with different embedding model, you will need to set this to the correct dimension of your model's output (e.g., 768, 1536).
        - Distance metric: **COSINE_SIMILARITY** as the distance metric for vector similarity search. Here are some common choices:
            - COSINE_SIMILARITY: Often used for text embeddings. Measures cosine similarity.
            - EUCLIDEAN_DISTANCE: Measures Euclidean distance.
            - DOT_PRODUCT: Dot product. Choose COSINE_SIMILARITY for text-based embeddings as a good default.

    Click "Create".
    Firestore will start creating the vector index. Index creation can take some time, especially for larger datasets. You'll see the index in a "Creating" state, and it will transition to "Ready" when it's built.


