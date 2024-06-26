from io import StringIO
import socket
import sys
import unittest
from unittest.mock import MagicMock, patch
import zlib

class FTPClient:
    def __init__(self, host='127.0.0.1', port=2000):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        """Connect to the FTP server."""
        # Connect to the FTP server
        self.sock.connect((self.host, self.port))

        # Receive the message
        response = self.sock.recv(1024)
        return response

    def send_command(self, command):
        """Send a command to the FTP server and compress it."""
        self.sock.sendall(zlib.compress((command + '\r\n').encode('utf-8')))
        response = self.sock.recv(1024)

        print(zlib.decompress(response).decode('utf-8'))

    def login(self, username, password):
        """Login to the FTP server."""
        # send USER command
        self.send_command("USER " + username)

        # send PASS command
        self.send_command("PASS " + password)

    def print_working_directory(self):
        """Print the current working directory."""
        self.send_command("PWD")

    def quit(self):
        """Quit the FTP server."""
        # quit command
        self.send_command("QUIT")

    def close(self):
        """Close the FTP connection."""
        self.sock.close()

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestFTPClient(unittest.TestCase):

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'220 Welcome to the FTP server\r\n')

        client = FTPClient()
        client.connect()
        
        mock_sock_instance.connect.assert_called_once_with(('127.0.0.1', 2000))
        print(f"connect called with {mock_sock_instance.connect.call_args}") 
        mock_sock_instance.recv.assert_called_once_with(1024)
        print(f"recv called with {mock_sock_instance.recv.call_args}")

    @patch('socket.socket')
    def test_send_command(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'331 Username OK, need password\r\n')

        client = FTPClient()
        client.connect()
        client.send_command("USER test")

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'USER test\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_print_working_directory(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'257 "/mock/directory"\r\n')

        client = FTPClient()
        client.connect()
        client.print_working_directory()

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'PWD\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_quit(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.return_value = zlib.compress(b'221 Goodbye\r\n')

        client = FTPClient()
        client.connect()
        client.quit()

        mock_sock_instance.sendall.assert_called_once_with(zlib.compress(b'QUIT\r\n'))
        print(f"sendall called with {mock_sock_instance.sendall.call_args}")
        mock_sock_instance.recv.assert_called_with(1024)

    @patch('socket.socket')
    def test_close(self, mock_socket):
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance

        client = FTPClient()
        client.connect()
        client.close()

        mock_sock_instance.close.assert_called_once()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        ftp_client = FTPClient()
        ftp_client.connect()
        ftp_client.login("user", "pass")
        ftp_client.print_working_directory()
        ftp_client.quit()
        ftp_client.close()
    
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
