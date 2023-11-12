import unittest
from unittest.mock import Mock, patch
from namecom_dns.namecom import NameCom, get_resource_record
from namecom_dns.namecom_update import get_external_ip


class TestNameCom(unittest.TestCase):
    EXTERNAL_IP = "10.0.0.1"
    API_USERNAME = "your-username"
    API_TOKEN = "your-token"
    RECORD_ID = 1234
    DOMAIN="example.com"
    HOST_NAME1 = "host"


    @patch("namecom_dns.namecom.requests.get")
    def test_list_records(self, mock_get):
        """
        Test case for the ListRecords method using the Name.com API.

        This test case creates a mock response for a successful API call, and then calls the list_records method of the namecom class. 
        The method should make a GET request to the Name.com API to retrieve a list of all resource records for the specified domain, and the response should contain a list of resource records.
        The test case asserts that the GET request was made with the correct URL and headers, and that the list of resource records returned by the method matches the expected value.

        Args:
            mock_get (MagicMock): A mock object for the requests.get method.

        Returns:
            None
        """
        
        # Create a mock response for successful API call
        mock_response = Mock()
        resource_records = {
            "records": [
            {
                "id": TestNameCom.RECORD_ID, # is path parameter and not required in the request body
                "domainName": "example.com", # is path parameter and not required in the request body
                "host": TestNameCom.HOST_NAME1, # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                        # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                        # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
                "fqdn": "fqdn1", #is read-only and not required in the request body
                "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
                "answer": TestNameCom.EXTERNAL_IP,   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                        # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
                "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
                "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
            },
            {
                "id": 5678, # is path parameter and not required in the request body
                "domainName": "example.com", # is path parameter and not required in the request body
                "host": "host2", # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                        # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                        # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
                "fqdn": "fqdn2", #is read-only and not required in the request body
                "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
                "answer": "5.6.7.8",   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                        # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
                "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
                "priority": 20,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
            }
        ]
        }
        mock_response.json.return_value = resource_records
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        namecom_instance = NameCom(TestNameCom.API_USERNAME, TestNameCom.API_TOKEN, TestNameCom.DOMAIN, TestNameCom.HOST_NAME1)

        records = namecom_instance.list_records()

        # Assertions
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["id"], TestNameCom.RECORD_ID)
        self.assertEqual(records[0]["host"], TestNameCom.HOST_NAME1)
        self.assertEqual(records[0]["answer"], TestNameCom.EXTERNAL_IP)
        self.assertEqual(records[1]["id"], 5678)
        self.assertEqual(records[1]["host"], "host2")
        self.assertEqual(records[1]["answer"], "5.6.7.8")
        mock_get.assert_called_once_with(
            f"https://api.name.com/v4/domains/{TestNameCom.DOMAIN}/records",
            headers=namecom_instance.headers
        )

    @patch("namecom_dns.namecom.requests.get")
    def test_get_record(self, mock_get):
        """
        Test case for GetRecord, retrieving a DNS record using the Name.com API.

        This test case creates a mock response for a successful API call and verifies that the correct API endpoint is called
        with the expected parameters. It also asserts that the record returned by the API matches the expected value.

        Args:
            mock_get: A mock object for the requests.get method.

        Returns:
            None
        """
        # Create a mock response for successful API call
        mock_response = Mock()
        resource_record = {
            "id": TestNameCom.RECORD_ID, # is path parameter and not required in the request body
            "domainName": "example.com", # is path parameter and not required in the request body
            "host": TestNameCom.HOST_NAME1, # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                    # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                    # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
            "fqdn": "fqdn", #is read-only and not required in the request body
            "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
            "answer": TestNameCom.EXTERNAL_IP,   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                    # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
            "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
            "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
        }
        mock_response.json.return_value = resource_record
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        namecom_instance = NameCom(TestNameCom.API_USERNAME, TestNameCom.API_TOKEN, TestNameCom.DOMAIN, TestNameCom.HOST_NAME1)

        record = namecom_instance.get_record(TestNameCom.RECORD_ID)

        # Assertions
        self.assertEqual(record, resource_record)
        mock_get.assert_called_once_with(
        f"https://api.name.com/v4/domains/{TestNameCom.DOMAIN}/records/{TestNameCom.RECORD_ID}",
        headers=namecom_instance.headers
        )

    @patch("namecom_dns.namecom.requests.post")
    def test_create_record(self, mock_post):
        """
        Test case for CreateRecord, creating a DNS record using the Name.com API.

        This test case creates a mock response for a successful API call and verifies that the correct API endpoint is called
        with the expected parameters. It also asserts that the record ID returned by the API matches the expected value.

        Args:
            mock_post: A mock object for the requests.post method.

        Returns:
            None
        """
        # Create a mock response for successful API call
        mock_response = Mock()
        resource_record = {
            "id": TestNameCom.RECORD_ID, # is path parameter and not required in the request body
            "domainName": "example.com", # is path parameter and not required in the request body
            "host": TestNameCom.HOST_NAME1, # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                    # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                    # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
            "fqdn": "fqdn", #is read-only and not required in the request body
            "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
            "answer": TestNameCom.EXTERNAL_IP,   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                    # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
            "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
            "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
        }
        mock_response.json.return_value = resource_record
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        namecom_instance = NameCom(TestNameCom.API_USERNAME, TestNameCom.API_TOKEN, TestNameCom.DOMAIN, TestNameCom.HOST_NAME1)

        record_id = namecom_instance.create_record(TestNameCom.EXTERNAL_IP)

        # Assertions
        self.assertEqual(record_id, TestNameCom.RECORD_ID)
        mock_post.assert_called_once_with(
        f"https://api.name.com/v4/domains/{TestNameCom.DOMAIN}/records",
        json=get_resource_record(id = 0, host=TestNameCom.HOST_NAME1, ip=TestNameCom.EXTERNAL_IP),
        headers=namecom_instance.headers
        )

    @patch("namecom_dns.namecom.requests.put")
    def test_update_record(self, mock_put):
        """
        Test case for the UpdateRecord method using the Name.com API.

        This test case creates a mock response for a successful API call, and then calls the update_record method of the namecom class with a record ID and an external IP address. 
        The method should make a PUT request to the Name.com API to update the record with the specified ID, and the request body should contain the updated resource record with the new IP address. 
        The test case asserts that the PUT request was made with the correct URL, request body, and headers.

        Args:
            mock_put (MagicMock): A mock object for the requests.put method.

        Returns:
            None
        """
        
        # Create a mock response for successful API call
        mock_response = Mock()
        resource_record = {
            "id": TestNameCom.RECORD_ID, # is path parameter and not required in the request body
            "domainName": "example.com", # is path parameter and not required in the request body
            "host": TestNameCom.HOST_NAME1, # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                    # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                    # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
            "fqdn": "fqdn", #is read-only and not required in the request body
            "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
            "answer": TestNameCom.EXTERNAL_IP,   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                    # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
            "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
            "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
        }
        mock_response.json.return_value = resource_record
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        namecom_instance = NameCom(TestNameCom.API_USERNAME, TestNameCom.API_TOKEN, TestNameCom.DOMAIN, TestNameCom.HOST_NAME1)

        namecom_instance.update_record(TestNameCom.RECORD_ID, TestNameCom.EXTERNAL_IP)

        # Assertions
        mock_put.assert_called_once_with(
            f"https://api.name.com/v4/domains/{TestNameCom.DOMAIN}/records/{TestNameCom.RECORD_ID}",
            json=get_resource_record(id = 0, host=TestNameCom.HOST_NAME1, ip=TestNameCom.EXTERNAL_IP),
            headers=namecom_instance.headers
        )

    @patch("namecom_dns.namecom.requests.delete")
    def test_delete_record(self, mock_delete):
        """
        Test case for the DeleteRecord method using the Name.com API.

        This test case creates a mock response for a successful API call, and then calls the delete_record method of the namecom class with a record ID. 
        The method should make a DELETE request to the Name.com API to delete the record with the specified ID. 
        The test case asserts that the DELETE request was made with the correct URL and headers.

        Args:
            mock_delete (MagicMock): A mock object for the requests.delete method.

        Returns:
            None
        """
        # Create a mock response for successful API call
        mock_response = Mock()
        mock_response.status_code = 204
        mock_delete.return_value = mock_response

        namecom_instance = NameCom(TestNameCom.API_USERNAME, TestNameCom.API_TOKEN, TestNameCom.DOMAIN, TestNameCom.HOST_NAME1)

        namecom_instance.delete_record(TestNameCom.RECORD_ID)

        # Assertions
        mock_delete.assert_called_once_with(
            f"https://api.name.com/v4/domains/{TestNameCom.DOMAIN}/records/{TestNameCom.RECORD_ID}",
            headers=namecom_instance.headers
        )
        
    @patch("namecom_update.requests.get")
    def test_get_external_ip(self, mock_get):
        """
        Test the get_external_ip function.

        This test creates a mock response for successful IP retrieval and asserts that the IP returned by the function
        matches the expected external IP. It also asserts that the mock GET request was made with the correct URL.

        :param mock_get: A mock GET request object.
        """
        # Create a mock response for successful IP retrieval
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = TestNameCom.EXTERNAL_IP
        mock_get.return_value = mock_response

        ip = get_external_ip()

        # Assertions
        self.assertEqual(ip, TestNameCom.EXTERNAL_IP)
        mock_get.assert_called_once_with("https://ipinfo.io/ip")

    @patch("namecom_update.requests.get")
    def test_get_external_ip_failure(self, mock_get):
        """
        Test case to verify that the get_external_ip function returns empty string when the IP retrieval fails.
        """
        # Create a mock response for unsuccessful IP retrieval
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = ''
        mock_get.return_value = mock_response

        ip = get_external_ip()

        # Assertions
        self.assertEqual(ip, "")
        mock_get.assert_called_once_with("https://ipinfo.io/ip")


if __name__ == "__main__":
    unittest.main()
