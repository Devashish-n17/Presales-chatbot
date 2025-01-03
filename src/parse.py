import os
import pathlib
from llama_parse import LlamaParse
from dotenv import load_dotenv

load_dotenv()

def parse_and_save_documents(input_dir, parser):
    documents = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            input_file_path = os.path.join(root, file)

            try:
                # Parse the document
                print(f"Parsing: {input_file_path}")
                parsed_documents = parser.load_data(input_file_path)
                if parsed_documents:
                    documents.extend(parsed_documents)
                    print(f"Parsed documents from: {input_file_path}")
            except Exception as e:
                print(f"Error parsing {input_file_path}: {e}")

    return documents

def main(input_directory):
    # Initialize LlamaParse with markdown result type
    try:
        parser = LlamaParse(result_type="markdown")
    except Exception as e:
        print(f"Error initializing LlamaParse: {e}. Make sure that you have a valid API key")
        return []

    # Parse documents
    return parse_and_save_documents(input_directory, parser)

if __name__ == "__main__":
    input_directory = "D:\\prod\\Final_1\\storage"  # Replace with your input directory
    documents = main(input_directory)