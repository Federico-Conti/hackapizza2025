import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import json
from setting import generate_embeddings, search_client
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
            text = result.document.export_to_markdown()  # Output

            # Explicitly set encoding to utf-8
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)

    def split_text(self, text):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["#","##","###"],
              
        )
        return text_splitter.split_text(text)

    def encode_key(self,key):
        # Encode the key in URL-safe Base64
        return base64.urlsafe_b64encode(key.encode()).decode().rstrip("=")
    
    def process_embeddings(self):
        for txt_file in tqdm(os.listdir(self.output_dir)):
            if not txt_file.endswith('.txt'):
                continue

            file_path = os.path.join(self.output_dir, txt_file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = self.split_text(text)

            for i, chunk in enumerate(chunks):
                encoded_id = self.encode_key(f"{txt_file}_{i}")
                embedding_result = generate_embeddings(chunk)
                print(f"Embd of: {i}")
                result = search_client.upload_documents(documents=[{
                    "id": encoded_id,
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