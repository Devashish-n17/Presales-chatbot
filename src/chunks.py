import os
from llama_index.core import Document, TreeIndex
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

def read_markdown_files(input_dir):
    documents = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    documents.append(Document(text=file_content))
    return documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter()
    chunked_documents = []
    for doc in documents:
        chunks = splitter.split_text(doc.text)
        chunked_documents.extend([Document(text=chunk, id_=doc.doc_id, metadata={}) for chunk in chunks])
    return chunked_documents

def main(input_dir):
    documents = read_markdown_files(input_dir)
    chunked_documents = chunk_documents(documents)
    index = TreeIndex.from_documents(chunked_documents)
    return index

if __name__ == "__main__":
    input_directory = "D:\\prod\\Final_1\\output_parsed_documents"  # Adjust as necessary
    index = main(input_directory)