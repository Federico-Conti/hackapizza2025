import os
from typing import Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from the specified file
load_dotenv("../../.env.local")

# Constants for environment variables
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = "2024-10-01-preview"
AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME = "ict-chatict_embeddingada002"

def getSearchClient(index_name: str = "questionsearch") -> SearchClient:
    """
    Initialize and return an Azure SearchClient instance.

    Args:
        index_name (str): The name of the search index. Default is 'questionsearch'.

    Returns:
        SearchClient: The initialized Azure SearchClient.
    """
    if not AZURE_SEARCH_SERVICE_ENDPOINT or not AZURE_SEARCH_ADMIN_KEY:
        raise ValueError("Azure Search endpoint or admin key is missing in environment variables.")
    
    credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    return SearchClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=credential)

def generate_embeddings(text: str) -> Any:
    """
    Generate embeddings for a given text using Azure OpenAI.

    Args:
        text (str): The text to generate embeddings for.

    Returns:
        Any: The generated embeddings.
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise ValueError("Azure OpenAI endpoint or API key is missing in environment variables.")

    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
    
    try:
        response = client.embeddings.create(
            model=AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise RuntimeError(f"Error generating embeddings: {e}")

if __name__ == "__main__":
    try:
        # Initialize the Search Client
        search_client = getSearchClient()
        print("Azure SearchClient initialized successfully:", search_client)

        # Example usage of embeddings generation
        sample_text = "This is an example text for embedding generation."
        embeddings = generate_embeddings(sample_text)
        print("Generated embeddings:", embeddings)
    except Exception as error:
        print(f"An error occurred: {error}")
