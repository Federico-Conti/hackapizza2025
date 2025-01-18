from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table


Base = declarative_base()

# dish_ingredient = Table(
#     'dish_ingredient',
#     Base.metadata,
#     Column('dish_id', Integer, ForeignKey('dish.id')),
#     Column('ingredient_name', String)
# )

# dish_technique = Table(
#     'dish_technique',
#     Base.metadata,
#     Column('dish_id', Integer, ForeignKey('dish.id')),
#     Column('technique_name', String)
# )

menu_dish = Table(
    'menu_dish',
    Base.metadata,
    Column('menu_id', Integer, ForeignKey('menu.id')),
    Column('dish_id', Integer, ForeignKey('dish.id'))
)

# Create the base class
class ChefDB(Base):
    """SQLAlchemy model for the Chef table"""
    __tablename__ = 'chef'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    psionica = Column(Integer, default=0)
    temporale = Column(Integer, default=0)
    gravitazionale = Column(Integer, default=0)
    antimateria = Column(Integer, default=0)
    magnetica = Column(Integer, default=0)
    quantistica = Column(Integer, default=0)
    luce = Column(Integer, default=0)

    # Relationship with Restaurant
    restaurants = relationship("RestaurantDB", back_populates="chef")


class RestaurantDB(Base):
    """SQLAlchemy model for the Restaurant table"""
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    planet = Column(String)
    chef_id = Column(Integer, ForeignKey('chef.id'))

    chef = relationship("ChefDB", back_populates="restaurants")
    menus = relationship("MenuDB", back_populates="restaurant")


class DishDB(Base):
    """SQLAlchemy model for the Dish table"""
    __tablename__ = 'dish'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    # One-to-many relationships for ingredients and techniques
    ingredients = relationship("DishIngredientDB", back_populates="dish", cascade="all, delete-orphan")
    techniques = relationship("DishTechniqueDB", back_populates="dish", cascade="all, delete-orphan")

    # Relationship with Menu through junction table
    menus = relationship('MenuDB', secondary=menu_dish, back_populates='dishes')


class DishIngredientDB(Base):
    """SQLAlchemy model for dish ingredients"""
    __tablename__ = 'dish_ingredient'

    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'))
    ingredient_name = Column(String)

    # Relationship with Dish
    dish = relationship("DishDB", back_populates="ingredients")


class DishTechniqueDB(Base):
    """SQLAlchemy model for dish techniques"""
    __tablename__ = 'dish_technique'

    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('dish.id'))
    technique_name = Column(String)

    # Relationship with Dish
    dish = relationship("DishDB", back_populates="techniques")


class MenuDB(Base):
    """SQLAlchemy model for the Menu table"""
    __tablename__ = 'menu'

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

    # Relationships
    restaurant = relationship("RestaurantDB", back_populates="menus")
    dishes = relationship("DishDB", secondary=menu_dish, back_populates='menus')
    


def create_tables(engine):
    """Create all tables in the database"""
    Base.metadata.create_all(engine)


def pydantic_to_db(restaurant_pydantic):
    """Convert Pydantic model to database models"""
    # First create the chef
    chef_db = ChefDB(
        name=restaurant_pydantic.chef.name,
        psionica=restaurant_pydantic.chef.psionica,
        temporale=restaurant_pydantic.chef.temporale,
        gravitazionale=restaurant_pydantic.chef.gravitazionale,
        antimateria=restaurant_pydantic.chef.antimateria,
        magnetica=restaurant_pydantic.chef.magnetica,
        quantistica=restaurant_pydantic.chef.quantistica,
        luce=restaurant_pydantic.chef.luce,
        livello_tecnologico=restaurant_pydantic.chef.livelloTecnologico
    )

    # Then create the restaurant
    restaurant_db = RestaurantDB(
        name=restaurant_pydantic.name,
        planet=restaurant_pydantic.planet,
        chef=chef_db
    )

    return restaurant_db


def pydantic_Menu_to_db(menu_pydantic, restaurant_db):
    dishes_db = []
    for dish_pydantic in menu_pydantic.dishes:
        dish_db = DishDB(name=dish_pydantic.name)

        # Add ingredients
        for ingredient in dish_pydantic.ingredients:
            ingredient_db = DishIngredientDB(ingredient_name=ingredient)
            dish_db.ingredients.append(ingredient_db)

        # Add techniques
        for technique in dish_pydantic.techniques:
            technique_db = DishTechniqueDB(technique_name=technique)
            dish_db.techniques.append(technique_db)

        dishes_db.append(dish_db)

    # Create the menu
    menu_db = MenuDB(
        restaurant=restaurant_db,
        dishes=dishes_db
    )

    return menu_db