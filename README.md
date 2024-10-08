# Проєкт для автоматизації аналізу та звітування

Цей проєкт містить кілька скриптів та конфігураційних файлів, що використовуються для автоматизації процесу аналізу, генерації звітів та інтеграції з CI/CD пайплайнами.

## Вміст репозиторію

### Скрипти

1. **[download_and_analyze.py](https://github.com/Zavada-Nazarii/SAST/blob/main/download_and_analyze.py)**
   - Скрипт спеціально для завантаження та аналізу файлів мобільних додатків. Він завантажує файли на сервер MobSF.

2. **[report_analises.py](https://github.com/Zavada-Nazarii/SAST/blob/main/report_analises.py)**
   - Використовується для аналізу звітів. Скрипт обробляє дані, отримані після проведення аналізу, і генерує звіти.

3. **[report_pdf.py](https://github.com/Zavada-Nazarii/SAST/blob/main/report_pdf.py)**
   - Призначений для генерації PDF-звітів на основі аналізу. Скрипт конвертує результати аналізу у формат PDF для подальшого використання.

4. **[SAST_Notification.py](https://github.com/Zavada-Nazarii/SAST/blob/main/SAST_Notification.py)**
   - Скрипт для надсилання сповіщень про результати статичного аналізу коду (SAST). Він інтегрується з системами сповіщень, такими як Slack.
   
5. **[upload_to_slack_pdf.py](https://github.com/Zavada-Nazarii/SAST/blob/main/upload_to_slack_pdf.py)**
   - Скрипт для надсилання сповіщень про результати статичного аналізу коду (SAST) саме файлів які є рузельтатом роботи **report_pdf.py** PDF-звітів. Він інтегрується з системами сповіщень, такими як Slack.

### Конфігураційні файли

1. **[gitlab-ci-someproject.yml](https://github.com/Zavada-Nazarii/SAST/blob/main/gitlab-ci-site.yml)**
   - Файл конфігурації для CI/CD процесів на GitLab. Використовується для автоматизації завантаження звітів та їх обробки.

2. **[gitlab-ci-slack.yml](https://github.com/Zavada-Nazarii/SAST/blob/main/gitlab-ci-slack.yml)**
   - Інший файл конфігурації для CI/CD процесів на GitLab, але з акцентом на інтеграцію з Slack для надсилання сповіщень.

3. **[gitlab-ci-mobsf.yml](https://github.com/Zavada-Nazarii/SAST/blob/main/gitlab-ci-mobsf.yml)**
   - Файл конфігурації для CI/CD процесів на GitLab для тригеру пайплайну щодо сканування релізного мобільного додатку після його збірки.

### Скрипт для імпорту

1. **[import_scan_result_searchService.sh](https://github.com/Zavada-Nazarii/SAST/blob/main/import_scan_result_searchService.sh)**
   - Bash-скрипт, що використовується для імпорту результатів сканування в систему. Він інтегрується з DefectDojo або іншими платформами для керування вразливостями.


