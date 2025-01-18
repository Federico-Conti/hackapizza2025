from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from pydantic import BaseModel, Field
from enum import Enum
from typing import List

# Enum per i filtri
class FilterType(Enum):
    LICENZE = "LICENZE"
    CHEF = "CHEF"
    RISTORANTE = "RISTORANTE"
    PIANETA = "PIANETA"
    TECNICA = "TECNICA"
    INGREDIENTE = "INGREDIENTE"

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

def process_query(query: str) -> str:
    # Prompt per il modello
    prompt = f"""
    Analizza la seguente domanda utente:
    "{query}"
    
    Restituisci un JSON con due campi:
    1. "filters": un dizionario con le chiavi corrispondenti ai valori dell'enum [{', '.join([f.value for f in FilterType])}], 
       dove il valore è True se il filtro deve essere applicato e False altrimenti.
    2. "keywords": una lista di parole chiave estratte dalla domanda che possono essere usate per la ricerca nei documenti.
    
    Esempio di output:
    {{
        "filters": {{
            "LICENZE": false,
            "CHEF": false,
            "RISTORANTE": false,
            "PIANETA": false,
            "TECNICA": true
        }},
        "keywords": ["Fermentazione Quantico Biometrica", "Affumicatura tramite Big Bang Microcosmico", "Cottura Sottovuoto Frugale Energeticamente Negativa"]
    }}
    """
    
    # Chiamata al modello
    result = model.chat(messages=[{'role': 'user', 'content': prompt}])
    
    # Restituisce direttamente la stringa di risposta del modello
    return result['choices'][0]['message']['content']

# Esempio di query
query = """
Quali piatti preparati con la Fermentazione Quantico Biometrica includono Erba Pipa?
"""
response = process_query(query)

# Stampa del risultato
print("Risultato:", response)