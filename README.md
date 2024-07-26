I apologize for that. Here's the corrected `README.md` file with the entire content in markdown form:

```markdown
# Zoom Recordings Sync Project

This project automates the process of listing Zoom users, retrieving and handling Zoom cloud recordings, and finally syncing these recordings to Google Drive. The project is divided into three stages:

- **Stage 1:** List Zoom users and export recording details to a CSV file.
- **Stage 2:** Download Zoom cloud recordings locally.
- **Stage 3:** Upload/sync Zoom cloud recordings to Google Drive, organized into folders by date.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine.
- Zoom account with API access using Server-to-Server OAuth.
- Google Cloud project with Google Drive API enabled and a service account with the necessary permissions.
- `tqdm` package for progress bars.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/zoom-recordings-sync.git
   cd zoom-recordings-sync
   ```

2. **Create a virtual environment and activate it:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the project directory and add the following environment variables:**

   ```ini
   ZOOM_CLIENT_ID=your_zoom_client_id
   ZOOM_CLIENT_SECRET=your_zoom_client_secret
   ZOOM_ACCOUNT_ID=your_zoom_account_id
   GOOGLE_DRIVE_FOLDER_ID=your_google_drive_folder_id
   GOOGLE_SERVICE_ACCOUNT_FILE=path_to_your_service_account_json_file
   ```

   Replace the placeholders with your actual credentials.

5. **Ensure your `.gitignore` file is configured to exclude sensitive files:**

   ```plaintext
   .env
   *.json
   zoom_sync.log
   Downloads/
   ```

## Usage

### Stage 1: List Zoom Users and Export Recording Details to CSV

1. **Run the script:**

   ```bash
   python stage_one_script.py
   ```

2. **Script Overview:**
   - Lists all users in the Zoom account.
   - Retrieves Zoom cloud recording details for each user.
   - Exports these details to a CSV file named `zoom_recordings.csv`.
   - Logs all actions performed.

### Stage 2: Download Zoom Cloud Recordings Locally

1. **Run the script:**

   ```bash
   python stage_two_script.py
   ```

2. **Script Overview:**
   - Lists all users in the Zoom account.
   - Retrieves Zoom cloud recording details for each user.
   - Downloads each recording locally to a `Downloads` directory, organized by date.
   - Logs all actions performed.

### Stage 3: Upload/Sync Zoom Cloud Recordings to Google Drive

1. **Run the script:**

   ```bash
   python stage_three_script.py
   ```

2. **Script Overview:**
   - Lists all users in the Zoom account.
   - Retrieves Zoom cloud recording details for each user.
   - Downloads each recording locally to a `Downloads` directory, organized by date.
   - Uploads the downloaded recordings to Google Drive, organized into folders by date.
   - Progress bars are displayed for both downloading and uploading processes.
   - Logs all actions performed.

## Troubleshooting

- Ensure that your environment variables are correctly set in the `.env` file.
- Check the `zoom_sync.log` file for detailed error messages if something goes wrong.
- Ensure that your Google service account has the necessary permissions to access and modify the specified Google Drive folder.

## Contributing

If you have any ideas, feel free to fork the repository and submit a pull request. Alternatively, you can open an issue with your suggestions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Zoom API](https://marketplace.zoom.us/docs/api-reference/zoom-api/)
- [Google Drive API](https://developers.google.com/drive/api/v3/about-sdk)
- [tqdm](https://github.com/tqdm/tqdm) for the progress bars
```