import sys
import unittest
from unittest.mock import patch, MagicMock
from ftplib import FTP
from io import StringIO



def send_custom_command(host, username, password, command):

    # Create an FTP object and connect to the FTP server
    ftp = FTP(host)

    # Log in to the server with the provided username and password
    ftp.login(username, password)

    # Send the custom command to the server
    response = ftp.sendcmd(command)

    # Print the server's response to the custom command
    print("Server response: ", response)

    # Properly close the connection
    ftp.quit()


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


class TestSendCustomCommand(unittest.TestCase):

    @patch('__main__.FTP')  # Patch the FTP class in the module where send_custom_command is defined
    def test_send_custom_command(self, MockFTP):
        # Create a mock FTP object
        mock_ftp_instance = MagicMock()
        MockFTP.return_value = mock_ftp_instance

        # Define the expected response from the sendcmd method
        mock_ftp_instance.sendcmd.return_value = "200 Command okay"

        # Call the function with test parameters
        host = 'localhost'
        username = 'hudan'
        password = '123'
        command = 'FEAT'
        send_custom_command(host, username, password, command)

        # Check that FTP was instantiated with the correct host
        MockFTP.assert_called_with(host)
        
        # Check that login was called with the correct username and password
        mock_ftp_instance.login.assert_called_with(username, password)
        print(f"login called with {mock_ftp_instance.login.call_args}") 
        
        # Check that sendcmd was called with the correct command
        mock_ftp_instance.sendcmd.assert_called_with(command)
        print(f"sendcmd called with {mock_ftp_instance.sendcmd.call_args}")
        
        # Check that quit was called to close the connection
        mock_ftp_instance.quit.assert_called_once()
        print(f"quit called with {mock_ftp_instance.quit.call_args}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        # Example usage
        send_custom_command('localhost', 'hudan', '123', 'FEAT')
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)