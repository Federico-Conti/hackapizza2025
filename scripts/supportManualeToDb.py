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

class ChildTechniqueDB(Base):
    """SQLAlchemy model for the ChildTechnique table"""
    __tablename__ = 'child_technique'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey('parent_technique.id'), nullable=False)

    # Relationship with ParentTechnique through junction table
    #parent_techniques = relationship('ParentTechniqueDB', secondary=link_technique, back_populates='child_techniques')
    parent = relationship('ParentTechniqueDB', back_populates='child_techniques')


class ParentTechniqueDB(Base):
    """SQLAlchemy model for the ParentTechnique table"""
    __tablename__ = 'parent_technique'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    # Relationships
    # child_techniques = relationship('ChildTechniqueDB', secondary=link_technique, back_populates='parent_techniques')
    child_techniques = relationship('ChildTechniqueDB', back_populates='parent', cascade='all, delete-orphan')


# Funzione per la conversione da Pydantic a DB
def pydantic_ParentTechnique_to_db(parent_technique_pydantic):

    print(parent_technique_pydantic.name)

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
