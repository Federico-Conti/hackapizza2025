import pandas as pd
from langchain_core.tools import tool

# import os

# from dotenv import load_dotenv
# from pandasai import SmartDataframe
# from pandasai.llm import IBMwatsonx, OpenAI
# from langchain_core.tools import tool


@tool
def get_planets_within_distance(planet_name, max_distance):
    """This function is used to select planets that are within a certain distance radius (indicated in light years) from the input planet"""
    # Load the distance matrix
    data = pd.read_csv("Data/Misc/Distanze.csv")
    data.set_index(data.columns[0], inplace=True)

    if planet_name not in data.index:
        raise ValueError(f"Planet '{planet_name}' not found in the distance matrix.")

    distances = data.loc[planet_name]
    close_planets = distances[distances <= max_distance].index.tolist()
    # close_planets.remove(planet_name)

    return close_planets


# print(get_planets_within_distance("Krypton", 317))

# def FindPlanet(query):

#     response = df_agent.chat(f"""
#     You're an expert Python developer. Your role is to generate the python code to extract information from a csv file.
#     The csv file contains a square matrix of distances between some planets. Distances are indicated in light years.
#     There are the columns: {planet_str}, that indicates planet names.
#     The number of rows is equal to the number of column - 1 and contains exactly the same order (on the diagonal there is the same planet).
#     [QUESTION] {query}
#     [END QUESTION]
#     This is the dataframe:
#     {example_}
#     The output must return a pandas dataframe.
#     """)
#     # print(response)

#     indexes = response.iloc[:, 0].tolist()

#     if isinstance(indexes[0], str):
#         parsed_planets = indexes
#     else:
#         parsed_planets = [planetNames[i] for i in indexes]

#     print("Indexes or Names:", indexes)
#     print("Parsed Planets:", parsed_planets)

#     return parsed_planets


# dotenv_path = 'env.download'
# load_dotenv(dotenv_path)
# llm = OpenAI(model="gpt-4o",
#              temperature=0)
# df_agent = SmartDataframe("Data/Misc/Distanze.csv",
#                           config={"llm": llm}
#                           )

# df_ = pd.read_csv("Data/Misc/Distanze.csv")
# planetNames = list(df_.columns)
# planet_str = ', '.join([f'element{i+1}' for i in range(len(planetNames))])
# planetNames.pop(0)
# example_ = df_.head(5)



