import subprocess
import sys
import json
import time

# services = [{
#   'service_name': '',
#   'repository_folder': '',
#   'local_branch_name': 'master',
#   'remote_branch_name': 'origin/master'
# },]


# Функция для обновления кода из GitHub
def update_code(service):
    # Остановка сервиса
    subprocess.run(['systemctl', 'stop', service['service_name']])

    # Обновляем код из репозитория
    subprocess.run(['git', 'pull'], cwd=service["repository_folder"])

    # Перезапуск сервиса
    subprocess.run(['systemctl', 'start', service['service_name']])


# Слушаем события из GitHub
def listen_events(service):
    cmd = ["git", "rev-list", "--count", "--left-right",
           f"{service['remote_branch_name']}...{service['local_branch_name']}"]
    result = subprocess.run(cmd, cwd=service["repository_folder"], capture_output=True, text=True)

    output = result.stdout.strip()[0]
    print(f'!!!{output}!!!')
    if output != "0":
        update_code(service)


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
