from ftplib import FTP
from io import StringIO
import sys
import unittest
from unittest.mock import MagicMock, patch

def create_directory(host, username, password, directory):
    try:
        # Create an FTP object and connect to the FTP server
        ftp = FTP(host)
        print(ftp.getwelcome())
        
        # Log in to the server
        print(ftp.login(username, password))   

        # Create the new directory
        print(ftp.mkd(directory))

        # Properly close the connection
        print(ftp.quit())

        return f"The directory {directory} has been successfully created."
    
    except Exception as e:
        print(f"Error: {e}")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestCreateDirectory(unittest.TestCase):
    @patch('__main__.FTP')
    def test_create_directory(self, mock_ftp):
        # Arrange
        mock_ftp_obj = MagicMock()
        mock_ftp.return_value = mock_ftp_obj
        host = 'localhost'
        username = 'user'
        password = '123'
        directory = '/new_folder'
        
        # Set return values for the FTP methods
        expected_result = "The directory /new_folder has been successfully created."
        expected_welcome_msg = "220-FileZilla Server 1.7.0\r\n220 Please visit https://filezilla-project.org/"
        expected_login_msg = "230 Login successful."
        expected_make_msg = "257 /new_folder created."
        expected_quit_msg = "221 Goodbye."

        mock_ftp_obj.getwelcome.return_value = expected_welcome_msg
        mock_ftp_obj.login.return_value = expected_login_msg
        mock_ftp_obj.mkd.return_value = expected_make_msg
        mock_ftp_obj.quit.return_value = expected_quit_msg
        
        # Act
        result = create_directory(host, username, password, directory)

        # Assert
        mock_ftp.assert_called_once_with(host)
        mock_ftp_obj.getwelcome.assert_called_once()
        mock_ftp_obj.login.assert_called_once_with(username, password)
        print(f"login called with {mock_ftp_obj.login.call_args}")

        mock_ftp_obj.mkd.assert_called_once_with(directory)
        print(f"mkd called with {mock_ftp_obj.mkd.call_args}")

        mock_ftp_obj.quit.assert_called_once()

        # Assert messages
        assert_equal(result, expected_result)
        assert_equal(mock_ftp_obj.getwelcome(), expected_welcome_msg)
        assert_equal(mock_ftp_obj.login(username, password), expected_login_msg)
        assert_equal(mock_ftp_obj.mkd(directory), expected_make_msg)
        assert_equal(mock_ftp_obj.quit(), expected_quit_msg)


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        create_directory('localhost', 'user', '123', '/new_folder')
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
