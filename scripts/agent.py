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
from langchain_openai import ChatOpenAI,AzureChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import operator
import json
import os

# Specifica il percorso del file JSON

load_dotenv(override=True)
db = SQLDatabase.from_uri("sqlite:///restaurants.db")
llm = AzureChatOpenAI(
    deployment_name="gpt-4o-mini",  # "llama-3.3-70b-versatile",
    temperature=0,

)
file_path = "Data/Misc/dish_mapping.json"

with open(file_path, 'r', encoding='utf-8') as file:
    dishes_data = json.load(file)

class AgentState(TypedDict):
    question:str
    generation:str
    names:list[str]
    ids:Annotated[list, operator.add]

class DishNames(BaseModel):
    names:list[str]= Field(
        description="Names of all dishes into the generated text"
    )
class SQLData(BaseModel):
    generation:list[str]= Field(
        description="Sentence that has the tool data"
    )


class AgentSQL():
    def __init__(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("answer_with_sql",self.answer_sql)
        workflow.add_node("get_names",self.get_name_node)
        workflow.add_node("get_ids",self.get_ids)
        workflow.add_node("solver",self.solver)
        workflow.add_edge(START,"answer_with_sql")
        workflow.add_edge("answer_with_sql","get_names")
        workflow.add_edge("get_names","get_ids")
        workflow.add_edge("get_ids","solver")
        workflow.add_edge("solver",END)
        
        self.graph = workflow.compile()



    def answer_sql(self,state):
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        schema = db.get_table_info()
        structured=llm.with_structured_output(SQLData)
        prompt_template = """
        You are an agent designed to interact with a SQL database.

        IMPORTANT
        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        [SCHEMA]
        {schema}

        Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
        You can order the results by a relevant column to return the most interesting examples in the database.

        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP,CREATE etc.) to the database.

        Then you should query the schema of the most relevant tables.
        """
        system_message = prompt_template.format(dialect="SQLite", top_k=100,schema=schema)

        agent_executor = create_react_agent(
            llm, toolkit.get_tools(), state_modifier=system_message
        )
        
        
        example_query=state["question"]
        result=agent_executor.invoke({"messages":[("user", example_query)]})
        return {"generation":result}
    
    def get_name_node(self,state):
        
        result=self.get_names().invoke({"question":state["question"],"generation":state["generation"]})

        return {"names":result.names}
    def get_names(self):
        structured_llm_grader = llm.with_structured_output(DishNames)

        # Prompt
        system = """You are a scraper assistant thats converts tool_call and data in dishes found"""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
            ]
        )

        return answer_prompt | structured_llm_grader
        
    def get_ids(self,state):
        a={"ids": [dishes_data[name] for name in state["names"] if name in dishes_data]}
        return a
    def solver(self,state):
        return {"messages":[AIMessage(content=str(state["ids"]))]}



    
        