import os
import pandas as pd

from dotenv import load_dotenv
from enum import Enum
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_ibm import WatsonxLLM
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from supportMenuToDb import Base, pydantic_to_db, pydantic_Menu_to_db
from tqdm import tqdm


df = pd.read_csv("Data/Misc/Distanze.csv")
planetNames = list(df.columns)
planetNames.pop(0)
planet_str = ', '.join([f'element{i+1}' for i in range(len(planetNames))])

class Chef(BaseModel):
    """Representation of a Chef with various skills."""
    name: str = Field(description="Name of the chef")
    psionica: int = Field(description="Psionic ability level")
    temporale: int = Field(description="Temporal ability level")
    gravitazionale: int = Field(description="Gravitational ability level")
    antimateria: int = Field(description="Antimatter ability level")
    magnetica: int = Field(description="Magnetic ability level")
    quantistica: int = Field(description="Quantum ability level")
    luce: int = Field(description="Light ability level")


class Dish(BaseModel):
    """Representation of a Dish"""
    ingredients: list[str] = Field(description="List of the ingredients in the dish")
    techniques: list[str] = Field(description="List of the techniques used to prepare the dish")


class Menu(BaseModel):
    """Representation of a Menu with all the dishes"""
    dishes: list[Dish] = Field(description="List of all the dishes in the menu")
    # restaurant: Restaurant = Field(default_factory=Restaurant, description="Name of the restaurant")


class Restaurant(BaseModel):
    """Representation of a Restaurant, including its chef."""
    restaurantName: str = Field(description="Name of the restaurant")
    planet: str = Field(description=f"Planet where the restaurant is located, these are the possible values: {planet_str}")
    chef: Chef = Field(description="Chef of the restaurant")
    # menu: Menu = Field(default_factory=Menu, description="Menu of the restaurant")


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


dotenv_path = 'env.download'
load_dotenv(dotenv_path)

# ibm_api_key = os.getenv('IBM_API_KEY')
# team_id = os.getenv('TEAM_ID')
# endpoint_url = os.getenv('ENDPOINT_URL')
# project_id = os.getenv('PROJECT_ID')
groq_api_key = os.getenv('GROQ_API_KEY')


# llm = ChatGroq(
#     model="mixtral-8x7b-32768",  # "llama-3.3-70b-versatile",
#     temperature=0,
# )
llm = ChatOpenAI(
    model="gpt-4o",  # "llama-3.3-70b-versatile",
    temperature=0,

)

# print(ibm_api_key)
# print(team_id)

engine = create_engine('sqlite:///restaurants2.db', echo=True)
create_tables(engine)
session = Session(engine)

# processedDocumentsPath = "Markdown/Menu_MD"
# for doc_ in tqdm(os.listdir(processedDocumentsPath)[:1]):

#     doc_path = f"{processedDocumentsPath}/{doc_}"
#     doc_path = "C:/Users/lucad/OneDrive/Desktop/hackapizza2025/Markdown/ProcessedDocuments/Anima Cosmica/Anima Cosmica_MENU.md"
#     print(f"Processing: {doc_path}")  # Replace with your processing logic

#     with open(doc_path, "r", encoding="utf-8") as f:
#         txt_ = f.read()

#     msg = [
#             HumanMessage(
#                 content=f"""
#                 You're an expert document reader. Your role is to read the following document and to store important information using a structured
#                 ouput. 
#                 Here is the document that you have to process:
#                 [START DOCUMENT]
#                 {txt_}
#                 [END DOCUMENT]
#                 """,
#             )
#         ]

#     model_structured = llm.bind_tools([Menu], strict=True)
#     answer = model_structured.invoke(msg)

#     # model_structured = llm.with_structured_output(Restaurant)
#     # answer = model_structured.invoke(msg)
#     print(answer)

#     # restaurant_db = pydantic_to_db(answer)
#     # session.add(restaurant_db)



