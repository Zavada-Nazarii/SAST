# Проєкт для автоматизації аналізу та звітування

Цей проєкт містить кілька скриптів та конфігураційних файлів, що використовуються для автоматизації процесу аналізу, генерації звітів та інтеграції з CI/CD пайплайнами.

## Вміст репозиторію

### Скрипти

1. **download_and_analyze.py**
   - Скрипт спеціально для завантаження та аналізу файлів мобільних додатків. Він завантажує файли на сервер MobSF.

2. **report_analises.py**
   - Використовується для аналізу звітів. Скрипт обробляє дані, отримані після проведення аналізу, і генерує звіти.

3. **report_pdf.py**
   - Призначений для генерації PDF-звітів на основі аналізу. Скрипт конвертує результати аналізу у формат PDF для подальшого використання.

4. **SAST_Notification.py**
   - Скрипт для надсилання сповіщень про результати статичного аналізу коду (SAST). Він інтегрується з системами сповіщень, такими як Slack.

### Конфігураційні файли

1. **gitlab-ci-someproject.yml**
   - Файл конфігурації для CI/CD процесів на GitLab. Використовується для автоматизації завантаження звітів та їх обробки.

2. **gitlab-ci-slack.yml**
   - Інший файл конфігурації для CI/CD процесів на GitLab, але з акцентом на інтеграцію з Slack для надсилання сповіщень.

### Скрипт для імпорту

1. **import_scan_result_searchService.sh**
   - Bash-скрипт, що використовується для імпорту результатів сканування в систему. Він інтегрується з DefectDojo або іншими платформами для керування вразливостями.


