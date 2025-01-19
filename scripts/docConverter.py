import os
import os
import pandas as pd


# Funzione per dividere il contenuto del file in sotto-file
def split_file(input_file):
    # Apriamo il file di input
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Troviamo tutte le sezioni che iniziano con '## Capitolo'
    chapters = content.split('## Capitolo')

    # Creiamo una cartella per i sotto-file
    output_dir = 'capitoli'
    os.makedirs(output_dir, exist_ok=True)

    # Scriviamo ogni capitolo in un file separato
    for i, chapter in enumerate(chapters[1:], start=1):
        chapter_title = f"Capitolo_{i}"
        output_file = os.path.join(output_dir, f"{chapter_title}.txt")
        

        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(f"## Capitolo{chapter}")
        
        print(f"Scritto {output_file}")

# Eseguiamo la funzione
input_file = 'Markdown/Manuale di Cucina.txt'
split_file(input_file)
