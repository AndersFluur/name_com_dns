#!/usr/bin/env python3
# Description: Update DNS records with external IP address

from namecom_dns.namecom import NameCom
import requests
import argparse
import time
import os
import sys
import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set log level
logger.setLevel(logging.INFO)

def get_external_ip():
    IP_CHECK_URL = "https://ipinfo.io/ip"
    response = requests.get(IP_CHECK_URL)
    if response.status_code == 200:
        return response.text.strip()
    else:
        return ""


def create_logging_handler(logdir="./"):
    # Create a file handler and set its log level
    if logdir:
        if not os.path.exists(logdir): # Create the log directory if it does not exist
            os.makedirs(logdir)
        log_file = os.path.join(logdir, 'namecom.log')
    else:
        log_file = 'namecom.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    # Create a log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

def main():                         
    # Define and parse command-line arguments
    parser = argparse.ArgumentParser(description="Update DNS records with external IP address")
    parser.add_argument("-n", "--name", required=False, help="Host name")
    parser.add_argument("-d", "--domain", required=True, help="Domain name")
    parser.add_argument("-i", "--interval", type=int, default=60, help="Polling interval in seconds")
    parser.add_argument("-t", "--test", type=bool, default=False, help="Test mode. Run loop interval number of times and exit.")
    parser.add_argument("-l", "--log", action="store_true", help="Log to namecom_dns.log")
    parser.add_argument("--logdir", type=str, default="./", help="Log to namecom_dns.log in the specified directory")

    
    args = parser.parse_args()

    if args.log:
        create_logging_handler(args.logdir)

    # Name.com API credentials
    APIUSERNAME_VAR = "NAMECOM_APIUSERNAME"
    APITOKEN_VAR = "NAMECOM_APITOKEN"

    # Check and assign API_USERNAME
    api_username = os.environ.get(APIUSERNAME_VAR)
    if not api_username:
        logger.info(f"Error: Environment variable {APIUSERNAME_VAR} is not set.")
        sys.exit(1)

    # Check and assign API_TOKEN
    api_token = os.environ.get(APITOKEN_VAR)
    if not api_token:
        logger.info(f"Error: Environment variable {APITOKEN_VAR} is not set.")
        sys.exit(1)

    logger.info(f"Starting service")   

    NameDotCom = NameCom(api_username, api_token, args.domain, args.name)
    
    # Set the id of DNS record for the host from start. It will be challenged below.
    id = 0

    current_ip = get_external_ip()
    if current_ip:
        logger.info(f"Initial  external IP: {current_ip}")
    else:
        current_ip = "0.0.0.0"
        logger.info(f"No Initial IP! Continuing with IP: {current_ip}")   
    
    # Check if there is a DNS A record already
    record = NameDotCom.read_host_record()
    if record:
        # There should be a record answer and an id
        current_ip = record["answer"]
        id = record["id"]
        logger.info(f"Initial Read of ID: {id}  IP: {current_ip}")
    else: # No DNS record for the host is found. Create one.
        id = NameDotCom.create_record(current_ip)
        logger.info(f"Created a new A record for FQDN: {args.name}.{args.domain} with IP: {current_ip} and ID: {id}")


    if args.test:
        number_of_loops = args.interval
    else:
        number_of_loops = 0
    while True:
        new_ip = get_external_ip()
        if new_ip and new_ip != current_ip:
            logger.info(f"New IP address detected: {new_ip}")
            if id != 0 and id != None:
                logger.info(f"Update for ID: {id}  IP: {new_ip}")
                NameDotCom.update_record(id, new_ip)
            else:
                logger.info(f"Create for  IP: {new_ip}")
                id = NameDotCom.create_record(new_ip)
            current_ip = new_ip
        
        if args.test and number_of_loops != 0:
            number_of_loops +=-1
            logger.info(f"Test mode. Run loop interval number of times and exit. loop={number_of_loops}")
        elif args.test and number_of_loops == 0:
            logger.info(f"Test mode. Run loop finished, exiting! loop={number_of_loops}")
            sys.exit(0)
        else:
            # Don't spam the log logger.info(f"Sleeping for {args.interval} seconds")
            time.sleep(args.interval)

if __name__ == "__main__":
    main()