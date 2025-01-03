import os, json
from io import BytesIO
from office365.sharepoint.client_context import ClientContext, UserCredential
from office365.sharepoint.files.file import File
from llama_parse import LlamaParse
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from llama_index.core import Document, TreeIndex, Settings
from llama_index.llms.gemini import Gemini
from tempfile import NamedTemporaryFile
import urllib.parse

from dotenv import load_dotenv
load_dotenv()
USERNAME = os.getenv('sharepoint_email')
PASSWORD = os.getenv('sharepoint_password')
SHAREPOINT_URL_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_SITE_NAME = os.getenv('sharepoint_site_name')
SHAREPOINT_DOC_LIB = os.getenv('sharepoint_doc_library')
LLAMA_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
Settings.llm = Gemini()

embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=GOOGLE_API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)

properties_file = 'Metadata.json'

conn = ClientContext(SHAREPOINT_URL_SITE).with_credentials(UserCredential(USERNAME, PASSWORD))

def _get_files_and_folders(folder_name=''):
    target_folder_url = f'{SHAREPOINT_DOC_LIB}/{folder_name}' if folder_name else SHAREPOINT_DOC_LIB
    root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
    root_folder.expand(["Files", "Folders"]).get().execute_query()
    return root_folder.files, root_folder.folders