### Processing CHEF
processedDocumentsPath = "Markdown/ProcessedDocuments"
for fold_doc in tqdm(os.listdir(processedDocumentsPath)[:2]):
    docs = os.listdir(f"{processedDocumentsPath}/{fold_doc}")
    chef_doc = next((doc for doc in docs if doc.endswith("_CHEF.md")), None)
    if chef_doc:
        chef_doc_path = f"{processedDocumentsPath}/{fold_doc}/{chef_doc}"
        print(f"Processing: {chef_doc_path}")  # Replace with your processing logic

        with open(chef_doc_path, "r", encoding="utf-8") as f:
            txt_ = f.read()

        msg = [
                HumanMessage(
                    content=f"""
                    You're an expert document reader. Your role is to read the following document and to store important information using a structured
                    ouput. 
                    Here is the document that you have to process:
                    [START DOCUMENT]
                    {txt_}
                    [END DOCUMENT]
                    """,
                )
            ]

        model_structured = llm.with_structured_output(Restaurant)
        answer = model_structured.invoke(msg)
        print(answer)

        restaurant_db = pydantic_to_db(answer)
        session.add(restaurant_db)

    menu_doc = next((doc for doc in docs if doc.endswith("_MENU.md")), None)
    if menu_doc:
        menu_doc_path = f"{processedDocumentsPath}/{fold_doc}/{menu_doc}"
        print(f"Processing: {menu_doc_path}")  # Replace with your processing logic

        with open(menu_doc_path, "r", encoding="utf-8") as f:
            txt_ = f.read()

        msg = [
                HumanMessage(
                    content=f"""
                    You're an expert document reader. Your role is to read the following document and to store important information using a structured
                    ouput. 
                    Here is the document that you have to process:
                    [START DOCUMENT]
                    {txt_}
                    [END DOCUMENT]
                    """,
                )
            ]

        model_structured = llm.with_structured_output(Menu)
        answer = model_structured.invoke(msg)
        print(answer)

        menu_db = pydantic_Menu_to_db(answer, restaurant_db)
        session.add(menu_db)


# processedDocumentsPath = "Markdown/ProcessedDocuments"
# idx = 1
# for fold_doc in tqdm(os.listdir(processedDocumentsPath)):
#     docs = os.listdir(f"{processedDocumentsPath}/{fold_doc}")
#     chef_doc = next((doc for doc in docs if doc.endswith("_MENU.md")), None)
#     if chef_doc:
#         chef_doc_path = f"{processedDocumentsPath}/{fold_doc}/{chef_doc}"
#         print(f"Processing: {chef_doc_path}")  # Replace with your processing logic

#         with open(chef_doc_path, "r", encoding="utf-8") as f:
#             txt_ = f.read()

#         msg = [
#                 HumanMessage(
#                     content=f"""
#                     You're an expert document reader. Your role is to read the following document and to store important information using a structured
#                     ouput. 
#                     Here is the document that you have to process:
#                     [START DOCUMENT]
#                     {txt_}
#                     [END DOCUMENT]
#                     """,
#                 )
#             ]

#         model_structured = llm.bind_tools([Restaurant], strict=True)
#         answer = model_structured.invoke(msg)
#         model_structured = llm.with_structured_output(Menu)
#         answer = model_structured.invoke(msg)
#         print(answer)

#         menuDB = pydantic_Menu_to_db(answer, idx)
#         session.add(menuDB)
#         idx += 1


session.commit()
session.close()


# parameters = {
#     "max_new_tokens": 200,
#     "min_new_tokens": 0,
#     "temperature": 0,
# }

# watsonx_llm = WatsonxLLM(
#     model_id="meta-llama/llama-3-3-70b-instruct",
#     url=endpoint_url,
#     apikey=ibm_api_key,
#     project_id=project_id,
#     params=parameters
# )


# msg = [
#         HumanMessage(
#             content=f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
#             You're an expert document reader. Your role is to read the following document and to store important information using a structured
#             ouput. 
#             Here is the document that you have to process:
#             [START DOCUMENT]
#             {txt_}
#             [END DOCUMENT]
#             Answer by filling the following dict in json format:
#             Restaurant: {{
#                 "name": # str, description="Name of the restaurant"
#                 "planet": # str, description="Planet where the restaurant is located, these are the possible values: {planet_str}"
#             }}
#             Chef: {{
#                 "name": # str, description = "Name of the chef"
#                 "psionica": # int, description="Psionic ability level"
#                 "temporale": # int, description="Temporal ability level"
#                 "gravitazionale": # int, description="Gravitational ability level"
#                 "antimateria": # int, description="Antimatter ability level"
#                 "magnetica": # int, description="Magnetic ability level"
#                 "quantistica": # int, description="Quantum ability level"
#                 "luce": #int, description="Light ability level"
#             }}
#             <|eot_id|><|start_header_id|>assistant<|end_header_id|>""",
#         )
#     ]



#print(msg)