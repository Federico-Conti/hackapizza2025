import os
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

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table



link_technique = Table(
    'link_technique',
    Base.metadata,
    Column('parent_technique_id', Integer, ForeignKey('parent_technique.id')),
    Column('child_technique_id', Integer, ForeignKey('child_technique.id'))
)

class ChildTechniqueDB(Base):
    """SQLAlchemy model for the ChildTechnique table"""
    __tablename__ = 'child_technique'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Relationship with ParentTechnique through junction table
    parentTechniques = relationship('ParentTechniqueDB', secondary=link_technique, back_populates='child_techniques')


class ParentTechniqueDB(Base):
    """SQLAlchemy model for the ParentTechnique table"""
    __tablename__ = 'parent_technique'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # Relationships
    child_techniques = relationship('ChildTechniqueDB', secondary=link_technique, back_populates='parentTechniques')

# Funzione per la conversione da Pydantic a DB
def pydantic_ParentTechnique_to_db(parent_technique_pydantic):
    child_techniques_db = []
    for child_technique_pydantic in parent_technique_pydantic.techniques:
        child_technique_db = ChildTechniqueDB(name=child_technique_pydantic.name)
        child_techniques_db.append(child_technique_db)

    # Crea il parent technique
    parent_technique_db = ParentTechniqueDB(
        name=parent_technique_pydantic.name,
        child_techniques=child_techniques_db
    )

    return parent_technique_db


# Modelli Pydantic
class ChildTechnique(BaseModel):
    name: str = Field(description="Name of the childTechnique")


class ParentTechnique(BaseModel):
    """Representation of a ParentTechnique with all the child techniques"""
    name: str = Field(description="Name of the Parent technique")
    techniques: list[ChildTechnique] = Field(description="List of all the child techniques in the ParentTechnique")




llm = ChatOpenAI(
    model="gpt-4o",  # "llama-3.3-70b-versatile",
    temperature=0,

)


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


engine = create_engine('sqlite:///restaurants.db', echo=True)
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
                    """,
                )
            ]

        model_structured = llm.with_structured_output(ParentTechnique)
        answer = model_structured.invoke(msg)
        print(answer)

        restaurant_db = pydantic_to_db(answer)
        session.add(restaurant_db)

        
session.commit()
session.close()
