import os
import argparse
import requests

# Функція для відправлення файлу в Slack канал
def upload_file_to_slack(file_path, channel_id, slack_token):
    file_name = os.path.basename(file_path)
    url = "https://slack.com/api/files.upload"
    headers = {
        "Authorization": f"Bearer {slack_token}"
    }
    data = {
        "channels": channel_id,
        "title": file_name,
        "filename": file_name
    }
    with open(file_path, 'rb') as file_content:
        response = requests.post(url, headers=headers, data=data, files={"file": file_content})
        if response.status_code != 200 or not response.json().get("ok"):
            print(f"Failed to upload {file_name} to channel {channel_id}: {response.text}")
        else:
            print(f"Successfully uploaded {file_name} to channel {channel_id}")

def main(args):
    # Список файлів для відправлення
    files_to_upload = [
        "searchService.pdf"
    ]

    # Відправлення файлів у один канал
    for file_name in files_to_upload:
        upload_file_to_slack(file_name, args.test_id, args.slack_token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload PDF files to Slack channel.")
    parser.add_argument("slack_token", help="Slack API token")
    parser.add_argument("--test_id", required=True, help="Channel ID for uploading all PDF files")
	
    args = parser.parse_args()
    main(args)

