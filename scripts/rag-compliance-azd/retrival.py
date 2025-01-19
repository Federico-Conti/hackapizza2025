from azure.search.documents.models import VectorizedQuery
from setting import generate_embeddings, search_client

def retrive_sources(query:str):
    query_embedding = generate_embeddings(query)

    vector_query = VectorizedQuery(
        vector=query_embedding, 
        k_nearest_neighbors=50, 
        fields="embedding"
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        top=3
    )
    
    results_list = list(results)
    content = "\n".join(["Sources:\n " + doc['contet'] + "\n" for doc in results_list])
    return content

