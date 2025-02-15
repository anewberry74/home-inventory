# This script calls get API to get device ID. Then use device ID to call /inventory/api/{inventory_id}/state to update the state of the device in the inventory.
import json
import requests


def main():
    response = requests.get("http://0.0.0.0:8000/inventory/api/")
    devices = response.json()
    for device in devices:
        id = device["id"]
        response = requests.patch(f"http://0.0.0.0:8000/inventory/api/{id}/state")
        print(response.json())


if __name__ == "__main__":
    main()