documents = []
def parse_and_document(file_stream, file_name, file_id):
    parser = LlamaParse(result_type="markdown").load_data(file_stream, extra_info={'file_name': file_name})
    with NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.md') as temp_file:
        for item in parser:
            temp_file.write(item.text)
        temp_file_path = temp_file.name
    
    if temp_file_path.endswith('.md'):
        with open(temp_file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
            documents.append(Document(text=file_content))

        os.remove(temp_file_path)

        # chunks = text_splitter.split_text(file_content)
        # chunked_documents = [Document(text=chunk, metadata={'file_id': file_id}) for chunk in chunks]

        # collection_name = 'sales'
        # persist_directory = './chroma_db'
        # if os.path.exists(persist_directory):
        #     vectorDB = Chroma(persist_directory=persist_directory, collection_name=collection_name, embedding_function=embeddings)
        #     vectorDB.add_documents([doc.text for doc in chunked_documents], metadata=[doc.metadata for doc in chunked_documents])
        # else:
        #     vectorDB = Chroma.from_documents([doc.text for doc in chunked_documents], embeddings, persist_directory=persist_directory, collection_name=collection_name)
        
        # index = TreeIndex.from_documents(chunked_documents)
        # return index
    return documents


def chunk_and_index(documents, file_id_list):
    chunked_documents = []
    for doc, file_id in zip(documents, file_id_list):
        chunks = text_splitter.split_text(doc.text)
        chunked_documents.extend([Document(text=chunk, metadata={'file_id':file_id}) for chunk in chunks])
    index = TreeIndex.from_documents(chunked_documents)
    print('-->>> Sent Index')
    return index   


def _download_file(file_name, folder_name):
    file_url = f'/sites/{SHAREPOINT_SITE_NAME}/{SHAREPOINT_DOC_LIB}/{folder_name}/{file_name}'
    file = File.open_binary(conn, file_url)
    file_obj = file.content
    file_stream = BytesIO(file_obj)
    print(f'\n-->>> {file_name} Downloaded')
    return file_stream
    

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
            parse_and_document(file_stream, file.name, file.unique_id)
            break

        for folder in folders:
            if folder.name.lower() != "forms":
                new_folder_name = f'{current_folder_name}/{folder.name}' if current_folder_name else folder.name
                process_folder(new_folder_name)
            break

    process_folder(folder_name)
    
    with open(properties_file, 'w') as file:
        json.dump(all_files_properties, file, indent=4)
    
    print('-->>> Completed...')
    return file_id_list


# Function to find name and url by file_id
def get_name_and_url(file_id, file_path):
    # Read the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)  # Load the JSON array directly
    
    # Search for the matching file_id
    for item in data:
        if item["file_unique_id"] == file_id:
            return item["file_name"], item["resource_url"]
    return None, None


if __name__ == '__main__':
    print('-->>> Started')
    file_id_list = get_file_properties()
    index = chunk_and_index(documents, file_id_list)
    query_engine = index.as_query_engine()
    while True:
        question = input('Ask : ')
        if question.lower() == 'exit': break

        search_by_id = ''
        response = query_engine.query(question)
        for s in response.source_nodes:
            search_by_id = s.metadata['file_id']
        

        name, url = get_name_and_url(search_by_id, 'D:\prod\pipeline\sharepoint-pipeline\Metadata.json')

        if name and url:
            print(f"File: {name}")
            print(f"URL: {url}")
        else:
            print("File ID not found.")


'''
loader = UnstructuredMarkdownLoader(file_path=temp_file_path)
data = loader.load()
os.remove(temp_file_path)
embeddings = GoogleGenerativeAIEmbeddings(model='models/embedding-001', google_api_key=GOOGLE_API_KEY)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
split_sentences = text_splitter.split_documents(data)

metadata = [{'file_id': file_id}] * len(split_sentences)
collection_name = 'sales'
persist_directory = './chroma_db'
if os.path.exists(persist_directory):
    vectorDB = Chroma(persist_directory=persist_directory, collection_name=collection_name, embedding_function=embeddings)
    vectorDB.add_documents(split_sentences, metadata=metadata)
else:
    vectorDB = Chroma.from_documents(split_sentences, embeddings, persist_directory=persist_directory, collection_name=collection_name)

print(f'-->>> Done with {file_name}')



Optimization Issues:
    1. time.sleep(2) in the Loop:
        This is a huge performance bottleneck. Pausing for 2 seconds for each file processed is incredibly slow, especially if you have a large number of files.
        This should be removed unless there's a very specific and valid reason for it, like rate limiting in an API.

    2. Sequential File Processing:
        The code processes files sequentially within each folder. If you have many files in a single folder, this will be slow. You could potentially leverage
        concurrency (e.g., using threads or asynchronous operations) to speed up the processing of multiple files simultaneously.

    3. String Concatenation in URL:
        Creating the resource_url using f'{...}/{f"{current_folder_name}/" if current_folder_name else ""}{encoded_file_name}' involves unnecessary conditional
        checks and string interpolation which could be slightly more efficient.

    4. Multiple execute_query Calls:
        The code calls execute_query multiple times within the loop. This can be optimized by batching the requests to reduce the number of network calls.
    
    5. Redundant Function Calls:
        The _get_files_and_folders function is called multiple times within the recursive process_folder function. It would be more efficient to call it once
        and pass the results to the recursive function.
    
    6. Unnecessary Recursion:
        The recursive function process_folder could be replaced with an iterative solution using a stack or queue to avoid potential stack overflow issues with
        deep folder structures.


Robustness Issues:
    1. Error Handling:
        The code lacks explicit error handling. What happens if _get_files_and_folders fails? What happens if urllib.parse.quote fails? The code should have
        try-except blocks to handle potential exceptions gracefully.

    2. Infinite Recursion:
        While the code has an implicit base case, a cyclical directory structure (e.g., a symbolic link creating a loop) could lead to infinite recursion and
        potentially a stack overflow error. It would be best to track visited folders to prevent this.

    3. Global Variables:
        Using global variables like SHAREPOINT_URL_SITE and SHAREPOINT_DOC_LIB isn't ideal. It reduces flexibility and can make testing difficult. It would be
        best to pass them as parameters or define them as class variables if necessary.

    4. Hardcoded Folder Exclusion
        Excluding the "forms" folder by hardcoding its name (folder.name.lower() != "forms") limits reusability of the code. It's better to accept a list of
        folders as an argument that should be excluded to make the function more flexible.

    5. urllib.parse.quote usage:
        While urllib.parse.quote handles URL encoding, it's crucial to use it correctly based on specific needs. If path components need to be combined, using
        urllib.parse.urljoin or similar techniques is more robust to handle base paths or special cases.
'''