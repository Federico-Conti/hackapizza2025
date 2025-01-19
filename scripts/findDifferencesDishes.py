import json
import sqlite3
import unicodedata

def normalize_string(input_str):
    """
    Normalize a string by:
    1. Converting Unicode escape sequences
    2. Normalizing special characters
    3. Standardizing apostrophes and quotes
    """
    # Handle None values
    if input_str is None:
        return ""
    
    # Convert escaped Unicode sequences
    if isinstance(input_str, str):
        input_str = input_str.encode('utf-8').decode('unicode-escape')
    
    # Normalize Unicode characters
    normalized = unicodedata.normalize('NFC', input_str)
    
    # Standardize different types of apostrophes and quotes
    replacements = {
        ''': "'",  # Right single quotation mark
        ''': "'",  # Left single quotation mark
        '"': '"',  # Left double quotation mark
        '"': '"',  # Right double quotation mark
        '′': "'",  # Prime
        '‵': "'",  # Reversed prime
        '´': "'",  # Acute accent
        '`': "'",  # Grave accent
    }
    
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    
    return normalized

# Load JSON file
with open('Data/Misc/dish_mapping.json', 'r', encoding="utf-8") as file:
    json_data = json.load(file)

# Extract and normalize keys from the JSON
json_keys = [normalize_string(key) for key in json_data.keys()]
print(f"Total JSON entries: {len(json_keys)}")

# Connect to the database
conn = sqlite3.connect('main.db')
cursor = conn.cursor()

# Fetch and normalize names from the Dish table
cursor.execute("SELECT name FROM Dish")
db_names = [normalize_string(row[0]) for row in cursor.fetchall()]
print(f"Total DB entries: {len(db_names)}")

# Find duplicates in database
seen = set()
duplicates = []
for name in db_names:
    if name in seen:
        duplicates.append(name)
    else:
        seen.add(name)

print("\nDuplicate names in DB:", duplicates)
print(f"Number of duplicates: {len(duplicates)}")

# Find names in the JSON that are not in the database
names_not_in_db = []
for key in json_keys:
    normalized_key = normalize_string(key)
    if normalized_key not in db_names:
        names_not_in_db.append(key)

print(f"\nNames in JSON but not in DB ({len(names_not_in_db)}):")
for name in sorted(names_not_in_db):
    print(f"- {name}")

# Find names in the database that are not in the JSON
names_not_in_json = []
for name in db_names:
    normalized_name = normalize_string(name)
    if normalized_name not in [normalize_string(k) for k in json_keys]:
        names_not_in_json.append(name)

print(f"\nNames in DB but not in JSON ({len(names_not_in_json)}):")
for name in sorted(names_not_in_json):
    print(f"- {name}")

# Close the database connection
conn.close()

# import json
# import sqlite3
# import unicodedata


# import json
# import sqlite3
# import unicodedata

# # Function to normalize special characters in strings
# def normalize_string(input_str):
#     return unicodedata.normalize('NFC', input_str)

# # Load JSON file
# with open('Data/Misc/dish_mapping.json', 'r', encoding="utf-8") as file:
#     json_data = json.load(file)

# # Extract keys from the JSON
# # json_keys = list(json_data.keys())
# json_keys = [normalize_string(key) for key in json_data.keys()]
# print(len(json_keys))
# import sqlite3

# # Connect to the database
# conn = sqlite3.connect('main.db')
# cursor = conn.cursor()

# # Fetch names from the Dish table
# cursor.execute("SELECT name FROM Dish")
# db_names = [row[0] for row in cursor.fetchall()]
# print(len(db_names))
# seen = set()
# duplicates = []

# # Loop through the list and find duplicates
# for name in db_names:
#     if name in seen:
#         duplicates.append(name)
#     else:
#         seen.add(name)

# print("Duplicate names:", duplicates)

# # Find names in the JSON that are not in the database
# names_not_in_db = [key for key in json_keys if key not in db_names]

# print("Names not in DB:", names_not_in_db)
# print(len(names_not_in_db))