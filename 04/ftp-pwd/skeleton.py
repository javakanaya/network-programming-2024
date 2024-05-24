from ftplib import FTP
from io import StringIO
import sys
import unittest
from unittest.mock import MagicMock, patch


def get_current_directory(host, username, password):
    # Create an FTP object and connect to the FTP server
    ftp = FTP(host)
    
    # Log in to the server
    print(ftp.login(username, password))   

    # Get the current working directory
    current_directory = ftp.pwd()
    print("current directory: ", current_directory)

    # Close the connection
    print(ftp.quit())

    return current_directory


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestGetCurrentDirectory(unittest.TestCase):
    @patch('__main__.FTP')  # Mock the FTP class in your_module
    def test_get_current_directory(self, MockFTP):
        # Create a mock FTP instance
        mock_ftp_instance = MagicMock()
        MockFTP.return_value = mock_ftp_instance

        # Set up the return values for the mock methods
        mock_ftp_instance.login.return_value = "230 Login successful."
        mock_ftp_instance.pwd.return_value = "/home/user"
        mock_ftp_instance.quit.return_value = "221 Goodbye."

        # Call the function with test credentials
        host = "localhost"
        username = "user"
        password = "123"
        current_directory = get_current_directory(host, username, password)

        # Assert that the FTP methods were called correctly
        MockFTP.assert_called_once_with(host)
        mock_ftp_instance.login.assert_called_once_with(username, password)
        print(f"login called with {mock_ftp_instance.login.call_args}") 

        mock_ftp_instance.pwd.assert_called_once()
        mock_ftp_instance.quit.assert_called_once()

        # Assert that the function returns the expected directory
        assert_equal(current_directory, "/home/user")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        # Call the function and print the result
        get_current_directory('localhost', 'user', '123')
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)