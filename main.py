from langgraph.graph import StateGraph
from typing import List
import json
from scripts.agent import AgentSQL  # Assumendo che il tuo codice sia salvato in agent_sql.py
import pandas as pd
# Funzione principale
def main():
    print("Avvio dell'Agent SQL...")
    
    # Inizializza l'agente SQL
    agent = AgentSQL()
    df=load_csv("domande.csv")
    questions = df['Question'].tolist()
    print("q",questions)
    image_data = agent.graph.get_graph(xray=True).draw_mermaid_png()
    with open("graph.png", "wb") as file:
        file.write(image_data)


    for question in questions:
        initial_state = {
        "question": question,
        }
        result=agent.graph.invoke(initial_state)
        
def load_csv(file_path):
    """Load CSV and return a DataFrame."""
    df = pd.read_csv(file_path)
    print("First 5 rows of the dataset:")
    print(df.head())
    return df

if __name__ == "__main__":
    main()

