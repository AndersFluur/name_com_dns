#!/usr/bin/python3

import unittest
from unittest.mock import patch, MagicMock, call
from name_com_dns.name_com import NameCom, get_resource_record
import name_dot_com_update

# Mock environment variables
def mock_get(var_name, default=None):
    print(f"getenv for '{var_name}'")
    if var_name == 'REQUESTS_CA_BUNDLE':
        return '/etc/ssl/certs/ca-certificates.crt'  # replace with the actual path to your CA bundle
    else:
        return 'test_value'

class TestMainLogic(unittest.TestCase):
        # Mock environment variables
    def mock_get(self, var_name, default=None):
        #print(f"get for '{var_name}'")
        if var_name == 'REQUESTS_CA_BUNDLE':
            return '/etc/ssl/certs/ca-certificates.crt'  # replace with the actual path to your CA bundle
        if var_name == 'API_USERNAME':
            return 'api_username'
        if var_name == 'API_TOKEN':
            return 'api_token'
        else:
            return 'sample_value'
        
    @patch('name_dot_com_update.get_external_ip')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('name_dot_com_update.NameCom')
    def test_main_logic_rr_exist_new_IP(self, mock_name_com, mock_parse_args, mock_get, mock_get_external_ip):
        """
         Verify that the main logic works as expected when the host record is found but the IP address is different.
        """
        
        mock_get_external_ip.return_value = '1.2.3.5'
        
        mock_get.side_effect = self.mock_get
        
        # Mock command-line arguments
        args = MagicMock()
        args.name = 'host1'
        args.domain = 'example.com'
        args.interval = 2
        args.test = True
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_name_com_instance = mock_name_com.return_value
        mock_name_com_instance.read_host_record.return_value = get_resource_record(id = 12345, host='host1', ip='1.2.3.4')
        
        #mock_name_com_instance.create_record.return_value = 12345
        mock_name_com_instance.update_record.return_value = 12345

        try:
            name_dot_com_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'API_USERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'API_TOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_name_com.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_name_com_instance.read_host_record.assert_called_once()
        #mock_name_com_instance.create_record.assert_called_once_with('1.2.3.4')
        mock_name_com_instance.update_record.assert_called_once_with(12345, '1.2.3.5')
        mock_get_external_ip.assert_called()

    @patch('name_dot_com_update.get_external_ip')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('name_dot_com_update.NameCom')
    def test_main_logic_no_rr_same_ip_address(self, mock_name_com, mock_parse_args, mock_get, mock_get_external_ip):
        """
         Verify that the main logic works as expected when no host record is found, but there is no change of IP address.
        """
        
        mock_get_external_ip.return_value = '1.2.3.5'
        
        mock_get.side_effect = self.mock_get
        
        # Mock command-line arguments
        args = MagicMock()
        args.name = 'host1'
        args.domain = 'example.com'
        args.interval = 2
        args.test = True
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_name_com_instance = mock_name_com.return_value
        mock_name_com_instance.read_host_record.return_value = None
        
        mock_name_com_instance.create_record.return_value = 12345
        mock_name_com_instance.update_record.return_value = 12345

        try:
            name_dot_com_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'API_USERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'API_TOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_name_com.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_name_com_instance.read_host_record.assert_called_once()
        mock_name_com_instance.create_record.assert_called_once_with('1.2.3.5')
        #mock_name_com_instance.update_record.assert_called_once_with(12345, '1.2.3.5')
        mock_get_external_ip.assert_called()

    @patch('name_dot_com_update.get_external_ip', side_effect=['1.2.3.5', '1.2.3.4', '1.2.3.4', '1.2.3.5'])
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('name_dot_com_update.NameCom')
    def test_main_logic_no_rr_change_ip_address(self, mock_name_com, mock_parse_args, mock_get, mock_get_external_ip):
        """
         Verify that the main logic works as expected when no host record is found.
         There is a change of IP address from when the current ip address intially read to first loop. Yet another loop and then a new IP at the last.
        """
                
        mock_get.side_effect = self.mock_get
        
        # Mock command-line arguments
        args = MagicMock()
        args.name = 'host1'
        args.domain = 'example.com'
        args.interval = 2
        args.test = True
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_name_com_instance = mock_name_com.return_value
        mock_name_com_instance.read_host_record.return_value = None
        
        mock_name_com_instance.create_record.return_value = 12345
        mock_name_com_instance.update_record.return_value = 12345

        try:
            name_dot_com_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'API_USERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'API_TOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_name_com.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_name_com_instance.read_host_record.assert_called_once()
        mock_name_com_instance.create_record.assert_called_once_with('1.2.3.5')
        # Check that update_record is called with the expected arguments
        update_calls = [call(12345, '1.2.3.4'), call(12345, '1.2.3.5')]
        mock_name_com_instance.update_record.assert_has_calls(update_calls)


if __name__ == '__main__':
    unittest.main()