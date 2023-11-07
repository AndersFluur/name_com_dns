#!/usr/bin/env python3

import argparse
import requests
import json
import time
import os
import sys
import base64

def get_resource_record(host, ip):

    # Define the data for updating an "A" record
    data = {
        # "id": is path parameter and not required in the request body
        # "domainName": is path parameter and not required in the request body
        "host": host, # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
        # "fqdn": ,is read-only and not required in the request body
        "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
        "answer": ip,   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                        # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
        "ttl": 300      # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
        #"priority": 10  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
    }
    return data

def get_external_ip():
    IP_CHECK_URL = "https://ipinfo.io/ip"
    response = requests.get(IP_CHECK_URL)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return ""
        
class name_com:

    def __init__(self, api_username, api_token, args):
        self.api_username = api_username
        self.api_token = api_token
        self.args = args
        
        # Determine the API server based on the api_username
        if api_username.endswith("-test"):
            API_BASE_URL = "https://api.dev.name.com/v4"
        else:
            API_BASE_URL = "https://api.name.com/v4"
            
        self.set_api_base_url(api_username)

        # Set the Content-Type header to application/json
        self.headers = {
            "Authorization": self.get_auth_header(),
            "Content-Type": "application/json"
        }

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

    def create_record(self, ip):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records"

        data = get_resource_record(self.args.name, ip)

        # Make the API request with authentication
        response = requests.post(api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            print("Response Data:")
            print(data)
            return data["id"]
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None
        
    def update_record(self, id, ip):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records/{id}"

        data = get_resource_record(self.args.name, ip)

        # Make the API request with authentication
        response = requests.put(api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            print("Response Data:")
            print(data)
            return data["id"]
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None
            
    def get_record(self, id):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records/{id}"

        # Make the API request with authentication
        response = requests.get(api_url, headers=self.headers)
    
        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            print(data)
            return data
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None

    def list_records(self):
        """"
         Return a List all records for a domain
         example:
         {
            "records": [
                {
                    "id": 12345,
                    "domainName": "example.org",
                    "host": "www",
                    "fqdn": "www.example.org",
                    "type": "A",
                    "answer": "10.0.0.1",
                    "ttl": 300
                }
            ]
        }
        """
       
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records"

        # Make the API request with authentication
        response = requests.get(api_url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            print(data["records"])
            return data["records"]
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None
        
    def delete_record(self, id):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.args.domain}/records/{id}"

        # Make the API request with authentication
        response = requests.delete(api_url)

        if response.status_code == 200:
            return True
        else:
            print(f"Error: Request failed with status code {response.status_code}")
            print("Response Content:")
            print(response.text)
            return None

    def read_host_record(self):
        records = self.list_records()
        if records:
            for record in records:
                print(record)
                if record["type"] == "A" and record["host"] == self.args.name:
                    return record
        else:
            return None
        
    def read_host_answer(self):
        record = self.read_host_record()
        if record:
            return record["answer"]
        else:
            return ""
                         
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

    NameDotCom = name_com(api_username, api_token, args)
    
    # Set the id of DNS record for the host from start. It will be challenged below.
    id = None

    # Same goes for the current IP address
    current_ip = ""

    record = NameDotCom.read_host_record()

    #  The host record is found or not found. If found there is a record id for it. If not found the id is None.
    if record: # If not None there should be a record answer and an id
        current_ip = record["answer"]
        id = record["id"]
    else: # No DS record for the host is found. Create one.
        current_ip = get_external_ip()
        if current_ip:
            print(f"Initial Create for IP: {current_ip}")
            id = NameDotCom.create_record(current_ip)
        else:
            print(f"No Initial IP: {current_ip}. Continuing without ID and IP")

    while True:
        new_ip = get_external_ip()
        if new_ip and new_ip != current_ip:
            print(f"New IP address detected: {new_ip}")
            if id:
                print(f"Update for ID: {id}  IP: {new_ip}")
                NameDotCom.update_record(id, new_ip)
            else:
                print(f"Create for  IP: {new_ip}")
                id = NameDotCom.create_record(new_ip)
            current_ip = new_ip
        time.sleep(args.interval)