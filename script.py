import requests
import csv
import os
import logging
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(filename='zoom_sync.log', level=logging.INFO)

# Constants for Zoom and Google API from environment variables
ZOOM_BASE_URL = "https://api.zoom.us/v2"
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')

# Helper function to get Zoom access token
def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    auth = (ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID}
    response = requests.post(url, headers=headers, auth=auth, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

# Stage 1: Retrieve Zoom Users and Recordings
def list_zoom_users():
    token = get_zoom_access_token()
    print(ZOOM_BASE_URL)
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ZOOM_BASE_URL}/users", headers=headers)
    print(response.json())
    response.raise_for_status()
    
    return response.json().get('users', [])

def list_zoom_recordings(user_id):
    token = get_zoom_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ZOOM_BASE_URL}/users/{user_id}/recordings", headers=headers)
    response.raise_for_status()
    return response.json().get('meetings', [])

def export_to_csv(recordings, filename='zoom_recordings.csv'):
    if not recordings:
        logging.info("No recordings to export.")
        return
    keys = recordings[0].keys()
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(recordings)
    logging.info(f"Exported {len(recordings)} recordings to {filename}")



# Stage 2: Download Recordings
def download_recordings(recordings):
    for recording in recordings:
        download_url = recording['download_url']
        local_filename = f"{recording['id']}.mp4"
        download_file(download_url, local_filename)
        logging.info(f"Downloaded recording {recording['id']} to {local_filename}")

def download_file(url, local_filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(local_filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

# Stage 3: Upload Recordings to Google Drive
def upload_to_google_drive(file_path, folder_id):
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build('drive', 'v3', credentials=credentials)
    file_metadata = {'name': os.path.basename(file_path), 'parents': [folder_id]}
    media = MediaFileUpload(file_path, mimetype='video/mp4')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    logging.info(f"Uploaded {file_path} to Google Drive with file ID {file.get('id')}")

# Main function
def main():
    users = list_zoom_users()
    all_recordings = []
    for user in users:
        recordings = list_zoom_recordings(user['id'])
        all_recordings.extend(recordings)

    export_to_csv(all_recordings)
    download_recordings(all_recordings)

    for recording in all_recordings:
        file_path = f"{recording['id']}.mp4"
        upload_to_google_drive(file_path, GOOGLE_DRIVE_FOLDER_ID)

if __name__ == "__main__":
    main()
