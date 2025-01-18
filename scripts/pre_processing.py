import json
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from enum import Enum
from typing import Tuple, Dict, List

# Enum per i filtri
class FilterType(Enum):
    LICENZA = "LICENZE"
    CHEF = "CHEF"
    RISTORANTE = "RISTORANTE"
    PIANETA = "PIANETA"
    TECNICA = "TECNICA"
    INGREDIENTE = "INGREDIENTE"
    ALTRO = "ALTRO"

# Credenziali per il modello Watsonx
credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key="AwfatdGk3za6K3e6Zn2KSE4WM4VBAjgMAxKSLM6IdilQ"
)

# Inizializzazione del modello
model = ModelInference(
    model_id="mistralai/mistral-large",
    credentials=credentials,
    project_id="e8e3fe0c-90f3-4897-858a-e7f659d21bb2",
    params={
        "max_tokens": 200
    }
)

def process_query(query: str) -> Tuple[Dict[str, bool], List[str]]:
    """
    Processa una query utente e restituisce un dizionario di filtri e una lista di parole chiave.

    Args:
        query (str): La domanda dell'utente.

    Returns:
        Tuple[Dict[str, bool], List[str]]: Dizionario con i filtri attivi e lista di parole chiave.
    """
    # Prompt per il modello
    prompt = f"""
    Analizza la seguente domanda utente:
    "{query}"
    
    Restituisci un JSON con due campi:
    1. "filters": un dizionario con le chiavi corrispondenti ai valori dell'enum [{', '.join([f.value for f in FilterType])}], 
       dove il valore è True se il filtro deve essere applicato e False altrimenti.
       Se identifichi filtri che non sono all'interno dell'ENUM metti il campo ALTRO a TRUE
       
    2. "keywords": una lista di parole chiave estratte dalla domanda che possono essere usate per la ricerca nei documenti.
    
    Esempio di output:
    {{
        "filters": {{
            "LICENZE": false,
            "CHEF": false,
            "RISTORANTE": false,
            "PIANETA": false,
            "TECNICA": true,
            "INGREDIENTE": false,
            "ALTRO": false
        }},
        "keywords": ["Fermentazione Quantico Biometrica", "Affumicatura tramite Big Bang Microcosmico", "Cottura Sottovuoto Frugale Energeticamente Negativa"]
    }}
    """
    
    # Chiamata al modello
    result = model.chat(messages=[{'role': 'user', 'content': prompt}])
    response = result['choices'][0]['message']['content']
    
    # Pulizia della risposta, rimuovendo "json" se presente all'inizio
    response_cleaned = response.strip()
    response_cleaned = response_cleaned[7:len(response_cleaned) - 4]
    
    # Parsing della risposta
    try:
        parsed_response = json.loads(response_cleaned)  # Converte in dizionario
        filters = parsed_response.get("filters", {})
        keywords = parsed_response.get("keywords", [])
    except json.JSONDecodeError as e:
        print("Errore nel parsing della risposta del modello:", e)
        filters = {}
        keywords = []
    
    return filters, keywords
