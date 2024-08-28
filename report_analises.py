import requests
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sys

def fetch_engagements(token):
    """Завантажує engagements, де status 'In Progress', та повертає список пар (ID, name)."""
    headers = {'Authorization': f'Token {token}'}
    response = requests.get('https://defectdojo/api/v2/engagements/', headers=headers)
    engagements = response.json().get('results', [])
    return [(engagement['id'], engagement.get('name', '')) for engagement in engagements if engagement.get('status') == 'In Progress']

def fetch_data(token, engagements):
    headers = {'Authorization': f'Token {token}'}
    data_dict = {}
    test_counters = {}  # Цей словник використовується для збереження лічильника для кожного тегу
    severity_counts = {}  # Для збереження кількості знахідок по severity

    for engagement_id, name in engagements:
        response = requests.get(f'https://defectdojo/api/v2/tests/?engagement={engagement_id}&limit=10000', headers=headers)
        tests = response.json().get('results', [])

        for test in sorted(tests, key=lambda x: x['id']):
            if test.get('scan_type') != 'Trivy Scan':
                test_id = test['id']
                tags = test.get('tags', [])
                for tag in tags:
                    key = (engagement_id, tag)
                    if key not in data_dict:
                        # Створення посилання на Engagement ID
                        engagement_link = f'https://defectdojo/engagement/{engagement_id}'
                        # Форматування без використання додаткових лапок
                        engagement_id_with_link = f'=HYPERLINK("{engagement_link}"; "{name}")'
                        data_dict[key] = {'Engagement ID': engagement_id_with_link, 'Engagement Name': name, 'Tag': tag}
                        test_counters[key] = 0  # Ініціалізація лічильника для кожного нового ключа
                        severity_counts[key] = {'high': [], 'critical': [], 'medium': [], 'low': [], 'info': []}

                    test_counters[key] += 1
                    count_key = f'Test {test_counters[key]} Counting finds'
                    findings_response = requests.get(f'https://defectdojo/api/v2/findings/?test={test_id}&limit=1000', headers=headers)
                    findings = findings_response.json().get('results', [])
                    findings_count = findings_response.json().get('count', 0)
                    # Додавання посилання на кількість знахідок
                    findings_count_with_link = f'=HYPERLINK("https://defectdojo/test/{test_id}"; "{findings_count}")'
                    data_dict[key][count_key] = findings_count_with_link

                    # Підрахунок severity
                    test_severity_counts = {'high': 0, 'critical': 0, 'medium': 0, 'low': 0, 'info': 0}
                    for finding in findings:
                        severity = finding.get('severity', '').lower()
                        if severity in test_severity_counts:
                            test_severity_counts[severity] += 1

                    for severity, count in test_severity_counts.items():
                        severity_counts[key][severity].append(count)

    # Обчислення максимального числа тестів для усіх тегів
    max_tests = max(test_counters.values(), default=0)

    # Заповнення відсутніх тестових колонок нулями
    for key, values in data_dict.items():
        for i in range(1, max_tests + 1):
            count_key = f'Test {i} Counting finds'
            if count_key not in values:
                values[count_key] = 0  # Заповнюємо відсутні колонки нулями
            for severity in severity_counts[key]:
                if len(severity_counts[key][severity]) < i:
                    severity_counts[key][severity].append(0)

    results = []
    for key, values in data_dict.items():
        results.append(values)
        for severity, counts in severity_counts[key].items():
            severity_row = {k: '' for k in values.keys()}
            severity_row['Engagement ID'] = ''
            severity_row['Engagement Name'] = ''
            severity_row['Tag'] = severity.capitalize()
            for i in range(max_tests):
                count_key = f'Test {i + 1} Counting finds'
                severity_row[count_key] = counts[i]
            results.append(severity_row)

    return results

def init_google_sheets(json_keyfile_path):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
    client = gspread.authorize(creds)
    return client

def create_google_sheet(data, sheet_url, json_keyfile_path):
    client = init_google_sheets(json_keyfile_path)
    sheet = client.open_by_url(sheet_url).sheet1

    # Очистка існуючого вмісту листа, починаючи з колонки B
    sheet.batch_clear(["B1:Z1000"])

    headers = list(data[0].keys())  # Заголовки стовпців
    rows = [list(item.values()) for item in data]  # Дані

    # Додаємо заголовки та дані, починаючи з колонки B
    all_data = [headers] + rows
    sheet.update('B1', all_data, raw=False)  # Використовуємо raw=False для форматування комірок як формул

if __name__ == "__main__":
    token = sys.argv[1]
    engagements = fetch_engagements(token)
    if engagements:
        data = fetch_data(token, engagements)
        if data:
            json_keyfile_path = './Report/reportsast-key.json'
            sheet_url = 'https://docs.google.com/spreadsheets/d/.../edit#gid=0'
            create_google_sheet(data, sheet_url, json_keyfile_path)
            print("Data has been uploaded to Google Sheets successfully.")
        else:
            print("No data to write to Google Sheets.")
    else:
        print("No engagements with 'In Progress' status found.")

