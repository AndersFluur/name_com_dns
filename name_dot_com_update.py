#!/usr/bin/env python3

import requests
import time
import os
import sys
import base64

# Name.com API credentials


# Environment variable names
API_USERNAME_VAR = "API_USERNAME"
API_TOKEN_VAR = "API_TOKEN"

# Check and assign API_USERNAME
api_username = os.environ.get("API_USERNAME")
if not api_username:
    print(f"Error: Environment variable {API_USERNAME_VAR} is not set.")
    sys.exit(1) # Exit the script with an error

# Check and assign API_TOKEN
api_token = os.environ.get(API_TOKEN_VAR)
if not api_token:
    print(f"Error: Environment variable {API_TOKEN_VAR} is not set.")
    sys.exit(1) # Exit the script with an error

# If both environment variables are set and not null, you can proceed
print("API_USERNAME:", api_username)
print("API_TOKEN:", api_token)


# Name.com domain and record details
DOMAIN = "fluur.net"
HOST = "host1"

# External IP check URL (you can use other services if you prefer)
IP_CHECK_URL = "https://ipinfo.io/ip"

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
    import requests

    # Define the API endpoint and request headers
    #Test API
    #api_url = f"https://api.dev.name.com/v4/domains/{DOMAIN}/records"

    #Production API
    api_url = f"https://api.name.com/v4/domains/{DOMAIN}/records"
    # Construct the authentication header
    auth_header = (api_username + ":" + api_token).encode("utf-8")
    auth_header = base64.b64encode(auth_header).decode("utf-8")

    # Define the data for adding an "A" record
    data = {
            "host": HOST,
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
    #response = requests.get(api_url, json=data, headers=headers)

    # Create the HTTP request without sending it
    http_request = requests.Request("POST", api_url, json=data, headers=headers)
    prepared_request = http_request.prepare()

    # Print the full HTTP request including headers and body
    print("Full HTTP Request:")
    print(f"{prepared_request.method} {prepared_request.url}")
    for key, value in prepared_request.headers.items():
        print(f"{key}: {value}")
    print()
    print(prepared_request.body)

    # To send the request, you can use the following:
    response = requests.Session().send(prepared_request)
    #sys.exit(1) # Exit the script with an error

    if response.status_code == 200:
        data = response.json()
        # Process the API response data as needed
        print(data)
    else:
                print(f"Error: Request failed with status code {response.status_code}")
                print("Response Content:")
                print(response.text)
                sys.exit(1) # Exit the script with an error
          

if __name__ == "__main__":
    current_ip = ""
    while True:
        new_ip = get_external_ip()
        if new_ip and new_ip != current_ip:
            print(f"New IP address detected: {new_ip}")
            update_dns(new_ip)
            current_ip = new_ip
        time.sleep(60)  # Wait for 60 seconds before checking again


