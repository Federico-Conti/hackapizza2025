from azure.search.documents.models import VectorizedQuery
from scripts.ragcomplianceazd import setting

def retrive_sources(query:str):
    print("QUERYYYY ",query)
    query_embedding = setting.generate_embeddings(query)

    vector_query = VectorizedQuery(
        vector=query_embedding, 
        k_nearest_neighbors=50, 
        fields="embedding"
    )

    results = setting.getSearchClient().search(
        search_text=None,
        vector_queries=[vector_query],
        top=5
    )
    
    results_list = list(results)
    content = "\n".join(["Sources:\n " + doc['contet'] + "\n" for doc in results_list])
    return content


