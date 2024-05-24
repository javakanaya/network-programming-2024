from ftplib import FTP
from io import StringIO
import sys
import unittest
from unittest.mock import MagicMock, patch


def rename_file_on_ftp(host, username, password, old_file_name, new_file_name):

    # Create an FTP object and connect to the FTP server
    ftp = FTP(host)
    
    # Log in to the server
    print(ftp.login(username, password))   

    # Use rename to change the file name on the server
    ftp.rename(old_file_name, new_file_name)

    # Properly close the connection
    print(ftp.quit())

    # Return a confirmation message
    return f"The file {old_file_name} has been renamed to {new_file_name}."


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestRenameFileOnFTP(unittest.TestCase):
    @patch('__main__.FTP')  # Replace 'your_module' with the name of your module
    def test_rename_file_on_ftp(self, MockFTP):
        # Create a mock FTP object
        mock_ftp_instance = MockFTP.return_value

        # Define the test parameters
        host = 'localhost'
        username = 'user'
        password = '123'
        old_file_name = 'upload.txt'
        new_file_name = 'new-upload.txt'

        mock_ftp_instance.login.return_value = "230 Login successful."
        mock_ftp_instance.quit.return_value = "221 Goodbye."

        # Call the function with the test parameters
        result = rename_file_on_ftp(host, username, password, old_file_name, new_file_name)

        # Check if the FTP methods were called with the correct parameters
        MockFTP.assert_called_with(host)
        mock_ftp_instance.login.assert_called_with(username, password)
        print(f"login called with {mock_ftp_instance.login.call_args}") 

        mock_ftp_instance.rename.assert_called_with(old_file_name, new_file_name)
        mock_ftp_instance.quit.assert_called()

        # Check the return value
        expected_result = f"The file {old_file_name} has been renamed to {new_file_name}."
        assert_equal(result, expected_result)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        # Usage example
        host = 'localhost'
        username = 'user'
        password = '123'
        old_file_name = 'upload.txt'
        new_file_name = 'new-upload.txt'

        result = rename_file_on_ftp(host, username, password, old_file_name, new_file_name)
        print(result)
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
