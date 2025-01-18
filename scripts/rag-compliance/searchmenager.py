from chromadb.config import Settings
from chromadb import Client
import numpy as np
from langchain.embeddings import OpenAIEmbeddings

# Initialize Chroma client
client = Client(Settings(
    persist_directory="db_directory",  # Directory to store the database
    chroma_db_impl="duckdb+parquet",   # Storage backend
))

# Create or get a collection
collection_name = "my_vector_collection"
collection = client.get_or_create_collection(
    name=collection_name,
    metadata={"description": "A collection for storing content and embeddings"}
)

# Example data
documents = [
    {"id": "1", "content": "This is the first document.", "embedding": np.random.rand(768).tolist()},
    {"id": "2", "content": "Another document with different content.", "embedding": np.random.rand(768).tolist()},
]

# Add data to the collection
for doc in documents:
    collection.add(
        ids=[doc["id"]],
        metadatas=[{"content": doc["content"]}],
        embeddings=[doc["embedding"]]
    )

# Query the collection
query_embedding = np.random.rand(768).tolist()
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5
)

# Print query results
for result in results['documents']:
    print("Found document:", result)
