from google.oauth2.credentials import  Credentials
from google.auth.transport.requests import Request
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

PAGE_TOKEN_FILE = "drive_page_token.txt"

def authenticate_drive():

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        # if creds and creds.expired and creds.refresh_token:
        #     creds.refresh(Request())
        # else:
        flow = InstalledAppFlow.from_client_secrets_file(Path(__file__).parent.joinpath('2drive.json'), SCOPES)  
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)
    return service



def load_saved_token():
    if os.path.exists(PAGE_TOKEN_FILE):
        with open(PAGE_TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None
    

def save_new_token(token):
    with open(PAGE_TOKEN_FILE, 'w') as f:
        f.write(token)


def get_service():
    
    service = authenticate_drive()

    page_token = load_saved_token()

    if not page_token:
        #getting the page token of the drive which is like a recent snapshot of the drive 
        token_resp = service.changes().getStartPageToken().execute()
        page_token = token_resp['startPageToken']
        save_new_token(page_token)
        print(f"Start token saved: {page_token}")
        return


    #this line checks for changes in the page token fromm the last page token seen
    response = service.changes().list(pageToken=page_token, spaces='drive').execute()
    if len(response['changes']) == 0:
        print('No changes.')

    #if any changes, it gets the info of all changes made
    for change in response.get('changes', []):
        file_id = change.get('fileId')
        file_info = change.get('file', {})

        #if deleted
        if file_info.get('trashed'):
            print(f"File {file_id} was trashed/deleted.")
            continue

        file_name = file_info.get('name')
        mime_type = file_info.get('mimeType') #identifies the format of the file and if its a folder
        print(f"\nFile added/changed: {file_name} (ID: {file_id}) - Type: {mime_type}")

        #if it's not a folder
        if not mime_type.startswith('application/vnd.google-apps.'):
            request = service.files().get_media(fileId=file_id)
            file_path = os.path.join("downloads", file_name)

            os.makedirs("downloads", exist_ok=True)
            with open(file_path, 'wb') as f:
                downloader = build('drive', 'v3', credentials=service._http.credentials)
                from googleapiclient.http import MediaIoBaseDownload

                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Downloading {file_name}")

            print(f"Downloaded {file_name}")


        if 'newStartPageToken' in response:
            new_token = response['newStartPageToken']
            save_new_token(new_token)
            print(f"New start page token saved: {new_token}")


if __name__ == '__main__':
    get_service()
