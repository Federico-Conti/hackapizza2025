from langchain_ibm import WatsonxLLM

class Restaurant:
    def __init__(self, name="", planet="", chef=None):
        self.name = name
        self.planet = planet
        self.chef = chef if chef else Chef()

    
class Chef:
    def __init__(self, name="", restaurant=None, psionica=0, temporale=0, gravitazionale=0, antimateria=0, magnetica=0, quantistica=0, luce=0):
        self.name = name
        self.restaurant = restaurant if restaurant else Restaurant()
        self.psionica = psionica
        self.temporale = temporale
        self.gravitazionale = gravitazionale
        self.antimateria = antimateria
        self.magnetica = magnetica
        self.quantistica = quantistica
        self.luce = luce


class Dish:
    def __init__(self, ingredients=None, techniques=None):
        self.ingredients = ingredients if ingredients else []
        self.techniques = techniques if techniques else []


watsonx_llm = WatsonxLLM(
    model_id="google/flan-ul2",
    url="https://us-south.ml.cloud.ibm.com",
    apikey="*****",
    project_id="*****",
)    






