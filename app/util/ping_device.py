import json
import requests
import ipaddress
import os
from subprocess import Popen, PIPE


def main():
    # Get from request to http://127.0.0.1:8000/inventory/api/
    # Get all devices
    response = requests.get("http://127.0.0.1:8000/inventory/api/")
    devices = response.json()
    for device in devices:
        # Get the IP address from the device
        ipaddr = device["ip"]
        # Get the status of the device
        status, ip_address = subnet_scan(ipaddr)
        print(f"IP Address: {ip_address} is {status}")


def subnet_scan(host):
    os_ping = Popen(["ping", "-c", "1", "-W", "2", host], stdout=PIPE, shell=False)
    os_ping.communicate()[0]
    if os_ping.returncode == 0:
        status = "up"
    else:
        status = "down"
    return status, host


if __name__ == "__main__":
    main()
