from chromadb.config import Settings
from chromadb import Client
import json
from embedded import process_embeddings

class SearchClient:
    def __init__(self):
        """Initialize Chroma client and collection."""
        self.client = Client(
            persist_directory="../../v_db",  # Directory to store the database
            chroma_db_impl="duckdb+parquet",  # Storage backend
        )
        self.collection = self.client.get_or_create_collection(
            name="vector_compliance",
            metadata={"description": "A collection for storing content and embedding compliance knowledge"}
        )
        print("Initialized Chroma client and collection.")

    def add_data_to_collection(self, file_path):
        """Load documents from a file and add them to the Chroma collection."""
        with open(file_path, "r") as file:
            documents = json.load(file)
        print(f"Loaded {len(documents)} documents from {file_path}.")

        for doc in documents:
            self.collection.add(
                ids=[doc["id"]],
                metadatas=[{"content": doc["content"]}],
                embeddings=[doc["embedding"]]
            )
        print(f"Added {len(documents)} documents to the collection.")

    def hybrid_search(self, query_text, query_embedding, n_results=5):
        """Perform a hybrid search using both embeddings and keywords."""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            query_texts=[query_text],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    # Initialize the search client
    search_client = SearchClient()
    search_client.add_data_to_collection("../../Data/CodiceGalattico/embeddings.json")
    # Add data to the collection (example usage, provide the path to your data file)
    # search_client.add_data_to_collection("data.json")



    # Example user input for a hybrid query
    user_query = "compliance requirements for data storage"
    user_query_emb = process_embeddings([user_query])
    print(user_query_emb)
    
    # # Perform the hybrid search
    # search_results = search_client.hybrid_search(query_text=user_query, query_embedding=user_query_emb, n_results=5)

    # # Print the results
    # for document, metadata in zip(search_results['documents'], search_results['metadatas']):
    #     print("Found document:", document)
    #     print("Metadata:", metadata)
