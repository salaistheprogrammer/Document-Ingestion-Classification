import os.path
import base64
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from pathlib import Path

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(Path(__file__).parent.joinpath('2gmail.json'), SCOPES)
            creds = flow.run_local_server(port=0)
        #if creds are'nt valid or token.json isn't already existing, update the exisitng token.json or create one respectively
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_emails_with_attachments(service):
    results = service.users().messages().list(userId='me', q="is:unread has:attachment").execute()
    messages = results.get('messages', [])

    if not messages:
        print("No new messages found.")
        return

    for msg in messages:
        msg_id = msg['id']
        message = service.users().messages().get(userId='me', id=msg_id).execute()

        service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()

        for part in message['payload'].get('parts', []):
            filename: str = part.get('filename')
            body = part.get('body', {})
            attachment_id = body.get('attachmentId')

            if attachment_id:
                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=attachment_id
                ).execute()

                formats = ('.pdf', '.word', '.wordx', '.doc', '.docx')

                ext = filename.endswith(formats)

                if ext:
                    data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    save_path = os.path.join(Path(__file__).parents[1] / "downloads", filename)
                    os.makedirs(Path(__file__).parents[1] / "downloads", exist_ok=True)
                    with open(save_path, 'wb') as f:
                        f.write(data)

                    print(f"Downloaded: {filename}")


if __name__ == '__main__':
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    while True:
        fetch_emails_with_attachments(service)
        time.sleep(30) 
