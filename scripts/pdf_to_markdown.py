import os

from docling.document_converter import DocumentConverter
from tqdm import tqdm

doc_path = "./Data/Menu"
all_doc = os.listdir(doc_path)
dir_output = "Markdown/Menu_MD"

if not os.path.exists(dir_output):
    os.makedirs(dir_output)

for doc_ in tqdm(all_doc):
    source = f"{doc_path}/{doc_}" 
    doc_name = doc_.replace(".pdf", "")

    converter = DocumentConverter()
    result = converter.convert(source)
    text = result.document.export_to_markdown()  # Output

    # Explicitly set encoding to utf-8
    with open(f"{dir_output}/{doc_name}.txt", "w", encoding="utf-8") as f:
        f.write(text)

# with open("Anima Cosmica.txt", "r") as f:
#     txt_ = f.read()

# print(txt_)