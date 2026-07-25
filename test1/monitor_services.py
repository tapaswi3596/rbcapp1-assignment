import json
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests


SERVICES = [
    "httpd",
    "rabbitmq-server",
    "postgresql",
]

API_URL = "http://localhost:5000/add"
OUTPUT_DIR = Path("service_status")


def get_service_status(service_name):
    result = subprocess.run(
        ["systemctl", "is-active", service_name],
        capture_output=True,
        text=True
    )

    if result.stdout.strip() == "active":
        return "UP"

    return "DOWN"


def create_status(service_name, status):
    return {
        "service_name": service_name,
        "service_status": status,
        "host_name": socket.gethostname(),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }


def save_status_file(service_name, status_data):
    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{service_name}-status-{timestamp}.json"

    file_path = OUTPUT_DIR / filename

    with open(file_path, "w") as file:
        json.dump(status_data, file, indent=4)

    return file_path


def send_to_api(file_path):
    with open(file_path, "rb") as file:
        response = requests.post(
            API_URL,
            files={"file": file},
            timeout=10
        )

    response.raise_for_status()

    return response.json()


def main():
    for service in SERVICES:
        status = get_service_status(service)
        status_data = create_status(service, status)
        file_path = save_status_file(service, status_data)

        print(f"{service}: {status}")
        print(f"Status file created: {file_path}")

        try:
            result = send_to_api(file_path)
            print(f"Uploaded successfully: {result}")

        except requests.RequestException as error:
            print(f"Could not upload {service} status: {error}")


if __name__ == "__main__":
    main()
