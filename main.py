import os
import subprocess
import sys
import json
import time

import requests

# services = {
#   'name': '',
#   'github_token': '',
#   'repository_name': '',
#   'repository_folder': ''
# }


# Функция для обновления кода из GitHub
def update_code(service):
    # Остановка сервиса
    subprocess.run(['systemctl', 'stop', service['name']])

    # Получаем список коммитов из GitHub
    response = requests.get(f'https://api.github.com/repos/{service["repository_name"]}/commits',
                            headers={'Authorization': f'Bearer {service["github_token"]}'})
    commits = response.json()

    # Получаем последний коммит
    last_commit = commits[0]

    # Клонируем репозиторий, если он не существует
    if not os.path.exists(service["repository_folder"]):
        subprocess.run(['git', 'clone',
                        f'https://github.com/{service["repository_name"]}.git', service["repository_folder"]])

    # Обновляем код из репозитория
    subprocess.run(['git', 'pull'], cwd=service["repository_folder"])

    # Перезапуск сервиса
    subprocess.run(['systemctl', 'start', service['name']])


# Слушаем события из GitHub
def listen_events(service):
    response = requests.get(f'https://api.github.com/repos/{service["repository_name"]}/events',
                            headers={'Authorization': f'Bearer {service["github_token"]}'})
    events = response.json()

    for event in events:
        handle_event(event['type'], service)


def main(services_file_path):
    with open(services_file_path, 'r') as f:
        services = json.loads(f.read())

    for service in services:
        listen_events(service)

    # Ждем 1 минуту и слушаем события снова
    time.sleep(60)
    main(services_file_path)


# Запуск сервиса
if __name__ == '__main__':
    services_file_path = sys.argv[1]
    main(services_file_path)
