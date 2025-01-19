import os
from dotenv import load_dotenv
from enum import Enum
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tqdm import tqdm

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table

Base = declarative_base()

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
