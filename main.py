from langgraph.graph import StateGraph
from typing import List
import json
from scripts.agent import AgentSQL  # Assumendo che il tuo codice sia salvato in agent_sql.py
import pandas as pd
# Funzione principale
def main():
    
    # Inizializza l'agente SQL
    agente = AgentSQL()
    df=load_csv("domande.csv")
    questions = df['Question'].tolist()[80:]
    row_ids = []
    responses=[]
    image_data = agente.graph.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as file:
        file.write(image_data)
    id=81
    for question in questions:
        initial_state = {
        "question": question,
        }
        config = None  # Replace with actual RunnableConfig if applicable
        stream_mode = 'values'  # This is the default, but you can change it
        output_keys = None  # Use if specific keys from the output are needed
        interrupt_before = None  # Use to specify interruptions before processing
        interrupt_after = None  # Use to specify interruptions after processing
        debug = None  # Enable debugging if needed
        kwargs = {}  # Additional keyword arguments if required
        result=agente.graph.invoke(initial_state)
        ids = result["ids"]
        if isinstance(ids, list):
            if len(ids)>1:
                result_str = ",".join(map(str, ids))  # Concatena i valori della lista
            elif len(ids)==1:
                result_str = str(ids[0])
            else:
                result_str="1"
        responses.append(result_str)
        row_ids.append(id)
        print(id)
        id += 1
        

    # Crea un DataFrame per salvare i risultati
        output_df = pd.DataFrame({
            "row_id": row_ids,
            "result": responses
        })

    # Salva il DataFrame in un file CSV
        output_df.to_csv("output_test3.csv", index=False)
        
        
def load_csv(file_path):
    """Load CSV and return a DataFrame."""
    df = pd.read_csv(file_path)
    return df

if __name__ == "__main__":
    main()

