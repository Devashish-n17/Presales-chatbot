import os, json
import urllib.parse
from io import BytesIO
from uuid import uuid4
from llama_parse import LlamaParse
from langchain_chroma import Chroma
from office365.sharepoint.client_context import ClientContext, UserCredential
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from office365.sharepoint.files.file import File
from langchain_core.documents import Document
from tempfile import NamedTemporaryFile

from dotenv import load_dotenv
load_dotenv()
USERNAME = os.getenv('sharepoint_email')
PASSWORD = os.getenv('sharepoint_password')
SHAREPOINT_URL_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC_LIB = os.getenv('sharepoint_doc_library')
LLAMA_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=GEMINI_API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)


properties_file = 'Metadata.json'

conn = ClientContext(SHAREPOINT_URL_SITE).with_credentials(UserCredential(USERNAME, PASSWORD))

def _get_files_and_folders(folder_name=''):
    target_folder_url = f'{SHAREPOINT_DOC_LIB}/{folder_name}' if folder_name else SHAREPOINT_DOC_LIB
    root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
    root_folder.expand(["Files", "Folders"]).get().execute_query()
    return root_folder.files, root_folder.folders

def _download_file(file_name, folder_name):
    file_url = f'/sites/{SHAREPOINT_SITE_NAME}/{SHAREPOINT_DOC_LIB}/{folder_name}/{file_name}'
    file = File.open_binary(conn, file_url)
    file_obj = file.content
    file_stream = BytesIO(file_obj)
    print(f'\n-->>> {file_name} Downloaded')
    return file_stream


def parse_and_document(file_stream, file_name, file_path):
    parser = LlamaParse(result_type="markdown").load_data(file_stream, extra_info={'file_name': file_name})
    
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.md') as temp_file:
        for item in parser:
            temp_file.write(item.text)
        temp_file_path = temp_file.name
    
    if temp_file_path.endswith('.md'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            chunks = text_splitter.split_text(file_content)
            docs = [Document(page_content=chunk, metadata={"file_name": file_name, "file_path": file_path}) for chunk in chunks]
        
        os.remove(temp_file_path)
        uuids = [str(uuid4()) for _ in range(len(docs))]
        collection_name, persist_directory = 'sales', './chroma_db'
        if os.path.exists(persist_directory):
            vector_store = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=persist_directory)
            ## chunking using semantic chunking / recursive
            ## 
            vector_store.add_documents(documents=docs, ids=uuids)
            # vector_store.add_documents(documents = docs,metadata =[ {"file_id": file_id,"file_name": file_name} for _ in range(len(docs))])
        else:
            vector_store = Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=persist_directory, collection_name=collection_name)


def get_file_properties(folder_name=''):
    all_files_properties = []
    file_id_list = []
    
    def process_folder(current_folder_name):
        files, folders = _get_files_and_folders(current_folder_name)
        encoded_doc_lib = urllib.parse.quote(SHAREPOINT_DOC_LIB, safe=":/")

        for file in files:
            encoded_file_name = urllib.parse.quote(file.name, safe=":/")
            resource_url = f'{SHAREPOINT_URL_SITE}/{encoded_doc_lib}/{f"{current_folder_name}/" if current_folder_name else ""}{encoded_file_name}'
            file_dict = {
                'file_name': file.name,
                'file_unique_id': file.unique_id,
                'resource_url': resource_url,
                'file_size': file.length,
            }
            all_files_properties.append(file_dict)
            file_id_list.append(file.unique_id)
            file_stream = _download_file(file.name, current_folder_name)
            parse_and_document(file_stream, file.name, resource_url)
            break

        for folder in folders:
            if folder.name.lower() != "forms":
                new_folder_name = f'{current_folder_name}/{folder.name}' if current_folder_name else folder.name
                process_folder(new_folder_name)
            break
    process_folder(folder_name)
    
    with open(properties_file, 'w') as file:
        json.dump(all_files_properties, file, indent=4)


if __name__ == '__main__':
    get_file_properties()
    print('Completed...')


# async def chunking(doc_text: list):
#     # Text splitter
#     text_splitter = RecursiveCharacterTextSplitter()
    
#     # Create documents from text
#     docs = text_splitter.create_documents([doc_text], metadata=[{"file_path": "text"}])
#     print(docs[0].page_content)
#     print(docs)
 