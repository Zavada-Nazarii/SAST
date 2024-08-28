import requests
import sys

def get_max_id(token, tags):
    max_ids = {}
    for tag in tags:
        url = f'https://defectdojo/api/v2/tests/?has_tags=true&tag={tag}'
        headers = {
            'accept': 'application/json',
            'Authorization': f'TOKEN {token}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            max_id = max(item['id'] for item in data['results']) if data['results'] else None
            if max_id:
                max_ids[tag] = max_id
        else:
            print(f"Error: Unable to fetch data for tag {tag}")
    return max_ids

def send_message_to_slack(token, channel_id, message):
    url = f'https://slack.com/api/chat.postMessage'
    payload = {
        'channel': channel_id,
        'as_user': 'SAST',
        'text': message,
        'pretty': 1
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 SAST_Notification.py <DEFECTDOJO_TOKEN> <SLACK_CHANNEL_ID> <SLACK_TOKEN> [<TAGS>]")
        sys.exit(1)

    defectdojo_token = sys.argv[1]
    slack_channel_id = sys.argv[2]
    slack_token = sys.argv[3]
    tags = sys.argv[4:]

    max_ids = get_max_id(defectdojo_token, tags)
    for tag, max_id in max_ids.items():
        report_link = f'https://defectdojo/reports/quick?url=/test/{max_id}'
        response = send_message_to_slack(slack_token, slack_channel_id, f'Service: {tag}, SAST Report Link: {report_link}')
        if response.get("ok"):
            print(f"Message sent successfully for tag {tag}")
        else:
            print(f"Failed to send message for tag {tag}: {response.get('error')}")


