import os
from dotenv import load_dotenv
from enum import Enum
from langchain_core.messages import HumanMessage
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, AzureChatOpenAI
# from langchain_ibm import WatsonxLLM
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from supportManualeToDb import Base, pydantic_ParentTechnique_to_db
from tqdm import tqdm

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table

load_dotenv(override=True)

# Modelli Pydantic
class ChildTechnique(BaseModel):
    name: str = Field(description="Name of the childTechnique")

class ParentTechnique(BaseModel):
    name: str = Field(description=f"The name of the parent technique, often followed by a brief description of its category.")
    techniques: list[ChildTechnique] = Field(description="A list containing subcategories with respect to the macrocategory.")


class ListMacro(BaseModel):
    macrocategories: list[str] = Field(description="The name of the macrocategory, often followed by a brief description of its category. It contains some subcategories.")


llm = AzureChatOpenAI(
    deployment_name="gpt-4o",  # "llama-3.3-70b-versatile",
    temperature=0,
)

def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


engine = create_engine('sqlite:///manuale.db', echo=True)
create_tables(engine)
session = Session(engine)

### Processing CHEF
processedDocumentsPath = "capitoli"
for file_ in tqdm(os.listdir(processedDocumentsPath)):
    if file_.endswith("_3.txt") or file_.endswith("_4.txt") or file_.endswith("_5.txt"):
        
        doc_path = f"{processedDocumentsPath}/{file_}"
        print(f"Processing: {doc_path}")  # Replace with your processing logic

        with open(doc_path, "r", encoding="utf-8") as f:
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
                    You have to provide as answer a list containing all the macrocategory of the technique.
                    """,
                )
            ]

        model_structured = llm.with_structured_output(ListMacro)
        answer_macrocategories = model_structured.invoke(msg)
        macrocategories = answer_macrocategories.macrocategories
        # print()

        
        for macro_cat in macrocategories:
            print(macro_cat)
            msg = [
                    HumanMessage(
                        content=f"""
                        You're an expert document reader. Your role is to read the following document and to store important information using a structured
                        ouput. 
                        Here is the document that you have to process:
                        [START DOCUMENT]
                        {txt_}
                        [END DOCUMENT]
                        You have to find the parentTechnique and childTechnique associated to: {macro_cat}
                        """,
                    )
                ]

            model_structured = llm.with_structured_output(ParentTechnique)
            answer = model_structured.invoke(msg)
            print(answer)

            technique_db = pydantic_ParentTechnique_to_db(answer)
            session.add(technique_db)

        
session.commit()
session.close()
