import requests
import base64
import logging

# Create a logger object
logger = logging.getLogger(__name__)
# Set log level
logger.setLevel(logging.INFO)


def log_method_args(method):
    def wrapper(self, *args, **kwargs):
        method_name = method.__name__
        args_str = ", ".join([f"{arg!r}" for arg in args])
        kwargs_str = ", ".join([f"{key}={value!r}" for key, value in kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))
        logger.info(f"Calling {method_name}({all_args})")
        result = method(self, *args, **kwargs)
        return result
    return wrapper

def get_resource_record(id = 0, host='', ip=''):

    # Define the data for updating an "A" record
    data = {
        "id": id, # Id is path parameter and not required in the request body
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

class NameCom:
    """
    This class provides methods for interacting with the Name.com API. The host name is currently implicit in the class.
    """

    @log_method_args
    def __init__(self, api_username, api_token, domain, host):
        self.api_username = api_username
        self.api_token = api_token
        self.domain = domain
        self.host = host
        
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
        logger.info('NameCom initialized')

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

    @log_method_args
    def create_record(self, ip):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.domain}/records"

        data = get_resource_record(id=0, host=self.host, ip=ip)

        # Make the API request with authentication
        response = requests.post(api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            logger.info("Response Data:")
            logger.info(data)
            return data["id"]
        else:
            logger.info(f"Error: Request failed with status code {response.status_code}")
            logger.info("Response Content:")
            logger.info(response.text)
            return None
        
    @log_method_args
    def update_record(self, id, ip):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.domain}/records/{id}"

        data = get_resource_record(id = 0, host=self.host, ip=ip)

        # Make the API request with authentication
        response = requests.put(api_url, json=data, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            logger.info("Response Data:")
            logger.info(data)
            return data["id"]
        else:
            logger.info(f"Error: Request failed with status code {response.status_code}")
            logger.info("Response Content:")
            logger.info(response.text)
            return None
            
    @log_method_args
    def get_record(self, id):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.domain}/records/{id}"

        # Make the API request with authentication
        response = requests.get(api_url, headers=self.headers)
    
        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            logger.info(data)
            return data
        else:
            logger.info(f"Error: Request failed with status code {response.status_code}")
            logger.info("Response Content:")
            logger.info(response.text)
            return None

    @log_method_args
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
        api_url = f"{self.API_BASE_URL}/domains/{self.domain}/records"

        # Make the API request with authentication
        response = requests.get(api_url, headers=self.headers)

        if response.status_code == 200:
            data = response.json()
            # Process the API response data as needed
            logger.info(data["records"])
            return data["records"]
        else:
            logger.info(f"Error: Request failed with status code {response.status_code}")
            logger.info("Response Content:")
            logger.info(response.text)
            return None
        
    @log_method_args
    def delete_record(self, id):
        # Define the API endpoint
        api_url = f"{self.API_BASE_URL}/domains/{self.domain}/records/{id}"

        # Make the API request with authentication
        response = requests.delete(api_url, headers=self.headers)

        if response.status_code == 204:
            return True
        else:
            logger.info(f"Error: Request failed with status code {response.status_code}")
            logger.info("Response Content:")
            logger.info(response.text)
            return None

    @log_method_args
    def read_host_record(self):
        """
        Return the record for the matching host and if 'A' record, if it exists. If not return None
        """
        records = self.list_records()
        if records:
            for record in records:
                logger.info(record)
                if record["type"] == "A" and record["host"] == self.host:
                    return record
        else:
            return None
        
    @log_method_args
    def read_host_answer(self):
        record = self.read_host_record()
        if record:
            return record["answer"]
        else:
            return ""
