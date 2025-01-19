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
from scripts.ragazd.retrival import retrive_sources
from scripts.csvTool import get_planets_within_distance
import operator
import json
import os
tools=[get_planets_within_distance]


load_dotenv(override=True)
db = SQLDatabase.from_uri("sqlite:///restaurants.db")
llm = AzureChatOpenAI(
    deployment_name="gpt-4o",  # "llama-3.3-70b-versatile",
    temperature=0,

)
file_path = "Data/Misc/dish_mapping.json"

with open(file_path, 'r', encoding='utf-8') as file:
    dishes_data = json.load(file)


class Filter(BaseModel):
    ingredients:bool= Field(
        description="Flag if the query involve ingredients criteria"
    )
    tecniques:bool= Field(
        description="Flag if the query involve tecniques criteria"
    )
    distances:bool= Field(
        description="Flag if the query involve distances criteria"
    )
    licenses:bool= Field(
        description="Flag if the query involve license criterias and compliance"
    )
class AgentState(TypedDict):
    question:str
    generation:Annotated[list, operator.add]
    names:list[str]
    ids:Annotated[list, operator.add]
    filters:dict
    distance_d:str=""
class DishNames(BaseModel):
    names:list[str]= Field(
        description="Names of all dishes into the generated text"
    )
class SQLData(BaseModel):
    generation:list[str]= Field(
        description="Sentence that has the tool data"
    )
class RAGModel(BaseModel):
    output:str= Field(
        description="Output about rephrased after new information"
    )


class AgentSQL():
    def __init__(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("prep",self.prep_node)
        workflow.add_conditional_edges(
        "prep",
            self.decide_for_distance,
            {
                "meter": "meter",
                "no_action": "answer_with_sql",
            },
        )
        workflow.add_node("answer_with_sql",self.answer_sql)
        workflow.add_node("get_names",self.get_name_node)
        workflow.add_node("get_ids",self.get_ids)
        workflow.add_node("rag",self.rag_node)
        workflow.add_node("meter",self.meter_node)
        workflow.add_node("solver",self.solver)
        workflow.add_edge(START,"prep")
        workflow.add_edge("prep","answer_with_sql")
        workflow.add_conditional_edges(
        "answer_with_sql",
            self.decide,
            {
                "rag": "rag",
                "no_action": "get_names",
            },
        )
        workflow.add_edge("rag","get_names")
        workflow.add_edge("meter","answer_with_sql")
        workflow.add_edge("get_names","get_ids")
        workflow.add_edge("get_ids","solver")
        workflow.add_edge("solver",END)
        
        self.graph = workflow.compile()
        
    def decide(self,state):
        print("state",state["question"],state["filters"])
        if(state["filters"]["licenses"]):
            return "rag"
        else:
         return "no_action"
    def decide_for_distance(self,state):
        if(state["filters"]["distances"]):
            return "meter"
        else:
            return "no_action"

    def prep(self):
        structured_llm_grader = llm.with_structured_output(Filter)
        # Prompt
        system = """You are an expert evaluator that needs to scrape information from the user question"""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question}"),
            ]
        )
        return answer_prompt | structured_llm_grader
    
        
    def prep_node(self,state):
        result=self.prep().invoke({"question":state["question"]})
        filters=Filter(ingredients=result.ingredients,tecniques=result.tecniques,distances=result.distances,licenses=result.licenses).dict()
        return {"filters":filters}
    def meter(self):
        llm_with_tools=llm.bind_tools(tools=tools)
        # Prompt
        system = """You are an expert evaluator about planet distance that can evaluate the distance between planets using your tools"""
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question}"),
            ]
        )
        return answer_prompt | llm_with_tools
    
        
    def meter_node(self,state):
        result=self.meter().invoke({"question":state["question"]})
        print("METER_NODE",result)
        return {"distance_d":result}
    def rag(self,state):
        structured_llm_outputter = llm.with_structured_output(RAGModel)
        # Prompt
        system = """
        You are an assistant for refine the output of the given question your scope is only rephrase with right value the Output. Be consistent and don't give other infos.If you don't know the answer don't change generation text.\n[IMPORTANT] IF YOU CAN?T ANSWER DON'T TELL ME AND DON?T CHANGE NOTHING.
        Question: {question}
        Output: {output} 
        Context: {context} 
        Answer:
        """
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "User question: \n\n {question} \n\n LLM output: {output} , Context of the knowledge: {context}"),
            ]
        )
        return answer_prompt | structured_llm_outputter

    def rag_node(self,state):
        query_data=state["question"]
        retrieved_docs = retrive_sources(query_data)
        result=self.rag(state).invoke({"question":state["question"],"output":str(state["generation"]),"context":retrieved_docs})
        print("RAGGGGG\n\n\n\n",result.output)
        return {"generation": [result.output]}

    def answer_sql(self,state):
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        planets=None
        schema = db.get_table_info()
        if("distance_d" in state):
            planets=state["distance_d"]
        structured=llm.with_structured_output(SQLData)
        prompt_template = """
        You are an agent designed to interact with a SQL database.

        IMPORTANT
        To start you should ALWAYS look at the tables in the database to see what you can query.
        Do NOT skip this step.
        [SCHEMA]
        {schema}
        

        {planets}

        Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
        Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
        You can order the results by a relevant column to return the most interesting examples in the database.

        You have access to tools for interacting with the database.
        Only use the below tools. Only use the information returned by the below tools to construct your final answer.
        You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

        DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP,CREATE etc.) to the database.

        Then you should query the schema of the most relevant tables.
        """
        if planets:
            system_message = prompt_template.format(dialect="SQLite", top_k=100,schema=schema,planets="[DISTANCE DETAILS SPOTTED] \n You have to consider only dishes from these planets \n"+str(planets))
        else:
            system_message = prompt_template.format(dialect="SQLite", top_k=100,schema=schema,planets=None)
        agent_executor = create_react_agent(
            llm, toolkit.get_tools(), state_modifier=system_message
        )
        example_query=state["question"]
        result=agent_executor.invoke({"messages":[("user", example_query)]})
        return {"generation":[result]}
    
    def get_name_node(self,state):
        
        result=self.get_names().invoke({"question":state["question"],"generation":str(state["generation"])})

        return {"names":result.names}
    def get_names(self):
        structured_llm_grader = llm.with_structured_output(DishNames)

        # Prompt
        system = """You are a scraper assistant thats converts general information about dishes in a Dish names. \n Another task is that you can receive tool_call with insight on dishes"""
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
        print("IDS",state["ids"])
        return {"messages":[AIMessage(content=str(state["ids"]))]}



    
        