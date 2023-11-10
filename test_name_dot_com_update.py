#!/usr/bin/python3
import unittest
from unittest.mock import Mock, patch
from name_dot_com_update import name_com, get_resource_record, get_external_ip


class TestNameCom(unittest.TestCase):
    EXTERNAL_IP = "10.0.0.1"

    # Add test for List Records
    # Add test for Get Record

    @patch("name_dot_com_update.requests.post")
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
            "id": 1234, # is path parameter and not required in the request body
            "domainName": "example.com", # is path parameter and not required in the request body
            "host": "host", # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                    # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                    # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
            "fqdn": "fqdn", #is read-only and not required in the request body
            "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
            "answer": "1.2.3.4",   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                    # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
            "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
            "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
        }
        mock_response.json.return_value = resource_record
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        api_username = "your-username"
        api_token = "your-token"
        args = Mock(domain="example.com", name="host")
        name_com_instance = name_com(api_username, api_token, args)

        record_id = name_com_instance.create_record(TestNameCom.EXTERNAL_IP)

        # Assertions
        self.assertEqual(record_id, 1234)
        mock_post.assert_called_once_with(
        f"https://api.name.com/v4/domains/{args.domain}/records",
        json=get_resource_record(args.name, TestNameCom.EXTERNAL_IP),
        headers=name_com_instance.headers
        )

    @patch("name_dot_com_update.requests.put")
    def test_update_record(self, mock_put):
        """
        Test case for the UpdateRecord method using the Name.com API.

        This test case creates a mock response for a successful API call, and then calls the update_record method of the name_com class with a record ID and an external IP address. 
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
            "id": 1234, # is path parameter and not required in the request body
            "domainName": "example.com", # is path parameter and not required in the request body
            "host": "host", # Host is the hostname relative to the zone: e.g. for a record for blog.example.org, domain would be "example.org" and host would be "blog".
                                    # An apex record would be specified by either an empty host "" or "@". A SRV record would be specified by "_{service}._{protocal}.{host}":
                                    # e.g. "_sip._tcp.phone" for _sip._tcp.phone.example.org.
            "fqdn": "fqdn", #is read-only and not required in the request body
            "type": "A",    # One of A, AAAA, CNAME, MX, NS, SRV, TXT, URL
            "answer": "1.2.3.4",   # answer is either the IP address for A or AAAA records; the target for ANAME, CNAME, MX, or NS records; the text for TXT records.
                                    # For SRV records, answer has the following format: "{weight} {port} {target}" e.g. "1 5061 sip.example.org".
            "ttl": 300,     # TTL is the time this record can be cached for in seconds. Name.com allows a minimum TTL of 300, or 5 minutes.
            "priority": 10,  # Priority is only required for MX and SRV records. It is an integer between 0 and 65535.
        }
        mock_response.json.return_value = resource_record
        mock_response.status_code = 200
        mock_put.return_value = mock_response

        api_username = "your-username"
        api_token = "your-token"
        args = Mock(domain="example.com", name="host")
        name_com_instance = name_com(api_username, api_token, args)

        record_id = 1234
        name_com_instance.update_record(record_id, TestNameCom.EXTERNAL_IP)

        # Assertions
        mock_put.assert_called_once_with(
            f"https://api.name.com/v4/domains/{args.domain}/records/{record_id}",
            json=get_resource_record(args.name, TestNameCom.EXTERNAL_IP),
            headers=name_com_instance.headers
        )

    @patch("name_dot_com_update.requests.delete")
    def test_delete_record(self, mock_delete):
        """
        Test case for the DeleteRecord method using the Name.com API.

        This test case creates a mock response for a successful API call, and then calls the delete_record method of the name_com class with a record ID. 
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

        api_username = "your-username"
        api_token = "your-token"
        args = Mock(domain="example.com", name="host")
        name_com_instance = name_com(api_username, api_token, args)

        record_id = 1234
        name_com_instance.delete_record(record_id)

        # Assertions
        mock_delete.assert_called_once_with(
            f"https://api.name.com/v4/domains/{args.domain}/records/{record_id}",
            headers=name_com_instance.headers
        )
        
    @patch("name_dot_com_update.requests.get")
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

    @patch("name_dot_com_update.requests.get")
    def test_get_external_ip_failure(self, mock_get):
        """
        Test case to verify that the get_external_ip function returns None when the IP retrieval fails.
        """
        # Create a mock response for unsuccessful IP retrieval
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        ip = get_external_ip()

        # Assertions
        self.assertIsNone(ip)
        mock_get.assert_called_once_with("https://ipinfo.io/ip")


if __name__ == "__main__":
    unittest.main()
