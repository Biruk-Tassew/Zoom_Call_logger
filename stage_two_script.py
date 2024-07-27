import requests
import os
import logging
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv
import io
import sys
import tqdm  # For progress bars

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(filename='zoom_sync.log', level=logging.INFO)

# Constants for Zoom from environment variables
ZOOM_BASE_URL = "https://api.zoom.us/v2"
ZOOM_CLIENT_ID = os.getenv('ZOOM_CLIENT_ID')
ZOOM_CLIENT_SECRET = os.getenv('ZOOM_CLIENT_SECRET')
ZOOM_ACCOUNT_ID = os.getenv('ZOOM_ACCOUNT_ID')

# Helper function to get Zoom access token
def get_zoom_access_token():
    url = "https://zoom.us/oauth/token"
    auth = (ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {"grant_type": "account_credentials", "account_id": ZOOM_ACCOUNT_ID}
    response = requests.post(url, headers=headers, auth=auth, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

# Function to list Zoom meetings
def list_zoom_meetings():
    token = get_zoom_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ZOOM_BASE_URL}/users/me/meetings", headers=headers)
    response.raise_for_status()
    return response.json().get('meetings', [])

# Function to list recordings for a specific meeting
def list_zoom_recordings(meeting_id):
    token = get_zoom_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ZOOM_BASE_URL}/meetings/{meeting_id}/recordings", headers=headers)
    response.raise_for_status()
    return response.json().get('recording_files', [])

# Function to search for a folder in Google Drive by name
def search_google_drive_folder(service, name, parent_id):
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and '{parent_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    return items[0]['id'] if items else None

# Function to create a folder in Google Drive
def create_google_drive_folder(service, name, parent_id):
    folder_id = search_google_drive_folder(service, name, parent_id)
    if folder_id:
        return folder_id

    # Create a new folder if it doesn't exist
    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    try:
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder['id']
    except Exception as e:
        logging.error(f"Error creating folder {name}: {e}")
        return None

# Function to download a file from a URL with progress indicator
def download_file(url, dest_path, headers):
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    block_size = 32 * 1024  # 32 KiB

    with open(dest_path, 'wb') as f, tqdm.tqdm(
        desc=dest_path,
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024
    ) as bar:
        for chunk in response.iter_content(block_size):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

    return dest_path

# Main function
def main():
    meetings = list_zoom_meetings()
    for meeting in meetings:
        recordings = list_zoom_recordings(meeting['id'])
        for recording in recordings:
            recording_date = datetime.strptime(recording['recording_start'], "%Y-%m-%dT%H:%M:%SZ")
            date_folder_name = recording_date.strftime('%Y-%m-%d')
            download_url = recording['download_url']
            headers = {"Authorization": f"Bearer {get_zoom_access_token()}"}

            # Create a local folder for the recordings
            local_folder_path = os.path.join("Downloads", date_folder_name)
            os.makedirs(local_folder_path, exist_ok=True)

            file_extension = os.path.splitext(download_url.split("?")[0])[1] or ".mp4"
            human_readable_name = f"{meeting['topic']}_{recording_date.strftime('%Y-%m-%d_%H-%M-%S')}{file_extension}"
            local_file_path = os.path.join(local_folder_path, human_readable_name)
            download_file(download_url, local_file_path, headers)

if __name__ == "__main__":
    main()
