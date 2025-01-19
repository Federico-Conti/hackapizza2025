import chromadb
import json
from embedded import process_embeddings  # Ensure this module is implemented correctly
from chromadb.config import Settings


class SearchClient:
    def __init__(self, db_path="../../vect-db"):
        """Initialize Chroma client and collection."""
        try:
            self.client = chromadb.PersistentClient(
                settings=Settings(persist_directory=db_path)
            )
            
            self.collection = self.client.get_or_create_collection(
                name="vector_compliance",
                metadata={
                    "description": "A collection for storing content and embedding compliance knowledge"
                },
            )
            print("Initialized Chroma client and collection.")
        except Exception as e:
            print(f"Failed to initialize Chroma client: {e}")
            raise

    def document_exists(self, doc_id):
        try:
            results = self.collection.get(ids=[doc_id])
            return bool(results.get("ids"))  # Check if any IDs are returned
        except Exception as e:
            print(f"Error checking document existence: {e}")
            return False

    def add_data_to_collection(self, file_path):
        try:
            with open(file_path, "r") as file:
                documents = json.load(file)

            if not isinstance(documents, list):
                raise ValueError("The JSON file should contain a list of documents.")

            new_docs = 0

            for doc in documents:
                # Validate document structure
                if not all(key in doc for key in ["id", "content", "embedding"]):
                    raise ValueError(f"Invalid document format: {doc}")

                # Check if document already exists
                if self.document_exists(doc["id"]):
                    print(f"Document with ID {doc['id']} already exists. Skipping.")
                    continue

                # Add document to the collection
                self.collection.add(
                    ids=[doc["id"]],
                    metadatas=[{"content": doc["content"]}],
                    embeddings=[doc["embedding"]],
                )
                new_docs += 1

            print(f"Added {new_docs} new documents to the collection.")
        except Exception as e:
            print(f"Failed to add data to the collection: {e}")
            raise

    def hybrid_search(self, query_text, query_embedding, n_results=3):
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                query_texts=[query_text],
                n_results=n_results,
            )
            return results
        except Exception as e:
            print(f"Hybrid search failed: {e}")
            raise


if __name__ == "__main__":
    # Initialize the search client
    search_client = SearchClient()
    
    # Example file path for adding data (update with actual file path)
    file_path = "../../Data/CodiceGalattico/embeddings.json"
    try:
        search_client.add_data_to_collection(file_path)
    except Exception as e:
        print(f"Error adding data to collection: {e}")

    # Example user input for a hybrid query
    user_query = "requisiti di conformità per l'archiviazione dei dati"

    try:
        # Generate embedding for the query
        user_query_emb = process_embeddings([user_query])[0]  # Ensure process_embeddings is correctly implemented

        # Perform the hybrid search
        search_results = search_client.hybrid_search(
            query_text=user_query, query_embedding=user_query_emb, n_results=3
        )
        # Extracting the content
        contents = []
        if search_results.get('metadatas'):
            for metadata_group in search_results['metadatas']:
                for metadata in metadata_group:
                    content = metadata.get('content')
                    if content:
                        contents.append(content)

        # Display extracted contents
        for i, content in enumerate(contents, 1):
            print(f"Content {i}:\n{content}\n")
    
    except Exception as e:
        print(f"Error during search: {e}")
