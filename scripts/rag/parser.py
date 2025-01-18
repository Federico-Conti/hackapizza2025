import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm
import json

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
            is_separator_regex=False,
        )
        return text_splitter.split_text(text)

    def process_embeddings(self):
        # embedding_model = OpenAIEmbeddings()
        # documents = []

        for txt_file in tqdm(os.listdir(self.output_dir)):
            if not txt_file.endswith('.txt'):
                continue

            file_path = os.path.join(self.output_dir, txt_file)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = self.split_text(text)
        return chunks
        #     for i, chunk in enumerate(chunks):
        #         embedding = embedding_model.embed_text(chunk)
        #         documents.append({
        #             "id": f"{txt_file}_{i}",
        #             "content": chunk,
        #             "embedding": embedding
        #         })

        # # Save the documents with embeddings as a JSON file
        # output_file = os.path.join(self.output_dir, "documents_with_embeddings.json")
        # with open(output_file, "w", encoding="utf-8") as f:
        #     json.dump(documents, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    doc_path = "../../Data/CodiceGalattico"
    output_dir = "../../Data/CodiceGalattico"

    processor = DocumentProcessor(doc_path, output_dir)
    processor.convert_documents()
    chunks = processor.process_embeddings()
    print(chunks[0])