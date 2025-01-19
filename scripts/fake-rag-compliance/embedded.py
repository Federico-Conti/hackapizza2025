import os
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import Embeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import json

dotenv_path = '../../.env.local'
load_dotenv(dotenv_path)
ibm_api_key = os.getenv('IBM_API_KEY')
team_id = os.getenv('TEAM_ID')
endpoint_url = os.getenv('ENDPOINT_URL')
project_id = os.getenv('PROJECT_ID')


def process_embeddings(chunks:list[str]):
    client = Credentials(
            url=endpoint_url,
            api_key=ibm_api_key
        )

    embed_params = {
        EmbedParams.TRUNCATE_INPUT_TOKENS: 500,
        EmbedParams.RETURN_OPTIONS: {
            'input_text': False
        }
    }

    embedding = Embeddings(
        model_id="intfloat/multilingual-e5-large",
        credentials=client,
        params=embed_params,
        project_id=project_id,
    )
    embedding_result = embedding.embed_documents(chunks)  
    return embedding_result