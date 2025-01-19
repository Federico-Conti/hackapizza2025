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
    questions = df['Question'].tolist()
    image_data = agente.graph.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as file:
        file.write(image_data)
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

        
def load_csv(file_path):
    """Load CSV and return a DataFrame."""
    df = pd.read_csv(file_path)
    return df

if __name__ == "__main__":
    main()

