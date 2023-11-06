#!/usr/bin/env python3

import argparse
import requests
import time
import os
import sys
import base64

import requests
import time
import os
import sys
import base64

class name_com:
    API_BASE_URL = ""
    IP_CHECK_URL = "https://ipinfo.io/ip"

    def __init__(self, api_username, api_token, args):
        self.api_username = api_username
        self.api_token = api_token
        self.args = args
        self.set_api_base_url(api_username)

    def set_api_base_url(self, api_username):
        if api_username.endswith("-test"):
            self.API_BASE_URL = "https://api.dev.name.com/v4"
        else:
            self.API_BASE_URL = "https://api.name.com/v4"

    def get_api_username(self):
        return self.api_username 

    def get_api_token(self):
        return self.api_token

    def get_auth_header(self):
        auth_header = (self.get_api_username() + ":" + self.get_api_token()).encode("utf-8")
        auth_header = base64.b64encode(auth_header).decode("utf-8")
        return "Basic " + auth_header

    def get_external_ip(self):
        response = requests.get(self.IP_CHECK_URL)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return None

    def update_dns(self, ip):
        # Define the API endpoint and request headers
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records"

        # Define the data for adding an "A" record
        data = {
            "host": self.args.name,
            "type": "A",
            "answer": ip,
            "ttl": 300
        }

        # Set the Content-Type header to application/json
        headers = {
            "Authorization": self.get_auth_header(),
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
    parser.add_argument("-n", "--name", required=True, help="Host name")
    parser.add_argument("-d", "--domain", required=True, help="Domain name")
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

    current_ip = ""
    name_com = name_com(api_username, api_token, args)
    while True:
        new_ip = name_com.get_external_ip()
        if new_ip and new_ip != current_ip:
            print(f"New IP address detected: {new_ip}")
            name_com.update_dns(new_ip)
            current_ip = new_ip
        time.sleep(args.interval)