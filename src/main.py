import os
import json
from dotenv import load_dotenv
from datetime import datetime
# from office365.runtime.auth.authentication_context import AuthenticationContext
# from office365.sharepoint.client_context import ClientContext
from src.parse import parse_and_save_documents
from src.chunks import main as chunk_documents

load_dotenv()

USERNAME = os.getenv('sharepoint_email')
PASSWORD = os.getenv('sharepoint_password')
SHAREPOINT_URL_SITE = os.getenv('sharepoint_url_site')
SHAREPOINT_DOC_LIB = os.getenv('sharepoint_doc_library')

print(USERNAME, PASSWORD, SHAREPOINT_URL_SITE, SHAREPOINT_DOC_LIB)

# LOCAL_STORAGE_PATH = 'D:\\prod\\Final_1\\storage'

# def fetch_documents():
#     ctx_auth = AuthenticationContext(SHAREPOINT_URL_SITE)
#     if ctx_auth.acquire_token_for_user(USERNAME, PASSWORD):
#         ctx = ClientContext(SHAREPOINT_URL_SITE, ctx_auth)
#         folder = ctx.web.get_folder_by_server_relative_url(SHAREPOINT_DOC_LIB)
#         ctx.load(folder)
#         ctx.execute_query()
#         return folder.files
#     else:
#         print(ctx_auth.get_last_error())
#         return []

# def main():
#     documents = fetch_documents()
#     if documents:
#         parse_and_save_documents(LOCAL_STORAGE_PATH, 'output_parsed_documents', documents)
#         chunked_index = chunk_documents('output_parsed_documents')
#         print("Chunking completed. Ready for queries.")
#     else:
#         print("No documents fetched.")

# if __name__ == '__main__':
#     main()