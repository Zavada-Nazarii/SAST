import os
import sys
import requests
import time

def upload_ipa_to_mobsf(ipa_file, auth_token):
    url = "http://0.0.0.0:8000/api/v1/upload"
    headers = {
        "Authorization": auth_token
    }
    print(f"Uploading file: {ipa_file}")
    print(f"File size: {os.path.getsize(ipa_file)} bytes")
    print(f"File exists: {os.path.exists(ipa_file)}")
    with open(ipa_file, 'rb') as f:
        files = {'file': (os.path.basename(ipa_file), f, 'application/octet-stream')}
        response = requests.post(url, headers=headers, files=files)
        if response.status_code == 200:
            result = response.json()
            print(f"Uploaded {ipa_file} to MobSF. Scan result: {result}")
            return result['hash']
        else:
            print(f"Failed to upload {ipa_file} to MobSF. Response: {response.text}")
            return None

def initiate_scan(auth_token, file_hash):
    url = "http://0.0.0.0:8000/api/v1/scan"
    headers = {
        "Authorization": auth_token
    }
    data = {
        "hash": file_hash
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print(f"Scan initiated for file with hash {file_hash}.")
    else:
        print(f"Failed to initiate scan for file with hash {file_hash}. Response: {response.text}")

def main(auth_token, shared_path, filename):
    # Перевірка чи файл існує
    file_path = os.path.join(shared_path, filename)
    if not os.path.exists(file_path):
        print(f"File {filename} does not exist in the directory {shared_path}.")
        return

    # Завантаження файлу до MobSF
    file_hash = upload_ipa_to_mobsf(file_path, auth_token)
    if file_hash:
        print("Waiting for 2 minutes before initiating scan...")
        time.sleep(120)  # Очікуємо 2 хвилин перед початком сканування, щоб файл завантажився
        initiate_scan(auth_token, file_hash)
        time.sleep(600)  # Очікуємо 10 хвилин до закінчення сканування, щоб можна було працювати із готовим звітом
    else:
        print(f"Failed to upload {filename} to MobSF.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 download_and_analyze.py <AUTHMobSF> <SHARED_PATH> <FILENAME>")
        sys.exit(1)
    auth_token = sys.argv[1]
    shared_path = sys.argv[2]
    filename = sys.argv[3]
    main(auth_token, shared_path, filename)

