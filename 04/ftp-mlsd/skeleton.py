from ftplib import FTP
from io import StringIO
import sys
import unittest
from unittest.mock import patch


def list_ftp_directory(host, username, password, directory):
    # Create an FTP object and connect to the FTP server
    ftp = FTP(host)
    print(ftp.getwelcome())
    
    # Log in to the server
    print(ftp.login(username, password))   

    # Use mlsd to get detailed list of files in the specified directory
    print(f"Contents of directory {directory}:")
    for name, facts in ftp.mlsd(directory):
        print(f"{name}:")
        for key, value in facts.items():
            print(f"  {key}: {value}")

    # Properly close the connection
    print(ftp.quit())


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestFTPListDirectory(unittest.TestCase):
    @patch('__main__.FTP')
    def test_list_ftp_directory(self, MockFTP):
        host = 'localhost'
        username = 'user'
        password = '123'
        directory = '/'
        expected_welcome_msg = "220-FileZilla Server 1.7.0\n220 Please visit https://filezilla-project.org/"
        expected_login_msg = "230 Login successful."
        expected_quit_msg = "221 Goodbye."

        # Set up the mock FTP object
        mock_ftp_instance = MockFTP.return_value
        mock_ftp_instance.getwelcome.return_value = expected_welcome_msg
        mock_ftp_instance.login.return_value = expected_login_msg
        mock_ftp_instance.mlsd.return_value = [
            ('file1.txt', {'type': 'file', 'size': '32', 'modify': '20210515094500', 'perms': 'awr'}),
            ('file2.txt', {'type': 'file', 'size': '174', 'modify': '20210516094500', 'perms': 'awr'}),
        ]
        mock_ftp_instance.quit.return_value = expected_quit_msg

        # Capture printed output
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            list_ftp_directory(host, username, password, directory)

            # Get printed output
            printed_output = mock_stdout.getvalue().strip().split('\n')

        # Define the expected output
        expected_output = [
            expected_welcome_msg.split('\n')[0],
            expected_welcome_msg.split('\n')[1],
            expected_login_msg,
            'Contents of directory /:',
            'file1.txt:',
            '  type: file',
            '  size: 32',
            '  modify: 20210515094500',
            '  perms: awr',
            'file2.txt:',
            '  type: file',
            '  size: 174',
            '  modify: 20210516094500',
            '  perms: awr',
            expected_quit_msg
        ]

        # Verify the mock FTP methods were called correctly
        MockFTP.assert_called_with(host)
        mock_ftp_instance.login.assert_called_with(username, password)
        print(f"login called with {mock_ftp_instance.login.call_args}") 

        mock_ftp_instance.mlsd.assert_called_with(directory)
        print(f"mlsd called with {mock_ftp_instance.mlsd.call_args}")
        mock_ftp_instance.quit.assert_called()

        # Verify the printed output
        assert_equal(printed_output[0], expected_output[0])
        assert_equal(printed_output[1], expected_output[1])
        assert_equal(printed_output[2], expected_output[2])
        assert_equal(printed_output[3], expected_output[3])
        assert_equal(printed_output[4], expected_output[4])
        assert_equal(printed_output[5], expected_output[5])
        assert_equal(printed_output[6], expected_output[6])
        assert_equal(printed_output[7], expected_output[7])
        assert_equal(printed_output[8], expected_output[8])
        assert_equal(printed_output[9], expected_output[9])
        assert_equal(printed_output[10], expected_output[10])


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        host = 'localhost'
        username = 'user'
        password = '123'
        directory = '.'
        list_ftp_directory(host, username, password, directory)

    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
