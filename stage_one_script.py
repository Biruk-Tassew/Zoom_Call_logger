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
    try:
        response = requests.get(f"{ZOOM_BASE_URL}/meetings/{meeting_id}/recordings", headers=headers)
        response.raise_for_status()
        return response.json().get('recording_files', [])
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logging.error(f"No recordings found for meeting ID {meeting_id}: {e}")
        else:
            logging.error(f"Error fetching recordings for meeting ID {meeting_id}: {e}")
        return []

# Function to get meeting details
def get_meeting_details(meeting_id):
    token = get_zoom_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(f"{ZOOM_BASE_URL}/meetings/{meeting_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"Error fetching meeting details for meeting ID {meeting_id}: {e}")
        return {}

# Function to export recordings to CSV
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

# Main function
def main():
    meetings = list_zoom_meetings()
    all_recordings = []
    for meeting in meetings:
        meeting_details = get_meeting_details(meeting['id'])
        user_email = meeting_details.get('host_email', 'N/A')
        meeting_topic = meeting_details.get('topic', 'N/A')
        meeting_timezone = meeting_details.get('timezone', 'N/A')

        recordings = list_zoom_recordings(meeting['id'])
        for recording in recordings:
            recording['user_email'] = user_email
            recording['meeting_topic'] = meeting_topic
            recording['meeting_timezone'] = meeting_timezone

            # Calculate duration using recording_start and recording_end
            recording_start = datetime.fromisoformat(recording.get('recording_start')).replace(tzinfo=timezone.utc)
            recording_end = datetime.fromisoformat(recording.get('recording_end')).replace(tzinfo=timezone.utc)
            recording_duration = recording_end - recording_start

            recording['duration'] = str(recording_duration)
            all_recordings.append(recording)

    export_to_csv(all_recordings)

if __name__ == "__main__":
    main()
