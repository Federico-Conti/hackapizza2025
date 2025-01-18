import os
import numpy as np
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

# Load environment variables
AZURE_SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = "2024-10-01-preview"
AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME = "ict-chatict_embeddingada002"

credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
index_name = "questionsearch"
search_client = SearchClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=credential)

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def generate_embeddings(text: str):
    embeddings_response = client.embeddings.create(
        model=AZURE_OPENAI_EMBEDDING_DEPLOYED_MODEL_NAME, 
        input=text, 
        dimensions=1536
    )
    return embeddings_response.data[0].embedding
