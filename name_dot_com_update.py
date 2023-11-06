#!/usr/bin/env python3

import argparse
import requests
import time
import os
import sys
import base64

def get_external_ip():
    response = requests.get(IP_CHECK_URL)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return None

def update_dns(ip):
    # Implement the logic to update the DNS record with the new IP
    # You can make API requests to Name.com to update the DNS record here
    # The API documentation is available at https://www.name.com/api-docs/

    # Define the API endpoint and request headers
    api_url = f"{API_BASE_URL}/domains/{args.domain}/records"

    # Construct the authentication header
    auth_header = (api_username + ":" + api_token).encode("utf-8")
    auth_header = base64.b64encode(auth_header).decode("utf-8")

    # Define the data for adding an "A" record
    data = {
        "host": args.host,
        "type": "A",
        "answer": ip,
        "ttl": 300
    }

    # Set the Content-Type header to application/json
    headers = {
        "Authorization": "Basic " + auth_header,
        "Content-Type": "application/json"
    }

    # Make the API request with authentication
    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Process the API response data as needed
        print(data)
    else:
        print(f"Error: Request failed with status code {response.status_code}")
        print("Response Content:")
        print(response.text)
        sys.exit(1)  # Exit the script with an error

if __name__ == "__main__":
    # Define and parse command-line arguments
    parser = argparse.ArgumentParser(description="Update DNS records with external IP address")
    parser.add_argument("host", help="Host name")
    parser.add_argument("domain", help="Domain name")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Polling interval in seconds")
    args = parser.parse_args()

    # Name.com API credentials
    API_USERNAME_VAR = "API_USERNAME"
    API_TOKEN_VAR = "API_TOKEN"

    # Check and assign API_USERNAME
    api_username = os.environ.get(API_USERNAME_VAR)
    if not api_username:
        print(f"Error: Environment variable {API_USERNAME_VAR} is not set.")
        sys.exit(1)

    # Check and assign API_TOKEN
    api_token = os.environ.get(API_TOKEN_VAR)
    if not api_token:
        print(f"Error: Environment variable {API_TOKEN_VAR} is not set.")
        sys.exit(1)

    # Determine the API server based on the api_username
    if api_username.endswith("-test"):
        API_BASE_URL = "https://api.dev.name.com/v4"
    else:
        API_BASE_URL = "https://api.name.com/v4"

    IP_CHECK_URL = "https://ipinfo.io/ip"

    current_ip = ""
    while True:
        new_ip = get_external_ip()
        if new_ip and new_ip != current_ip:
            print(f"New IP address detected: {new_ip}")
            update_dns(new_ip)
            current_ip = new_ip
        time.sleep(args.interval)