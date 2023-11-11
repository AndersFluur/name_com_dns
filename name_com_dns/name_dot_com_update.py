# Description: Update DNS records with external IP address

from name_com_dns.name_com import NameCom
import requests
import argparse
import time
import os
import sys

def get_external_ip():
    IP_CHECK_URL = "https://ipinfo.io/ip"
    response = requests.get(IP_CHECK_URL)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return ""
        
def main():                         
    # Define and parse command-line arguments
    parser = argparse.ArgumentParser(description="Update DNS records with external IP address")
    parser.add_argument("-n", "--name", required=True, help="Host name")
    parser.add_argument("-d", "--domain", required=True, help="Domain name")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Polling interval in seconds")
    parser.add_argument("-t", "--test", type=bool, default=False, help="Test mode. Run loop interval number of times and exit.")
    
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

    NameDotCom = NameCom(api_username, api_token, args.domain, args.name)
    
    # Set the id of DNS record for the host from start. It will be challenged below.
    id = 0

    current_ip = get_external_ip()
    if current_ip:
        print(f"Initial  external IP: {current_ip}")
    else:
        current_ip = "0.0.0.0"
        print(f"No Initial IP! Continuing with IP: {current_ip}")   
    
    # Check if there is a DNS A record already
    record = NameDotCom.read_host_record()
    if record:
        # There should be a record answer and an id
        current_ip = record["answer"]
        id = record["id"]
        print(f"Initial Read if ID: {id}  IP: {current_ip}")
    else: # No DNS record for the host is found. Create one.
        id = NameDotCom.create_record(current_ip)
        print(f"Created a new A record with IP: {current_ip} and ID: {id}")


    if args.test:
        number_of_loops = args.interval
    else:
        number_of_loops = 0
    while True:
        new_ip = get_external_ip()
        if new_ip and new_ip != current_ip:
            print(f"New IP address detected: {new_ip}")
            if id != 0 and id != None:
                print(f"Update for ID: {id}  IP: {new_ip}")
                NameDotCom.update_record(id, new_ip)
            else:
                print(f"Create for  IP: {new_ip}")
                id = NameDotCom.create_record(new_ip)
            current_ip = new_ip
        
        if args.test and number_of_loops != 0:
            number_of_loops +=-1
            print(f"Test mode. Run loop interval number of times and exit. loop={number_of_loops}")
        elif args.test and number_of_loops == 0:
            print(f"Test mode. Run loop finished, exiting! loop={number_of_loops}")
            sys.exit(0)
        else:
            print(f"Sleeping for {args.interval} seconds")
            time.sleep(args.interval)

if __name__ == "__main__":
    main()