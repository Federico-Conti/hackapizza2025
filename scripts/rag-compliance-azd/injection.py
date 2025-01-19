import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import json
from setting import generate_embeddings, getSearchClient
import base64
from docling.document_converter import DocumentConverter

class DocumentProcessor:
    def __init__(self, doc_path, output_dir, chunk_size=1000, chunk_overlap=20):
        self.doc_path = doc_path
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def convert_documents(self):
        all_docs = os.listdir(self.doc_path)
        for doc_ in tqdm([doc for doc in all_docs if doc.endswith('.pdf')]):
            doc_name = doc_.replace(".pdf", "")
            output_file = f"{self.output_dir}/{doc_name}.txt"

            if os.path.exists(output_file):
                print(f"Skipping {output_file} as it already exists.")
                continue

            source = f"{self.doc_path}/{doc_}"
            converter = DocumentConverter()
            result = converter.convert(source)
            text = result.document.export_to_markdown() 

            # Explicitly set encoding to utf-8
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)

    def split_text(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["#","##"],
              
        )
        return text_splitter.split_text(text)

    def getChunks(self):
         for txt_file in tqdm(os.listdir(self.output_dir)):
            if not txt_file.endswith('.txt'):
                continue

            file_path = os.path.join(self.output_dir, txt_file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = self.split_text(text)
            return chunks
        
    def process_embeddings(self):
            chunks = self.getChunks()
            for i, chunk in enumerate(chunks):
                embedding_result = generate_embeddings(chunk)
                print(f"Embd of: {i}")
                result = getSearchClient().upload_documents(documents=[{
                    "id": str(i),
                    "contet": chunk,
                    "embedding": embedding_result
                }])
            print("Upload of new document succeeded: {}".format(result[0].succeeded))         
     
if __name__ == "__main__":
    doc_path = "../../Data/CodiceGalattico"
    output_dir = "../../Data/CodiceGalattico"
    
    processor = DocumentProcessor(doc_path, output_dir)
    processor.convert_documents()
    processor.process_embeddings()
