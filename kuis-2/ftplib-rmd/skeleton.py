import sys
import unittest
from unittest.mock import patch, MagicMock
from ftplib import FTP
from io import StringIO


def remove_directory(host, username, password, directory_to_remove):
    # Create an FTP object and connect to the FTP server
    ftp = FTP(host)

    # Log in to the server
    ftp.login(username, password)

    # Remove the directory
    try:
        ftp.rmd(directory_to_remove)
        print(f"Directory '{directory_to_remove}' has been removed successfully.")
    except Exception as e:
        print(f"Failed to remove directory: {e}")

    # Properly close the connection
    ftp.quit()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestRemoveDirectory(unittest.TestCase):

    @patch('__main__.FTP')
    def test_remove_directory_success(self, mock_ftp_class):
        # Create a mock FTP instance
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp

        # Call the function to test
        remove_directory('localhost', 'hudan', '123', '/new_folder')

        # Assertions to check if the methods were called correctly
        mock_ftp.login.assert_called_once_with('hudan', '123')
        print(f"login called with {mock_ftp.login.call_args}") 
        mock_ftp.rmd.assert_called_once_with('/new_folder')
        print(f"rmd called with {mock_ftp.rmd.call_args}")
        mock_ftp.quit.assert_called_once()
        print(f"quit called with {mock_ftp.quit.call_args}")

    @patch('__main__.FTP')
    # @patch('builtins.print')  # Mock the print function
    def test_remove_directory_failure(self, mock_ftp_class):
        # Create a mock FTP instance
        mock_ftp = MagicMock()
        mock_ftp_class.return_value = mock_ftp

        # Configure the mock to raise an exception when rmd is called
        mock_ftp.rmd.side_effect = Exception('Failed to remove directory')

        # Call the function to test
        remove_directory('localhost', 'hudan', '123', '/new_folder')

        # Assertions to check if the methods were called correctly
        mock_ftp.login.assert_called_once_with('hudan', '123')
        print(f"login called with {mock_ftp.login.call_args}") 
        mock_ftp.rmd.assert_called_once_with('/new_folder')
        print(f"rmd called with {mock_ftp.rmd.call_args}")
        mock_ftp.quit.assert_called_once()
        print(f"quit called with {mock_ftp.quit.call_args}")


# Usage example
if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        host = 'localhost'
        username = 'hudan'
        password = '123'
        directory_to_remove = '/new_folder'

        remove_directory(host, username, password, directory_to_remove)
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
