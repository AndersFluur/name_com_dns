import unittest
from unittest.mock import patch, MagicMock, call
from namecom_dns.namecom import get_resource_record
import os
import namecom_update

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
        if var_name == 'NAMECOM_APIUSERNAME':
            return 'api_username'
        if var_name == 'NAMECOM_APITOKEN':
            return 'api_token'
        else:
            return 'sample_value'
        
    @patch('namecom_update.get_external_ip')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('namecom_update.NameCom')
    def test_main_logic_rr_exist_new_IP(self, mock_namecom, mock_parse_args, mock_get, mock_get_external_ip):
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
        args.log = True
        args.logdir = os.getcwd()
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_namecom_instance = mock_namecom.return_value
        mock_namecom_instance.read_host_record.return_value = get_resource_record(id = 12345, host='host1', ip='1.2.3.4')
        
        #mock_namecom_instance.create_record.return_value = 12345
        mock_namecom_instance.update_record.return_value = 12345

        try:
            namecom_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'NAMECOM_APIUSERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'NAMECOM_APITOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_namecom.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_namecom_instance.read_host_record.assert_called_once()
        #mock_namecom_instance.create_record.assert_called_once_with('1.2.3.4')
        mock_namecom_instance.update_record.assert_called_once_with(12345, '1.2.3.5')
        mock_get_external_ip.assert_called()

    @patch('namecom_update.get_external_ip')
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('namecom_update.NameCom')
    def test_main_logic_no_rr_same_ip_address(self, mock_namecom, mock_parse_args, mock_get, mock_get_external_ip):
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
        args.log = True
        args.logdir = os.getcwd()
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_namecom_instance = mock_namecom.return_value
        mock_namecom_instance.read_host_record.return_value = None
        
        mock_namecom_instance.create_record.return_value = 12345
        mock_namecom_instance.update_record.return_value = 12345

        try:
            namecom_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'NAMECOM_APIUSERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'NAMECOM_APITOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_namecom.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_namecom_instance.read_host_record.assert_called_once()
        mock_namecom_instance.create_record.assert_called_once_with('1.2.3.5')
        #mock_namecom_instance.update_record.assert_called_once_with(12345, '1.2.3.5')
        mock_get_external_ip.assert_called()

    @patch('namecom_update.get_external_ip', side_effect=['1.2.3.5', '1.2.3.4', '1.2.3.4', '1.2.3.5'])
    @patch('os.environ.get')
    @patch('argparse.ArgumentParser.parse_args')
    @patch('namecom_update.NameCom')
    def test_main_logic_no_rr_change_ip_address(self, mock_namecom, mock_parse_args, mock_get, mock_get_external_ip):
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
        args.log = True
        args.logdir = os.getcwd()
        mock_parse_args.return_value = args

        # Mock NameCom class and its methods
        mock_namecom_instance = mock_namecom.return_value
        mock_namecom_instance.read_host_record.return_value = None
        
        mock_namecom_instance.create_record.return_value = 12345
        mock_namecom_instance.update_record.return_value = 12345

        try:
            namecom_update.main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # assert that the exit code is 0
    
        calls = mock_get.call_args_list
        api_username_calls = [call for call in calls if call[0][0] == 'NAMECOM_APIUSERNAME']
        api_token_calls = [call for call in calls if call[0][0] == 'NAMECOM_APITOKEN']
        self.assertEqual(len(api_username_calls), 1)
        self.assertEqual(len(api_token_calls), 1)

        # Assert that the methods were called with the correct arguments
        mock_namecom.assert_called_with('api_username', 'api_token', 'example.com', 'host1')
        mock_namecom_instance.read_host_record.assert_called_once()
        mock_namecom_instance.create_record.assert_called_once_with('1.2.3.5')
        # Check that update_record is called with the expected arguments
        update_calls = [call(12345, '1.2.3.4'), call(12345, '1.2.3.5')]
        mock_namecom_instance.update_record.assert_has_calls(update_calls)


if __name__ == '__main__':
    unittest.main()