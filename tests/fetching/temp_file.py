import os
from io import BytesIO
from dotenv import load_dotenv
from office365.sharepoint.client_context import ClientContext, UserCredential
from office365.sharepoint.files.file import File
from pathlib import PurePath

load_dotenv()
USERNAME = os.getenv('sharepoint_email')
PASSWORD = os.getenv('sharepoint_password')

SHAREPOINT_URL_SITE_1 = 'https://nitoronline.sharepoint.com/sites/presales'
SHAREPOINT_SITE_NAME_1 = 'presales'
SHAREPOINT_DOC_LIB_1 = 'Shared Documents/1.Presales ISV_Platforms/Enterprise & Tech Enterprise/Proposals'

conn = ClientContext(SHAREPOINT_URL_SITE_1).with_credentials(UserCredential(USERNAME, PASSWORD))

SOURCE_FOLDER = 'Praj'
DEST_FOLDER = 'D:\prod\pipeline\sharepoint-pipeline\store'

target_folder_url = f'{SHAREPOINT_DOC_LIB_1}/{SOURCE_FOLDER}' if SOURCE_FOLDER else f'{SHAREPOINT_DOC_LIB_1}'
root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
root_folder.expand(["Files", "Folders"]).get().execute_query()

files_list = root_folder.files
print(files_list)

def download_file(file_name):
    file_url = f'/sites/{SHAREPOINT_SITE_NAME_1}/{SHAREPOINT_DOC_LIB_1}/{SOURCE_FOLDER}/{file_name}'
    file = File.open_binary(conn, file_url)
    return file.content

def save_file(file_n, file_obj):
    file_dir_path = PurePath(DEST_FOLDER, file_n)
    with open(file_dir_path, 'wb') as f:
        f.write(file_obj)

for file in files_list:
    file_obj = download_file(file.name)
    save_file(file.name, file_obj)

