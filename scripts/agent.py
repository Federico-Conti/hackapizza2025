from langgraph.graph import END, StateGraph, START
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from enum import Enum
from typing import Any, Dict, List, Annotated, Sequence, TypedDict, Literal,Optional
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_ibm import WatsonxLLM
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent



db = SQLDatabase.from_uri("sqlite:///restaurants.db")
llm = ChatOpenAI(
        model_id="meta-llama/llama-3-3-70b-instruct",
        url="https://us-south.ml.cloud.ibm.com",
        apikey="AwfatdGk3za6K3e6Zn2KSE4WM4VBAjgMAxKSLM6IdilQ",
        project_id="e8e3fe0c-90f3-4897-858a-e7f659d21bb2",
    )

toolkit = SQLDatabaseToolkit(db=db, llm=llm)


prompt_template = """
You are an agent designed to interact with a SQL database.

IMPORTANT
To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.

Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.

You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

Then you should query the schema of the most relevant tables.
"""
system_message = prompt_template.format(dialect="SQLite", top_k=1)

agent_executor = create_react_agent(
    powerfull_llm, toolkit.get_tools(), state_modifier=system_message
)
example_query = "Qual'è lo chef con il punteggio più alto nella skill chiamata psionica? table chef (chef)"

result=agent_executor.invoke(
    {"messages": [("user", example_query)]},
)
print(result)



# class AgentState(TypedDict):
#     question:str
#     tags: List[str]
#     keywords: List[str]
#     answer:str



 
    