import os
from docling.document_converter import DocumentConverter
from tqdm import tqdm

# Percorso del file sorgente e della directory di output
source = "Data/Misc/Manuale di Cucina.pdf"
dir_output = "Markdown"

# Creazione della directory di output se non esiste
os.makedirs(dir_output, exist_ok=True)

converter = DocumentConverter()

print("Convertendo il documento...")
result = converter.convert(source)
text = result.document.export_to_markdown()

# Divide il documento ogni volta che incontra un titolo contenente "Capitolo"
print("Dividendo il documento in sezioni...")
sections = text.splitlines()  # Divide il testo in righe
current_section = []
section_count = 0

for line in tqdm(sections, desc="Processando linee"):
    if "Capitolo" in line:  # Controlla se la linea contiene la parola "Capitolo"
        # Salva la sezione corrente (se esiste)
        if current_section:
            section_count += 1
            section_filename = os.path.join(dir_output, f"Capitolo_{section_count}.txt")
            with open(section_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(current_section))
            current_section = []  # Resetta la sezione corrente
    # Aggiungi la linea alla sezione corrente
    current_section.append(line)

# Salva l'ultima sezione (se esiste)
if current_section:
    section_count += 1
    section_filename = os.path.join(dir_output, f"Capitolo_{section_count}.txt")
    with open(section_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(current_section))

print(f"Divisione completata. Salvate {section_count} sezioni nella directory '{dir_output}'.")
