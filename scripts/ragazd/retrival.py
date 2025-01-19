from azure.search.documents.models import VectorizedQuery
import os
from typing import Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables from the specified file
load_dotenv(override=True)

# Constants for environment variables
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT_2")
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
    
def retrive_sources(query:str):
    query_embedding = generate_embeddings(query)

    vector_query = VectorizedQuery(
        vector=query_embedding, 
        k_nearest_neighbors=50, 
        fields="embedding"
    )

    results = getSearchClient().search(
        search_text=None,
        vector_queries=[vector_query],
        top=5
    )
    
    results_list = list(results)
    content = "\n".join(["Sources:\n " + doc['contet'] + "\n" for doc in results_list])
    return content


